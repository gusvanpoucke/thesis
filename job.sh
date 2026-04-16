#!/bin/bash
#PBS -N test
#PBS -l walltime=01:00:00
#PBS -l nodes=1:ppn=1

cd $PBS_O_WORKDIR

module load Python/3.11.5-GCCcore-13.3.0
module load numpy

python job.py
