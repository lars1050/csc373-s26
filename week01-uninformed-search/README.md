### CSC373: Week 01 Uninformed Search

This code implements Tree Search (both Breadth-First and Depth-First Search) to find the solution to a given problem.

Files:
- solver.py: primary driver that pairs a problem and an algorithm
- problem.py: Parent class Problem the provides framework for search
- search.py: implementation of BFS, DFS, and A* (not yet used)
- sudoku.py: problem framework for solving a Sudoku puzzle (and example puzzles)
- cryptarithmetic.py: problem framework for solving an arithmetic Cryptarithmetic puzzle (and example puzzles)


Parameters:
- constraining: in sudoku.py. If False, successors of a given state consider all digits. If True, successors contain only those digits that meet the constraints of Sudoku (e.g. all elements in a row are unique)
- cyclic: in search.py. If False, will not maintain an explored set.

Solve a puzzle by calling the solver via the command line, like this:

```
python solver.py sudoku 1 bfs
```

This would solve problem[1] in sudoku.py using a Breadth-First Search. The output includes the number of nodes created and the time to solve the puzzle. It also shows the path through the tree from the initial state to the goal state.

Or this:

```
python solver.py crypt 0 dfs
```

This would solve problem[0] in cryptarithmetic.py using a Depth-First Search.
