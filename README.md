# Godot DQN Agent

A Reinforcement Learning project that trains a Deep Q-Network (DQN) agent to play a custom 2D Platformer in Godot 4.

## Get Started

### 1. Python Environment Setup

1. **Install Anaconda** — download Anaconda via `winget` (available but not limited to).

2. **Open Anaconda Prompt**.

3. **Install `nb_conda_kernels`**:
   ```bash
   conda install -c conda-forge nb_conda_kernels
   ```

4. **Create the environment** — navigate to the root directory of this repo, then run:
   ```bash
   conda env create -f environment.yml
   ```

5. **Launch Jupyter Notebook** — open Jupyter Notebook in Anaconda Navigator and choose the environment (kernel) you just created (`godot-dqn`).

### Adding / Removing Packages

- Update `environment.yml` first, then execute the following in the same directory in Anaconda Prompt:
  ```bash
  conda env update -f environment.yml --prune
  ```

### 2. Godot Game Setup
- Ensure you have Godot 4.x installed.
- Open `godot-src/project.godot` in the Godot Editor.
- The game is configured to automatically communicate with the Python RL agent over WebSockets (default port 11000).

### 3. Running the Agent
- Open the Jupyter Notebook `dqn-src/DQN_Agent.ipynb`.
- Make sure to select the kernel in Jupyter (`godot-dqn`).
- Run the cells in order:
  - The first cells start the Python WebSocket server and define the DQN agent, environment wrapper, and plotting helpers.
  - The Phase 4 training cell (`await train()`) automatically launches Godot in headless mode and trains for 500 episodes. Real-time metrics (reward, loss, epsilon) are plotted as training progresses. Weights are saved to `dqn-src/dqn_model.pth` when training finishes or is interrupted.
  - The Phase 5 evaluation cell (`await test_agent()`) plays 5 test episodes using the saved weights with epsilon = 0 (fully deterministic).
- **Headless Automation**: The notebook uses Python's `subprocess` to automatically launch the Godot engine in headless mode. You do *not* need to manually press Play in the Godot Editor.
- To visually watch the trained agent play, remove the `--headless` flag from the Phase 5 cell's `subprocess.Popen` call before running it.
