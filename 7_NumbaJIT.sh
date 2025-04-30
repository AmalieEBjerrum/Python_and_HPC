#!/bin/bash
#BSUB -J 7_NumbaJIT
#BSUB -q hpc
#BSUB -W 1:30
#BSUB -R "rusage[mem=1GB]"
#BSUB -R "select[model==XeonGold6226R]"
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -o 7_NumbaJIT.out
#BSUB -e 7_NumbaJIT.err


set -x

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

# Run the Python script
time python 7_NumbaJIT.py 100
