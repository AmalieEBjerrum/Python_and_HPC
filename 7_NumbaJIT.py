from os.path import join
import numpy as np
import time
from numba import jit

# Original Jacobi function
def jacobi_original(u, interior_mask, max_iter, atol=1e-6):
    u = np.copy(u)

    for i in range(max_iter):
        u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] + u[:-2, 1:-1] + u[2:, 1:-1])
        u_new_interior = u_new[interior_mask]
        delta = np.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()
        u[1:-1, 1:-1][interior_mask] = u_new_interior

        if delta < atol:
            break
    return u

@jit(nopython=True)
def jacobi_numba(u, interior_mask, max_iter, atol=1e-6):
    u = u.copy()
    n, m = u.shape
    u_new = np.empty((n - 2, m - 2), dtype=u.dtype)

    mask_i, mask_j = np.where(interior_mask)

    for _ in range(max_iter):
        # Compute new values for the interior
        for i in range(1, n - 1):
            for j in range(1, m - 1):
                u_new[i - 1, j - 1] = 0.25 * (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1])

        # Apply mask and compute max delta
        delta = 0.0
        for idx in range(len(mask_i)):
            i, j = mask_i[idx], mask_j[idx]
            new_val = u_new[i - 1, j - 1]
            diff = abs(u[i, j] - new_val)
            if diff > delta:
                delta = diff
            u[i, j] = new_val

        if delta < atol:
            break

    return u

# Load data function
def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask

if __name__ == '__main__':
    import sys
    from os.path import join

    # Directory and parameters
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    MAX_ITER = 20_000
    ABS_TOL = 1e-4

    # Get the number of buildings as input
    if len(sys.argv) != 2:
        print("Usage: python 7_1.py <number_of_buildings>")
        sys.exit(1)

    try:
        num_buildings = int(sys.argv[1])
    except ValueError:
        print("Error: <number_of_buildings> must be an integer.")
        sys.exit(1)

    # Load a subset of building IDs
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()
    building_ids = building_ids[:num_buildings]  # Use the specified number of floorplans

    # Time the original Jacobi function
    original_times = []
    for bid in building_ids:
        u, interior_mask = load_data(LOAD_DIR, bid)
        start = time.time()
        jacobi_original(u, interior_mask, MAX_ITER, ABS_TOL)
        elapsed = time.time() - start
        original_times.append(elapsed)
        print(f"Original Jacobi for {bid}: {elapsed:.4f} seconds")

    # Time the Numba-optimized Jacobi function
    numba_times = []
    for bid in building_ids:
        u, interior_mask = load_data(LOAD_DIR, bid)
        start = time.time()
        jacobi_numba(u, interior_mask, MAX_ITER, ABS_TOL)
        elapsed = time.time() - start
        numba_times.append(elapsed)
        print(f"Numba Jacobi for {bid}: {elapsed:.4f} seconds")

    # Compare performance
    print("\nPerformance Comparison:")
    for i, bid in enumerate(building_ids):
        print(f"Building {bid}:")
        print(f"  Original Time: {original_times[i]:.4f} seconds")
        print(f"  Numba Time: {numba_times[i]:.4f} seconds")
        print(f"  Speed-up: {original_times[i] / numba_times[i]:.2f}x")