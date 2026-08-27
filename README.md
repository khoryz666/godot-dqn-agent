# Godot DQN Agent 🎮🤖

A complete Reinforcement Learning pipeline that trains a Deep Q-Network (DQN) agent to play a custom 2D Platformer built in Godot 4.

## 🚀 Quick Start Guide

Follow these steps to set up your environment, launch the game, and start training your AI agent!

### 1. Environment Setup

We use Conda to manage our Python dependencies.

1. **Install Anaconda** (or Miniconda) on your system.
2. Open your **Anaconda Prompt** and navigate to this repository's root directory.
3. Install the Jupyter kernel manager:
   ```bash
   conda install -c conda-forge nb_conda_kernels
   ```
4. Create the environment from the provided configuration file:
   ```bash
   conda env create -f environment.yml
   ```
*(Note: If you ever need to update packages, edit `environment.yml` and run `conda env update -f environment.yml --prune`)*

### 2. Godot Setup

1. Ensure you have **Godot 4.x** installed.
2. Open `godot-src/project.godot` in the Godot Editor.
3. **Important Note:** You do *not* need to manually press Play in Godot! Our Python scripts will automatically launch the game in the background.

### 3. How to Train the Agent

You can interact with and train the agent using the provided Jupyter Notebook.

1. Open Anaconda Navigator, launch **Jupyter Notebook**, and open `dqn-src/DQN_Agent.ipynb`.
2. In the top right corner of Jupyter, ensure your kernel is set to **`conda env:godot-dqn`**.
3. **Run the Cells in Order:**
   - The first few cells establish the WebSocket server and configure the AI's neural network.
   - **Phase 4 (Training):** Running `await train()` automatically launches Godot in headless mode and begins training the agent for 500 episodes. Real-time metrics will plot directly in your notebook. If you stop the cell, your model weights will be safely saved to `dqn_model.pth`.
   - **Phase 5 (Evaluation):** Running `await test_agent()` loads your trained weights and tests the agent over 50 deterministic episodes, printing a detailed performance table.

**Want to watch the AI play?**
By default, the agent trains in "headless" mode for maximum speed (no graphics). To visually watch your trained agent play the game during Phase 5, remove the `--headless` flag from the `subprocess.Popen` command before running the cell!

### 4. 🎛️ Automated Hyperparameter Tuning (Advanced)

If you want to step away and let your computer find the absolute mathematically best configuration over 24-48 hours, use the standalone optimizer script instead of the notebook.

1. Open your Anaconda Prompt and navigate to `dqn-src`.
2. Activate your environment: `conda activate godot-dqn`
3. Run the script: `python optimize.py`

**What it does:**
- It uses a **Hyperband (successive halving)** strategy instead of blind random search: it tests many configurations cheaply, keeps only the best third at each stage, and gradually invests more training episodes in the survivors (`27 → 9 → 3 → 1` configs at `4 / 15 / 48 / 100` episodes).
- By default it launches **3 independent parallel searches** (one Godot instance per port) so the results can be compared for consistency.
- It logs every configuration of every stage in real-time to `hyperband_run_<n>.csv`, and each run's winner to `hyperband_summary.csv`.
- Whenever a run breaks the global high score, it automatically dumps the winning configuration to `best_config.json` and saves the winning PyTorch weights to `best_dqn_model.pth` (each run also saves its own artifacts as `best_config_run_<n>.json` / `best_dqn_model_run_<n>.pth`).

**Useful options:**
- `python optimize.py --runs 5` — run five searches instead of three.
- `python optimize.py --sequential` — run searches one after another (useful on weaker CPUs).
- `python optimize.py --base-port 11000` — change the first WebSocket port (one port per run).
