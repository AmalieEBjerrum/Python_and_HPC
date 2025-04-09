#!/bin/bash
#BSUB -J 5a_para
#BSUB -q hpc
#BSUB -W 0:30
#BSUB -R "rusage[mem=10GB]"
#BSUB -n 64
#BSUB -R "span[hosts=1]"
#BSUB -o 5a_para.out
#BSUB -e 5a_para.err

# Load conda environment
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

# Change to your working directory
cd /zhome/64/7/156562

# Run the script with various worker counts
time python 5_para.py 100 1 2 4 8 16 32 64
