#!/bin/bash
#BSUB -J MP_Sim
#BSUB -q hpc
#BSUB -W 0:30
#BSUB -R "rusage[mem=10GB]"
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -o MP_sim.out
#BSUB -e MP_sim.err


source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613


time python simulate.py 50
