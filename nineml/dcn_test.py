from mpi4py import MPI
simulator = 'neuron'
import nineml
if simulator == 'neuron':
    from pype9.cells.neuron import CellMetaClass  # @UnusedImport
else:
    from pype9.cells.nest import CellMetaClass  # @Reimport

import os.path
#import unittest
'''
from nineml import load, Document
from nineml.user.multicomponent import (
    MultiComponent, SubComponent, PortExposure, MultiCompartment,
    FromSibling, FromDistal, FromProximal, Mapping, Domain)
from nineml.abstraction import (
    Dynamics, Regime, AnalogReceivePort, OutputEvent, AnalogSendPort, On,
    StateAssignment)
from nineml.user.port_connections import PortConnection
from nineml.user.component import DynamicsProperties
'''
from neuron import h


def insert_domain(mc, sec, domain):
    modlist = []
    for subcomp in domain.dynamics.subcomponents:
        modlist.append(subcomp.name)
        sec.insert(subcomp.name)
    #print modlist
    #for domain in mc.domains:
    #    print domain
    #    for comp in domain.dynamics.subcomponents:
            

def setup_sections(mc):
    tree = mc.tree
    pc = h.ParallelContext()

    ##############################################################
    # show mechanisms
    h.chk_mcomplex()

    ##############################################################
    # set up sections
    sections = []
    section_def_template = 'create %s[%d]'
    h(section_def_template % (mc.name, len(tree)))
    for sec in h.allsec():
        sections.append(sec)
    #for i in range(len(tree)):
    #    sections.append(h.Section(mc.comp1.name+'['+str(i)+']'))


    ##############################################################
    # connect sections
    for i,sec in enumerate(sections):
        parent = tree[i]
        #print "%d to %d" % (i, tree[i])
        if(parent != 0):
            sec.connect(sections[parent-1], 1, 0)

    ##############################################################
    # insert phisiology
    for i,sec in enumerate(sections):
        #print "set %s to %d" % (mc.mapping.domain_name(i), i)
        insert_domain(mc, sec, mc.domain(i))
        
    #for domain in mc.domains:
    #    for comp in domain.dynamics.subcomponents:
            
            
            
    #for i,sec in enumerate(sections):
        #sec.insert('hh')
        #print mc.comp1.domain(i)
        #if(mc.comp1.mapping[1][i]==0):
        #    sec.insert('hh')
        #else:
        #    sec.insert('pas')

    ##############################################################
    # show topology    
    if(pc.id()==0):
        print tree
        #h.topology()


    ##############################################################
    # test split
    cplx = h.multisplit()
    num_cmp = 0
    for sec in h.allsec():
        num_cmp += 1


    ##############################################################
    # show topology and result
    setup_time = 0
    calc_time = 0
    if(pc.id()==0):
        print "\n##############################################################"
        print "# setup time = %.2f sec" % setup_time
        print "# calc time = %.2f sec" % calc_time
        print "#"


    for i in range(int(pc.nhost())):
        pc.barrier()
        if(i==pc.id()):
            print "# %d/%d : %d compartment (%d)" % (pc.id(), pc.nhost(), num_cmp, cplx)

    print "#"
    #for i in range(int(pc.nhost())):
    #    pc.barrier()
    #    if(i==pc.id()):
    #        h.topology()


def main():
    h('{nrn_load_dll("/home/nebula/git/CerebellarNuclei/x86_64/.libs/libnrnmech.so")}')
    h.load_file("multisplit.hoc")

    dcn = nineml.read(os.path.join(
        os.environ['HOME'], 'git', 'CerebellarNuclei', '9ml',
        'dcn.xml'))['DCN']
    
    #dcn_cell = CellMetaClass(dcn)
    setup_sections(dcn)
    #runsimulation()
    #show_info()


if __name__ == '__main__':
    main()
    #mc = TestMultiCompartment()
    #xml = mc.test_multicompartment_xml()
