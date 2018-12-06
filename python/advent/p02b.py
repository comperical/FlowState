import json
from collections import deque

import utility as U
from finite_state import *

class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "HAI" : "F:FC",
            "HAJ" : "F:PI",
            "PI": "HAI",
            "PJ": "HAJ",
            "TIJ" : "T:MS",
            "MS" : "SC"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        
        self.inputdata = deque([])
        self.solpair = None

    def get_result(self):
        istr = self.inputdata[self.solpair[0]]
        jstr = self.inputdata[self.solpair[1]]

        overlap = [c for i, c in enumerate(istr) if c == jstr[i]]
        return "".join(overlap)


    def s1_init_machine(self):
        self.inputdata = U.read_input_deque('p02')
        assert all([len(s.strip()) > 0 for s in self.inputdata])

    def s6_prep_idx_list(self):
        self.idx_list = deque(range(len(self.inputdata)))

    def s8_have_another_idx(self):
        return len(self.idx_list) > 0

    def s10_prep_jdx_list(self):
        self.jdx_list = deque(range(self.idx_list[0]+1, len(self.inputdata)))

    def s12_have_another_jdx(self):
        return len(self.jdx_list) > 0

    def s14_test_idx_jdx(self):
        istr = self.inputdata[self.idx_list[0]].strip()
        jstr = self.inputdata[self.jdx_list[0]].strip()

        def diffat(p):
            return 1 if istr[p] != jstr[p] else 0

        diffsum = sum([diffat(p) for p in range(len(istr))])

        if diffsum == 1:
            print("Got near-hit for {} vs {}".format(istr, jstr))

        return diffsum == 1

    def s16_poll_jdx(self):
        self.jdx_list.popleft()

    def s18_poll_idx(self):
        self.idx_list.popleft()

    def s19_mark_success(self):
        self.solpair = (self.idx_list[0], self.jdx_list[0])

    def s20_success_complete(self):
        pass    

    def s21_failure_complete(self):
        print("Failed!!!")

        
        
    