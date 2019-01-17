import json
import copy
import hashlib

from functools import reduce
from collections import deque
from collections import Counter

import utility as U
from finite_state import *

class Nanobot:

    def __init__(self, s):
        
        alpha = s.find("=<")
        omega = s.find(">,")

        self.coords = [int(cs) for cs in s[alpha+2:omega].split(",")]
        assert len(self.coords) == 3

        rpos = s.find("r=")
        self.rpower = int(s[rpos+2:])

    def can_see(self, nbot):

        def mdist(idx):
            return abs(self.coords[idx] - nbot.coords[idx])

        netdist = sum([mdist(idx) for idx in range(3)])
        return netdist <= self.rpower

    def __str__(self):
        cstr = ",".join([str(c) for c in self.coords])
        return "pos=<{}>, r={}".format(cstr, self.rpower)




class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))

        self.is_test = False

        self.nanobots = []

        self.maxnano = None

        self.maxinrange = -1

    def get_result(self):
        return self.maxinrange

    def s1_init_machine(self):
        infile = 'p23test' if self.is_test else 'p23'
        lines = U.read_input_deque(infile)

        for s in lines:
            nbot = Nanobot(s)
            assert str(nbot) == s.strip(), "Got nbot={} but orig={}".format(nbot, s)
            self.nanobots.append(nbot)

        self.nanobots = [Nanobot(s) for s in lines]
        print("Read {} Nano bots".format(len(self.nanobots)))

    def s4_find_strongest_nanobot(self):
        
        self.maxnano = max(self.nanobots, key=lambda x: x.rpower)
        print("Found maxnano={}".format(self.maxnano))

    def s10_find_nanos_in_range(self):
        inrange = [nbot for nbot in self.nanobots if self.maxnano.can_see(nbot)]
        self.maxinrange = len(inrange)


    def s30_success_complete(self):
        pass


def run_tests():
    
    pmach = PMachine()
    pmach.is_test = True
    pmach.run2_completion()
    assert pmach.get_result() == 7
