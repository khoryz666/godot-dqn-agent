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
- The game is configured to automatically communicate with the Python RL agent over WebSockets (default port 11000). The `RLBridge` autoload reconnects automatically if the Python server is (re)started.
- The notebook launches Godot headlessly itself: on Windows it expects the executable at `~\scoop\apps\godot\current\godot.console.exe`; on other platforms it uses `godot` from `PATH`. Adjust the `godot_exe` line in the notebook if your installation differs.

### 3. Running the Agent
- Open the Jupyter Notebook `dqn-src/DQN_Agent.ipynb`.
- Make sure to select the kernel in Jupyter (`godot-dqn`).
- Run the cells in order:
  - The first cells start the Python WebSocket server and define the DQN agent, environment wrapper, and plotting helpers.
  - The Phase 4 training cell (`await train()`) automatically launches Godot in headless mode and trains for 500 episodes. Real-time metrics (reward, loss, epsilon) are plotted as training progresses. Weights are saved to `dqn-src/dqn_model.pth` when training finishes or is interrupted. If Godot disconnects mid-run, training aborts with a clear error instead of silently producing garbage episodes.
  - The Phase 5 evaluation cell (`await test_agent()`) plays 50 test episodes using the saved weights with epsilon = 0 (fully deterministic) and prints a metrics table (completion rate, snail avoidance, fall rate, average apples/distance, etc.). A warning is shown if no trained model file exists.
- **Headless Automation**: The notebook uses Python's `subprocess` to automatically launch the Godot engine in headless mode. You do *not* need to manually press Play in the Godot Editor.
- To visually watch the trained agent play, remove the `--headless` flag from the Phase 5 cell's `subprocess.Popen` call before running it.

### 4. Automated Hyperparameter Tuning
If you want to run an exhaustive, hands-off search to find the absolute best parameters over a long period (e.g., 48 hours), use the included Python script instead of the Jupyter Notebook.

1. Open your Anaconda Prompt and navigate to this repository's `dqn-src` folder.
2. Activate your environment: `conda activate godot-dqn`
3. Run the optimization script: `python optimize.py`

**How it works & Retrieving Results:**
- The script runs 100 trials of completely unique, random hyperparameter combinations (learning rate, batch size, gamma, etc.).
- It trains the agent for 400 episodes and runs 15 deterministic evaluation episodes to calculate a "true" unbiased score for that configuration.
- **`search_results.csv`**: Every single trial's score and configuration is appended to this file in real-time. If you stop the script, your data is safe.
- **`best_config.json`** & **`best_dqn_model.pth`**: Whenever a new high score is achieved, the script automatically saves the winning configuration and the corresponding PyTorch model weights to these files.
