#!/bin/bash
#BSUB -J MP_Sim_results
#BSUB -q hpc
#BSUB -W 0:10
#BSUB -R "rusage[mem=10GB]"
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -o MP_sim_results.out
#BSUB -e MP_sim_results.err


source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613


time python simulate_results.py 10
