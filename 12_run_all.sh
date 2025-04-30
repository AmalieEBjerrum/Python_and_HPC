#!/bin/sh
#BSUB -q c02613
#BSUB -J 12_run_all
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=2GB]"
#BSUB -gpu "num=1:mode=exclusive_process" 
#BSUB -W 04:00 
#BSUB -o 12_run_all.out
#BSUB -e 12_run_all.err



source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

# Run the Python script
python 12_run_all.py 4571
