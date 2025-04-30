#!/bin/bash
#BSUB -J 6_dynamic
#BSUB -q hpc
#BSUB -W 0:30
#BSUB -R "rusage[mem=3GB]"
#BSUB -n 32
#BSUB -R "select[model==XeonGold6226R]"
#BSUB -R "span[hosts=1]"
#BSUB -o 6_dynamic.out
#BSUB -e 6_dynamic.err

# Load conda environment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

# Change to your working directory
cd /zhome/64/7/156562

# Run the script with various worker counts
time python 6_dynamic.py 100 1 2 4 8 16 32
