import pylab
import numpy
from neuron import h 


class Cell():

    def __init__(self):
        self.soma    = h.Section ()  
        self.apical  = h.Section () 
        self.basilar = h.Section() 
        self.axon    = h.Section ()

        self.dendrites = [] 
        self.dendrites.append(self.apical)
        self.dendrites.append(self.basilar)

    def topology(self):
        self.apical.connect(self.soma, 1, 0)
        self.basilar.connect(self.soma, 0, 0)
        self.axon.connect(self.soma, 0, 0)

    def geometory(self):
        self.soma.L = 30	
        self.soma.nseg = 1   
        self.soma.diam = 30 

        self.apical.L = 600 
        self.apical.nseg = 23 
        self.apical.diam = 1

        self.basilar.nseg = 5	
        self.basilar.diam = 2	
        self.basilar.L = 200	
        
        self.axon.L = 1000	
        self.axon.nseg = 37	
        self.axon.diam = 1	
        
    def biophysics(self):
        for sec in h.allsec():
            sec.Ra = 100 
            sec.cm = 1

        self.soma.insert('hh')
        self.apical.insert('pas')
        self.basilar.insert('pas')

        for sec in self.dendrites:
            for seg in sec:
                seg.pas.g = 0.0002 
                seg.pas.e = -65
                
        self.axon.insert('hh')

        self.syn = h.AlphaSynapse(0.5, sec=self.soma)
        self.syn.onset = 0.5 
        self.syn.gmax = 0.05 
        self.syn.e = 0


def main(): 

    cell = Cell()
    cell.topology()
    cell.geometory()
    cell.biophysics()

    dt = 0.025 
    tstop = 200.0 
    v_init = -65.0

    t = numpy.arange(0.0, tstop, dt)
    npts = t.size
    v = numpy.zeros(npts)
    v[0] = v_init

    cvode = h.CVode()
    cvode.active(1)
    cvode.atol(1.0e-5)

    h.finitialize(v_init) 
    for i in range(1,npts):
        cvode.solve(h.t + dt) 
        v[i] = cell.soma(0.5).v

    pylab.plot(t,v)
    pylab.draw()
    pylab.show()

   
if __name__ == '__main__':
    main()
