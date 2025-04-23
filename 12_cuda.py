import numpy as np
from numba import cuda
from os.path import join
import time
import csv


# CUDA kernel: performs a single Jacobi iteration
@cuda.jit
def jacobi_kernel(u, u_new, n, m):
    i, j = cuda.grid(2)

    # Work only on interior points (not the boundary)
    if 1 <= i < n - 1 and 1 <= j < m - 1:
        u_new[i, j] = 0.25 * (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1])

def jacobi_cuda(u, interior_mask, max_iter):
    u = np.array(u, dtype=np.float32)
    n, m = u.shape

    # Transfer arrays to device
    d_u = cuda.to_device(u)
    d_u_new = cuda.device_array_like(d_u)

    # Thread block and grid dimensions
    threads_per_block = (16, 16)
    blocks_per_grid_x = (n + threads_per_block[0] - 1) // threads_per_block[0]
    blocks_per_grid_y = (m + threads_per_block[1] - 1) // threads_per_block[1]
    blocks_per_grid = (blocks_per_grid_x, blocks_per_grid_y)

    # Transfer the mask once!
    mask_i, mask_j = np.where(interior_mask)
    d_mask_i = cuda.to_device(np.ascontiguousarray(mask_i))
    d_mask_j = cuda.to_device(np.ascontiguousarray(mask_j))

    for _ in range(max_iter):
        jacobi_kernel[blocks_per_grid, threads_per_block](d_u, d_u_new, n, m)

        apply_mask_update[blocks_per_grid, threads_per_block](d_u, d_u_new, d_mask_i, d_mask_j, len(mask_i))

        # Swap the grids
        d_u, d_u_new = d_u_new, d_u

    return d_u.copy_to_host()


# CUDA kernel for masked updates
@cuda.jit
def apply_mask_update(u, u_new, mask_i, mask_j, mask_len):
    idx = cuda.grid(1)
    if idx < mask_len:
        i = mask_i[idx]
        j = mask_j[idx]
        u[i, j] = u_new[i, j]

# Load data function
def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask

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


if __name__ == '__main__':
    import time
    from os.path import join
    import sys

    # Directory and parameters
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    MAX_ITER = 20_000

    # Get the number of buildings as input
    if len(sys.argv) != 2:
        print("Usage: python 8_1.py <number_of_buildings>")
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

        

    cuda_times = []
    results = []

    for bid in building_ids:
        u, interior_mask = load_data(LOAD_DIR, bid)
        start = time.time()
        u_final = jacobi_cuda(u, interior_mask, MAX_ITER)
        elapsed = time.time() - start
        cuda_times.append(elapsed)

        stats = summary_stats(u_final, interior_mask)
        stats.update({
            'building_id': bid,
            'time_seconds': elapsed
        })
        results.append(stats)

        print(f"{bid}: {stats['mean_temp']:.2f}°C, std={stats['std_temp']:.2f}, "
              f">18°C: {stats['pct_above_18']:.1f}%, <15°C: {stats['pct_below_15']:.1f}%, "
              f"time={elapsed:.2f}s")


# Define the CSV field order
    fieldnames = ['building_id', 'mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15', 'time_seconds']

    # Save to CSV
    with open("building_temperature_stats.csv", "w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nAverage CUDA Time: {sum(cuda_times) / len(cuda_times):.4f} seconds")
    print(f"Total CUDA Time: {sum(cuda_times):.4f} seconds")
    print(f"Stats saved to 'building_temperature_stats.csv'")