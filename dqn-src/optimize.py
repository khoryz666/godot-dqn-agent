import asyncio
import csv
import websockets
import json
import numpy as np
import subprocess
import os
import time
import random
import torch
from datetime import datetime

from dqn_agent import DQNAgent

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
        print(f"WebSocket server started at ws://{self.host}:{self.port}")

    async def stop_server(self):
        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
            print("WebSocket server stopped.")

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

async def wait_for_godot(env: GodotEnv, timeout: float = 30.0):
    start = time.time()
    while env.websocket is None:
        if time.time() - start > timeout:
            raise RuntimeError("Godot did not connect in time.")
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
                print(f"Cleaned up {len(pids)} stray headless Godot process(es).")
        except Exception as e:
            print(f"Warning: stray Godot cleanup failed: {e}")
    else:
        try:
            subprocess.run(["pkill", "-f", "godot.*--headless.*" + project_path],
                           capture_output=True, timeout=10)
        except Exception:
            pass

async def evaluate_agent(agent, env, num_episodes=20):
    """Evaluates the agent deterministically."""
    # Temporarily set epsilon to 0 for evaluation
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
            if step_count > 1000:
                break
                
        if env.websocket is None:
            raise RuntimeError("Godot disconnected during evaluation.")
        total_score += score
        if cause_of_death == "completed":
            completed += 1
            
    agent.policy_net.train()
    agent.epsilon = old_epsilon # restore epsilon
    return total_score / num_episodes, completed / num_episodes

async def run_trial(config, trial_id, godot_exe, project_path):
    print(f"\n--- Starting Trial {trial_id} ---")
    print(f"Config: {config}")
    
    state_size = 9
    action_size = 6
    agent = DQNAgent(state_size, action_size, config)
    env = GodotEnv()
    
    try:
        await env.start_server()
    except RuntimeError as e:
        print(f"Trial {trial_id} failed to start server: {e}")
        return -float('inf'), None
    
    godot_process = None
    best_eval_score = -float('inf')
    
    try:
        cleanup_stray_godot(project_path)
        godot_process = subprocess.Popen([godot_exe, "--headless", "--path", project_path])
        await wait_for_godot(env)
        
        num_episodes = 400 # Training episodes per trial
        
        for episode in range(num_episodes):
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
                if step_count > 1000:
                    done = True

            if env.websocket is None:
                raise RuntimeError("Godot disconnected during trial.")
                    
            # Evaluate every 100 episodes
            if (episode + 1) % 100 == 0:
                avg_score, comp_rate = await evaluate_agent(agent, env, num_episodes=15)
                print(f"Trial {trial_id} | Ep {episode+1}/{num_episodes} | Eval Score: {avg_score:.2f} | Completion: {comp_rate*100:.1f}%")
                if avg_score > best_eval_score:
                    best_eval_score = avg_score
                    
    except Exception as e:
        print(f"Trial {trial_id} failed: {e}")
    finally:
        if godot_process is not None:
            godot_process.terminate()
        await env.stop_server()
        
    return best_eval_score, agent

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

async def main():
    godot_exe = "godot" if os.name == "posix" else os.path.expanduser(r"~\scoop\apps\godot\current\godot.console.exe")
    project_path = os.path.abspath(os.path.join("..", "godot-src"))
    
    num_trials = 100 # Can run for 48 hours depending on episode speed
    best_overall_score = -float('inf')
    best_config = None
    
    print("Starting 48-Hour Automated Hyperparameter Search...")
    
    tested_configs = set()
    
    for trial in range(1, num_trials + 1):
        if len(tested_configs) >= 324:
            print("All 324 unique combinations have been exhausted. Ending search early.")
            break
            
        while True:
            config = generate_random_config()
            config_str = json.dumps(config, sort_keys=True)
            if config_str not in tested_configs:
                tested_configs.add(config_str)
                break
                
        score, agent = await run_trial(config, trial, godot_exe, project_path)
        
        if score > best_overall_score:
            best_overall_score = score
            best_config = config
            print(f">>> NEW BEST SCORE: {score:.2f} <<<")
            
            # Save best model and config
            torch.save(agent.policy_net.state_dict(), "best_dqn_model.pth")
            with open("best_config.json", "w") as f:
                json.dump(best_config, f, indent=4)
                
        print(f"--- Trial {trial} Finished. Current Best Score: {best_overall_score:.2f} ---")
        
        # Log to CSV
        with open("search_results.csv", "a", newline="") as f:
            csv.writer(f).writerow([datetime.now().isoformat(), trial, score, json.dumps(config)])

if __name__ == "__main__":
    # Create CSV header if it doesn't exist
    if not os.path.exists("search_results.csv"):
        with open("search_results.csv", "w", newline="") as f:
            csv.writer(f).writerow(["timestamp", "trial", "best_eval_score", "config"])
            
    asyncio.run(main())
