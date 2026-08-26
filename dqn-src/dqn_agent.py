import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np

from dqn_model import QNetwork
from replay_buffer import ReplayBuffer

class DQNAgent:
    def __init__(self, state_size: int, action_size: int, config: dict):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = config.get("gamma", 0.99)
        self.epsilon = config.get("epsilon_start", 1.0)
        self.epsilon_min = config.get("epsilon_min", 0.01)
        self.epsilon_decay = config.get("epsilon_decay", 0.995)
        self.batch_size = config.get("batch_size", 64)
        self.learning_rate = config.get("learning_rate", 1e-3)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Policy and Target Networks
        self.policy_net = QNetwork(state_size, action_size).to(self.device)
        self.target_net = QNetwork(state_size, action_size).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.learning_rate)
        self.memory = ReplayBuffer(config.get("buffer_size", 100000))

    def get_action(self, state: list) -> int:
        """
        Returns an action using epsilon-greedy policy.
        """
        if random.random() < self.epsilon:
            return random.randrange(self.action_size)
            
        state_tensor = torch.tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.no_grad():
            q_values = self.policy_net(state_tensor)
        return int(torch.argmax(q_values).item())

    def update_epsilon(self):
        """
        Decay the exploration rate.
        """
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def train_step(self):
        """
        Sample a batch from memory and train the policy network.
        Returns the loss value.
        """
        if len(self.memory) < self.batch_size:
            return 0.0
            
        states, actions, rewards, next_states, dones = self.memory.sample(self.batch_size)
        
        states = torch.tensor(states, dtype=torch.float32, device=self.device)
        actions = torch.tensor(actions, dtype=torch.long, device=self.device).unsqueeze(1)
        rewards = torch.tensor(rewards, dtype=torch.float32, device=self.device).unsqueeze(1)
        next_states = torch.tensor(next_states, dtype=torch.float32, device=self.device)
        dones = torch.tensor(dones, dtype=torch.float32, device=self.device).unsqueeze(1)
        
        # Current Q values
        current_q_values = self.policy_net(states).gather(1, actions)
        
        # Target Q values
        with torch.no_grad():
            next_q_values = self.target_net(next_states).max(1)[0].unsqueeze(1)
            target_q_values = rewards + (self.gamma * next_q_values * (1 - dones))
            
        # Compute loss
        loss = nn.SmoothL1Loss()(current_q_values, target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.policy_net.parameters(), 10.0)
        self.optimizer.step()
        
        return loss.item()

    def update_target_network(self):
        """
        Sync target network weights with policy network.
        """
        self.target_net.load_state_dict(self.policy_net.state_dict())
