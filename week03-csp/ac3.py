from collections import deque

def ac3(problem):
    """
    problem consists of ...
        variables: List of variable names
        domains: Dict mapping variable -> list of possible values
        constraints: List of (var1, var2, constraint_func) tuples
                    where constraint_func(val1, val2) returns True if constraint satisfied
    """

    # Initialize queue with all arcs (i.e. constraints)
    queue = deque()
    for x in problem.variables:
        for c in problem.constraints[x]:
            # ((i,j),lambda) tuple
            queue.append(c)

    # keep going until there are no more constraints to apply
    while queue:
        (x,y),fn = queue.popleft()
        if revise(x,y,fn,problem.domains):
            
            # maybe there is not solution. domain is now empty
            if len(problem.domains[x]) == 0:
                return False
            
            # Add all arcs (k, x) where k is a neighbor of x (but not y)
            for (x_val,neighbor),xn_constraint in problem.constraints[x]:
                for (n,z),nz_constraint in problem.constraints[neighbor]:
                    if z==x and n!=y:
                        queue.append(((n,z),nz_constraint))
                        
    # reduced domains as much as possible
    return True


def revise(x,y,fn,domains):
    """
    Make variable x arc-consistent with variable y.
    Remove values from x's domain that have no valid assignment in y's domain.
    
    Returns:
        True if we revised (removed values from) x's domain
    """
    revised = False

    # why would there be None ???
    if fn is None:
        return False
    
    # Check each value in x's domain against all values in the y's domain
    for val_x in list(domains[x]):  # Use list() to avoid modifying during iteration
        
        # Check if there exists any value in y's domain that satisfies the constraint
        satisfiable = any(fn(val_x, val_y) for val_y in domains[y])

        # if no value in y's domain can be used with this value of x's domain ...
        if not satisfiable:
            domains[x].remove(val_x)
            revised = True
    
    return revised

