'thanks claude.ai'

from problem import Problem

# Example: Cryptarithmetic Puzzle
class Cryptarithmetic(Problem):
    '''
    Cryptarithmetic puzzle solver.
    Example: AB + BC = CA where each letter is a unique digit 0-4.
    Find an assignment of char:digit that makes the math work.

    A state for this problem is a tuple (dict:to_assign, tuple of digits)
    '''

    def __init__(self, problem, digits=range(10)):
        """
        Args with example "AB + A = BA"
            problem[0]: First operand (e.g., "AB")
            problem[1]: Second operand (e.g., "BC")
            problem[2]: Sum (e.g., "CA")
            digits: Available digits (default 0-9)
        """

        # initialize the components of the problem
        self.operand1 = problem[0]
        self.operand2 = problem[1]
        self.result = problem[2]
        self.digits = list(digits)
        
        # Create dictionary of char:digit assignments from operands and result
        self.letters = set("".join(problem))
        self.to_assign = { c:None for c in self.letters }
        self.to_assign['remain'] = len(self.letters)
        
        # Leading letters can't be 0 -- record those letters
        self.leading = {value[0] for value in problem}

    def __str__(self):
        return f'Cryptarithmetic: {self.operand1}+{self.operand2} = {self.result}'


    def get_initial_state(self):
        '''
        State is a tuple of assignments
        (letter_idx, digit_assigned, remaining_digits)
        letter_idx: next letter to be assigned in list self.letters
        digit_assigned: dictionary of already assigned values
        remaining_digits: not yet assigned to any character
        '''
        return (self.to_assign, self.digits)


    def is_goal(self, state):
        """Check if all letters assigned and equation holds."""
        '''
        print('in is goal')
        for x in state:
            print(x,end=' ')
        print()
        '''

        assignments, digits = state

        # have all the letters been assigned? no -- well not at the goal
        if assignments['remain'] != 0:
            return False
        
        # Evaluate the equation - convert operands/result to string equivalent
        # cast to int and see if they add up
        val1 = int(''.join(str(assignments[char]) for char in self.operand1))
        val2 = int(''.join(str(assignments[char]) for char in self.operand2))
        sum_result = int(''.join(str(assignments[char]) for char in self.result))
        
        return val1 + val2 == sum_result


    def get_successors(self, state):
        """Assign next letter to each available digit."""

        assignments, digits = state
        
        # have all the letters been assigned? yes, then no successors
        if assignments['remain'] == 0:
            return []

        # find a letter to assign
        letter = ''
        for key,value in assignments.items():
            if None==value:
                # found one to assign
                letter = key
                break
        
        #print(f'\nassign to {letter} from {assignments} and {digits}')
        successors = []
        # determine all possible assignments to letter (from above)
        for digit in digits:
            #print(f'considering {digit}')
            # Skip 0 for leading letters
            if digit == 0 and letter in self.leading:
                continue

            # if we do not copy, then we would be modifying the one data structure
            new_assignments = assignments.copy()
            new_assignments[letter] = digit
            new_assignments['remain'] -= 1
            new_digits = digits.copy()
            new_digits.remove(digit)
            #print(f'new: {new_assignments}. {new_dgits}')
            
            action = f"{letter}={digit}"
            new_state = (new_assignments, new_digits)
            #print(f'new state: {new_state}')

            # successor: action to get here, resulting state, cost of action
            successors.append((action, new_state, 1))
        
        return successors

    def heuristic(self, state):
        """Number of digits left to assign."""
        assignments, digits = state
        return len(digits)

    '''
    def pretty_print(self,state) :
        length = len(self.result) + 2
        underscore = "-"*length;
        print(f'{self.operand1:>{length}}')
        print(f'{("+ "+self.operand2):>{length}}')
        print(f'{underscore}')
        print(f'{self.result:>{length}}')
    '''
        

problems = [ ['SEND','MORE','MONEY'],
             ["AB", "BA", "CC"]
             ]

    
