#!/bin/bash
#BSUB -J jacobi_numba_test          # Job name
#BSUB -o jacobi_output.log          # Output log file
#BSUB -e jacobi_error.log           # Error log file
#BSUB -n 4                          # Number of cores (tasks)
#BSUB -R "span[hosts=1]"            # Ensure all cores are on the same host
#BSUB -W 01:00                      # Time limit (hh:mm)
#BSUB -M 4000                       # Memory per core in MB
#BSUB -R "rusage[mem=10GB]"
#BSUB -W 0:30 

set -x

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

# Run the Python script
python 7_1.py 20
