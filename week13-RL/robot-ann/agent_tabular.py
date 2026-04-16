"""
agent_tabular.py  —  Tabular Q-learning agent
===============================================
State: (col, row, frozenset of remaining food positions)
Action: U / D / L / R
"""

import random
from world import (ACTIONS, COLS, ROWS, FOODS, STEP_PENALTY,
                   OFFGRID_PENALTY, HOME_REWARD, FOOD_REWARD,
                   PITFALL_PENALTY, HAZARD_PENALTY)

ALPHA     = 0.10
GAMMA     = 0.90
EPS_START = 1.00
EPS_MIN   = 0.05
EPS_DECAY = 0.995   # slower decay — state space is much larger


class TabularAgent:
    def __init__(self):
        self.reset()

    def reset(self):
        self.Q        = {}   # sparse dict — only seen states
        self.epsilon  = EPS_START
        self.episodes = 0
        self.steps    = 0

    def _q(self, state, action):
        return self.Q.get((state, action), 0.0)

    def _max_q(self, state):
        return max(self._q(state, a) for a in ACTIONS)

    def _best_action(self, state):
        return max(ACTIONS, key=lambda a: self._q(state, a))

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(ACTIONS)
        return self._best_action(state)

    def update(self, state, action, reward, next_state, done):
        old_q  = self._q(state, action)
        target = reward if done else reward + GAMMA * self._max_q(next_state)
        self.Q[(state, action)] = old_q + ALPHA * (target - old_q)
        self.steps += 1

    def end_episode(self):
        self.episodes += 1
        self.epsilon   = max(EPS_MIN, self.epsilon * EPS_DECAY)

    def best_action_for_pos(self, pos, foods_left):
        """Best action given position and current food set."""
        state = (pos[0], pos[1], frozenset(foods_left))
        return self._best_action(state)

    def q_values_for_pos(self, pos, foods_left):
        """Q-values for all actions at a position."""
        state = (pos[0], pos[1], frozenset(foods_left))
        return {a: self._q(state, a) for a in ACTIONS}

    def run_episode(self, world):
        """Run one full episode. Returns total reward."""
        world.reset()
        total = 0
        while not world.done:
            state  = world.state()
            action = self.choose_action(state)
            reward, done, actual, off_grid = world.step(action)
            next_state = world.state()
            self.update(state, action, reward, next_state, done)
            total += reward
        self.end_episode()
        return total

    def run_n_episodes(self, world, n):
        """Run n episodes silently. Returns list of total rewards."""
        rewards = []
        for _ in range(n):
            rewards.append(self.run_episode(world))
        return rewards
