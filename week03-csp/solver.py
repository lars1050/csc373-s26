import ac3
from ac3_search import TreeSearch

import sudoku_csp
from sudoku_csp import SudokuCSP

#import kenken

#import queens
#from queens import NqueensCSP



def solve(problem,algo):
    print(f"\n{'-' * 60}")
    print(f"{algo.upper()}: {problem}")
    print(f"{'-' * 60}")

    import time
    start_time = time.perf_counter()

    if algo=='ac3':
        result = ac3.ac3(problem)
        print(problem.domains)
    elif algo=='search':
        tree = TreeSearch(problem)
        doms = tree.search()
        if None==doms:
            print('no solution found')
        else:
            print(doms)
            
            for p in problem.solution:
                right = problem.size - p - 1
                print(f'|{"   |"*p} Q |{"   |"*right}')
            
    else:
        print(f'ERROR: Algorithm {algo} is not recognized.')

    end_time = time.perf_counter()
    print(f'Execution time: {(end_time-start_time):.6f} seconds')


if __name__ == '__main__':

    import sys

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
        problem = SudokuCSP(sudoku_csp.problems[problem_number])
    
    #elif 'ken'==problem_type:
    #    problem = kenken.KenKenCSP()
        
    #elif 'queens'==problem_type:
    #    problem = queens.NqueensCSP(problem_number)

    else:
        print(f'Error: problem type {problem_type} not recognized.')
        raise Exception
    

    solve(problem,algorithm)
    





