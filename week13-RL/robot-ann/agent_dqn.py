"""
agent_dqn.py  —  Deep Q-Network agent
=======================================
State vector: [col/9, row/9, food1, food2, food3, food4]  (6 inputs)
Output:       Q-value for each of 4 actions

DQN ingredients:
  - Experience replay buffer
  - Target network (frozen copy, updated every TARGET_UPDATE steps)
  - Batch training (train on random sample of past experiences)
"""

import random
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque

from world import (ACTIONS, COLS, ROWS, FOODS)

# ── Hyperparameters ───────────────────────────────────────────────────────────
ALPHA         = 0.001   # learning rate for optimizer
GAMMA         = 0.90
EPS_START     = 1.00
EPS_MIN       = 0.05
EPS_DECAY     = 0.995

BUFFER_SIZE   = 10_000  # max experiences stored
BATCH_SIZE    = 64      # experiences sampled per training step
TARGET_UPDATE = 50      # steps between target network syncs
TRAIN_START   = 200     # don't train until buffer has this many experiences

FOODS_LIST = list(FOODS)   # fixed order for state encoding


# ── Network ───────────────────────────────────────────────────────────────────
class QNetwork(nn.Module):
    """
    Small MLP: 6 inputs → 128 → 128 → 4 outputs
    Input:  [col/9, row/9, food1_present, food2_present, food3_present, food4_present]
    Output: Q-value for each action [U, D, L, R]
    """
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(6, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 4),
        )

    def forward(self, x):
        return self.net(x)


# ── Replay buffer ─────────────────────────────────────────────────────────────
class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)

    def __len__(self):
        return len(self.buffer)


# ── DQN Agent ─────────────────────────────────────────────────────────────────
class DQNAgent:
    def __init__(self):
        self.reset()

    def reset(self):
        self.policy_net  = QNetwork()
        self.target_net  = QNetwork()
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        self.optimizer   = optim.Adam(self.policy_net.parameters(), lr=ALPHA)
        self.buffer      = ReplayBuffer(BUFFER_SIZE)
        self.epsilon     = EPS_START
        self.episodes    = 0
        self.steps       = 0
        self.last_loss   = None

    def encode_state(self, world_state):
        """
        Convert (col, row, frozenset_of_foods) to a float tensor of length 6.
        """
        col, row, foods_remaining = world_state
        vec = [
            col / (COLS - 1),
            row / (ROWS - 1),
        ] + [1.0 if f in foods_remaining else 0.0 for f in FOODS_LIST]
        return torch.tensor(vec, dtype=torch.float32)

    def choose_action(self, world_state):
        if random.random() < self.epsilon:
            return random.choice(ACTIONS)
        state_t = self.encode_state(world_state).unsqueeze(0)
        with torch.no_grad():
            q_vals = self.policy_net(state_t)
        return ACTIONS[q_vals.argmax().item()]

    def push(self, state, action, reward, next_state, done):
        """Store experience in replay buffer."""
        self.buffer.push(
            self.encode_state(state),
            ACTIONS.index(action),
            reward,
            self.encode_state(next_state),
            done
        )

    def train_step(self):
        """Sample a batch and do one gradient descent step."""
        if len(self.buffer) < TRAIN_START:
            return None

        batch      = self.buffer.sample(BATCH_SIZE)
        states     = torch.stack([b[0] for b in batch])
        actions    = torch.tensor([b[1] for b in batch], dtype=torch.long)
        rewards    = torch.tensor([b[2] for b in batch], dtype=torch.float32)
        next_states= torch.stack([b[3] for b in batch])
        dones      = torch.tensor([b[4] for b in batch], dtype=torch.float32)

        # Current Q values for actions taken
        current_q = self.policy_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)

        # Target Q values from frozen target network
        with torch.no_grad():
            max_next_q = self.target_net(next_states).max(1)[0]
            target_q   = rewards + GAMMA * max_next_q * (1 - dones)

        loss = nn.MSELoss()(current_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.steps += 1

        # Sync target network periodically
        if self.steps % TARGET_UPDATE == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

        self.last_loss = loss.item()
        return loss.item()

    def end_episode(self):
        self.episodes += 1
        self.epsilon   = max(EPS_MIN, self.epsilon * EPS_DECAY)

    def q_values_for_pos(self, pos, foods_left):
        """Q-values for display — mirrors tabular agent interface."""
        from world import FOODS
        state = (pos[0], pos[1], frozenset(foods_left))
        state_t = self.encode_state(state).unsqueeze(0)
        with torch.no_grad():
            q_vals = self.policy_net(state_t).squeeze(0).tolist()
        return {a: q_vals[i] for i, a in enumerate(ACTIONS)}

    def best_action_for_pos(self, pos, foods_left):
        q = self.q_values_for_pos(pos, foods_left)
        return max(q, key=q.get)

    def run_episode(self, world):
        """Run one full episode. Returns total reward."""
        world.reset()
        total = 0
        while not world.done:
            state  = world.state()
            action = self.choose_action(state)
            reward, done, actual, off_grid = world.step(action)
            next_state = world.state()
            self.push(state, action, reward, next_state, done)
            self.train_step()
            total += reward
        self.end_episode()
        return total

    def run_n_episodes(self, world, n):
        rewards = []
        for _ in range(n):
            rewards.append(self.run_episode(world))
        return rewards
