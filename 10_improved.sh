#!/bin/sh
#BSUB -q c02613
#BSUB -J 10_improved
#BSUB -n 4 
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=4GB]"
#BSUB -gpu "num=1:mode=exclusive_process" 
#BSUB -W 00:30 
#BSUB -o 10_improved.out
#BSUB -e 10_improved.err


source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time nsys profile -o 10_improved_2 python 10_improved.py 20

