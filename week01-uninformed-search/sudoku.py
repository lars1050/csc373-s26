from problem import Problem

constraining = True

class Sudoku(Problem):
    '''
    Sets up problem to be solved by search technique.
    A sudoku puzzle is represented by a flat list of all rows.
    Any slot with a 0 needs to be assigned.
    '''
    
    def __init__(self,initial_state):
        '''
        initial_state: sizexsize length list represents puzzle.
            any unassigned slot is filled with a 0
        '''
        
        self.initial_state = initial_state
        self.solution = None
        self.max_digit = int(len(initial_state)**0.5)
        print(f'\nSolving a {self.max_digit}x{self.max_digit} puzzle',end=' ')
        print(f'with {initial_state.count(0)} unassigned slots.')
        
        # 4 boxes in 4x4 sudoku, each 2x2 (store those indices)
        if self.max_digit == 4:
            self.boxes = [[0,1,4,5],[2,3,6,7],[8,9,12,13],[10,11,14,15]]
            
        # 6 boxes in 4x6 sudoku, each 2x3 (store those indices)
        elif self.max_digit == 6:
            base = [0,1,2,6,7,8]
            self.boxes = []
            for b in range(3):
                # left box
                self.boxes.append(base)
                # right box
                self.boxes.append([el+3 for el in base])
                # next set (2 rows down)
                base = [el+12 for el in base]

        # 9 boxes in 9x9 sudoku, each 3x3 (store those indices)
        else:
            base = [0,1,2,9,10,11,18,19,20]
            self.boxes = []
            for b in range(3):
                # left most
                self.boxes.append(base)
                # middle box
                self.boxes.append([el+3 for el in base])
                # right most
                self.boxes.append([el+6 for el in base])
                # next set (3 rows down)
                base = [el+27 for el in base]
        #print(f'boxes {self.boxes}')
        
    def __str__(self):
        return f'Sudoko {self.initial_state}'
    
    def get_initial_state(self):
        return self.initial_state
    
    def is_goal(self, state):

        # not done if puzzle has open slots
        if 0 in state:
            return False

        # slot filled with only viable numbers...no 0's then done
        if constraining:
            self.solution = state
            return True

        # filled in but could be wrong ... are all the rows unique?
        for row in range(0,len(state),self.max_digit):
            if len(set(state[row:row+self.max_digit])) != self.max_digit :
                return False

        # are all the columns unique?
        for col in range(0,self.max_digit):
            if len(set(state[col:len(state):self.max_digit])) != self.max_digit:
                return False

        # are all the boxes unique?
        for b in self.boxes:
            if len(set([state[i] for i in b])) != self.max_digit:
                return False

        # it all checked out
        self.solution = state
        return True

    def get_options(self,state,index):
        '''
        state: representation of current assignments on sudoku board
        index: next box to be filled

        find all possible digits that can be placed at state[index]
        '''

        # all the possible digits
        digits = [i for i in range(1,self.max_digit+1)]

        if not constraining:
            return digits

        start_row = index//self.max_digit * self.max_digit
        start_col = index - start_row

        # create a list of all assigned slots in the puzzle
        # that are relevant to state[index]. this includes those
        # in the same row, same column, and same box (hard coded above)
        row_els = state[start_row:start_row+self.max_digit]
        col_els = state[start_col:len(state):self.max_digit]
        # get the elements in the box
        for b in self.boxes:
            if index in b:
                box_els = [state[i] for i in b]
                break

        # all that state[index] cannot be assigned (1 rep per digit)
        elements = set(row_els + col_els + box_els)
        
        # find those not in elements
        #   and define as possible assignment for state[index]
        okay = []
        for d in digits:
            if not d in elements:
                okay.append(d)
        digits = [i for i in okay]
        
        return digits
       
        
    def get_successors(self, state):
        """Return list of (action, next_state, cost) tuples."""

        successors = []
        try:
            # unassigned have value 0
            next_slot = state.index(0)

            
            # create a new state with each possible assignment
            options = self.get_options(state,next_slot)
            #print(f'options for [{next_slot}] is {options}')
            for digit in options:
                new_state = state.copy()
                new_state[next_slot] = digit
                action = f"[{next_slot}]={digit}"
                new_state = (new_state)
                #print(f'new state: {new_state}')

                # successor: action to get here, resulting state, cost of action
                successors.append((action, new_state, 1))
            return successors
            
        except ValueError:
            ''' everything filled - no successors '''
            return []
            
    
    def heuristic(self, state):
        """Return estimated cost from state to goal."""
        # number left to assign
        return state.count(0)

    def pretty_print(self,state):
        index = 0
        for r in range(self.max_digit):
            for c in range(self.max_digit):
                print(f'{state[index]:2}',end=' ')
                index += 1
            print()
        print()


# -------------------------------------------
# define several problems that we might solve
blank4 = [
    0,0, 0,0,
    0,0, 0,0,
    0,0, 0,0,
    0,0, 0,0 ]

blank6 = [
    0,0,0, 0,0,0,
    0,0,0, 0,0,0,
    0,0,0, 0,0,0,
    0,0,0, 0,0,0,
    0,0,0, 0,0,0,
    0,0,0, 0,0,0 ]

blank9 = [
    0,0,0, 0,0,0, 0,0,0,
    0,0,0, 0,0,0, 0,0,0,
    0,0,0, 0,0,0, 0,0,0,
    0,0,0, 0,0,0, 0,0,0,
    0,0,0, 0,0,0, 0,0,0,
    0,0,0, 0,0,0, 0,0,0,
    0,0,0, 0,0,0, 0,0,0,
    0,0,0, 0,0,0, 0,0,0,
    0,0,0, 0,0,0, 0,0,0, ]


problem0 = [0,0,0,3, 0,4,0,0, 1,0,0,4, 0,0,3,0]

problem1 = [
    2,0,0, 6,0,5,
    0,0,6, 0,1,2,
    0,5,1, 0,0,3,
    3,0,4, 0,0,6,
    0,3,5, 0,0,1,
    0,0,2, 0,3,4 ]

problem2 = [
    0,0,5, 0,0,6,
    0,0,0, 1,4,0,
    0,0,0, 3,0,2,
    0,6,0, 0,0,0,
    0,0,0, 0,2,0,
    2,0,1, 0,0,0 ]

problem3 = [ 0,7,0, 5,8,3, 0,2,0,
         0,5,9, 2,0,0, 3,0,0,
         3,4,0, 0,0,6, 5,0,7,
         7,9,5, 0,0,0, 6,3,2,
         0,0,3, 6,9,7, 1,0,0,
         6,8,0, 0,0,2, 7,0,0,
         9,1,4, 8,3,5, 0,7,6,
         0,3,0, 7,0,1, 4,9,5,
         5,6,7, 4,2,9, 0,1,3
         ]

problem4 = [ 0,4,0, 1,0,0, 9,0,0,
         0,0,0, 0,0,0, 0,0,0,
         0,5,9, 0,0,0, 2,1,6,
         0,6,0, 0,0,0, 1,5,0,
         0,0,4, 5,0,0, 0,0,2,
         3,0,0, 4,0,1, 0,0,0,
         0,0,0, 0,0,8, 0,0,7,
         0,3,0, 2,0,0, 0,0,0,
         0,0,7, 0,0,6, 0,0,9 ]

# solved problem2. copy and systematically remove some elements for testing
problem5 = [
     4,1,5, 2,3,6, 
     6,2,3, 1,4,5,
     1,5,4, 3,6,2,
     3,6,2, 5,1,4,
     5,3,6, 4,2,1,
     2,4,1, 6,5,3 ]

problem_count = 6
problems = [ eval('problem'+str(i)) for i in range(0,problem_count) ]

if __name__ == '__main__':
    for p in problems:
        s = Sudoku(p)
        s.pretty_print(p)
        print()


