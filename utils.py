import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def get_input(path):
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