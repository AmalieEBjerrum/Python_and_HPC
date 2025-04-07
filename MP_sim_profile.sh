#!/bin/bash
#BSUB -J MP_Sim_profile
#BSUB -q hpc
#BSUB -W 0:10
#BSUB -R "rusage[mem=10GB]"
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -o MP_sim_profile.out
#BSUB -e MP_sim_profile.err


source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613


kernprof -l simulate_profile.py 20
