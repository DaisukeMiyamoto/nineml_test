from mpi4py import MPI
from neuron import h
import pylab

def load_model(filename):
    cell = h.CellSwc(filename, 0, 0, 0)
    for sec in h.allsec():
        sec.insert('hh')

    return cell


def set_iclamp(stim_sec_name, pc=0):
    stim = 0
    for sec in h.allsec():
        if(sec.name() == stim_sec_name):
            print "Stim Compartment = %s in #%d" % (stim_sec_name, pc.id())
            stim = h.IClamp(0.5, sec=sec)
            stim.amp = 1.0
            stim.delay = 100.0
            stim.dur = 200.0
    return(stim)

def set_vec_v(rec_sec_name, pc=0):
    vec_v = 0
    for sec in h.allsec():
        if(sec.name() == rec_sec_name):
            print "Record Compartment = %s in #%d" % (rec_sec_name, pc.id())
            vec_v = h.Vector()
            vec_v.record(sec(0.5)._ref_v)
    
    return(vec_v)

def show_section():
    for sec in h.allsec():
        print sec.name()

def show_result(pc, setup_time, calc_time, cplx):
    if(pc.id() == 0):
        print "\n##############################################################"
        print "# setup time = %.2f sec" % setup_time
        print "# calc time = %.2f sec" % calc_time 
        print "#"

    num_cmp = 0
    for sec in h.allsec():
        num_cmp += 1

    for i in range(int(pc.nhost())):
        pc.barrier()
        if(i == pc.id()):
            print "# %d/%d :\t%d compartment (%d)" % (pc.id(), pc.nhost(), num_cmp, cplx)

def show_plot(vec_t, vec_v):
    pylab.plot(vec_t, vec_v)
    pylab.show()

# implementing
'''
def save_mcomplex(lb):
    mt = h.MechanismType(0)
    #name = ""
    h('strdef name')
    for i in range(int(mt.count())):
        mt.select(i)
        mt.selected(h.name)
        print "%g %s" % (lb.m_complex_[0].x[i], h.name)
'''

def main():
    h.load_file("multisplit.hoc")
    h('{nrn_load_dll("/home/nebula/git/split/specials/x86_64/.libs/libnrnmech.so")}')

    tstop = 100
    pc = h.ParallelContext()
    start = h.startsw()

    ######################################################
    # load model
    cell = load_model("./1056.swc")

    ######################################################
    # generate mcomplex.dat
    #lb = h.MyLoadBalance()
    #lb.ExperimentalMechComplex()
    #save_mcomplex(lb)
    #pc.barrier()
    #h.mcomplex()
    h.chk_mcomplex()

    ######################################################
    # set up multi split
    cplx = h.multisplit()
    pc.multisplit()
    pc.set_maxstep(10)

    ######################################################
    # set stim and record of v
    stim = set_iclamp("CellSwc[0].Dend[2000]", pc)
    vec_t = h.Vector()
    vec_t.record(h._ref_t)
    vec_v = set_vec_v("CellSwc[0].Dend[100]", pc)
    setup_time = h.startsw() - start

    ######################################################
    # run simulation
    start = h.startsw()
    h.stdinit()
    pc.psolve(tstop)
    pc.barrier()
    calc_time = h.startsw() - start

    ######################################################
    # disp info
    show_result(pc, setup_time, calc_time, cplx)
    #show_section()
    #if(vec_v != 0):
    #    show_plot(vec_t, vec_v)
    pc.done()


if __name__== '__main__':
    main()

