#!/bin/bash
#PBS -N test
#PBS -l walltime=01:00:00
#PBS -l nodes=1:ppn=1

cd $PBS_O_WORKDIR

module load python/3.12
module load numpy

python job.py
