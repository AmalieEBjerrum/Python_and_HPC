#!/bin/sh
#BSUB -q c02613
#BSUB -J 12_jacobi        
#BSUB -o 12_jacobi_output.log    
#BSUB -e 12_jacobi_error.log     
#BSUB -n 4                          
#BSUB -R "span[hosts=1]"            
#BSUB -W 01:00                      
#BSUB -R "rusage[mem=3GB]"
#BSUB -gpu "num=1:mode=shared"




source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

# Run the Python script
python 12_cuda.py 200
