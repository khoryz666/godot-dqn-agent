# DQN Agent Training Details

## Deep Q-Network (DQN) Overview
DQN is a reinforcement learning algorithm that uses a neural network to approximate the Q-value function. The Q-value represents the expected future reward for taking a specific action in a given state.

## Architecture
- **Input:** 9-dimensional game state: 
  - Normalized player X & Y position
  - Normalized player X & Y velocity
  - Grounded flag (1.0 or 0.0)
  - Distance vector (dx, dy) to the nearest apple
  - Distance vector (dx, dy) to the nearest enemy
- **Hidden Layers:** Two fully connected layers with 128 hidden units each and ReLU activation.
- **Output:** Q-values for each of the 6 possible discrete actions.
- **Loss & Optimization:** Uses Huber Loss (`SmoothL1Loss`) and Gradient Clipping (max norm 10.0) via an Adam optimizer. This ensures stability and prevents exploding gradients during massive early TD-errors.

## Training Mechanism
1. **Experience Replay:** As the agent interacts with the environment, it stores experiences `(state, action, reward, next_state, done)` in a memory buffer.
2. **Frame Skipping:** Godot only requests a decision every 4 physics frames, holding the previous action in the interim. This prevents the agent from jittering in place and allows random exploration to effectively traverse the map.
3. **Batch Training:** During training, a random batch of experiences is sampled from the buffer. This breaks correlation between consecutive actions and stabilizes learning.
4. **Target Network:** Two identical neural networks are used:
   - **Policy Network:** Actively updated and used to select actions.
   - **Target Network:** A frozen copy of the Policy Network, updated periodically (every 1000 steps). It calculates the target Q-values during loss calculation to prevent unstable feedback loops.
5. **Epsilon-Greedy Exploration:** The agent balances exploration and exploitation via an $\epsilon$ parameter. $\epsilon$ decays linearly over a set number of *total steps taken* (e.g. 40,000 steps) rather than per-episode, ensuring a guaranteed minimum amount of gameplay experience is acquired.

## Reward Structure
- **+10.0** for collecting a reward (apple)
- **+10.0** bonus for level completion (eating 2 apples triggers completion)
- **-10.0** for dying — hitting an enemy (snail) or falling off the map
- **-0.01** small time penalty per physics frame to encourage faster completion
- **Continuous Delta-Distance Shaping:** On every frame, the agent receives a reward equal to `(previous_distance_to_apple - current_distance_to_apple)`. This acts as a dense "breadcrumb trail" that teaches the agent to move toward apples immediately.

## Key Hyperparameters
- `learning_rate`: How much the network weights are updated (e.g., 0.001)
- `gamma` ($\gamma$): Discount factor for future rewards (e.g., 0.99)
- `batch_size`: Number of experiences trained on per step (e.g., 64)
- `buffer_size`: Total capacity of the experience replay memory (e.g., 100,000)
- `target_update_freq`: How often the Target Network syncs with the Policy Network (e.g., every 1000 steps)
- `epsilon_decay_steps`: The number of steps over which random exploration drops to its minimum (e.g., 40,000)
