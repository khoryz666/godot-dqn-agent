# Project Goals: Godot 2D Platformer DQN Agent

This document outlines the step-by-step goals for successfully training a Deep Q-Network (DQN) agent to play the Godot 2D Platform Collector Game.

## Phase 1: Environment Setup & Interface (Godot ↔ Python)
- [ ] Establish communication bridge between Godot game and Python environment (e.g., sockets, ZeroMQ, or Godot RL Agents).
- [ ] Expose Godot environment API to receive actions and return `(next_state, reward, done_status, score)`.

## Phase 2: State, Action, and Reward Design
- [ ] Define the discrete action space (0: Do nothing, 1: Move right, 2: Move left, 3: Jump, 4: Move right + jump, 5: Move left + jump).
- [ ] Define the state representation (player position, grounded flag, distances to rewards/enemies, raycast distances).
- [ ] Define the reward function (positive for progress/collecting, negative for enemies/falling, step penalty).

## Phase 3: DQN Agent Implementation (Python)
- [ ] Initialize the Q-Network (PyTorch or TensorFlow).
- [ ] Implement the Target Network for stability.
- [ ] Implement the Experience Replay buffer.
- [ ] Implement Epsilon-Greedy strategy with epsilon decay for exploration.

## Phase 4: Training & Hyperparameter Tuning
- [ ] Implement the training loop connecting the Python agent to Godot.
- [ ] Log metrics (total reward per episode, survival time, loss).
- [ ] Tune hyperparameters (learning rate, discount factor, epsilon decay, batch size, target update frequency).

## Phase 5: Evaluation & Visualization
- [ ] Test the trained agent with exploration disabled (Epsilon = 0).
- [ ] Generate plots using `matplotlib` (Learning curves, Reward vs. Episode).
- [ ] Clean up code and add comprehensive comments for report submission.
