from numba import cuda
from os.path import join
import time

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
    # Load data
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

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

    # Run jacobi iterations for each floor plan
    MAX_ITER = 20_000
    ABS_TOL = 1e-4

    all_u = np.empty_like(all_u0)
    for i, (u0, interior_mask) in enumerate(zip(all_u0, all_interior_mask)):
        u = jacobi(u0, interior_mask, MAX_ITER, ABS_TOL)
        all_u[i] = u

    # Print summary statistics in CSV format
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))  # CSV header
    for bid, u, interior_mask in zip(building_ids, all_u, all_interior_mask):
        stats = summary_stats(u, interior_mask)
        print(f"{bid},", ", ".join(str(stats[k]) for k in stat_keys))