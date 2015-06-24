from mpi4py import MPI
simulator = 'neuron'
import nineml
if simulator == 'neuron':
    from pype9.cells.neuron import CellMetaClass  # @UnusedImport
    from neuron import h
else:
    from pype9.cells.nest import CellMetaClass  # @Reimport
import os.path
import sys
import matplotlib.pyplot as plt

h.load_file("multisplit.hoc")
LIBNRNMECHPATH = "/home/nebula/git/CerebellarNuclei/x86_64/.libs/libnrnmech.so"


class MultiCompartmentSplit:
    def __init__(self, mc):
        self.pc = h.ParallelContext()
        self.mc = mc
        self.tree = mc.tree
        self.name = mc.name
        self.sections = []
        self.section_def_template = 'create %s[%d]'
        self.complexity = 0
        self.setup_time = 0
        self.calc_time = 0
        self.num_compartment = 0

        self.tstop = 2000           # [msec]

        self.vec_v = 0              # one vec_v is not good 
        self.vec_t = 0

    #def show_mech_cost(self):
        

    def set_vec_t(self):
        self.vec_t = h.Vector()
        self.vec_t.record(h._ref_t)

    def set_vec_v(self, rec_sec_name):
        for sec in h.allsec():
            if(sec.name() == rec_sec_name):
                print "Record Compartment = %s in #%d" % (rec_sec_name, self.pc.id())
                self.vec_v = h.Vector()
                self.vec_v.record(sec(0.5)._ref_v)
    
    def show_all_sections(self):
        for sec in self.sections:
            h.psection(sec=sec)

    def insert_domain(self, sec, domain):
        start = h.startsw()
        modlist = []
        for subcomp in domain.dynamics.subcomponents:
            modlist.append(subcomp.name)
            sec.insert(subcomp.name)
            for prop in subcomp.dynamics.properties:
                ############################################
                # this is not good and old style
                #
                sec.push()
                h(prop.name+'_'+subcomp.name+' = '+str(prop.value))
                h.pop_section()
                # 
                #sec.setter(prop.name+'_'+subcomp.name, prop.value)
                ############################################
        self.setup_time += h.startsw() - start

    def check_complexity_file(self):
        # show mechanisms
        #h.chk_mcomplex()
        h.mcomplex()

    def setup_sections(self):
        start = h.startsw()
        
        ###################################################
        # set up sections
        self.sections = []
        # old style, but it is need for section_name in hoc
        h(self.section_def_template % (self.name, len(self.tree)))
        for sec in h.allsec():
            self.sections.append(sec)


        ###################################################
        # connect sections
        for i,sec in enumerate(self.sections):
            parent = self.tree[i]
            #print "%d to %d" % (i, tree[i])
            if(parent != 0):
                sec.connect(self.sections[parent-1], 1, 0)

        self.num_compartment = 0
        for sec in h.allsec():
            self.num_compartment += 1

        self.setup_time += h.startsw() - start

    def setup_mechanisms(self):
        start = h.startsw()
        for i,sec in enumerate(self.sections):
            #print "set %s to %d" % (mc.mapping.domain_name(i), i)
            self.insert_domain(sec, self.mc.domain(i))
        
        self.setup_time += h.startsw() - start
        

    def multisplit(self):
        start = h.startsw()
        self.complexity = h.multisplit()
        self.pc.multisplit()
        self.pc.set_maxstep(10)

        self.num_compartment = 0
        for sec in h.allsec():
            self.num_compartment += 1

        self.setup_time += h.startsw() - start


    def run_simulation(self):
        start = h.startsw()
        h.stdinit()
        self.pc.psolve(self.tstop)
        self.pc.barrier()
        self.calc_time = h.startsw() - start

    def show_info(self):
        sys.stdout.flush()
        self.pc.barrier()

        if(self.pc.id()==0):
            print "\n##############################################################"
            print "# setup time = %.2f sec" % self.setup_time
            print "# calc time = %.2f sec" % self.calc_time
            print "#"
        sys.stdout.flush()
        self.pc.barrier()

        for i in range(int(self.pc.nhost())):
            if(i==self.pc.id()):
                print "# %d/%d : %d compartment (%d)" % (self.pc.id(), self.pc.nhost(), self.num_compartment, self.complexity)
            sys.stdout.flush()
            self.pc.barrier()

        if(self.pc.id()==0):
            print "#"

    def show_topology(self, id):
        if id < 0:
            for i in range(int(self.pc.nhost())):
                if(i==pc.id()):
                    h.topology()
                sys.stdout.flush()
                self.pc.barrier()
        else:
            if(id == self.pc.id()):
                h.topology()
        

    def show_plot(self):
        if(self.vec_v!=0):
            t = self.vec_t.as_numpy()
            v = self.vec_v.as_numpy()
            plt.plot(t, v, color='b')
            plt.title('simulation result with '+str(int(self.pc.nhost()))+" CPU cores")
            plt.xlabel('time [msec]')
            plt.ylabel('Membrane Potential [mv]')
            plt.axis(xmin=0, xmax=max(t), ymin=-80, ymax=10)
            plt.show()
            


def main():
    h('{nrn_load_dll("'+LIBNRNMECHPATH+'")}')

    dcn = nineml.read(os.path.join(
        os.environ['HOME'], 'git', 'CerebellarNuclei', '9ml',
        'dcn.xml'))['DCN']
    
    mc = MultiCompartmentSplit(dcn)
    #dcn_cell = CellMetaClass(dcn)

    mc.check_complexity_file()
    mc.setup_sections()
    mc.setup_mechanisms()
    mc.multisplit()
    mc.set_vec_t()
    mc.set_vec_v('DCN[100]')
    #mc.show_all_sections()

    
    mc.run_simulation()

    mc.show_info()
    mc.show_plot()

if __name__ == '__main__':
    main()
