#!/bin/bash
#BSUB -J 1_5_a
#BSUB -q hpc
#BSUB -W 0:30
#BSUB -R "rusage[mem=10GB]"
#BSUB -n 8
#BSUB -R "span[hosts=1]"
#BSUB -o logs/1_5_a.out
#BSUB -e logs/1_5_a.err

module load python3/3.10.12

# Adjust number of buildings and worker counts as needed
N=50
WORKERS_LIST=(1 2 4 8)

echo "Starting static parallel speedup benchmark..."
SERIAL_TIME=$(python3 -c "import time, subprocess; s=time.time(); subprocess.run(['python3', 'simulate.py', str($N)], stdout=subprocess.DEVNULL); print(time.time() - s)")
echo "Serial time: $SERIAL_TIME" > speedup_results.csv

for W in "${WORKERS_LIST[@]}"
do
    echo "Running with $W workers..."
    TIME=$(python3 -c "import time, subprocess; s=time.time(); subprocess.run(['python3', 'simulate_parallel_static.py', str($N), str($W)], stdout=subprocess.DEVNULL); print(time.time() - s)")
    echo "$W,$TIME" >> speedup_results.csv
done
