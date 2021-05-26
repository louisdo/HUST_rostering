import math, random, json
import numpy as np
from tqdm import tqdm
from utils import get_input, NumpyEncoder
from argparse import ArgumentParser


def init(params: dict, F):
    data, shift_count = np.zeros((params["N"], params["D"]), dtype = int), np.zeros((params["D"], 5))
    shift_count[:,0] = params["N"]
    return data, shift_count


def encouragement_score(shift_count: np.array, d: int, s: int, params: dict):
    # the higher the encouragement score, the more suitable the assignment
    if s != 0:
        if shift_count[d, s] == params["alpha"]:
            return 1
        elif params["alpha"] < shift_count[d, s] <= params["beta"]: 
            return params["alpha"] - shift_count[d, s]
        elif params["alpha"] > shift_count[d, s]: return params["alpha"] - shift_count[d, s]
        elif params["beta"] < shift_count[d, s]: return params["beta"] - shift_count[d, s]
    elif s == 0:
        min_off = max(0, params["N"] - 4 * params["beta"])
        max_off = params["N"] - 4 * params["alpha"]
        if min_off <= shift_count[d, s] <= max_off: return 0
        elif shift_count[d, s] < min_off: return min_off - shift_count[d, s]
        elif shift_count[d, s] > max_off: return max_off - shift_count[d, s]


def check(data:np.array, shift_count: np.array, params: dict):
    for n in range(params["N"]):
        for d in range(params["D"] - 1):
            if data[n][d] == 4 and data[n][d + 1] != 0: return False

    for d in range(params["D"]):
        for s in range(1, 5):
            if not params["alpha"] <= shift_count[d, s] <= params["beta"]: return False
    return True

def objective(data: np.array):
    night_shift = data == 4
    night_shift = np.sum(night_shift, axis = 1)
    return np.max(night_shift)


def f(data: np.array, shift_count: np.array, n: int, d: int, s: int, params: dict, check: bool):
    night_shifts_score = 0 if not check else objective(data)
        
    en_score = encouragement_score(shift_count, d, s, params)
    #print(night_shifts_score, en_score)
    return en_score - night_shifts_score


leaky_relu = lambda x: np.where(x > 0, x, x * 0.01)

def choose(fs: dict, avail_shifts: list):
    if len(avail_shifts) == 1: return avail_shifts[0]
    probs = np.array([fs[s] for s in avail_shifts])
    probs -= np.min(probs)
    
    #print(probs)
    norm_fact = np.sum(probs)
    if norm_fact == 0: return random.choice(avail_shifts)
    normed_probs = probs / norm_fact
    try:
        return np.random.choice(avail_shifts, 1, p=normed_probs)[0]
    except: print(probs)
    


def optimize(params: dict, F: list, num_reps: int):
    data, shift_count = init(params, F)
    
    iteration = 0
    saved_n = None
    saved_d = None
    BEST = 1e8
    BEST_SCHEDULE = None
    _CHECK = False
    with tqdm(total = num_reps) as pbar:
        while iteration < num_reps:
            if saved_n is not None and saved_d is not None and saved_d < params["D"] - 1:
                n = saved_n
                d = saved_d + 1
            else: 
                n = random.choice(range(params["N"]))
                d = random.choice(range(params["D"]))
            
            if d + 1 in F[n]: 
                saved_n = None
                saved_d = None
                continue
                
            prev_shift = data[n, d]
            if shift_count[d, prev_shift] > 0: shift_count[d, prev_shift] -= 1
                
            avail_shifts = range(0, 5)
            if d - 1 >= 0 and data[n, d - 1] == 4:
                avail_shifts = [0]
                
            fs = {s: 0 for s in avail_shifts}
            for s in avail_shifts:
                data[n, d] = s
                shift_count[d, s] += 1
                fs[s] = f(data, shift_count, n, d, s, params, _CHECK)
                shift_count[d, s] -= 1
            
            
            #if len(avail_shifts) > 1 and all([val < 0 for val in fs.values()]): chosen_shift = 0
            chosen_shift = choose(fs, avail_shifts)
            if chosen_shift == 4:
                saved_n = n
                saved_d = d
            else: 
                saved_n = None
                saved_d = None
                
            data[n, d] = chosen_shift
            shift_count[d, chosen_shift] += 1


            if check(data, shift_count, params):
                _CHECK = True
                score = objective(data)
                if score < BEST: 
                    print("found solution, score of solution:", score)
                    BEST = score
                    BEST_SCHEDULE = data.copy()
                    if BEST == 1: 
                        print("found best possible solution, early stopped")
                        break
            else: _CHECK = False

            iteration += 1
            pbar.update()
            #pbar.set_postfix({"probs": " ".join([str(round(p, 2)) for p in fs.values()])})
        
    return BEST, BEST_SCHEDULE, data, shift_count



if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--input-path", required = True, type = str)
    parser.add_argument("--num-reps", default = 10000, type = int)
    args = parser.parse_args()

    INPUT_PATH = args.input_path
    NUM_REPS = args.num_reps

    N, D, alpha, beta, F = get_input(INPUT_PATH)
    params = {
        "N": N, "D": D, "alpha": alpha, "beta": beta
    }
    print(F)
    print(params)

    best_score, best_schedule, data, shift_count = optimize(params, F, NUM_REPS)
    with open("./output_sa.json", "w") as f:
        json.dump({
            "best_score":best_score,
            "best_schedule": best_schedule,
            "data": data,
            "shift_count": shift_count
        }, f, cls = NumpyEncoder)