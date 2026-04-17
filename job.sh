#!/bin/bash
#PBS -N wait_first_vns
#PBS -l walltime=30:00:00
#PBS -l nodes=1:ppn=1

cd $PBS_O_WORKDIR

module load Python/3.11.3-GCCcore-12.3.0
module load SciPy-bundle/2023.07-gfbf-2023a

python job.py
