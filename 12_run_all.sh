#!/bin/sh
#BSUB -q gpua100
#BSUB -J 12_run_all
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=4GB]"
#BSUB -gpu "num=1:mode=shared"
#BSUB -W 03:00 
#BSUB -o 12_run_all.out
#BSUB -e 12_run_all.err



source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

# Run the Python script
python 12_run_all.py all
