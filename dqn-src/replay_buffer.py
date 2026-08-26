import random
import numpy as np
from collections import deque
from typing import Tuple, List

class ReplayBuffer:
    """
    Experience Replay memory buffer.
    """
    def __init__(self, capacity: int):
        self.memory = deque(maxlen=capacity)

    def add(self, state: List[float], action: int, reward: float, next_state: List[float], done: bool):
        """
        Save an experience transition to memory.
        """
        self.memory.append((state, action, reward, next_state, done))

    def sample(self, batch_size: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Randomly sample a batch of experiences.
        """
        batch = random.sample(self.memory, batch_size)
        
        states = np.array([exp[0] for exp in batch], dtype=np.float32)
        actions = np.array([exp[1] for exp in batch], dtype=np.int64)
        rewards = np.array([exp[2] for exp in batch], dtype=np.float32)
        next_states = np.array([exp[3] for exp in batch], dtype=np.float32)
        dones = np.array([exp[4] for exp in batch], dtype=np.float32)
        
        return states, actions, rewards, next_states, dones

    def __len__(self):
        return len(self.memory)
