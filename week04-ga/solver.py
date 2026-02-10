import swimmer
import student
import scheduler
import ga
import selection_fns
import animate

def evolve_swimmer():
    problem =  swimmer.Swimmer(10,8)
    ai = ga.GA(selection_fns.generalized)
    evolved = ai.solve(problem)
    for e in evolved:
        print(f'Fitness: {e[1]}')

    #animate.animate(evolved[0][0])
    winner = evolved[-1][0]
    for i in range(0,len(winner),2):
        angley = winner[i]
        anglez = winner[i+1]
        point = animate.calc_position(angley,anglez)
        print(f'({point[0]:.1f}, {point[1]:.1f}, {point[2]:.1f}),',end='')
    print()
    animate.animate(winner)

def evolve_schedule():

    # student count can be modified to <= 200
    # if you want more than 200 students, uncomment make_students_csv
    student_count = 50
    
    # other parts of the code would have to be modified to change courses
    courses = ['A','B','C','D','E']

    # if you want to make a new batch of students, uncomment this
    # student.make_students_csv(student_count,courses)

    # load students from csv file into list of Student objects
    students = student.get_students(student_count)
    
    problem = scheduler.Scheduler(students,courses)
    ai = ga.GA(selection_fns.generalized)
    evolved = ai.solve(problem)
    winner = evolved[-1][0]
    problem.print_roster(winner)

#evolve_swimmer()
evolve_schedule()

