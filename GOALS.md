# Project Goals: Godot 2D Platformer DQN Agent

This document outlines the step-by-step goals for successfully training a Deep Q-Network (DQN) agent to play the Godot 2D Platform Collector Game.

## Phase 1: Environment Setup & Interface (Godot ↔ Python)
- [x] Establish communication bridge between Godot game and Python environment (e.g., sockets, ZeroMQ, or Godot RL Agents).
- [x] Expose Godot environment API to receive actions and return `(next_state, reward, done_status, score)`.

## Phase 2: State, Action, and Reward Design
- [x] Define the discrete action space (0: Do nothing, 1: Move right, 2: Move left, 3: Jump, 4: Move right + jump, 5: Move left + jump).
- [x] Define the 9-dimensional state representation (position, velocity, grounded flag, dx/dy vectors to nearest apple and nearest enemy).
- [x] Define the reward function (positive for progress/collecting, negative for enemies/falling, step penalty).
- [x] Keep apple score separate from shaping rewards so the completion condition stays accurate.

## Phase 3: DQN Agent Implementation (Python)
- [x] Initialize the Q-Network (PyTorch or TensorFlow).
- [x] Implement the Target Network for stability.
- [x] Implement the Experience Replay buffer.
- [x] Implement Epsilon-Greedy strategy with epsilon decay for exploration.

## Phase 4: Training & Hyperparameter Tuning
- [x] Implement the training loop connecting the Python agent to Godot.
- [x] Log metrics (total reward per episode, survival time, loss).
- [x] Tune hyperparameters (learning rate, discount factor, epsilon decay, batch size, target update frequency).
- [x] Implement Hyperband successive-halving optimizer script for advanced tuning.
- [x] Implement Catastrophic Forgetting protection (Best Model Checkpointing) and CSV Logging.

## Phase 5: Evaluation & Visualization
- [x] Test the trained agent with exploration disabled (Epsilon = 0).
- [x] Generate plots using `matplotlib` (Learning curves, Reward vs. Episode, Loss vs Episode).
- [x] Clean up code and add comprehensive comments for report submission.
- [x] Restructure project into clean `models/` and `logs/` artifact directories for robust distribution.
