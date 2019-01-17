import json

from itertools import product

import utility as U
from finite_state import *

class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        
        self.points = []

        self.x_contrib = {}
        self.y_contrib = {}

    def get_result(self):
        return self.gregsize

    def s1_init_machine(self):
        
        def getxy(istr):
            xs, ys = istr.split(",")
            return (int(xs), int(ys))

        inlist = U.read_input_deque('p06')

        for idx, istr in enumerate(inlist):
            pt = getxy(istr)
            self.points.append(pt)

        print("Reading {} input points".format(len(self.points)))


    def get_contrib_map(self, coords):

        minc = min(coords)-1
        maxc = max(coords)+1

        def contrib(cp):
            return sum([abs(cp - c) for c in coords])

        return { cp : contrib(cp) for cp in range(minc, maxc+1) } 

    def s4_build_x_contrib_map(self):
        self.x_contrib = self.get_contrib_map([pt[0] for pt in self.points])
        print(self.x_contrib)

    def s5_build_y_contrib_map(self):        
        self.y_contrib = self.get_contrib_map([pt[1] for pt in self.points])


    def s10_count_region_size(self):
        self.gregsize = sum([c[0] + c[1] <= 10000 for c in product(self.x_contrib.values(), self.y_contrib.values())])

    def s30_success_complete(self):
        pass    

        
        
def run_tests():
    pass