#!/bin/sh
#BSUB -q c02613
#BSUB -J 7_NumbaJIT
#BSUB -n 4 
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=4GB]"
#BSUB -gpu "num=1:mode=exclusive_process" 
#BSUB -W 00:30 
#BSUB -o 7_NumbaJIT.out
#BSUB -e 7_NumbaJIT.err


set -x

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

# Run the Python script
time python 7_NumbaJIT.py 100
