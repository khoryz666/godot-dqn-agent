import argparse
import asyncio
import csv
import json
import os
import random
import subprocess
import time
import torch
import websockets
from datetime import datetime

from dqn_agent import DQNAgent

STATE_SIZE = 9
ACTION_SIZE = 6
MAX_STEPS_PER_EPISODE = 1000

HYPERBAND_BUDGETS = [4, 15, 48, 100]
HYPERBAND_CONFIGS = [27, 9, 3, 1]
HYPERBAND_EVAL_EPS = [3, 5, 8, 12]


class GodotEnv:
    def __init__(self, host='127.0.0.1', port=11000):
        self.host = host
        self.port = port
        self.server = None
        self.websocket = None
        self.last_state = []
        self.last_reward = 0.0
        self.last_done = False
        self.last_score = 0.0
        self.last_info = {}
        self.response_event = asyncio.Event()

    async def start_server(self):
        try:
            self.server = await websockets.serve(self.handler, self.host, self.port)
        except OSError as e:
            raise RuntimeError(f"Failed to bind ws://{self.host}:{self.port}") from e
        print(f"WebSocket server started at ws://{self.host}:{self.port}", flush=True)

    async def stop_server(self):
        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
            print(f"WebSocket server on port {self.port} stopped.", flush=True)

    async def handler(self, websocket, path=None):
        self.websocket = websocket
        try:
            async for message in websocket:
                data = json.loads(message)
                self.last_state = data.get('state', [])
                self.last_reward = data.get('reward', 0.0)
                self.last_done = data.get('done', False)
                self.last_score = data.get('score', 0.0)
                self.last_info = data.get('info', {})
                self.response_event.set()
        except websockets.exceptions.ConnectionClosed:
            self.websocket = None
            self.response_event.set()

    async def step(self, action: int):
        if self.websocket:
            self.response_event.clear()
            await self.websocket.send(json.dumps({"action": action}))
            if await self._wait_for_response():
                return self.last_state, self.last_reward, self.last_done, self.last_score, self.last_info
        return [], 0.0, True, 0.0, {}

    async def reset(self):
        if self.websocket:
            self.response_event.clear()
            await self.websocket.send(json.dumps({"command": "reset"}))
            if await self._wait_for_response():
                return self.last_state
        return []

    async def _wait_for_response(self, timeout: float = 30.0) -> bool:
        try:
            await asyncio.wait_for(self.response_event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            self.websocket = None
            return False


async def wait_for_godot(env: GodotEnv, timeout: float = 60.0):
    start = time.time()
    while env.websocket is None:
        if time.time() - start > timeout:
            raise RuntimeError(f"Godot did not connect in time (port {env.port}).")
        await asyncio.sleep(0.5)


def cleanup_stray_godot(project_path: str):
    """Kill orphaned headless Godot instances of this project (left behind by a
    hard-killed process) so they cannot hijack the WebSocket connection."""
    if os.name == "nt":
        try:
            ps = ("Get-CimInstance Win32_Process | Where-Object { "
                  "$_.Name -in @('godot.console.exe','godot.exe') -and "
                  "$_.CommandLine -match '--headless' -and "
                  "$_.CommandLine -match [regex]::Escape('" + project_path + "') } | "
                  "Select-Object -ExpandProperty ProcessId")
            result = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                                    capture_output=True, text=True, timeout=30)
            pids = [p.strip() for p in result.stdout.split() if p.strip().isdigit()]
            for pid in pids:
                subprocess.run(["taskkill", "/PID", pid, "/T", "/F"],
                               capture_output=True, timeout=10)
            if pids:
                print(f"Cleaned up {len(pids)} stray headless Godot process(es).", flush=True)
        except Exception as e:
            print(f"Warning: stray Godot cleanup failed: {e}", flush=True)
    else:
        try:
            subprocess.run(["pkill", "-f", "godot.*--headless.*" + project_path],
                           capture_output=True, timeout=10)
        except Exception:
            pass


async def evaluate_agent(agent, env, num_episodes=10):
    """Evaluates the agent deterministically. Returns (avg_score, completion_rate)."""
    old_epsilon = agent.epsilon
    agent.epsilon = 0.0
    agent.policy_net.eval()

    total_score = 0.0
    completed = 0

    for _ in range(num_episodes):
        state = await env.reset()
        done = False
        step_count = 0
        cause_of_death = ""
        score = 0.0

        while not done and env.websocket is not None:
            action = agent.get_action(state)
            next_state, reward, done, score, info = await env.step(action)
            state = next_state
            step_count += 1
            if info.get("cause_of_death", "") != "":
                cause_of_death = info.get("cause_of_death", "")
            if step_count > MAX_STEPS_PER_EPISODE:
                break

        if env.websocket is None:
            raise RuntimeError("Godot disconnected during evaluation.")
        total_score += score
        if cause_of_death == "completed":
            completed += 1

    agent.policy_net.train()
    agent.epsilon = old_epsilon
    return total_score / num_episodes, completed / num_episodes


async def train_episodes(agent, env, num_episodes):
    """Trains the agent for a given number of episodes using the live connection."""
    for _ in range(num_episodes):
        state = await env.reset()
        done = False
        step_count = 0

        while not done and env.websocket is not None:
            action = agent.get_action(state)
            next_state, reward, done, score, info = await env.step(action)

            agent.memory.add(state, action, reward, next_state, done)
            agent.train_step()
            agent.update_epsilon()

            if agent.total_steps % 1000 == 0:
                agent.update_target_network()

            state = next_state
            step_count += 1
            if step_count > MAX_STEPS_PER_EPISODE:
                done = True

        if env.websocket is None:
            raise ConnectionError("Godot disconnected during training.")


def generate_random_config():
    return {
        "gamma": random.choice([0.99, 0.95, 0.90]),
        "epsilon_start": 1.0,
        "epsilon_min": random.choice([0.01, 0.05]),
        "epsilon_decay_steps": random.choice([20000, 40000, 60000]),
        "batch_size": random.choice([32, 64, 128]),
        "learning_rate": random.choice([1e-3, 5e-4, 1e-4]),
        "buffer_size": random.choice([50000, 100000])
    }


def unique_configs(n, used):
    configs = []
    while len(configs) < n:
        config = generate_random_config()
        key = json.dumps(config, sort_keys=True)
        if key in used:
            continue
        used.add(key)
        configs.append(config)
    return configs


async def run_hyperband(run_id, godot_exe, project_path, port,
                        budgets=HYPERBAND_BUDGETS,
                        n_configs=HYPERBAND_CONFIGS,
                        eval_eps=HYPERBAND_EVAL_EPS):
    """One full Hyperband (successive halving) search. Returns a summary dict."""
    start_time = time.time()
    log_path = f"hyperband_run_{run_id}.csv"
    with open(log_path, "w", newline="") as f:
        csv.writer(f).writerow(["timestamp", "run_id", "rung", "rank",
                                "budget_spent", "eval_score", "completion_rate",
                                "promoted", "config"])

    env = GodotEnv(port=port)
    try:
        await env.start_server()
    except RuntimeError as e:
        print(f"[Run {run_id}] failed to start server: {e}", flush=True)
        return None

    godot_process = None
    used_configs = set()
    survivors = [{"config": c, "agent": DQNAgent(STATE_SIZE, ACTION_SIZE, c),
                  "budget_spent": 0} for c in unique_configs(n_configs[0], used_configs)]

    def launch_godot():
        return subprocess.Popen([godot_exe, "--headless", "--path", project_path,
                                 "--", "--rl-port", str(port)])

    async def ensure_godot():
        nonlocal godot_process
        if env.websocket is not None:
            return
        if godot_process is not None:
            try:
                godot_process.terminate()
            except Exception:
                pass
            godot_process = None
        godot_process = launch_godot()
        await wait_for_godot(env)

    try:
        await ensure_godot()
        print(f"[Run {run_id}] Godot connected on port {port}. "
              f"Starting Hyperband: {n_configs} configs, budgets {budgets}.", flush=True)

        for rung in range(len(budgets)):
            budget_target = budgets[rung]
            for entry in survivors:
                extra = budget_target - entry["budget_spent"]
                if extra > 0:
                    try:
                        await ensure_godot()
                        await train_episodes(entry["agent"], env, extra)
                        entry["budget_spent"] = budget_target
                    except (ConnectionError, RuntimeError) as e:
                        print(f"[Run {run_id}] Rung {rung}: config "
                              f"{entry['config']} training failed ({e}); dropping.", flush=True)
                        entry["budget_spent"] = -1
                        env.websocket = None

            rows = []
            for entry in survivors:
                if entry["budget_spent"] < 0:
                    rows.append({**entry, "score": -float("inf"), "comp": 0.0})
                    continue
                try:
                    await ensure_godot()
                    score, comp = await evaluate_agent(entry["agent"], env, eval_eps[rung])
                except (RuntimeError, ConnectionError) as e:
                    print(f"[Run {run_id}] Rung {rung}: eval failed for "
                          f"{entry['config']} ({e}); dropping.", flush=True)
                    score, comp = -float("inf"), 0.0
                    env.websocket = None
                rows.append({**entry, "score": score, "comp": comp})

            rows.sort(key=lambda r: r["score"], reverse=True)
            keep = min(n_configs[rung], len(rows)) if rung + 1 < len(n_configs) else 1
            promoted = {id(r) for r in rows[:keep]}

            with open(log_path, "a", newline="") as f:
                writer = csv.writer(f)
                for rank, r in enumerate(rows):
                    is_promoted = 1 if id(r) in promoted else 0
                    writer.writerow([datetime.now().isoformat(), run_id, rung, rank + 1,
                                     r["budget_spent"], r["score"], f"{r['comp']*100:.1f}",
                                     is_promoted, json.dumps(r["config"])])
                    print(f"[Run {run_id}] Rung {rung} | rank {rank+1} | "
                          f"budget {r['budget_spent']}/{budget_target} | "
                          f"score {r['score']:.2f} | comp {r['comp']*100:.1f}% | "
                          f"promoted={is_promoted}", flush=True)

            survivors = [r for r in rows[:keep]]
            print(f"[Run {run_id}] Rung {rung} done. "
                  f"{keep} config(s) advanced to next rung.", flush=True)

        winner = survivors[0]
        if winner["budget_spent"] <= 0:
            raise RuntimeError("All configs failed; no winner.")

        score, comp = winner["score"], winner["comp"]
        torch.save(winner["agent"].policy_net.state_dict(),
                   f"best_dqn_model_run_{run_id}.pth")
        with open(f"best_config_run_{run_id}.json", "w") as f:
            json.dump(winner["config"], f, indent=4)

        duration = time.time() - start_time
        print(f"[Run {run_id}] WINNER: {winner['config']} | "
              f"score {score:.2f} | comp {comp*100:.1f}% | "
              f"duration {duration/3600:.2f}h", flush=True)
        return {"run_id": run_id, "best_score": score, "completion_rate": comp,
                "config": winner["config"], "duration_s": duration}

    finally:
        if godot_process is not None:
            try:
                godot_process.terminate()
            except Exception:
                pass
        await env.stop_server()


def update_global_best(summary, run_id):
    if summary is None:
        return
    best_path = "best_config.json"
    replace = True
    if os.path.exists(best_path):
        with open(best_path) as f:
            old = json.load(f)
        replace = old.get("_best_score", -float("inf")) < summary["best_score"]
    if replace:
        with open(best_path, "w") as f:
            json.dump({**summary["config"], "_best_score": summary["best_score"],
                       "_run_id": run_id}, f, indent=4)
        model_src = f"best_dqn_model_run_{run_id}.pth"
        if os.path.exists(model_src):
            with open(model_src, "rb") as src, open("best_dqn_model.pth", "wb") as dst:
                dst.write(src.read())
        print(f"[Run {run_id}] NEW GLOBAL BEST: {summary['best_score']:.2f}", flush=True)


async def main():
    parser = argparse.ArgumentParser(description="Hyperband hyperparameter search for DQN agent.")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--base-port", type=int, default=11000)
    parser.add_argument("--sequential", action="store_true",
                        help="Run searches one after another instead of in parallel.")
    args = parser.parse_args()

    godot_exe = ("godot" if os.name == "posix" else
                 os.path.expanduser(r"~\scoop\apps\godot\current\godot.console.exe"))
    project_path = os.path.abspath(os.path.join("..", "godot-src"))

    cleanup_stray_godot(project_path)

    if not os.path.exists("hyperband_summary.csv"):
        with open("hyperband_summary.csv", "w", newline="") as f:
            csv.writer(f).writerow(["timestamp", "run_id", "best_eval_score",
                                    "completion_rate", "duration_s", "config"])

    print(f"Starting Hyperband search: {args.runs} run(s), "
          f"budgets {HYPERBAND_BUDGETS}, configs {HYPERBAND_CONFIGS}.", flush=True)

    async def execute(run_id):
        try:
            summary = await run_hyperband(run_id, godot_exe, project_path,
                                          args.base_port + run_id - 1)
        except Exception as e:
            print(f"[Run {run_id}] crashed: {e}", flush=True)
            summary = None
        with open("hyperband_summary.csv", "a", newline="") as f:
            csv.writer(f).writerow([datetime.now().isoformat(), run_id,
                                    summary["best_score"] if summary else -float("inf"),
                                    f"{summary['completion_rate']*100:.1f}" if summary else "0.0",
                                    f"{summary['duration_s']:.0f}" if summary else "0",
                                    json.dumps(summary["config"]) if summary else "{}"])
        update_global_best(summary, run_id)
        return summary

    if args.sequential:
        for run_id in range(1, args.runs + 1):
            await execute(run_id)
    else:
        await asyncio.gather(*[execute(run_id) for run_id in range(1, args.runs + 1)])

    print("Hyperband search finished. See hyperband_summary.csv and "
          "hyperband_run_*.csv for outcomes.", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
