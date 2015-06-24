from itertools import chain
from mpi4py import MPI
from neuron import h
import pylab

Section = h.Section

soma = Section()
apical = Section()
basilar = Section()
axon = Section()

apical.connect(soma, 1, 0)
basilar.connect(soma, 0, 0)
axon.connect(soma, 0, 0)

soma.L = 30
soma.nseg = 1
soma.diam = 30

apical.L = 600
apical.nseg = 23
apical.diam = 1

basilar.L = 200
basilar.nseg = 5
basilar.diam = 2

axon.L = 1000
axon.nseg = 37
axon.diam = 1

for sec in h.allsec():
    sec.Ra = 100
    sec.cm = 1

soma.insert('hh')
apical.insert('pas')
basilar.insert('pas')
axon.insert('hh')

for seg in chain(apical, basilar):
    seg.pas.g = 0.0002
    seg.pas.e = -65

syn = h.AlphaSynapse(0.5, sec=soma)
syn.onset = 0.5
syn.gmax = 0.05
syn.e = 0

#g = h.Graph()
#g.size(0, 5, -80, 40)
#g.addvar('v(0.5)', sec=soma)

h.dt = 0.025
tstop = 20
v_init = -65

h.finitialize(v_init)
h.fcurrent()

vec = {}
for var in 'v', 't':
    vec[var] = h.Vector()

vec['v'].record(axon(0.5)._ref_v)
vec['t'].record(h._ref_t)


#g.begin()
h.load_file("stdrun.hoc")
h.init()
h.tstop=100
h.run()
#while h.t < tstop:
#    h.fadvance()
    #g.plot(h.t)
    #print "%f : %f" % (h.t, soma.v)

#g.flush()

pylab.plot(vec['t'], vec['v'])
pylab.show()

