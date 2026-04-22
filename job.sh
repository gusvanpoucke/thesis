#!/bin/bash
#PBS -N split_wait
#PBS -l walltime=02:00:00
#PBS -l nodes=1:ppn=1
#PBS -t 0-20
#PBS -o logs/output_${PBS_ARRAYID}.out
#PBS -e logs/error_${PBS_ARRAYID}.err

cd $PBS_O_WORKDIR

mkdir -p logs

module load Python/3.11.3-GCCcore-12.3.0
module load SciPy-bundle/2023.07-gfbf-2023a

python job_split_routes_wait.py ${PBS_ARRAYID}
