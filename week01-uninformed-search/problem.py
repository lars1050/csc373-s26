from abc import ABC, abstractmethod

class Problem(ABC):
    """Abstract base class for search problems."""
        
    @abstractmethod
    def get_initial_state(self):
        """Return the initial state of the problem."""
        pass
    
    @abstractmethod
    def is_goal(self, state):
        """Return True if state is a goal state."""
        pass
    
    @abstractmethod
    def get_successors(self, state):
        """Return list of (action, next_state, cost) tuples."""
        pass
    
    @abstractmethod
    def heuristic(self, state):
        """Return estimated cost from state to goal."""
        pass

    def pretty_print(self,state):
        print(state)
    
    def show_path(self, goal_node):
        '''Print the path from initial to goal state (or None).'''
        if goal_node:
            print(f"Solution found! Depth: {goal_node.depth}")
            print(f"Path cost: {goal_node.path_cost}")
            print(f"Actions: {goal_node.get_path()}")
        else:
            print("No solution found.")
        

