### CSC373: Week 02 Informed Search (A-Star)

The Search is the same as in Week 01. The problems have a defined heuristic that can be used for A* Search. This heuristic, along with the path cost, is used to set the priority of nodes in the frontier. The aim is to find the optimal (minimum) path to the goal state.

Files:
- solver.py: primary driver that pairs a problem and an algorithm
- problem.py: Parent class Problem the provides framework for search
- search.py: implementation of BFS, DFS, and A* (not yet used)
- eight.py: classic slide puzzle with 8 tiles
- route.py: ever-present Romania map to demonstrate A*
- grid\_world.py: agent in a grid seeking gold and avoiding obstacles


Solve the sliding puzzle by calling the solver via the command line, like this:

```
python3 solver.py eight 1 astar
```

This would solve problem[1] in eight.py using the A-Star Search. The output includes the number of nodes created and the time to solve the puzzle. It also shows the path through the tree from the initial state to the goal state.

Solve the map route from Arad to Bucharest by calling the solver like this:
```
python3 solver.py route Arad astar
```

Solve the grid world puzzle in a grid of 20x20 like this:
```
python3 solver.py grid 20 astar
```

Note that you can run BFS or DFS by replacing astar with "bfs" or "dfs".




