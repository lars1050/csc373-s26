class Student:

    def __init__(self,data):
        '''
        Create a student object based on a list of information.
        List is in the order: last,first,prefA,B,C,D,E
        The prefA,B,... is the student ranking for that course.
        The higher the ranking, the more they prefer that course.
        '''
        self.last = data[0]
        self.first = data[1]

        # create a dictionary that holds the preference/rank for each course
        self.preferences = {}
        index = 2
        for course in range(ord("A"),ord("E")+1):
            self.preferences[chr(course)] = data[index]
            index += 1

    def __str__(self):
        # pretty print function
        out_string = self.get_name()+' '
        for k,v in self.preferences.items():
            out_string += f'{k}:{v} '
        return out_string

    def get_preference(self,course):
        return self.preferences[course]

    def get_name(self):
        return self.last+","+self.first

def get_students(length):
    '''
    Create a list of students based on the students.csv file

    OUTPUT: List of Student objects of specified length
    
    The csv holds a list of students that have been randomly constructed
    from the function below. You can make a new set of random students
    in the constructor by calling that function.

    Each line of the file is this:
        last name, first name, preferences for the 5 classes in ABCDE order

    Preferences in the csv file are a random permutation of the numbers 1,2,3,4,5
    '''
    
    # Open file of students (made randomly with below function)
    f = open('students.csv')
    student_info = f.readlines()
    f.close()

    # Organize students into a list structure
    students = []
    for line in student_info:
        # make csv line into a list, cast, and add to students
        lister = line[:-1].split(',')
        for i in range(2,len(lister)):
            lister[i] = int(lister[i])
        students.append(Student(lister))
        
    return students[:length]
    
'''
This creates a csv file with random students.
Each row in the file is a student.
Each student has a last name, first name, followed by a series of rankings of courses.
'''

firsts = ["Amy", "Erik", "Pavel", "Matt", "Abdi", "Sadaq", "Miguel", "Jocelyn",
          "Adnan", "Luis", "Emily", "Drew", "Everett", "Ayden", "Walta", "Joshua",
          "Keiran", "Elias", "Faiaz", "Sergio", "Ivan", "Max", "Mohamed", "Awal",
          "Chelsey", "Johnny", "Pao", "Jaron", "Liban", "Taha", "Tenley", "Josh",
          "Xeng", "Gabriel", "Asli", "Hodan", "Jamila", "Amaal", "Ari", "Quinn",
          "Mohamud", "Derek", "Dori", "Guleid", "Yuva", "Rudwan", "Aisha", "Hamsa",
          "Ethan", "Talib", "Kwadwo", "Melissa", "Jake", "Chris", "Skyler", "Zach",
          "Liban", "Fatima", "Kodjo", "Corey", "Kebba", "Hannah", "Eric", "Jeffrey",
          "Esmeralda", "Leah", "Halah", "Krystal", "Rahma", "Romeo", "Ivie", "Andy",
          "Karen", "Elisha", "Khadro", "Adna", "Sundus", "Mohamed", "Ivan",
          "Timothy", "Vinny", "Mayali", "Betelehem", "Ermais", "Matt", "Collin",
          "Tommy", "Moua", "Long", "Miriam", "Keenan", "Sumayyah", "Nathan",
          "Matthew", "Angel", "Vivika", "Thor", "Brandon", "Andy", "Erica",
          "Bailey", "Ariana", "Linus", "Elliott", "Vincent", "Josh", "Sean",
          "Katelynn", "Saryn", "Bjorn", "Doua", "Amina", "Muna", "Xera", "Khaalid",
          "Mitchell", "Zakaria", "Leban", "Chris", "Khalid", "Ryan", "Alinase",
          "Brian", "Anna", "Zak", "Nikita", "Luke", "Ridwan", "Najma", "Brooklyn",
          "Ella", "Ceazar", "Mackenzie", "Stephanie", "Myles", "Christopher",
          "Kevin", "Jason", "Justin", "Odin", "Katie", "Jacob", "Lucy", "Vincent",
          "Najma", "Ly" ]
    
lasts = [ "Larson", "Steinmetz", "Atukorala","Pattanayak", "Haines", "Doree",
          "Belik", "Zobitz", "Sorensen", "Voyles", "Flint", "Chen", "Chafee",
          "Crowe", "Averbeck", "Klassin", "Brandl", "Mohamud", "Ahmed", "Xiong",
          "Memeti", "Lee", "Ng", "Nguyen", "Abdi", "Czech", "Vang", "OKeefe",
          "Atto", "Leal", "Hersi", "Mohammad", "Abukar", "Mckinnon", "Osman",
          "Yang", "Yusuf", "Edow", "Kempenich", "Adan", "Ali", "Hagen", "Torres",
          "Warns", "Beeby", "Gottimukala", "Alvarado","Boyer", "Sati", "Wadhawan",
          "Vo", "Ramales", "Owusu","Carrillo","Hopper","Lovelace","Ellis", "Bryan",
          "Fatty", "Abdullahi", "Abukar", "Adem", "Ahmed", "Bashige", "Belayneh",
          "Bigwood", "Clark", "Davidson", "Maxmud", "Mccarl", "Mensah", "Mohamed",
          "Moktar", "Ochoa Martinez", "Saw Tamalar", "Tran", "Xiong", "Yusuf" ]

def make_students_csv(count,courses,fname='students.csv'):
    '''
    Create a csv file with "count" students.
    Each student will have a randomly generated name
    and randomly generated rankings for courses.
    The row is last,first,pref A, pref B, ... , pref E
    '''
    import random
    
    f = open(fname,'w')
    # create a list [1 2 3 4 5]
    rankings = [i+1 for i in range(len(courses))]
    for i in range(count):
        student = random.choice(lasts)+','+random.choice(firsts)+','
        # shuffle the rankings (at [0] is rank for A, [1] for B, ...)
        random.shuffle(rankings)
        # make the csv string with all info for student
        student += ','.join([str(r) for r in rankings]) + '\n'
        f.write(student)
    f.close()
    
            
