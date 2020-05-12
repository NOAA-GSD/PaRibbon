########################################################################
# Name  : Bmata                                                        #
# Desc  : B-Matrix Analysis program main driver                        #
# Author: L. Stringer                                                  #
#         D. Rosenberg                                                 #
# Date:   April 2020                                                   #
########################################################################
import os, sys
import numpy as np
from   mpi4py import MPI
from   netCDF4 import Dataset
import time
import btools

# Get world size and rank:
comm     = MPI.COMM_WORLD
mpiTasks = MPI.COMM_WORLD.Get_size()
mpiRank  = MPI.COMM_WORLD.Get_rank()
name     = MPI.Get_processor_name()

print("main: tasks=",mpiTasks, " rank=", mpiRank,"machine name=",name)
sys.stdout.flush()

#
# Get the local data.
#
(N,nens,gdims) = btools.BTools.getSlabData("Tmerged10.nc", "T", 0, mpiTasks, mpiRank, 2, 1)
if mpiRank == 0:
  print (mpiRank, ": main: constructing BTools, nens   =",nens)
  print (mpiRank, ": main: constructing BTools, gdims  =",gdims)
  print (mpiRank, ": main: constructing BTools, N.shape=",N.shape)
  sys.stdout.flush()

#
# Instantiate the BTools class before building B:
#
prdebug = False
BTools = btools.BTools(comm, MPI.FLOAT, nens, gdims, prdebug)

threshold  = 0.8
N = np.asarray(N, order='C')
x=N.flatten()

# Here's where the work is done!
t0 = time.time()
lcount,B,I,J = BTools.buildB(x, threshold) 
t1 = time.time()
 
# Write out the results.
sprefix = "Bmatrix"
BTools.writeResults(B, I, J, sprefix, mpiRank)
 
comm.barrier()
gcount = comm.allreduce(lcount, op=MPI.SUM) # global number of entries

ldt = t1 - t0;
gdt = comm.allreduce(ldt, op=MPI.MAX) # global number of entries

comm.barrier()
if mpiRank == 0:
  print(mpiRank, ": main: max number entries  : ", (np.prod(gdims))**2)
  print(mpiRank, ": main: number entries found: ", gcount)
  print(mpiRank, ": main: data written to file: ", sprefix)
  print(mpiRank, ": main: execution time      : ", gdt)
