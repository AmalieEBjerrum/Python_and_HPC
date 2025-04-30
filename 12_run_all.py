from os.path import join
import sys

import numpy as np
import cupy as cp

def load_data(load_dir, bid):
    SIZE = 512
    domain_np = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask_np = np.load(join(load_dir, f"{bid}_interior.npy"))

    # Transfer to GPU
    u = cp.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = cp.asarray(domain_np)
    interior_mask = cp.asarray(interior_mask_np)

    return u, interior_mask

def jacobi_batch(u_batch, interior_mask_batch, max_iter, atol=1e-6):
    """
    u_batch: (N, 514, 514)
    interior_mask_batch: (N, 512, 512)
    """
    u = cp.copy(u_batch)

    for i in range(max_iter):
        # Compute u_new: average of neighbors, vectorized over batch
        u_new = 0.25 * (
            u[:, 1:-1, :-2] + u[:, 1:-1, 2:] +
            u[:, :-2, 1:-1] + u[:, 2:, 1:-1]
        )

        # Only update interior points
        u_center = u[:, 1:-1, 1:-1]
        delta = cp.abs(u_center - u_new)

        max_delta = cp.max(delta * interior_mask_batch)

        # Update only interior points
        u_center[interior_mask_batch] = u_new[interior_mask_batch]

        if max_delta < atol:
            break

    return u

def summary_stats_batch(u_batch, mask_batch):
    N = u_batch.shape[0]
    results = []

    for i in range(N):
        u_interior = u_batch[i, 1:-1, 1:-1][mask_batch[i]]
        stats = cp.asarray([
            u_interior.mean(),
            u_interior.std(),
            cp.sum(u_interior > 18) / u_interior.size * 100,
            cp.sum(u_interior < 15) / u_interior.size * 100
        ])
        results.append(stats)

    results = cp.stack(results).get()
    return results

if __name__ == '__main__':
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'

    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    if len(sys.argv) < 2:
        N = 1
    else:
        N = int(sys.argv[1])
    building_ids = building_ids[:N]

    # Load floor plans
    all_u0 = cp.empty((N, 514, 514))
    all_interior_mask = cp.empty((N, 512, 512), dtype=cp.bool_)
    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask

    # Run vectorized Jacobi
    MAX_ITER = 20_000
    ABS_TOL = 1e-4

    all_u = jacobi_batch(all_u0, all_interior_mask, MAX_ITER, ABS_TOL)

    # Compute stats all at once
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    all_stats = summary_stats_batch(all_u, all_interior_mask)

    # Print CSV
    print('building_id, ' + ', '.join(stat_keys))
    for bid, stats in zip(building_ids, all_stats):
        print(f"{bid},", ", ".join(str(x) for x in stats))
