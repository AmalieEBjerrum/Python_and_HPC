#!/bin/bash
#BSUB -J 1_5_a
#BSUB -q hpc
#BSUB -W 0:30
#BSUB -R "rusage[mem=10GB]"
#BSUB -n 32
#BSUB -R "span[hosts=1]"
#BSUB -o 1_5_a.out
#BSUB -e 1_5_a.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

module load python3/3.10.12

# Number of buildings to simulate
N=100
# Test this range of worker counts
WORKERS_LIST=(1 2 4 8 12 16 24 32)

# Output file
OUTFILE=speedup_results.csv

# Header for CSV
echo "workers,time" > $OUTFILE

# Measure serial baseline
echo "Running serial version..."
SERIAL_TIME=$(python3 -c "import time, subprocess; s=time.time(); subprocess.run(['python3', 'simulate.py', str($N)], stdout=subprocess.DEVNULL); print(time.time() - s)")
echo "Serial time: $SERIAL_TIME"

# Measure parallel versions
for W in "${WORKERS_LIST[@]}"
do
    echo "Running with $W workers..."
    TIME=$(python3 -c "import time, subprocess; s=time.time(); subprocess.run(['python3', 'simulate_parallel_static.py', str($N), str($W)], stdout=subprocess.DEVNULL); print(time.time() - s)")
    echo "$W,$TIME" >> $OUTFILE
done

# Save serial time at the end
echo "Serial,$SERIAL_TIME" >> $OUTFILE
