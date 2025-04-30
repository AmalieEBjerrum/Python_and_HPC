#!/bin/sh
#BSUB -J 8_Cudakernel
#BSUB -q gpua100
#BSUB -W 0:30
#BSUB -R "rusage[mem=1GB]"
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -o 8_Cudakernel.out
#BSUB -e 8_Cudakernel.err
#BSUB -gpu "num=1:mode=shared"




source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

# Run the Python script
time python 8_Cudakernel.py 100
