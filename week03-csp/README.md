### CSC373: Week 03 AC3 and Constraint Satisfaction Problems

This code implements AC3 (Arc Consistency) and AC3 with Search

Files:
- solver.py: primary driver that pairs a problem and an algorithm
- ac3.py: algorithm for solving CSPs
- ac3\_search.py: algorithm that interleaves AC3 and search
- sudoku.py: problem framework for solving Sudoku puzzles (and example puzzles)
- kenken.py: partially complete problem framework for specific kenken 
- queens.py: partially complete problem framework for solving nQueens 

To run sudoku, selecting problem [1]:
```
python3 solver.py sudoku 1 ac3 
python3 solver.py sudoku 3 search
```

To run kenken (there is only 1 problem to solve)
```
python3 solver.py ken 0 ac3 
```

To run nqueens (specify the "n"):
```
python3 solver.py queens 4 ac3 
python3 solver.py queens 8 search
```

Sudoku is complete. Use this as a guide for completing nqueens. KenKen was completed during class time.
