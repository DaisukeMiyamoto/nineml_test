import os.path
import unittest
from mpi4py import MPI
from nineml import load, Document
from nineml.user.multicomponent import (
    MultiComponent, SubComponent, PortExposure, MultiCompartment,
    FromSibling, FromDistal, FromProximal, Mapping, Domain)
from nineml.abstraction import (
    Dynamics, Regime, AnalogReceivePort, OutputEvent, AnalogSendPort, On,
    StateAssignment)
from nineml.user.port_connections import PortConnection
from nineml.user.component import DynamicsProperties

from neuron import h

examples_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                            'xml', 'neurons')


class TestMultiCompartment():
    def __init__(self):
        self.xml = ''
        self.a_props = Dynamics(
            name='A',
            aliases=['A1:=P1', 'A2 := ARP1 + SV2', 'A3 := SV1'],
            regimes=[
                Regime(
                    'dSV1/dt = -SV1 / (P2*t)',
                    'dSV2/dt = SV1 / (ARP1*t) + SV2 / (P1*t)',
                    transitions=[On('SV1 > P1', do=[OutputEvent('emit')]),
                                 On('spikein', do=[OutputEvent('emit')])],
                    name='R1',
                ),
                Regime(name='R2', transitions=On('SV1 > 1', to='R1'))
            ],
            analog_ports=[AnalogReceivePort('ARP1'),
                          AnalogReceivePort('ARP2'),
                          AnalogSendPort('A1'), AnalogSendPort('A2')],
            parameters=['P1', 'P2']
        )

        self.b_props = Dynamics(
            name='B',
            aliases=['A1:=P1', 'A2 := ARP1 + SV2', 'A3 := SV1',
                     'A4 := SV1^3 + SV2^3'],
            regimes=[
                Regime(
                    'dSV1/dt = -SV1 / (P2*t)',
                    'dSV2/dt = SV1 / (ARP1*t) + SV2 / (P1*t)',
                    'dSV3/dt = -SV3/t + P3/t',
                    transitions=[On('SV1 > P1', do=[OutputEvent('emit')]),
                                 On('spikein', do=[
                                    OutputEvent('emit'),
                                    StateAssignment('SV1', 'P1')])],
                    name='R1',
                ),
                Regime(name='R2', transitions=[
                    On('SV1 > 1', to='R1'),
                    On('SV3 < 0.001', to='R2',
                       do=[StateAssignment('SV3', 1)])])
            ],
            analog_ports=[AnalogReceivePort('ARP1'),
                          AnalogReceivePort('ARP2'),
                          AnalogSendPort('A1'),
                          AnalogSendPort('A2'),
                          AnalogSendPort('A3'),
                          AnalogSendPort('SV3')],
            parameters=['P1', 'P2', 'P3']
        )
        self.comp1 = MultiCompartment(
            name='test',
            tree=[0, 1, 2, 3, 2, 3],
            mapping=Mapping({0: 'soma', 1: 'dendrites'}, [0, 0, 0, 1, 1, 1]),
            domains=[
                Domain(
                    name='soma',
                    dynamics=self.a_props,
                    port_connections=[
                        PortConnection('ARP1', FromDistal('A1')),
                        PortConnection('ARP2', FromProximal('A2')),
                        PortConnection('ARP3',
                                       FromDistal('A3', domain='dendrites'))]),
                Domain(
                    name='dendrites',
                    dynamics=self.b_props,
                    port_connections=[
                        PortConnection('ARP1', FromDistal('A1')),
                        PortConnection('ARP2', FromProximal('A2'))])])

    def test_multicompartment_xml(self):
        self.xml = Document(self.comp1, self.a_props, self.b_props).to_xml()
        #print xml
        #xml = comp1.to_xml()
        
        return(self.xml)


def setup_sections(mc):
    tree = mc.comp1.tree
    pc = h.ParallelContext()

    ##############################################################
    # show mechanisms
    h.chk_mcomplex()

    ##############################################################
    # set up sections
    sections = []
    section_def_template = 'create %s[%d]'
    h(section_def_template % (mc.comp1.name, len(tree)))
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
        sec.insert('hh')
        #print mc.comp1.domain(i)
        #if(mc.comp1.mapping[1][i]==0):
        #    sec.insert('hh')
        #else:
        #    sec.insert('pas')

    ##############################################################
    # show topology    
    if(pc.id()==0):
        print tree
        h.topology()


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
    for i in range(int(pc.nhost())):
        pc.barrier()
        if(i==pc.id()):
            h.topology()



if __name__ == '__main__':
    h('{nrn_load_dll("../../nineml_catalog/neurons/9build/neuron/Izhikevich2003Properties/src/x86_64/.libs/libnrnmech.so")}')
    h.load_file("multisplit.hoc")

    mc = TestMultiCompartment()
    xml = mc.test_multicompartment_xml()

    setup_sections(mc)



