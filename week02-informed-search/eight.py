'Thanks claude.ai'

from problem import Problem

# Example: 8-Puzzle Problem
class EightPuzzle(Problem):
    """8-puzzle problem: 3x3 grid with one empty space."""
    
    def __init__(self, initial, goal=None):
        self.initial = initial
        self.goal = goal if goal else (1, 2, 3, 4, 5, 6, 7, 8, 0)

    def __str__(self):
        return f'8-puzzle {self.initial}'
    
    def get_initial_state(self):
        return self.initial
    
    def is_goal(self, state):
        return state == self.goal
    
    def get_successors(self, state):
        """Generate successor states by moving tiles into empty space."""
        successors = []
        blank = state.index(0)
        row, col = blank // 3, blank % 3
        
        # Possible moves: up, down, left, right
        moves = []
        if row > 0: moves.append(('up', blank - 3))
        if row < 2: moves.append(('down', blank + 3))
        if col > 0: moves.append(('left', blank - 1))
        if col < 2: moves.append(('right', blank + 1))
        
        for action, new_blank in moves:
            new_state = list(state)
            new_state[blank], new_state[new_blank] = new_state[new_blank], new_state[blank]
            successors.append((action, tuple(new_state), 1))
        return successors
    
    def heuristic(self, state):
        """Manhattan distance heuristic."""
        distance = 0
        for i, tile in enumerate(state):
            if tile != 0:
                goal_idx = self.goal.index(tile)
                curr_row, curr_col = i // 3, i % 3
                goal_row, goal_col = goal_idx // 3, goal_idx % 3
                distance += abs(curr_row - goal_row) + abs(curr_col - goal_col)
        return distance

problems = [
    (1,5,2,4,0,3,7,8,6),
    (4,1,3,2,8,5,0,7,6),
    ( 8,6,7,2,5,4,3,0,1) # most difficult (31 moves)
    ]


        



