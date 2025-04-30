# Wall Heating Simulation Project
**02613 Python and High Performance Computing - Mini-Project**

Project by:
s204297 - Lotte Alstrup
s194693 - Rikke Alstrup
s243654 - Amalie Bjerrum

## Repository Structure

| File | Description |
|------|-------------|
| `3_visualization.py` | Generates `.npy` files of initial grids, interior masks, and simulation results for visualization and debugging. |
| `3_visualization.sh` | Batch script for generating visual data using `3_visualization.py`. |
| `4_profile.py` | Profiles the Jacobi solver using `@profile` decorator for performance diagnostics. |
| `4_profile.sh` | Submits `4_profile.py` to the HPC queue and uses `kernprof` to generate detailed timing info. |
| `5_para.py` | Static multiprocessing (CPU) implementation of the Jacobi solver over floorplans. |
| `5_para.sh` | Batch job script to run `5_para.py` with multiple worker counts. |
| `6_dynamic.py` | Parallel solution using dynamic scheduling (worker pulls next available task when free). |
| `6_dynamic.sh` | Batch script to launch `6_dynamic.py` on the cluster. |
| `7_NumbaJIT.py` | CPU-accelerated Jacobi implementation using `@jit` from Numba. |
| `7_NumbaJIT.sh` | Batch job script to execute the Numba-accelerated solution. |
| `8_Cudakernel.py` | CUDA kernel version using Numba to offload each Jacobi iteration to GPU threads. |
| `8_Cudakernel.sh` | GPU batch script for running the custom CUDA kernel solution. |
| `9_CuPy.py` | GPU solution using CuPy, leveraging NumPy-like syntax for device arrays. |
| `9_CuPy.sh` | Job script to run the CuPy implementation on GPU hardware. |
| `10_improved.py` | Optimized vectorized batched Jacobi GPU implementation using CuPy for max throughput. |
| `10_improved.sh` | GPU profiling job using `nsys` for `10_improved.py`. |
| `10_profile.py` | Identical to `9_CuPy.py` but intended for GPU profiling (e.g., `nsys`). |
| `10_profile.sh` | Job script to profile `10_profile.py` using `nsys`. |
| `12_run_all.py` | Executes batched Jacobi on all 4571 buildings and prints all results in CSV format. |
| `12_run_all.sh` | Long runtime batch job to run full dataset processing on GPU. |

---
## Running the Code

### Example: Static Parallel CPU (5_para.py) number of buildings and then number of workers
```bash
python 5_para.py 100 1 2 4 8 16 32

### Example: The rest of the scripts just give number of buildings you wanna run
python 7_NumbaJIT.py 10

# Make sure to initilize the environment before sending the batch jobs:
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613