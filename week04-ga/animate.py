import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

import random
import math

# Thank you claude.ai for you guidance and code
# And thanks Dr. Dasgupta in physics

arm_length = 5

def calc_position(ay,az):
    
    # convert degrees to radians
    ay = ay*math.pi/180
    az = az*math.pi/180

    # using forward kinematics to calculate the position of
    # the end of the arm in 3 dimensional space
    x = arm_length * math.cos(az) * math.cos(ay)
    y = arm_length * math.sin(az) * math.cos(ay)
    z = arm_length * math.sin(ay)
    
    return [x, y, z]

def calculate_distance(prev_position, curr_position, time):
    # how much the arm changed position along the y-axis
    delta_y = curr_position[1] - prev_position[1]
    # the rate of change
    velocity = delta_y / time

    # scale the distance by velociy. The faster the mostion, the further it travelled.
    return delta_y * velocity*velocity

def animate(angles,time_step=20):

    # create in between motion for the angles for better animation
    angles = list(angles) + [angles[0],angles[1]]
    more_angles = []
    for i in range(0,len(angles)-3,2):
        deltay = (angles[i+2] - angles[i])/time_step
        deltaz = (angles[i+3] - angles[i+1])/time_step
        starty = angles[i]
        startz = angles[i+1]
        for t in range(time_step):
            more_angles += [ starty + t*deltay, startz + t*deltaz ]
            
            
    
    positions = []
    for i in range(0,len(more_angles),2):
        positions.append(calc_position(more_angles[i],more_angles[i+1]))

    #print(positions)

    # Define the starting point
    origin = [0, 0, 0]
    opposite_origin = [-1,0,0]

    # Create the figure and axes object
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Initialize quiver plot with placeholder data
    quiver = ax.quiver(*origin, 0,5,0, color='r')

    # Set the axis limits
    max_val = 10  # Set based on your max vector component
    ax.set_xlim([-max_val, max_val])
    ax.set_ylim([-max_val, max_val])
    ax.set_zlim([-max_val, max_val])

    # Set the axis labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Vector Animation')

    # Function to draw a transparent plane
    def plot_xy_plane(ax, z_height=0):
        # Create a grid of x, y points
        xx, yy = np.meshgrid(np.linspace(-max_val, max_val, 10), 
                             np.linspace(-max_val, max_val, 10))
        
        # z values are all the same to create a flat plane
        zz = np.ones_like(xx) * z_height
        
        # Plot the plane
        ax.plot_surface(xx, yy, zz, color='g', alpha=0.3, rstride=1, cstride=1)


    # Function to create a sphere
    def plot_sphere(ax, center, radius, color='b'):
        # Create a sphere
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 20)
        
        x = center[0] + radius * np.outer(np.cos(u), np.sin(v))
        y = center[1] + radius * np.outer(np.sin(u), np.sin(v))
        z = center[2] + radius * np.outer(np.ones(np.size(u)), np.cos(v))
        
        # Plot the sphere
        ax.plot_surface(x, y, z, color=color, alpha=0.7, rstride=2, cstride=2)


    # Function to update the plot in each animation frame
    def update(frame):
        ax.clear()  # Clear previous frame
        
        # Set up the axes again
        ax.set_xlim([-max_val, max_val])
        ax.set_ylim([-max_val, max_val])
        ax.set_zlim([-max_val, max_val])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        
        # Define vectors for each frame
        #vectors = [
        #    [0, 5, 0],
        #    [5, 5, 0],
        #    [5, 0, 0]
        #]

        vectors = positions
        
        # Get current vector based on frame number
        current_vector = vectors[frame % len(vectors)]
        opposite_vector = [ -current_vector[0], current_vector[1], current_vector[2] ]

        start_vector = vectors[0]
        start_opposite = [ -start_vector[0], start_vector[1], start_vector[2] ]


        plot_xy_plane(ax,z_height=0)

        plot_sphere(ax,[-0.5,0,0], radius=0.5,color='blue')

        ax.quiver(-0.5,0,0, 0,-10,0, color='b')
        ax.quiver(*origin, *start_vector, color='g')
        ax.quiver(*opposite_origin, *start_opposite, color='g')
        
        # Add a quiver plot with the current vector
        ax.quiver(*origin, *current_vector, color='r', label=f'Vector: {current_vector}')
        ax.quiver(*opposite_origin, *opposite_vector, color='r', label=f'Vector: {current_vector}')

        ax.set_title(f'Vector: {current_vector}')
        ax.legend()
        
        return ax

    # Create animation
    ani = FuncAnimation(fig, update, frames=len(more_angles), interval=100, blit=False, repeat=True)

    plt.tight_layout()
    plt.show()

