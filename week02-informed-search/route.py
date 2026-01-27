from problem import Problem

# Example: Romania Route Finding Problem
class RomaniaMap(Problem):
    """
    Route finding in Romania with cities and road distances.
    Actions have different costs based on road distances.
    """
    
    def __init__(self, start):
        self.start = start
        self.goal = 'Bucharest'
        
        # Road connections: (city1, city2, distance)
        self.roads = [
            ('Arad', 'Zerind', 75),
            ('Arad', 'Sibiu', 140),
            ('Arad', 'Timisoara', 118),
            ('Zerind', 'Oradea', 71),
            ('Oradea', 'Sibiu', 151),
            ('Timisoara', 'Lugoj', 111),
            ('Lugoj', 'Mehadia', 70),
            ('Mehadia', 'Drobeta', 75),
            ('Drobeta', 'Craiova', 120),
            ('Sibiu', 'Fagaras', 99),
            ('Sibiu', 'Rimnicu', 80),
            ('Rimnicu', 'Craiova', 146),
            ('Rimnicu', 'Pitesti', 97),
            ('Craiova', 'Pitesti', 138),
            ('Fagaras', 'Bucharest', 211),
            ('Pitesti', 'Bucharest', 101),
            ('Bucharest', 'Giurgiu', 90),
            ('Bucharest', 'Urziceni', 85),
            ('Urziceni', 'Hirsova', 98),
            ('Hirsova', 'Eforie', 86),
            ('Urziceni', 'Vaslui', 142),
            ('Vaslui', 'Iasi', 92),
            ('Iasi', 'Neamt', 87),
        ]
        
        # Build adjacency map
        self.connections = {}
        for city1, city2, dist in self.roads:
            if city1 not in self.connections:
                self.connections[city1] = []
            if city2 not in self.connections:
                self.connections[city2] = []
            self.connections[city1].append((city2, dist))
            self.connections[city2].append((city1, dist))
        
        # Straight-line distances to Bucharest (for heuristic)
        self.straight_line = {
            'Arad': 366, 'Bucharest': 0, 'Craiova': 160, 'Drobeta': 242,
            'Eforie': 161, 'Fagaras': 176, 'Giurgiu': 77, 'Hirsova': 151,
            'Iasi': 226, 'Lugoj': 244, 'Mehadia': 241, 'Neamt': 234,
            'Oradea': 380, 'Pitesti': 100, 'Rimnicu': 193, 'Sibiu': 253,
            'Timisoara': 329, 'Urziceni': 80, 'Vaslui': 199, 'Zerind': 374
        }
    
    def __str__(self):
        return f'Romania route from {self.start} to {self.goal}'
    
    def get_initial_state(self):
        return self.start
    
    def is_goal(self, state):
        return state == self.goal
    
    def get_successors(self, state):
        """Return neighboring cities with road distances as costs."""
        if state not in self.connections:
            return []
        
        successors = []
        for city, distance in self.connections[state]:
            action = f"{state} -> {city}"
            successors.append((action, city, distance))
        
        return successors
    
    def heuristic(self, state):
        """Straight-line distance to goal."""
        #return 0
        return self.straight_line.get(state, 0)

    def show_path(self, final_node):
        if final_node:
            print(f"Solution found from {self.start} to {self.goal}.")
            print(f"Depth: {final_node.depth} (number of cities)")
            print(f"Total distance: {final_node.path_cost} km")
            print(f"\nRoute:")
            path = final_node.get_state_path()
            for i, city in enumerate(path):
                if i < len(path) - 1:
                    print(f"  {i+1}. {city}")
                else:
                    print(f"  {i+1}. {city} (GOAL)")
        else:
            print("No solution for {self.start} to {self.goal}.")
        

