import json
from collections import deque, Counter

import utility as U
from finite_state import *

class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "HAP" : "F:SC", 
            "HPP" : "F:HAP",
            "RPP" : "HAP"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))

        self.polymers = deque([])


    def get_result(self):
        return len(self.polymers)

    def s1_init_machine(self):
        self.big_input = U.read_input_deque('p05')[0]
        self.input_pos = 0


    def s4_have_another_polymer(self):
        return self.input_pos < len(self.big_input)

    def s6_read_next_polymer(self):
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

    def s30_success_complete(self):
        pass    

        
        
    