import search

import grid_world
import route
import eight

def solve(problem,algo):
    print(f"\n{'-' * 60}")
    print(f"{algo.upper()}: {problem}")
    print(f"{'-' * 60}")
    
    result = search.search(problem, algo)
    problem.pretty_print(result.get_path())
    problem.show_path(result)

if __name__ == '__main__':

    import sys

    # command line arguments [solver.py, problem, problem #, algo]
    if len(sys.argv) < 4:
        print('ERROR: problem, problem #, and algorithm required.')
        raise Exception
    try:
        problem_type = sys.argv[1]
        specific_problem = sys.argv[2]
        algorithm = sys.argv[3]
    except Exception as e:
        print('ERROR: command line arguments incorrect.')

    if 'grid'==problem_type:
        # problem setting corresponds to grid world size
        problem = grid_world.GridWorld(grid_size=int(specific_problem), pit_percent=15)

    elif 'route'==problem_type:
        # problem setting ignored in this case
        problem = route.RomaniaMap(specific_problem)

    elif 'eight'==problem_type:
        # problem setting corresponds to [index] of problems in eight.py
        problem = eight.EightPuzzle(eight.problems[int(specific_problem)])

    else:
        print(f'Error: problem type {problem_type} not recognized.')
        raise Exception

    solve(problem,algorithm)
    





