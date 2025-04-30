from os.path import join
import sys
import numpy as np
from multiprocessing.pool import ThreadPool
import multiprocessing
import csv
from multiprocessing import Pool


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

if __name__ == '__main__':
    from time import time
    from multiprocessing import cpu_count

    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    MAX_ITER = 20_000
    ABS_TOL = 1e-4

    # Load building IDs
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    # Read arguments
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    worker_counts = [int(arg) for arg in sys.argv[2:]] if len(sys.argv) > 2 else [1]
    building_ids = building_ids[:N]

    # Open CSV file for writing speed-up results
    with open("speedup_results.csv", "a") as f_csv:
        f_csv.write("workers,time\n")

        for n_proc in worker_counts:
            print(f"\nRunning with {n_proc} workers on {N} buildings...")
            start = time()

            with Pool(n_proc) as pool:
                results = pool.map(process_building, building_ids, chunksize=len(building_ids)//n_proc)

            elapsed = time() - start
            f_csv.write(f"{n_proc},{elapsed:.4f}\n")
            print(f"Time: {elapsed:.2f} seconds")

            # Optional: print stats for first run only
            if n_proc == worker_counts[0]:
                stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
                print('\nbuilding_id, ' + ', '.join(stat_keys))
                for bid, stats in results:
                    print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))
            
            print("Saving speedup_results.csv to:")
