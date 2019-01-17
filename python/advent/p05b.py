import json
from collections import deque, Counter

import utility as U
from finite_state import *

class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "HAP" : "F:LPR", 
            "HPP" : "F:HAP",
            "RPP" : "HAP",
            "HMP" : "F:SC",
            "LPR" : "HMP"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        self.polymers = deque([])

        self.probes = None

        # Probe to result length
        self.results = {} 


    def get_result(self):
        rlist = [(k, v) for k,v in self.results.items()]
        rlist = sorted(rlist, key=lambda x: x[1])
        print(rlist[0])
        return rlist[0][1]

    def s1_init_machine(self):
        self.org_input = U.read_input_deque('p05')[0]

    def s2_init_probe_list(self):
        pset = set([p.lower() for p in self.org_input])
        self.probes = deque(pset)

    def s3_have_more_probes(self):
        return len(self.probes) > 0

    def s4_set_next_probe(self):
        self.curprobe = self.probes.pop()

    def s5_prepare_probe_input(self):
        prvlen = len(self.org_input)

        assert self.curprobe == self.curprobe.lower(), "Must be lower case"
        self.big_input = self.org_input.replace(self.curprobe, '').replace(self.curprobe.upper(), '')
        self.input_pos = 0
        self.polymers = deque([])

        print("Original length is {}, lenght is {} after removal of {}".format(len(self.org_input), len(self.big_input), self.curprobe))

    def s8_have_another_polymer(self):
        return self.input_pos < len(self.big_input)

    def s9_read_next_polymer(self):
        self.polymers.append(self.big_input[self.input_pos])
        self.input_pos += 1

    def s10_have_polymer_pair(self):
        if len(self.polymers) < 2:
            return False

        pa = self.polymers[-1]
        pb = self.polymers[-2]

        #print("Have {} -- {} ".format(pa, pb))

        return pa != pb and pa.lower() == pb.lower()

    def s11_remove_polymer_pair(self):

        for _ in range(2):
            lastp = self.polymers.pop()
            #print("Popped {}".format(lastp))


    def s15_log_probe_result(self):
        self.results[self.curprobe] = len(self.polymers)
        print("result for probe={} is {}".format(self.curprobe, len(self.polymers)))


    def s30_success_complete(self):
        pass    

        
        
    