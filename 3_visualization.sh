#!/bin/bash
#BSUB -J 3_visualization
#BSUB -q hpc
#BSUB -W 0:10
#BSUB -R "rusage[mem=10GB]"
#BSUB -R "select[model==XeonGold6226R]"
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -o 3_visualization.out
#BSUB -e 3_visualization.err


source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613


time python 3_visualization.py 10
