import json
from collections import deque

import utility as U
from finite_state import *

def read_input_deque():
    indq = deque([])

    inputpath = os.path.join(U.get_data_dir(), 'p02.txt')

    with open(inputpath, 'r') as fh:
        for line in fh:
            indq.append(line.strip())

    return indq

class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "HAI" : "F:PC",
            "NHT" : "F:NHD",
            "NHD" : "F:HAI",
            "LD": "HAI"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        
        self.inputdata = deque([])
        self.next_counts = None

        self.count_three = 0
        self.count_two = 0

    def get_result(self):
        return self.count_three * self.count_two
    
    def s1_init_machine(self):
        pass

    def s2_read_input(self):
        self.inputdata = read_input_deque()

    def s6_have_another_item(self):
        return len(self.inputdata) > 0

    def s8_prepare_next_counts(self):
        nextitem = self.inputdata.popleft()
        self.next_counts = {}

        for c in nextitem:
            self.next_counts.setdefault(c, 0)
            self.next_counts[c] += 1

        #print("Counts for input {} are {}".format(nextitem, self.next_counts))

    def s10_next_has_triple(self):
        return any([v == 3 for k, v in self.next_counts.items()])

    def s11_log_triple(self):
        self.count_three += 1
    
    def s14_next_has_double(self):
        return any([v == 2 for k, v in self.next_counts.items()])

    def s15_log_double(self):
        self.count_two += 1

    def s20_problem_complete(self):
        pass    
        
        
    