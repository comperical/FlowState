import json
from collections import deque

import utility as U
from finite_state import *

class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "HAI" : "F:RI",
            "IFR" : "F:LV"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        
        self.inputdata = deque([])
        self.frequency = 0
        self.visited = set()
        self.first_revisit = None

    def get_result(self):
        return self.first_revisit
    
    def s1_init_machine(self):
        pass

    def s2_read_input(self):
        inputpath = os.path.join(U.get_data_dir(), 'p01.txt')
        #print("input path is {}".format(inputpath))

        with open(inputpath, 'r') as fh:
            for line in fh:
                self.inputdata.append(int(line))

        #print("Loaded {} input items".format(len(self.inputdata)))

    def s4_log_visit(self):
        self.visited.add(self.frequency)

    def s6_have_another_item(self):
        return len(self.inputdata) > 0  

    def s10_add_new_item(self):
        nextitem = self.inputdata.popleft()
        self.frequency += nextitem
        #print("read nextitem={}, new total is {}".format(nextitem, self.frequency))
    
    def s11_is_first_revisit(self):
        return self.first_revisit == None and self.frequency in self.visited

    def s12_mark_first_revisit(self):
        print("Got first revisit at {}".format(self.frequency))
        self.first_revisit = self.frequency

    def s15_problem_complete(self):
        pass    
        
        
        
    