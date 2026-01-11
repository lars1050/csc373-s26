
import search

import cryptarithmetic as crypt
import sudoku
from sudoku import Sudoku

import sys              

def solve(problem,algo):
    print(f"\n{'-' * 60}")
    print(f"{algo.upper()}: {problem}")
    print(f"{'-' * 60}")
    
    result = search.search(problem, algo)
    #problem.pretty_print(result.state)
    problem.show_path(result)

if __name__ == '__main__':

    # command line arguments [solver.py, problem, problem #, algo]
    if len(sys.argv) < 4:
        print('ERROR: problem, problem #, and algorithm required.')
        raise Exception
    try:
        problem_type = sys.argv[1]
        problem_number = int(sys.argv[2])
        algorithm = sys.argv[3]
    except Exception as e:
        print('ERROR: command line arguments incorrect.')

    if 'sudoku'==problem_type:
        problem = Sudoku(sudoku.problems[problem_number])
        
    elif 'crypt'==problem_type:
        problem = crypt.Cryptarithmetic(crypt.problems[problem_number])

    else:
        print(f'Error: problem type {problem_type} not recognized.')
        raise Exception

    solve(problem,algorithm)





