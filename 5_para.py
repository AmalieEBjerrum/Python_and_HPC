from os.path import join
import sys
import numpy as np
import multiprocessing
import time

def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask

def jacobi(u, interior_mask, max_iter, atol=1e-6):
    u = np.copy(u)
    for i in range(max_iter):
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
    u0, interior_mask = load_data(LOAD_DIR, bid)
    u = jacobi(u0, interior_mask, MAX_ITER, ABS_TOL)
    stats = summary_stats(u, interior_mask)
    return bid, stats

def speedup(n_proc_vector, building_ids):
    speed_ups = []
    times = []
    baseline_time = None
    all_results = []

    for n_proc in n_proc_vector:
        start = time.time()
        with multiprocessing.Pool(n_proc) as pool:
            results = pool.map(process_building, building_ids, chunksize=len(building_ids) // n_proc or 1)
        all_results.append(results)
        elapsed = time.time() - start
        times.append(elapsed)
        if baseline_time is None:
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

    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    N = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    worker_counts = [int(arg) for arg in sys.argv[2:]] if len(sys.argv) > 2 else [1]
    building_ids = building_ids[:N]

    # Run Jacobi in parallel and gather results
    speed_ups, all_results = speedup(worker_counts, building_ids)

    # Print summary statistics for first run
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))
    for bid, stats in all_results[0]:
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))
