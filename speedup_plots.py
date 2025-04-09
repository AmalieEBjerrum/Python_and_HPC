import matplotlib.pyplot as plt
import pandas as pd

# Read and parse the CSV file
with open("speedup_results.csv", "r") as f:
    lines = f.readlines()

# Extract serial time
serial_time_line = lines[0]
serial_time = float(serial_time_line.split(":")[1].strip())

# Read parallel worker timings
data = [line.strip().split(",") for line in lines[1:]]
workers = [int(w) for w, _ in data]
times = [float(t) for _, t in data]

# Compute speed-ups
speedups = [serial_time / t for t in times]

# Plot
plt.figure(figsize=(8, 5))
plt.plot(workers, speedups, marker="o")
plt.title("Speed-up vs Number of Workers (Static Scheduling)")
plt.xlabel("Number of Workers")
plt.ylabel("Speed-up")
plt.grid(True)
plt.savefig("speedup_plot.png")
plt.show()
