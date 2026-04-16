"""
world.py  —  10×10 stochastic gridworld
========================================
Cell types:
  "empty"    — normal cell, step penalty
  "food"     — non-terminal reward, disappears when collected
  "hazard"   — non-terminal penalty, survives (not collected)
  "pitfall"  — terminal penalty
  "home"     — terminal high reward

Transition model:
  80% intended direction, 10% left-perpendicular, 10% right-perpendicular
  Off-grid move → -1 reward, episode ends
"""

import random

# ── Grid dimensions ───────────────────────────────────────────────────────────
COLS, ROWS = 10, 10

# ── Rewards ───────────────────────────────────────────────────────────────────
STEP_PENALTY    = -0.1
FOOD_REWARD     = 3.0
HAZARD_PENALTY  = -2.0
PITFALL_PENALTY = -5.0
HOME_REWARD     = 10.0
OFFGRID_PENALTY = -1.0

# ── Fixed cell layout ─────────────────────────────────────────────────────────
# (col, row) — (0,0) is top-left
HOME     = (9, 0)   # top-right corner — terminal +10

FOODS    = [        # non-terminal +3, disappear when collected
    (2, 1),
    (7, 3),
    (1, 7),
    (6, 6),
]

HAZARDS  = [        # non-terminal -2, do not disappear
    (4, 2),
    (3, 6),
    (7, 8),
]

PITFALLS = [        # terminal -5
    (5, 4),
    (2, 8),
]

# All special cells for quick lookup
SPECIAL = {}
SPECIAL[HOME] = "home"
for f in FOODS:    SPECIAL[f] = "food"
for h in HAZARDS:  SPECIAL[h] = "hazard"
for p in PITFALLS: SPECIAL[p] = "pitfall"

# Starting position — bottom-left
START = (0, 9)

# ── Action definitions ────────────────────────────────────────────────────────
ACTIONS = ["U", "D", "L", "R"]
DELTAS  = {"U":(0,-1), "D":(0,1), "L":(-1,0), "R":(1,0)}

# Perpendicular slips: for each intended action, the two 90-degree alternatives
PERP = {
    "U": ["L", "R"],
    "D": ["R", "L"],
    "L": ["D", "U"],
    "R": ["U", "D"],
}

ARROWS = {"U":"↑", "D":"↓", "L":"←", "R":"→"}

# ── Transition function ───────────────────────────────────────────────────────
def sample_action(intended):
    """Return actual action taken given intended action (80/10/10)."""
    r = random.random()
    if r < 0.80:
        return intended
    elif r < 0.90:
        return PERP[intended][0]
    else:
        return PERP[intended][1]


# ── World state ───────────────────────────────────────────────────────────────
class World:
    """
    Holds the mutable state of one episode:
      - agent position
      - which food caches remain
      - done flag
    """
    def __init__(self):
        self.reset()

    def reset(self):
        self.pos          = START
        self.foods_left   = set(FOODS)   # which food cells still have food
        self.done         = False
        self.last_reward  = None
        self.last_action  = None
        self.last_actual  = None         # actual direction after slip
        self.off_grid_pos = None         # attempted position if off-grid

    def get_cell_type(self, pos):
        """Return current cell type — food disappears after collection."""
        if pos == HOME:
            return "home"
        if pos in PITFALLS:
            return "pitfall"
        if pos in HAZARDS:
            return "hazard"
        if pos in self.foods_left:
            return "food"
        return "empty"

    def state(self):
        """
        Full state for tabular Q-learning:
        (col, row, foods_remaining_frozenset)
        """
        return (self.pos[0], self.pos[1], frozenset(self.foods_left))

    def simple_state(self):
        """Position-only state — for display / DQN input."""
        return self.pos

    def step(self, intended_action):
        """
        Take one step. Returns (reward, done, actual_action, off_grid).
        Mutates world state in place.
        """
        if self.done:
            return 0, True, intended_action, False

        actual = sample_action(intended_action)
        dc, dr = DELTAS[actual]
        nc, nr = self.pos[0]+dc, self.pos[1]+dr

        self.last_action = intended_action
        self.last_actual = actual
        self.off_grid_pos = None

        # Off-grid
        if not (0 <= nc < COLS and 0 <= nr < ROWS):
            self.off_grid_pos = (
                max(-1, min(COLS, nc)),
                max(-1, min(ROWS, nr))
            )
            reward      = OFFGRID_PENALTY
            self.done   = True
            self.last_reward = reward
            return reward, True, actual, True

        new_pos   = (nc, nr)
        cell_type = self.get_cell_type(new_pos)
        self.pos  = new_pos

        if cell_type == "home":
            reward    = HOME_REWARD
            self.done = True
        elif cell_type == "pitfall":
            reward    = PITFALL_PENALTY
            self.done = True
        elif cell_type == "food":
            reward = FOOD_REWARD
            self.foods_left.discard(new_pos)   # food disappears
        elif cell_type == "hazard":
            reward = HAZARD_PENALTY
        else:
            reward = STEP_PENALTY

        self.last_reward = reward
        return reward, self.done, actual, False
