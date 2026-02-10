import random

debugging = False

def generalized(population,fitness):
    '''
    Selection for procreation is based on Monte Carlo selection.
    The higher the fitness, the more likely to be chosen.
    The population size will remain stable (2 parents = 2 children)
    '''
    
    next_generation = []
    
    # every set of parents create 2 children, so do this popsize/2
    for i in range(len(population)//2):

        # randomly select parents. better fitness = better probability of selection
        parent1 = population[monte_carlo_selection(fitness)]
        parent2 = population[monte_carlo_selection(fitness)]


        # Construct each child with "half" of parent1 and "half" of parent2
        # Split the course preferences (DNA string) at some random location
        # to generate the two "halves" 
        divide_at = random.randrange(1,len(parent1))
        next_generation.append(parent1[:divide_at]+parent2[divide_at:])
        next_generation.append(parent2[:divide_at]+parent1[divide_at:])

    return next_generation
        

def monte_carlo_selection(weights):
    '''
    Modified from claude.ai
    monte carlo selection randomly selects from a list based on how
    much each is "weighted". The more it is weighted, the more likely
    it is to be selected.
    '''
    
    total = sum(weights)
    normalized = [int(w/total*100+.5)/100 for w in weights]
    if debugging:
        print(f'normalized: {normalized}')
        
    # Generate random number betwen 0 and 1
    r = random.random()
    
    # randomly select based on probability for each item
    # returns the index of the item to be selected
    selection_probability = 0
    for i in range(len(normalized)):
        selection_probability += normalized[i]
        if r <= selection_probability:
            return i
        
    # in case the weights do not perfectly total 1.0 (due to rounding error)
    return i

if __name__ == '__main__':

    # try out monte_carlo_selection
    fitness = [ 5, 1, 3, 3, 2, 1, 1, 1, 5]
    print(f'fitness: {fitness}')
    
    debugging = True    # to see normalized weights
    select = monte_carlo_selection(fitness)
    print(f'index {select} : {fitness[select]}')

    debugging = False
    print("selected these values with repeated call to monte carlo")
    for _ in range(40):
        select = monte_carlo_selection(fitness)
        print(f'{fitness[select]}',end=' ')
    print()
    
    
    
