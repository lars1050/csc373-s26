import copy

class NqueensCSP:

    def __init__(self,size):

        self.initial_state = [0 for _ in range(size)]
        self.size = size
        self.solution = None
        print(f'\nSolving a {size}-Queens Problem')

        self.variables = list(range(size))
        self.domains = {i: list(range(size)) for i in range(size)}
        
        self.set_constraints()

    def get_initial_state(self):
        return self.initial_state

    def is_goal(self):
        # if all domains reduced to 1 value, we are done
        for dom in self.domains.values():
            if len(dom) != 1:
                return False
        self.solution = [ self.domains[i][0] for i in range(self.size)]
        return True

    def reset_domains(self,d):
        self.domains = d

    def set_constraints(self):

        # not equal lambda function (they cannot be set to the same column)
        fne = 

        # they cannot be diagonal. row diff != col diff
        # call this function to create between specific rows
        # use it like this to make constraint: (((q1,q2),fdiag(q1,q2)))
        def fdiag(q1,q2):
            # a,b are the columns from the domain
            # q1 and q1 are the rows (variable reference)
            return lambda a,b: abs(a-b) != abs(q1-q2)

        # create constraint list for each variable

            
        # create constraints for each pair of queens
        for q1 in range(self.size):
            for q2 in range(q1+1,self.size):
                # set not in same column

                # set not diagonal


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

        # Found a leaf: no children probably means it is a solution
        if None==to_assign:
            return successors

        # each domain value of the selected variable is a successor (child)
        for value in domains[to_assign]:
            
            # create a new state with var assigned to that value
            new_domains = copy.deepcopy(domains)
            new_domains[var] = [value]
            action = f'{var}=[{value}]'
            successors.append((action, (new_domains), 1))
            
        return successors
