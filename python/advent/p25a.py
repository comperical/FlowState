import json
import copy

from collections import deque

import utility as U
from finite_state import *

class Star:

    def __init__(self, coordstr, strid):
        self.coords = [int(c) for c in coordstr.split(",")]
        assert len(self.coords) == 4

        self.starid = strid
        self.cnstid = strid

    def __str__(self):
        return "ID={}/{} ".format(self.starid, self.cnstid) + ",".join([str(c) for c in self.coords])

    def mdist(self, other):
        return sum([abs(c[0] - c[1]) for c in zip(self.coords, other.coords)])


class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "HAL" : "F:SC",
            "LSC" : "T:PLS",
            "PLS" : "HAL"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))

        self.test_code = None

        self.stars = []

        self.links = deque([])

    def get_result(self):
        cset = set([star.cnstid for star in self.stars])
        return len(cset)


    def s1_init_machine(self):
        infile = 'p25'
        infile += '' if self.test_code == None else 'test' + self.test_code

        for line in U.read_input_deque(infile):
            nstar = Star(line, len(self.stars))
            #assert str(nstar) == line.strip()
            self.stars.append(nstar)



    def s4_build_star_links(self):

        for idx, astar in enumerate(self.stars):
            for jdx, bstar in enumerate(self.stars):
                if jdx <= idx:
                    continue

                a2bdist = astar.mdist(bstar)

                if a2bdist <= 3:
                    self.links.append((astar, bstar))


    def s12_have_another_link(self):
        return len(self.links) > 0

    def get_const_pair(self):
        constids = sorted([self.links[0][0].cnstid, self.links[0][1].cnstid])
        return constids[0], constids[1]

    def s16_link_same_constellation(self):
        aconst, bconst = self.get_const_pair()
        return aconst == bconst

    def s20_reassign_constellation(self):

        aconst, bconst = self.get_const_pair()

        for star in self.stars:
            if star.cnstid == bconst:
                star.cnstid = aconst

    def s22_poll_link_stack(self):
        self.links.popleft()

    def s30_success_complete(self):
        pass


def run_tests():
    
    testmap = { 'A' : 2, 'B' : 4, 'C': 3, 'D': 8 }

    for tcode, expect in testmap.items():
        pmach = PMachine()
        pmach.test_code = tcode
        pmach.run2_completion()
        print("For tcode {}, expected {}, result is {}".format(tcode, expect, pmach.get_result()), end='')
        assert pmach.get_result() == expect
        print("... success")

