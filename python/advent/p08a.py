import json
import string
from collections import deque, Counter

import utility as U
from finite_state import *


class Node:

    def __init__(self, pnode):

        self.parent = pnode

        self.kids = []
        self.meta = []

        self.num_kids = None
        self.num_meta = None

    def get_meta_sum(self):
        return sum([k.get_meta_sum() for k in self.kids]) + sum(self.meta)

    def get_p2_sum(self):
        return sum(self.value_generator())

    def value_generator(self):
        if len(self.kids) == 0:
            yield sum(self.meta)
            return

        for m in self.meta:
            n = m-1
            if 0 <= n and n < len(self.kids):
                yield self.kids[n].get_p2_sum()

class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {   
            "DWK" : "F:DWM",
            "DWM" : "F:ATT",
            "ATT" : "T:SC",
            "PTP" : "DWK",
            "DDK" : "RNI",
            "RNM" : "DWM"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        
        self.inputs = deque([])


    def get_result(self):
        #return self.curnode.get_meta_sum()

        return self.curnode.get_p2_sum()

    def s1_init_machine(self):
        self.curnode = Node(None)

        lines = U.read_input_deque('p08')
        assert len(lines) == 1

        for nstr in lines[0].split():
            self.inputs.append(int(nstr))

        #print("Read inputs: {}".format(self.inputs))


    def s10_read_node_init(self):
        self.curnode.num_kids = self.inputs.popleft()
        self.curnode.num_meta = self.inputs.popleft()

    def s12_done_with_kids(self):
        return len(self.curnode.kids) < self.curnode.num_kids

    def s14_create_kid(self):
        self.curnode.kids.append(Node(self.curnode))

    def s15_drop_down2_kid(self):
        self.curnode = self.curnode.kids[-1]

    def s20_done_with_meta(self):
        return len(self.curnode.meta) < self.curnode.num_meta

    def s21_read_next_meta(self):
        nextmeta = self.inputs.popleft()
        self.curnode.meta.append(nextmeta)

    def s24_at_the_top(self):
        return self.curnode.parent == None

    def s26_pop_to_parent(self):
        self.curnode = self.curnode.parent

    def s30_success_complete(self):
        pass    

        
        
    