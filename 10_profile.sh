#!/bin/sh
#BSUB -q c02613
#BSUB -J 10_profile
#BSUB -n 4 
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=4GB]"
#BSUB -gpu "num=1:mode=exclusive_process" 
#BSUB -W 00:30 
#BSUB -o 10_profile.out
#BSUB -e 10_profile.err


source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time nsys profile -o 10_profile_forreal python 10_profile.py 100

