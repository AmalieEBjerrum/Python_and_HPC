#!/bin/sh
#BSUB -q c02613
#BSUB -J jacobi_cuda_test          
#BSUB -o jacobi_cuda_output.log    
#BSUB -e jacobi_cuda_error.log     
#BSUB -n 4                          
#BSUB -R "span[hosts=1]"            
#BSUB -W 01:00                      
#BSUB -R "rusage[mem=1GB]"
#BSUB -gpu "num=1:mode=shared"




source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

# Run the Python script
python 8_1_test.py 20
