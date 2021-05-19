import numpy as np
import sys
np.random.seed(20)
N = int(sys.argv[1])
D = int(sys.argv[2])
def generate(N, D):
    lam = int(N / 5)
    tmp = 1 + np.random.poisson(lam, 2)

    alpha = tmp.min()
    beta = tmp.max()

    if alpha > lam and beta > lam:
        alpha = lam * 2 - alpha

    elif alpha < lam and beta < lam:
        beta = lam * 2 - beta

    person_day_off = [[] for _ in range(N)]

    for person in range(N):
        for day in range(D):
            prob = np.random.binomial(1, 0.05)
            if prob == 1:
                person_day_off[person].append(day + 1)
            else:
                continue
    
    return alpha, beta, person_day_off

def write(path):
    with open(path + 'data_' + str(N) + '_' + str(D) + '.txt', 'w') as f:
        f.write(str(N) + ' ')
        f.write(str(D) + ' ')
        f.write(str(alpha) + ' ')
        f.write(str(beta) + '\n')
        for list_day_off in person_day_off:
            for day_off in list_day_off:
                f.write(str(day_off) + ' ')
            f.write('-1\n')

alpha, beta, person_day_off = generate(N, D)
write(path = 'dataset\\')