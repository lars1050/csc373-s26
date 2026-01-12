"THANK YOU claude.ai"

from abc import ABC, abstractmethod
from collections import deque
import heapq

cyclic = False

class Node:
    """Node in the search tree."""
    
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0 if parent is None else parent.depth + 1
    
    def __lt__(self, other):
        """For priority queue comparison."""
        return self.path_cost < other.path_cost
    
    def get_path(self):
        """Return list of actions from root to this node."""
        path = deque([])
        node = self
        while node.parent is not None:
            path.appendleft(node.action)
            node = node.parent
        return path
    
    def get_state_path(self):
        """Return list of states from root to this node."""
        path = deque([])
        node = self
        while node is not None:
            path.appendleft(node.state)
            node = node.parent
        return path


class TreeSearch(ABC):
    """Base class for tree search algorithms."""
    
    def __init__(self):
        self.frontier = []
        self.counter = 0  # For tie-breaking in priority queue
    
    @abstractmethod
    def priority(self, node, problem):
        """Return priority value for node (lower = higher priority)."""
        pass
    
    def push(self, node, problem):
        """Add node to frontier with appropriate priority."""
        priority = self.priority(node, problem)
        heapq.heappush(self.frontier, (priority, self.counter, node))
        self.counter += 1
    
    def pop(self):
        """Remove and return highest priority node."""
        return heapq.heappop(self.frontier)[2]
    
    def is_empty(self):
        """Check if frontier is empty."""
        return len(self.frontier) == 0
    
    def search(self, problem):
        """Execute tree search algorithm."""
        initial = Node(problem.get_initial_state())
        #print(f'\nStart State: {problem.get_initial_state()}')
        
        if problem.is_goal(initial.state):
            return initial

        # add state to frontier -- priority queue
        self.push(initial, problem)
        if cyclic:
            explored = set()
        nodes_generated = 1
        
        while not self.is_empty():
            # pop based on priority queue
            node = self.pop()
            
            if cyclic and str(node.state) in explored:
                continue
            
            if problem.is_goal(node.state):
                print(f"\nNodes generated: {nodes_generated}")
                return node
            
            if cyclic:
                explored.add(str(node.state))
            
            for action, state, cost in problem.get_successors(node.state):
                if cyclic and str(state) in explored:
                    continue
                else:
                    nodes_generated += 1
                    child = Node(state, node, action, node.path_cost + cost)
                    self.push(child, problem)
        
        print(f"Nodes generated: {nodes_generated}")
        return None


class BFS(TreeSearch):
    """Breadth-first search: prioritize by depth (FIFO)."""
    
    def priority(self, node, problem):
        return node.depth


class DFS(TreeSearch):
    """Depth-first search: prioritize by negative depth (LIFO)."""
    
    def priority(self, node, problem):
        return -node.depth


class AStar(TreeSearch):
    """A* search: prioritize by f(n) = g(n) + h(n)."""
    
    def priority(self, node, problem):
        return node.path_cost + problem.heuristic(node.state)

ALGORITHMS = {
    'bfs': BFS,
    'dfs': DFS,
    'astar': AStar
}

def search(problem, algorithm='bfs'):
    """
    Search for a solution to the problem.
    
    Args:
        problem: Instance of Problem class
        algorithm: 'bfs', 'dfs', 'astar' (case-insensitive), or a TreeSearch class
    
    Returns:
        Node representing goal state, or None if no solution found
    """
    if isinstance(algorithm, str):
        algorithm = algorithm.lower()
        if algorithm not in ALGORITHMS:
            raise ValueError(f"Unknown algorithm: {algorithm}. Choose from {list(ALGORITHMS.keys())}")
        algorithm = ALGORITHMS[algorithm]

    import time
    searcher = algorithm()
    start_time = time.perf_counter()
    solution = searcher.search(problem)
    end_time = time.perf_counter()
    print(f'Execution time: {(end_time-start_time):.6f} seconds')
    return solution


