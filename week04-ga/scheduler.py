'''
A Genetic Algorithm is a search technique for solving a problem.
It explores a solution space by creating a population of "solutions".
It then calculates the fitness of each solution and uses that fitness
to create the next generation.

The more fit an individual is, the more likely they will be selected as a
parent for the next generation. To make a new individual for the next
generation, 2 people are chosen at random. Those with a higher fitness score
are more likely to be selected. The solutions are recombined to make 2
new individuals. On occasion, one of the individuals is subject to a "mutation" --
a random modification to the individual solution.

In this problem, which is a classic scheduling problem,
the goal is to enroll each student in 1 course.
Ideally, each student would be enrolled in their preferred course (ie. the one
ranked the highest), and every course would have the same number of students.

enrolled[] is an "individual" is a string of characters from "A" to "E"
This is a distribution of students into courses.
ex: enrolled[0] = "B" means that student[0] is enrolled in course "B"
'''

import random

class Scheduler:

    def __init__(self, students, courses):
        self.students = students
        self.student_count = len(students)
        self.courses = courses
        self.ideal_enrollment = self.student_count // len(courses)

    def get_individual(self):
        return [ random.choice(self.courses) for i in range(self.student_count)]

    def evaluate_fitness(self,individual):
        '''
        keep in mind that an "individual" means a single solution
        An individual is a collection of student's course assignments
        '''
        fitness = 0
        for i in range(len(individual)):
            # fitness based on the preference/rank of the course
            # that this student was enrolled in
            course = individual[i]
            fitness += self.students[i].get_preference(course)
        for c in self.courses:
            # trying to maximize fitness.
            # if a course is overenrolled, decrease fitness
            enrollment = individual.count(c)
            fitness += min(0,self.ideal_enrollment-enrollment)

        return fitness

    def mutate(self,individual):
        # enroll some random student in a random course
        rand_student = random.randrange(0,len(self.students))
        individual[rand_student] = random.choice(self.courses)       
        

    def print_roster(self,schedule):
        # create a dictionary to hold the list of students enrolled in each course
        rosters = { "A":[], "B":[], "C":[], "D":[], "E":[] }

        for i in range(len(schedule)):
            # add student[i] to the roster which they were assigned.
            # note that the position [i] in the schedule corresponds to the students[i]
            rosters[schedule[i]].append(self.students[i])

        # print the roster
        for k,v in rosters.items():
            print(k)
            for s in v:
                print(s)

        
