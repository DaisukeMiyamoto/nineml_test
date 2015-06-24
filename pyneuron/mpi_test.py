from mpi4py import MPI
from neuron import h

pc = h.ParallelContext()

s = "mpi4py %d/%d, ParallelContext %d/%d\n"

cw = MPI.COMM_WORLD

print s % (cw.rank, cw.size, \
           pc.id(),pc.nhost())
pc.done()
