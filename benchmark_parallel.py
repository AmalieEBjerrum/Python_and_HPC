import time
import subprocess
import matplotlib.pyplot as plt

N_BUILDINGS = 100  # You can adjust this
WORKERS_LIST=(1 2 4 8 12 16 24 32) # Try as many as your system allows
SERIAL_CMD = ["python3", "simulate.py", str(N_BUILDINGS)]
PARALLEL_CMD_TEMPLATE = ["python3", "simulate_parallel_static.py", str(N_BUILDINGS)]

def measure_runtime(cmd):
    start = time.perf_counter()
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    end = time.perf_counter()
    return end - start

# Measure serial time
print("Measuring serial runtime...")
serial_time = measure_runtime(SERIAL_CMD)
print(f"Serial time: {serial_time:.2f} seconds")

# Measure parallel times
parallel_times = []
for n in WORKERS_LIST:
    print(f"Measuring parallel runtime with {n} workers...")
    env = {"NUM_WORKERS": str(n)}
    # Use env variable or change simulate_parallel_static.py to accept n_workers as sys.argv[2]
    parallel_time = measure_runtime(PARALLEL_CMD_TEMPLATE + [str(n)])
    parallel_times.append(parallel_time)
    print(f"Parallel time with {n} workers: {parallel_time:.2f} seconds")

# Compute speed-ups
speedups = [serial_time / t for t in parallel_times]

# Plot
plt.figure()
plt.plot(WORKERS, speedups, marker='o')
plt.xlabel("Number of Workers")
plt.ylabel("Speed-up")
plt.title(f"Speed-up vs Workers for N={N_BUILDINGS}")
plt.grid(True)
plt.savefig("speedup_plot.png")
plt.show()
