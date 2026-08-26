# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- **Phase 2: State, Action, and Reward Design** integrated into Godot:
  - `player.gd` now exports a 4-dimensional state (position, grounded, distances to nearest apple and enemy) and accepts 6 discrete RL actions.
  - `apple.gd` assigns a +10 reward upon collection.
  - `player.gd` assigns a -10 penalty on death (falling or enemy collision).
  - `main.gd` orchestrates the RL step by sending the state and pausing the game until an action is received via `RLBridge`.
- Conda `environment.yml` with `websockets`, `jupyter`, and `pytorch` dependencies.
- Godot 4.x WebSocket client (`rl_bridge.gd`) as an Autoload to communicate with Python.
- Python Jupyter notebook (`dqn-src/DQN_Agent.ipynb`) with an async WebSocket server `GodotEnv`.
- `GOALS.md` to track project progress towards training the DQN agent.
- `CHANGELOG.md` to document project changes.
