#!/bin/bash
#BSUB -J initial
#BSUB -q hpc
#BSUB -W 0:30
#BSUB -R "rusage[mem=1GB]"
#BSUB -n 4
#BSUB -R "select[model==XeonGold6226R]"
#BSUB -R "span[hosts=1]"
#BSUB -o initial.out
#BSUB -e initial.err


source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613


time python initial.py 100
