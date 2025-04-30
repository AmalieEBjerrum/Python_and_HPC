import numpy as np
from numba import cuda
from os.path import join
import time
import sys


# CUDA kernel: performs Jacobi update only on interior_mask points
@cuda.jit
def jacobi_kernel_masked(u, u_new, mask_i, mask_j, mask_len):
    idx = cuda.grid(1)
    if idx < mask_len:
        i = mask_i[idx] + 1
        j = mask_j[idx] + 1
        u_new[i, j] = 0.25 * (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1])

def jacobi_cuda(u, interior_mask, max_iter):
    u = np.array(u, dtype=np.float32)
    n, m = u.shape

    # Transfer arrays to device
    d_u = cuda.to_device(u.copy())
    d_u_new = cuda.to_device(u.copy())

    mask_i, mask_j = np.where(interior_mask)
    mask_i = np.ascontiguousarray(mask_i, dtype=np.int32)
    mask_j = np.ascontiguousarray(mask_j, dtype=np.int32)
    d_mask_i = cuda.to_device(mask_i)
    d_mask_j = cuda.to_device(mask_j)
    mask_len = len(mask_i)

    # Thread config for 1D kernel
    threads_per_block = 128
    blocks_per_grid = (mask_len + threads_per_block - 1) // threads_per_block

    for _ in range(max_iter):
        jacobi_kernel_masked[blocks_per_grid, threads_per_block](d_u, d_u_new, d_mask_i, d_mask_j, mask_len)
        d_u, d_u_new = d_u_new, d_u  # Swap pointers

    return d_u.copy_to_host()


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
    import numpy as np
# Directory and parameters
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    MAX_ITER = 20_000

        # Load a subset of building IDs
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    # Get the number of buildings as input
    if len(sys.argv) < 2:
        N = 1
    else:
        N = int(sys.argv[1])
    building_ids = building_ids[:N]



    # Load floor plans
    all_u0 = np.empty((N, 514, 514))
    all_interior_mask = np.empty((N, 512, 512), dtype='bool')
    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask

    # Run CUDA Jacobi iterations for each floor plan
    all_u = np.empty_like(all_u0)
    cuda_times = []
    for i, (u0, interior_mask) in enumerate(zip(all_u0, all_interior_mask)):
        start = time.time()
        u = jacobi_cuda(u0, interior_mask, MAX_ITER)  # Use CUDA kernel
        elapsed = time.time() - start
        cuda_times.append(elapsed)
        all_u[i] = u
        print(f"CUDA Jacobi for {building_ids[i]}: {elapsed:.4f} seconds")

    # Compute and print summary statistics in CSV format
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('\nbuilding_id, ' + ', '.join(stat_keys))  # CSV header
    for bid, u, interior_mask in zip(building_ids, all_u, all_interior_mask):
        stats = summary_stats(u, interior_mask)
        print(f"{bid},", ", ".join(f"{stats[k]:.4f}" for k in stat_keys))

    # Compute and print the average CUDA time
    avg_cuda_time = sum(cuda_times) / len(cuda_times)
    print(f"Total CUDA Time: {sum(cuda_times):.4f} seconds")
    print(f"\nAverage CUDA Time: {avg_cuda_time:.4f} seconds")
