import copy

class SudokuCSP:

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

        # each variable is a number corresponding to location in puzzle
        # upper-left is var 0, then proceed row-wise
        self.variables = [i for i in range(len(self.initial_state))]
        
        self.set_domains()
        self.set_constraints()

    def get_initial_state(self):
        return self.initial_state

    def is_goal(self):
        # if all domains reduced to 1 value, we are done
        for dom in self.domains.values():
            if len(dom) != 1:
                return False
        return True

    def set_domains(self):
        '''
        Creating a dictionary of domains for each variable.
        If in the initial state it has a value, then that is its domain.
        A variable is identified by its index in the state.
        The state is a flat list.
        '''
        self.domains = {}
        
        # for each variable (position) of the puzzle
        for idx in range(len(self.initial_state)):
            
            # if has a value, that is its domain, otherwise it can be any digit
            if 0 != self.initial_state[idx]:
                self.domains[idx] = [self.initial_state[idx]]
            else:
                self.domains[idx] = [d for d in range(1,self.max_digit+1)]

    def reset_domains(self,d):
        self.domains = d

    def set_constraints(self):

        # create dictionary of constraints
        # key: variable, value is [((var1,var2),fn),((var1,var3),fn),...]

        # uniqueness is the only constraint between all variables
        fne = lambda a,b:a!=b

        # establish a lis of constraints for every variable
        self.constraints = {}
        for var in range(len(self.initial_state)):
            self.constraints[var] = []
            
        # for each row in the puzzle, set constraints
        for row in range(0,len(self.initial_state),self.max_digit):
            # for each pair in that row
            for i in range(row,row+self.max_digit):
                for j in range(i+1,row+self.max_digit):
                    '''
                    self.constraints[i].append(((i,j),fne))
                    self.constraints[j].append(((j,i),fne))
                    '''
                    if ((i,j),fne) not in self.constraints[i]:
                        self.constraints[i].append(((i,j),fne))
                    if ((j,i),fne) not in self.constraints[j]:
                        self.constraints[j].append(((j,i),fne))
                                                   
        # for each col in the puzzle, set constraints
        for col in range(self.max_digit):
            # for each pair in that column
            for i in range(col,len(self.initial_state),self.max_digit):
                for j in range(i+self.max_digit,len(self.initial_state),self.max_digit):
                    if ((i,j),fne) not in self.constraints[i]:
                        self.constraints[i].append(((i,j),fne))
                    if ((j,i),fne) not in self.constraints[j]:
                        self.constraints[j].append(((j,i),fne))

        # set box constraints
        for box in self.boxes:
            # for each pair in the box
            for i in range(len(box)):
                for j in range(i+1,len(box)):
                    if ((box[i],box[j]),fne) not in self.constraints[i]:
                        self.constraints[box[i]].append(((box[i],box[j]),fne))
                    if ((j,i),fne) not in self.constraints[j]:
                        self.constraints[box[j]].append(((box[j],box[i]),fne))


    def get_successors(self,domains):
        '''
        To do this the smart way, we would find either
        - variable with the minimum length domain > 1, and consider all assignments (MRV)
        - variable that has the most constraints

        But we will do this the easy way ...
        '''
        successors = []
        to_assign = None
        
        # the easiest is to find the first var that has |dom|>1
        for var,dom in domains.items():
            if len(dom) > 1:
                to_assign = var
                break

        if None==to_assign:
            return successors

        # each possible value in the domain is a successor (child)
        for value in domains[to_assign]:
            # create a new state with var assigned to that value
            new_domains = copy.deepcopy(domains)
            new_domains[var] = [value]
            action = f'{var}=[{value}]'
            successors.append((action, (new_domains), 1))
        return successors

                    
        
problem0 = [0, 0, 0, 3,
     0, 4, 0, 0,
     1, 0, 0, 4,
     0, 0, 3, 0 ]

problem1 = [
    2,0,0, 6,0,5,
    0,0,6, 0,1,2,
    0,5,1, 0,0,3,
    3,0,4, 0,0,6,
    0,3,5, 0,0,1,
    0,0,2, 0,3,4 ]

problem2 = [0, 0, 0, 3,
     0, 0, 0, 0,
     0, 0, 0, 0,
     0, 0, 0, 0 ]

problem3 = [ 0,4,0, 1,0,0, 9,0,0,
         0,0,0, 0,0,0, 0,0,0,
         0,5,9, 0,0,0, 2,1,6,
         0,6,0, 0,0,0, 1,5,0,
         0,0,4, 5,0,0, 0,0,2,
         3,0,0, 4,0,1, 0,0,0,
         0,0,0, 0,0,8, 0,0,7,
         0,3,0, 2,0,0, 0,0,0,
         0,0,7, 0,0,6, 0,0,9 ]

problems = [problem0, problem1 ,problem2, problem3]
                                     

