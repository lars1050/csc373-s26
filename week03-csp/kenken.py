import copy

class KenKenCSP:
    '''
    This problem is set up as the puzzle that we worked on in class.
    It has the general framework to apply to any KenKen of any size,
    but the mathematical constraints for any puzzle would have to be
    hard coded into this puzzle.
    '''

    def __init__(self):
        
        self.puzzle_size = 9
        self.max_digit = 3
        print(f'\nSolving a {self.max_digit}x{self.max_digit} puzzle',end=' ')

        self.solution = None
        
        # each var is a number representing the position in the puzzle
        self.variables = [i for i in range(9)]

        # domains are the same for all, unless the one value is given
        self.domains = {}
        for idx in range(self.puzzle_size):
            self.domains[idx] = [1,2,3]
        self.domains[2] = [2]
        
        self.set_constraints()

    def is_goal(self):
        # if all domains reduced to 1 value, we are done
        for dom in self.domains.values():
            if len(dom) != 1:
                return False
        return True

    def set_constraints(self):

        # create dictionary of constraints
        # key: variable, value is [((var1,var2),fn),((var1,var3),fn),...]

        # uniqueness is a constraint between all variables across rows and columns
        fne = 

        # create a list of constraints for each variable
        self.constraints = {}
        for var in self.variables:
            self.constraints[var] = []
            
        # set row constraints
        # for each row in the puzzle
        for row in range(0,self.puzzle_size,self.max_digit):
            # for each digit in that row
            for i in range(row,row+self.max_digit):
                # for each "next" digit in this row
                for j in range(i+1,row+self.max_digit):
                    


        # set col constraints
        for col in range(self.max_digit):
            for i in range(col,self.puzzle_size,self.max_digit):
                for j in range(i+self.max_digit,self.puzzle_size,self.max_digit):



        # set mathematical constraints

        
                    

                                     

