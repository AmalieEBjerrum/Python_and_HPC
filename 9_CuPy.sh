#!/bin/sh
#BSUB -q c02613
#BSUB -J 9_CuPy 
#BSUB -n 4 
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=1GB]"
#BSUB -gpu "num=1:mode=exclusive_process" 
#BSUB -W 00:30 
#BSUB -o 9_CuPy.out
#BSUB -e 9_CuPy.err


source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time python 9_CuPy.py 100

