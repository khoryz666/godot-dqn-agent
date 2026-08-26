# Godot DQN Agent

A Reinforcement Learning project that trains a Deep Q-Network (DQN) agent to play a custom 2D Platformer in Godot 4.

## Get Started

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

5. **Launch Jupyter Notebook** — open Jupyter Notebook in Anaconda Navigator and choose the environment (kernel) you just created.

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
- Make sure to select the kernel in Jupyter.
- Run the notebook cells to start the Python WebSocket server.
- Press **Play** in the Godot Editor to connect the game to the agent and begin training/testing!
