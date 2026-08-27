# DQN Agent Training Details

## Deep Q-Network (DQN) Overview
DQN is a reinforcement learning algorithm that uses a neural network to approximate the Q-value function. The Q-value represents the expected future reward for taking a specific action in a given state.

## Godot ↔ Python Communication Architecture
- **Server:** An asynchronous Python WebSocket server (`websockets` library) runs inside the Jupyter Notebook on `ws://127.0.0.1:11000`.
- **Client:** Godot connects as a client through the `RLBridge` autoload (`rl_bridge.gd`). If the connection drops, it automatically reconnects once per second.
- **Decision Cadence (Frame Skipping):** Godot repeats the previously chosen action for 4 physics frames, then pauses the game tree, sends `(state, reward, done, score, info)` to Python, and waits for the next action.
- **Timeouts:** Python waits up to 30 seconds for every Godot response. Training and evaluation abort cleanly with an error message if Godot disconnects mid-run.
- **Headless Mode:** Both `train()` and `test_agent()` launch Godot with `--headless` via `subprocess` for maximum speed (rendering is skipped).

## State Space (9 dimensions)
- Normalized player X & Y position (`/1000.0`)
- Normalized player X & Y velocity (`/1000.0`)
- Grounded flag (1.0 or 0.0)
- Distance vector (dx, dy) to the nearest uneaten apple (clamped to [-1, 1])
- Distance vector (dx, dy) to the nearest enemy (clamped to [-1, 1])

## Action Space (6 discrete actions)
0: Do nothing · 1: Move right · 2: Move left · 3: Jump · 4: Move right + jump · 5: Move left + jump

## Network Architecture
- **Input:** 9-dimensional game state
- **Hidden Layers:** Two fully connected layers with 128 hidden units each and ReLU activation.
- **Output:** Q-values for each of the 6 possible discrete actions.
- **Loss & Optimization:** Huber Loss (`SmoothL1Loss`) with Adam (`lr = 0.001`) and gradient clipping (max norm 10.0). This ensures stability and prevents exploding gradients during massive early TD-errors.

## Training Mechanism
1. **Experience Replay:** As the agent interacts with the environment, it stores experiences `(state, action, reward, next_state, done)` in a memory buffer of capacity 100,000.
2. **Frame Skipping:** Godot only requests a decision every 4 physics frames, holding the previous action in the interim. This prevents the agent from jittering in place and allows random exploration to effectively traverse the map.
3. **Batch Training:** During training, a random batch of 64 experiences is sampled from the buffer. This breaks correlation between consecutive actions and stabilizes learning.
4. **Target Network:** Two identical neural networks are used:
   - **Policy Network:** Actively updated and used to select actions.
   - **Target Network:** A frozen copy of the Policy Network, synced every 1000 steps. It calculates the target Q-values during loss calculation to prevent unstable feedback loops.
5. **Epsilon-Greedy Exploration:** The agent balances exploration and exploitation via an $\epsilon$ parameter. $\epsilon$ decays **linearly from 1.0 to 0.01 over 40,000 total steps taken** (not per episode), guaranteeing a minimum amount of gameplay experience is acquired before the policy becomes mostly greedy.
6. **Training Loop:** 500 episodes with a 1000-step failsafe per episode. Live metrics (reward, loss, epsilon) are plotted every 10 episodes, and weights are saved to `dqn_model.pth` when training finishes or is interrupted.

## Reward Structure
- **+10.0** for collecting a reward (apple) — also adds **+10 to the score**
- **+10.0** bonus reward for level completion (score ≥ 20, i.e., eating 2 apples triggers completion)
- **-10.0** for dying — hitting an enemy (snail) or falling off the map
- **-0.01** small time penalty per physics frame (≈ -0.04 per decision step) to encourage faster completion
- **Continuous Delta-Distance Shaping:** On every decision step, the agent receives `(previous_distance_to_apple - current_distance_to_apple) / 100`. Moving closer to an apple yields a positive reward, moving away yields a penalty. The shaping is suppressed when an apple has just been collected (to avoid a spurious penalty when the target switches) or when no apples remain.
- **Score vs Reward:** Shaping rewards affect the reward signal only. The score counter counts *apples only*, so the completion condition and evaluation metrics cannot be polluted by shaping.

## Evaluation
- `test_agent()` plays 50 episodes with epsilon = 0 (fully deterministic) using the saved `dqn_model.pth` weights.
- A warning is printed if no trained model file is found (the untrained agent would then be evaluated).
- Godot reports the exact cause of death (completed / snail / fall) and distance traveled per episode; the notebook aggregates:
  - Average reward, score, and apples eaten
  - Completion rate, snail avoidance %, snail collision %, and fall rate %
  - Average distance traveled, average Godot episode time, and average wall-clock time

## Key Hyperparameters
- `learning_rate`: How much the network weights are updated (e.g., 0.001)
- `gamma` ($\gamma$): Discount factor for future rewards (e.g., 0.99)
- `epsilon_start` / `epsilon_min`: Exploration bounds (1.0 → 0.01)
- `epsilon_decay_steps`: Number of steps over which exploration decays linearly (40,000)
- `batch_size`: Number of experiences trained on per step (64)
- `buffer_size`: Total capacity of the experience replay memory (100,000)
- Target network sync: every 1000 steps (fixed in the training loop)
- `frame_skip`: Number of physics frames per decision step (4, in `main.gd`)
