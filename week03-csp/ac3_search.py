import ac3

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


class TreeSearch():
    
    def __init__(self,csp_problem):
        self.frontier = []
        self.counter = 0  # For tie-breaking in priority queue
        self.problem = csp_problem

    def push(self, node):
        """Add node to frontier with appropriate priority."""
        self.frontier.append(node)
        self.counter += 1
    
    def pop(self):
        """Remove and return top of stack."""
        node = self.frontier[-1]
        self.frontier = self.frontier[:-1]
        return node
    
    def is_empty(self):
        """Check if frontier is empty."""
        return len(self.frontier) == 0
    
    def search(self):
        """Execute tree search algorithm."""

        ac3.ac3(self.problem)
        
        if self.problem.is_goal():
            print('Problem Solved!!')
            return self.problem.domains

        print("AC3 insufficient to find solution. Starting search.")
        initial = Node(self.problem.domains)
        
        # add state to frontier -- stack (for dfs search)
        self.frontier = [initial]
        nodes_generated = 1
        
        while not self.is_empty():

            # pop from "stack"
            node = self.pop()

            # successors will be in order as listed on domain (not intelligent)
            for action, child_state, cost in self.problem.get_successors(node.state):

                self.problem.reset_domains(child_state)
                
                # try satisfying constraints with this assignment
                if not ac3.ac3(self.problem):
                    # fail
                    continue

                # some domains remain. are they all down to 1 ?
                if self.problem.is_goal():
                    return child_state
                else:
                    nodes_generated += 1
                    child = Node(child_state, node, action, node.path_cost + cost)
                    self.push(child)
        
        print(f"Nodes generated: {nodes_generated}")
        return None
        


