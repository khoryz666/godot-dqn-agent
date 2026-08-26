# Godot DQN Agent

A Reinforcement Learning project that trains a Deep Q-Network (DQN) agent to play a custom 2D Platformer in Godot 4.

## Setup Instructions

### 1. Python Environment (Conda)
This project uses Conda to manage its Python dependencies. 
To install the environment and the required Jupyter kernel, run:

```bash
# Create the conda environment from the environment.yml file
conda env create -f environment.yml

# Activate the newly created environment
conda activate godot-dqn

# Register the environment as a Jupyter kernel
python -m ipykernel install --user --name godot-dqn --display-name "Python 3 (godot-dqn)"
```

### 2. Godot Game Setup
- Ensure you have Godot 4.x installed.
- Open `godot-src/project.godot` in the Godot Editor.
- The game is configured to automatically communicate with the Python RL agent over WebSockets (default port 11000).

### 3. Running the Agent
- Open the Jupyter Notebook `dqn-src/DQN_Agent.ipynb`.
- Make sure to select the `Python 3 (godot-dqn)` kernel in Jupyter.
- Run the notebook cells to start the Python WebSocket server.
- Press **Play** in the Godot Editor to connect the game to the agent and begin training/testing!
