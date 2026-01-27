from problem import Problem

import random
import copy

class Location:
    """Simple location class to represent row, col position."""
    def __init__(self, row=0, col=0):
        self.row = row
        self.col = col
    
    def __eq__(self, other):
        return self.row == other.row and self.col == other.col
    
    def __hash__(self):
        return hash((self.row, self.col))
    
    def __repr__(self):
        return f"({self.row},{self.col})"

    def distance(self,other):
        # manhattan distance
        return abs(self.row - other.row) + abs(self.col - other.col)


# Each direction NSEW signifies changes in row and column (in grid coordinates)
MOVES = {"N": Location(row=-1, col=0), "E": Location(row=0, col=1),
         "S": Location(row=1, col=0), "W": Location(row=0, col=-1)}


class GridWorld(Problem):
    """
    Grid world adapted for A* tree search.
    Agent must navigate around pits to reach destination.
    
    State representation: Location(row, col) - the robot's current position
    """
    
    def __init__(self, grid_size=7, pit_percent=10, powerup=True):
        """
        Args:
            grid_size: Size of the square grid
            pit_percent: Percentage of grid cells that are pits
            power: Are power stations present that boost score
        """
        self.size = grid_size
        self.powerup = -5 if powerup else 1
        
        # Create a new random grid
        self.grid = [[0 for i in range(self.size)] for j in range(self.size)]
        self.pit_count = int(pit_percent / 100 * self.size * self.size)
        self._add_random_pits(self.pit_count)

        # Create power stations
        self.power_count = int(.05 * self.size * self.size)
        for i in range(self.power_count):
            self._add_random('power')
            
        # Create state: tuple of agent random starting location and initial power
        self.state = self._get_open_location()
        self.start_state = Location(self.state.row,self.state.col)

        # Identify a random goal position in the grid (there is gold there)
        self.destination = self._add_random("destination")
        print(f'start {self.start_state} dest {self.destination}')
    
    def _add_random_pits(self, number_pits):
        """Randomly place pits in the environment."""
        for i in range(number_pits):
            self._add_random("pit")

    def _get_open_location(self):
        '''Need to not randomly place things on top of each other'''
        found = False
        while not found:
            row = random.randrange(self.size)
            col = random.randrange(self.size)
            if self.grid[row][col] == 0:
                location = Location(row,col)
                found = True
        return location
    
    def _add_random(self, entity):
        """Find an open space to place this entity."""
        placed = False
        while not placed:
            row = random.randrange(self.size)
            col = random.randrange(self.size)
            if self.grid[row][col] == 0:
                self.grid[row][col] = entity
                placed = True
        return Location(row=row, col=col)
    
    # ===== Methods required for tree search =====
    
    def get_initial_state(self):
        """Return the starting location of the agent."""
        return self.start_state
    
    def is_goal(self, state):
        """Check if agent has reached its destination."""
        return state == self.destination
    
    def get_successors(self, state):
        """
        Generate all valid moves from current state.
        Returns list of (action, new_state, cost) tuples.
        """
        successors = []
        
        for direction in MOVES.keys():
            new_row = state.row + MOVES[direction].row
            new_col = state.col + MOVES[direction].col
            
            # Check if move is valid (within bounds)
            if (0<=new_row<self.size and 0<=new_col<self.size):
                
                new_state = Location(row=new_row, col=new_col)
                
                # how much did that cost to get to that location??
                if self.grid[new_row][new_col] == "pit":
                    successors.append((direction, new_state, 10))
                elif self.grid[new_state.row][new_state.col] == 'power':
                    successors.append((direction, new_state, self.powerup))
                else:
                    successors.append((direction, new_state, 1))
        
        return successors
    
    def heuristic(self, state):
        """
        Manhattan distance heuristic: distance from current position to destination.
        This is admissible because it never overestimates the actual path cost.
        """
        return state.distance(self.destination)
    
    # ===== Utility methods =====
    
    def pretty_print(self, path=None):
        """
        Display the grid with robot (R), gold (G), pits (X), and optionally the path.
        """
        # Create a copy of grid for display
        display_grid = [row[:] for row in self.grid]
        
        # Mark path if provided
        '''
        if path:
            for location in path:
                if display_grid[location.row][location.col] == 0:
                    display_grid[location.row][location.col] = '.'
        '''
        
        # Mark start and goal (overwrite path markers if needed)
        display_grid[self.start_state.row][self.start_state.col] = 'A'
        display_grid[self.destination.row][self.destination.col] = '*'

        # display the path
        location = Location(self.start_state.row, self.start_state.col)
        for move in path:
            if 'N'==move:
                location.row -= 1
                arrow = '↑'
            elif 'E'==move:
                location.col += 1
                arrow = '→'
            elif 'S'==move:
                location.row += 1
                arrow = '↓'
            elif 'W'==move:
                location.col -= 1
                arrow = '←'
            if location == self.destination:
                break   # do not overwrite the destination marker
            if display_grid[location.row][location.col] != 'power' and \
                display_grid[location.row][location.col] != 'pit':
                display_grid[location.row][location.col] = arrow
        
        # Print grid
        #print("  " + " ".join(str(i) for i in range(self.size)))
        for i, row in enumerate(display_grid):
            row_str = []
            for cell in row:
                if cell == "pit":
                    row_str.append('|')
                elif cell == 0:
                    row_str.append('·')
                elif cell == 'power':
                    row_str.append('+')
                else:
                    row_str.append(str(cell))
            print(f" {' '.join(row_str)}")
        print()
        
