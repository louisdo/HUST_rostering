import time
import sys
from ortools.linear_solver import pywraplp

def input(path):
    with open(path) as f:
        firstline = f.readline().split()
        N = int(firstline[0])
        D = int(firstline[1])
        alpha = int(firstline[2])
        beta = int(firstline[3])

        person_day_off = []
        for i in range(N):
            line = f.readline()
            person_day_off.append([int(day_off) for day_off in line.split()[:-1]])

        return N, D, alpha, beta, person_day_off

path = 'dataset\\' + sys.argv[1]
N, D, alpha, beta, person_day_off = input(path)

print('N = ', N)
print('D = ', D)
print('alpha = ', alpha)
print('beta = ', beta)

# solver
solver = pywraplp.Solver.CreateSolver('CBC')
INF = solver.infinity()
big_num = 1e6

# variables
x = [[[solver.IntVar(0, 1, 'x[' + str(person) + '][' + str(day) + '][' + str(shift) + ']') for shift in range(5)] for day in range(D)] for person in range(N)]
y = solver.IntVar(0, D, 'y')

#constraints
for day in range(D):
    for person in range(N):
        c = solver.Constraint(1, 1)
        for shift in range(5):
            c.SetCoefficient(x[person][day][shift], 1)

for day in range(D):
    for shift in range(4):
        c = solver.Constraint(alpha, beta)
        for person in range(N):
            c.SetCoefficient(x[person][day][shift], 1)

for person in range(N):
        c = solver.Constraint(-INF, 0)
        for day in range(D):
            c.SetCoefficient(x[person][day][3], 1)
            c.SetCoefficient(y, -1)

for day in range(D - 1):
    for person in range(N):
            c1 = solver.Constraint(-INF, big_num - 1)
            c2 = solver.Constraint(-INF, big_num + 1)
            c1.SetCoefficient(x[person][day][3], big_num)
            c1.SetCoefficient(x[person][day + 1][4], -1)
            c2.SetCoefficient(x[person][day][3], big_num)
            c2.SetCoefficient(x[person][day + 1][4], 1)

for person, list_day_off in enumerate(person_day_off):
    for day_off in list_day_off:
        solver.Add(x[person][day_off - 1][4] == 1)

#obj function
obj = solver.Objective()
obj.SetCoefficient(y, -1)
obj.SetMaximization()

#solve
start = time.time()
result_status = solver.Solve()
end = time.time()
assert result_status == pywraplp.Solver.OPTIMAL
print('optimal value = ', - solver.Objective().Value())
print('elapsed time = ', end - start)

'''
#print schedule
for person in range(N):
    for day in range(D):
        for shift in range(5):
            if x[person][day][shift].solution_value() == 1:
                print(shift if shift != 4 else '_', end = ' ')
    print()
'''