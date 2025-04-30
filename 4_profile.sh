#!/bin/bash
#BSUB -J 4_profile
#BSUB -q hpc
#BSUB -W 1:30
#BSUB -R "rusage[mem=10GB]"
#BSUB -R "select[model==XeonGold6226R]"
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -o 4_profile.out
#BSUB -e 4_profile.err


source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613


kernprof -l 4_profile.py 100
