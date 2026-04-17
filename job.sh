#!/bin/bash
#PBS -N parallel_test
#PBS -l walltime=01:00:00
#PBS -l nodes=1:ppn=21

cd $PBS_O_WORKDIR

module load Python/3.11.3-GCCcore-12.3.0
module load SciPy-bundle/2023.07-gfbf-2023a

python job.py
