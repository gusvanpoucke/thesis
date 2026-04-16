#!/bin/bash
#PBS -N test
#PBS -l walltime=01:00:00
#PBS -l nodes=1:ppn=1

cd $PBS_O_WORKDIR

module load numpy
module load cProfile
module load pstats
module load json
module load time
module load os
module load random
module load re
module load math
module load pathlib

python job.py
