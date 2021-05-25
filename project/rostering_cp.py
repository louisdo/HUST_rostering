import time
import sys 
from ortools.sat.python import cp_model

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

# model
model = cp_model.CpModel()

#variables
x = [[[model.NewIntVar(0, 1, 'x[' + str(person) + '][' + str(day) + '][' + str(shift) + ']') for shift in range(5)] for day in range(D)] for person in range(N)]
y = model.NewIntVar(0, D, 'y')

#constraints
for day in range(D):
    for person in range(N):
        model.Add(sum(x[person][day][shift] for shift in range(5)) == 1)

for day in range(D):
    for shift in range(5):
        model.Add(sum(x[person][day][shift] for person in range(N)) >= alpha)
        model.Add(sum(x[person][day][shift] for person in range(N)) <= beta)

for person in range(N):
    model.Add(sum(x[person][day][3] for day in range(D)) <= y)

for day in range(D - 1):
    for person in range(N):
        b = model.NewBoolVar('b')
        model.Add(x[person][day][3] == 1).OnlyEnforceIf(b)
        model.Add(x[person][day][3] != 1).OnlyEnforceIf(b.Not())
        model.Add(x[person][day + 1][4] == 1).OnlyEnforceIf(b)


for person, list_day_off in enumerate(person_day_off):
    for day_off in list_day_off:
        model.Add(x[person][day_off - 1][4] == 1)

#obj function
model.Minimize(y)

#solver
cp_solver = cp_model.CpSolver()

#solve
start = time.time()
result_status = cp_solver.Solve(model)
end = time.time()
assert result_status == cp_model.OPTIMAL
print('optimal value = ', cp_solver.ObjectiveValue())
print('elapsed time = ', end - start)

'''
#print schedule
for person in range(N):
    for day in range(D):
        for shift in range(5):
            if cp_solver.Value(x[person][day][shift]) == 1:
                print(shift if shift != 4 else '_', end = ' ')
    print()
'''