# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- **Hyperband hyperparameter search in `0. Hyperparameter Optimization.py`**: replaced the exhaustive 100-trial random search with a successive-halving (Hyperband) strategy that tests 27 configurations cheaply and progressively invests more episodes in the best third (`27 → 9 → 3 → 1` configs at `4 / 15 / 48 / 100` training episodes). Supports multiple independent parallel runs (default 3, `--runs` / `--sequential` / `--base-port` CLI flags), per-rung logging to `hyperband_run_<n>.csv`, and a per-run winner (`best_config_run_<n>.json`, `best_dqn_model_run_<n>.pth`) plus a global best summary in `hyperband_summary.csv`.
- **Per-port WebSocket configuration in Godot**: `rl_bridge.gd` accepts an `--rl-port <port>` command-line user argument (defaults to 11000) so multiple parallel optimizer runs can each talk to their own Godot instance.
- **Phase 3: DQN Agent Implementation (Python)**:
  - `dqn_model.py`: PyTorch `QNetwork` implementation for function approximation.
  - `replay_buffer.py`: `ReplayBuffer` class for storing and sampling experience transitions.
  - `dqn_agent.py`: `DQNAgent` class encapsulating target network syncing, epsilon-greedy action selection, and Huber loss optimization.
  - `1. Create DQN Agent.ipynb`: Fully integrated asynchronous training loop, combining the websocket server and modular DQN logic, complete with live `matplotlib` metric plotting.
- **Phase 4 & 5: Advanced Training & Evaluation (Python)**:
  - `dqn_agent.py` & `dqn_model.py`: Upgraded architecture to 128 hidden units, Huber Loss (`SmoothL1Loss`), gradient clipping, and step-based epsilon decay.
  - Custom metrics loop added to `test_agent()` to report Completion Rate, Snail Avoidance, and Average Distance.
- **Phase 2: State, Action, and Reward Design** integrated into Godot:
  - `player.gd` now exports a 9-dimensional state (position, velocity, grounded, (dx, dy) to nearest apple and enemy) and accepts 6 discrete RL actions.
  - `apple.gd` assigns a +10 score upon collection, and `main.gd` grants a +10 completion bonus upon eating 2 apples.
  - Continuous delta-distance reward shaping implemented in `main.gd` to guide the agent.
  - `player.gd` assigns a -10 penalty on death (falling or enemy collision).
  - `main.gd` orchestrates the RL step by utilizing a 4-frame action repeat (Frame Skip) to reduce jitter and improve exploration.
- Conda `environment.yml` with `websockets`, `jupyter`, and `pytorch` dependencies.
- Godot 4.x WebSocket client (`rl_bridge.gd`) as an Autoload to communicate with Python, featuring a robust 1-second debounce reconnect timer.
- Python Jupyter notebook (`dqn-src/1. Create DQN Agent.ipynb`) with an async WebSocket server `GodotEnv` (now with platform-agnostic paths and robust cleanup logic).
- `GOALS.md` to track project progress towards training the DQN agent.
- `CHANGELOG.md` to document project changes.

### Fixed
- **Plot output wiping status lines**: `plot_metrics` now updates the figure in place (`display_id`) instead of calling `clear_output`, so the printed episode metrics lines remain visible during training.
- **Checkpoint clobbering on aborted runs**: `train()` now only overwrites `dqn_model.pth` when all episodes complete or training is interrupted manually. A Godot disconnect mid-run no longer destroys a good model.
- **Unhandled crash on incompatible checkpoints**: `test_agent()` now catches weight-loading failures (e.g. stale or wrong-architecture `.pth` files) and evaluates an untrained agent with a warning instead of crashing.
- **Null-tree errors during scene transitions**: `main.gd` guards `_on_action_received` and `_on_reset_requested` with `is_inside_tree()` so messages arriving mid-reload no longer spam errors or get dropped.
- **Stray Godot cleanup**: `train()`, `test_agent()`, and `0. Hyperparameter Optimization.py` now kill orphaned headless Godot processes of this project before launching, so a hard-killed kernel cannot leave a zombie game that hijacks the WebSocket connection.
- **State tuple unpacking**: `GodotEnv.step()` failure path returned a mismatched tuple; now returns a consistent 5-tuple.
- **Score pollution by reward shaping**: `RLBridge` now separates `add_score()` from `add_reward()` so delta-distance shaping no longer counts toward the 2-apple completion condition or the evaluation metrics.
- **Double state-sending on player death**: the game tree pauses immediately on death and `main.gd` suppresses duplicate terminal states via a `_sent_terminal` flag.
- **First-episode deadlock**: `main.gd` now wires the `action_received`/`reset_requested` signals unconditionally, since the WebSocket handshake hasn't finished when the scene loads.
- **Spurious negative shaping on apple collection**: `apple.gd` resets the tracked distance so switching to the next apple target doesn't penalize the agent.
- **Epsilon decay start value**: `DQNAgent` now decays from the configured `epsilon_start` instead of a hardcoded 1.0, and guards against malformed/empty states.
- **Silent garbage runs on disconnect**: training and evaluation now raise a clear error when Godot disconnects mid-run instead of completing hundreds of empty episodes and overwriting the model.
- **WebSocket send failures**: `step()`/`reset()` handle `ConnectionClosed` gracefully.
- **Missing model warning**: `test_agent()` prints a warning when no trained weights exist.
- **Process cleanup**: `godot_process` is guarded against `UnboundLocalError` if the Godot launch fails.
- **Manual play**: player death now pauses the game only when connected to the RL server, so manual play is unaffected.
- `dqn-src/.gitignore` converted from UTF-16 to UTF-8 so Git parses it correctly.
