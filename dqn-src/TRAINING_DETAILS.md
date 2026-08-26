# DQN Agent Training Details

## Deep Q-Network (DQN) Overview
DQN is a reinforcement learning algorithm that uses a neural network to approximate the Q-value function. The Q-value represents the expected future reward for taking a specific action in a given state.

## Architecture
- **Input:** 5-dimensional game state: normalized player X position, normalized Y position, grounded flag, distance to the nearest apple, distance to the nearest enemy.
- **Hidden Layers:** Fully connected layers with ReLU activation
- **Output:** Q-values for each of the 6 possible discrete actions

## Training Mechanism
1. **Experience Replay:** As the agent interacts with the environment, it stores experiences `(state, action, reward, next_state, done)` in a memory buffer.
2. **Batch Training:** During training, a random batch of experiences is sampled from the buffer. This breaks correlation between consecutive actions and stabilizes learning.
3. **Target Network:** Two identical neural networks are used:
   - **Policy Network:** Actively updated and used to select actions.
   - **Target Network:** A frozen copy of the Policy Network, updated periodically. It calculates the target Q-values during loss calculation to prevent unstable feedback loops.
4. **Epsilon-Greedy Exploration:** The agent balances exploration (taking random actions) and exploitation (using the best known action) via an $\epsilon$ parameter. $\epsilon$ starts high (e.g., 1.0) and decays over time to a minimum value.

## Reward Structure
- **+10** for collecting a reward (apple)
- **-10** for dying — hitting an enemy (snail) or falling off the map
- **-0.01** small time penalty per step to encourage faster completion

Note: there is currently no end-goal condition in the level, so the episode only ends on death or the 1000-step failsafe.

## Key Hyperparameters (To be tuned)
- `learning_rate`: How much the network weights are updated (e.g., 0.001)
- `gamma` ($\gamma$): Discount factor for future rewards (e.g., 0.99)
- `batch_size`: Number of experiences trained on per step (e.g., 64)
- `buffer_size`: Total capacity of the experience replay memory (e.g., 100,000)
- `target_update`: How often the Target Network syncs with the Policy Network (every 10 episodes)
- `epsilon_decay`: The rate at which random exploration decreases
