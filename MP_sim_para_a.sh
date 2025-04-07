#!/bin/bash
#BSUB -J MP_Sim_Para_a
#BSUB -q hpc
#BSUB -W 0:30
#BSUB -R "rusage[mem=10GB]"
#BSUB -n 8
#BSUB -R "span[hosts=1]"
#BSUB -o MP_sim_para_a.out
#BSUB -e MP_sim_para_a.err


source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613


time python sim_para.py 10 1 2 4 6
