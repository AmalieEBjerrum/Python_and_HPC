from os.path import join
import sys
import numpy as np
from multiprocessing.pool import ThreadPool
import multiprocessing 
import time
import matplotlib.pyplot as plt

def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


def jacobi(u, interior_mask, max_iter, atol=1e-6):
    u = np.copy(u)

    for i in range(max_iter):
        # Compute average of left, right, up and down neighbors, see eq. (1)
        u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] + u[:-2, 1:-1] + u[2:, 1:-1])
        u_new_interior = u_new[interior_mask]
        delta = np.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()
        u[1:-1, 1:-1][interior_mask] = u_new_interior

        if delta < atol:
            break
    return u


def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    mean_temp = u_interior.mean()
    std_temp = u_interior.std()
    pct_above_18 = np.sum(u_interior > 18) / u_interior.size * 100
    pct_below_15 = np.sum(u_interior < 15) / u_interior.size * 100
    return {
        'mean_temp': mean_temp,
        'std_temp': std_temp,
        'pct_above_18': pct_above_18,
        'pct_below_15': pct_below_15,
    }



def process_building(bid):
    # Load floor plan data for the building
    u0, interior_mask = load_data(LOAD_DIR, bid)
    
    # Run the Jacobi iterations for the given floor plan
    u = jacobi(u0, interior_mask, MAX_ITER, ABS_TOL)

    # Compute summary statistics
    stats = summary_stats(u, interior_mask)
    return bid, stats

def speedup(n_proc_vector, building_ids):
    speed_ups = []
    times = []
    baseline_time = None
    results = None
    all_results = []

    for n_proc in n_proc_vector:
        start = time.time()

        pool = multiprocessing.Pool(n_proc)
        results = pool.map(process_building, building_ids, chunksize= n_proc)
        all_results.append(results)
        pool.close()
        pool.join()

        elapsed = time.time() - start
        times.append(elapsed)
        if baseline_time is None:  # first run is our baseline (usually n_proc = 1)
            baseline_time = elapsed
            speed_ups.append(1)
        else:
            speed_ups.append(baseline_time / elapsed)
        print(f"Workers: {n_proc}, Time: {elapsed:.2f} seconds, Speed-up: {speed_ups[-1]:.2f}")

    return speed_ups, all_results

if __name__ == '__main__':
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    MAX_ITER = 20_000
    ABS_TOL = 1e-4
    
    # Load building IDs
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    if len(sys.argv) < 2:
        N = 1
    else:
        N = int(sys.argv[1])
    building_ids = building_ids[:N]

    if len(sys.argv) > 2:
        n_proc_vector = [int(arg) for arg in sys.argv[2:]]
    else:
        n_proc_vector = [1]
    
    speed_ups, results = speedup(n_proc_vector, building_ids)

    # Save the speed-ups plot
    plt.figure()
    plt.plot(n_proc_vector, speed_ups, marker='o')
    plt.xlabel("Number of Workers")
    plt.ylabel("Speed-up")
    plt.title("Speed-up vs. Number of Workers")
    plt.grid(True)
    plt.savefig("/zhome/4d/5/147570/speedup_plot.png")
    plt.close()

    # Print CSV header
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))

    # Iterate through results and print summary statistics
    for bid, stats in results:
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))
