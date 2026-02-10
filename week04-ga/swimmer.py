import math
import random

class Swimmer:
    '''
    Evolve the swim stroke of a creature to maximize forward motion based on that stroke.
    The simulation is extremely oversimplified.
    
    Motion is dependent on the distance traveled of the "hand" along the y-axis.

    Rotation around the y-axis moves the arm "up" and "down" -- towards the top of the water and the ground.
    Rotation around the z-axis moves the arm "forward" and "backward".

    The [x,y,z] position of the "hand" can be calculated from those 2 angles of rotation and arm length.
    This calculation is called forward kinematics.

    2 PAIRS of angles results in 2 points in space: p1 = [x1,y1,z1] and p2 = [x2,y2,z2].
    The difference y2-y1 is used as the distance traveled (i.e. forward motion).
    The velocity is that difference/(time to travel from p1 to p2), and it is a multiplier of the distance.
    The faster it moves, the greater the multiplier (i.e. the greater the forward motion)
    '''
    
    def __init__(self,trajectory_length,arm_length):

        # length is number of angle pairs x2
        self.trajectory_length = trajectory_length

        self.arm_length = arm_length
        
        # arbitrary change in time between each angle
        self.time_step = 10


    def get_individual(self):

        # individual is a series of pairs of angles
        return [ random.randint(-90,90) for i in range(self.trajectory_length) ]
    

    def evaluate_fitness(self,individual):

        # trajectory has to be full circle (i.e. it ends where it started)
        individual = list(individual) + [individual[0],individual[1]]
        fitness = 0
        for i in range(0,len(individual)-4,2):
            # position of hand at angle i//2
            y1 = individual[i]
            z1 = individual[i+1]
            point1 = self.calculate_xyz(y1,z1)

            # position of hand at next angle 
            y2 = individual[i+2]
            z2 = individual[i+3]
            point2 = self.calculate_xyz(y2,z2)

            fitness += self.calculate_distance(point1,point2)
            
        return fitness
        

    def mutate(self,individual):
        # randomly modify one of the angles of the individual
        individual[random.randrange(0,len(individual))] = random.randint(-90,90)


    def calculate_xyz(self,ay,az):
        # convert degrees to radians
        ay = ay*math.pi/180
        az = az*math.pi/180

        # using forward kinematics to calculate the position of
        # the end of the arm in 3 dimensional space
        x = self.arm_length * math.cos(az) * math.cos(ay)
        y = self.arm_length * math.sin(az) * math.cos(ay)
        z = self.arm_length * math.sin(ay)
    
        return [x, y, z]

    def calculate_distance(self,prev_position, curr_position):
        # how much the arm changed position along the y-axis
        delta_y = curr_position[1] - prev_position[1]
        # the rate of change
        velocity = delta_y / self.time_step

        # scale the distance by velociy. The faster the motion, the further it traveled.
        return delta_y * velocity*velocity

