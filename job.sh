#!/bin/bash
#PBS -N full_max_wait
#PBS -l walltime=32:00:00
#PBS -l nodes=1:ppn=1
#PBS -t 0-20
#PBS -o logs/output_${PBS_ARRAYID}.out
#PBS -e logs/error_${PBS_ARRAYID}.err

cd $PBS_O_WORKDIR

mkdir -p logs

module load Python/3.11.3-GCCcore-12.3.0
module load SciPy-bundle/2023.07-gfbf-2023a

python job_fullness_max_wait.py ${PBS_ARRAYID}
