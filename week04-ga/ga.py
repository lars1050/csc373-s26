import random

class GA:

    def __init__(self,fselect):

        # probability of an individual being mutated
        self.mutation_rate = .1

        # max iterations of evolution
        self.max_generations = 200

        # number of individuals in the population
        self.population_size = 20

        # function for selecting parents for procreation
        self.selection_fn = fselect

    def solve(self,problem):

        # Create initial population
        population = []
        for _ in range(self.population_size):
            population.append(problem.get_individual())

        # Establish a "best" fitness and corresponding individual
        # individual and fitness correspond by their index
        fitness = []
        for ind in population:
            fitness.append(problem.evaluate_fitness(ind))

        # find the most fit individual
        best_fitness = max(fitness)
        best_individual = population[fitness.index(best_fitness)]

        # print status to the screen at this frequency
        report_frequency = self.max_generations//10

        # track how the best individual evolved over generations
        evolved = []

        # evolve for specified generations
        for generation in range(self.max_generations):

            if generation%report_frequency == 0:
                evolved.append([best_individual,best_fitness])
                print(f'Evolved {generation} generations. Best Fitness {best_fitness}')

            # calculate fitness of every individal
            fitness = [ problem.evaluate_fitness(ind) for ind in population ]

            best_in_population = max(fitness)
            if best_in_population > best_fitness:
                # best of this generation is best over all generations
                best_fitness = best_in_population
                best_individual = population[fitness.index(best_fitness)]

            else:
                # previous generation had a more fit individual. keep them
                population.append(best_individual)
                fitness.append(best_fitness)
                # note that this adds 1 to the population.

            # create next generation
            population = self.selection_fn(population,fitness)

            # mutate 1 individual with some probability
            if random.random() < self.mutation_rate:
                problem.mutate(population[random.randrange(0,len(population))])

            # record the best of this generation
            evolved.append([best_individual,best_fitness])

        return evolved


