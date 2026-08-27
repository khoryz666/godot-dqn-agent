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
- It autonomously runs hundreds of uniquely randomized parameter combinations (learning rate, batch size, etc.).
- It logs every single trial in real-time to `search_results.csv`.
- Whenever it breaks its own high score, it automatically dumps the winning configuration to `best_config.json` and saves the winning PyTorch weights to `best_dqn_model.pth`.
