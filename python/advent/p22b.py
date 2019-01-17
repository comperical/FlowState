import json
import copy
from collections import deque

import utility as U
from finite_state import *

import heapq

EQUIPMENT_OKAY_MAP = { 'rocky' : 'GT', 'wet': 'GN', 'narrow': 'TN' }

class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "AHP" : "T:PIQ",
            "IRR" : "T:PIQ",
            "EOFR" : "F:PIQ",
            "PIQ" : "AHP",
            "RF" : "T:SC"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))

        self.caveinfo = None

        self.depth = 10914
        self.target = (9, 739)    

        # Tuple of x/y/E, E=Equip, E = G(ear)/T(orch)/N(either) ---> Minute

        self.explores = {}

        # this is a priority queue of (minute, (x/y/E))
        self.incoming = []

    def get_time2_target(self):
        targtple = (self.target[0], self.target[1], 'T')
        return self.explores.get(targtple, None)

    def get_result(self):
        return self.get_time2_target()

    def s1_init_machine(self):
        
        import p22a
        submachine = p22a.PMachine()
        submachine.depth = self.depth
        submachine.target = self.target
        submachine.request_padding = 1000
        submachine.run2_completion()
        self.caveinfo = copy.copy(submachine.caveinfo)
        print("Grabbed caveinfo from submachine, have {} positions".format(len(self.caveinfo)))

        self.incoming.append((0, (0, 0, 'T')))

    def s8_already_have_position(self):
        return self.get_incoming_tuple() in self.explores

    def get_incoming_minute(self):
        return self.incoming[0][0]

    def get_incoming_tuple(self):
        return self.incoming[0][1]

    def get_incoming_point(self):
        tple = self.get_incoming_tuple()
        return (tple[0], tple[1])

    def get_incoming_equip(self):
        return self.get_incoming_tuple()[2]


    def s10_is_region_rock(self):
        nextpt = self.get_incoming_point()
        return nextpt[0] < 0 or nextpt[1] < 0

    def s12_check_region_okay(self):
        nextpt = self.get_incoming_point()
        assert nextpt in self.caveinfo, "Attempt to access position {} for which he have no caveinfo".format(nextpt)

    def s13_equip_okay_for_region(self):
        nextpt = self.get_incoming_point()
        equip = self.get_incoming_equip()
        cinfo = self.caveinfo[nextpt]

        eqstr = EQUIPMENT_OKAY_MAP.get(cinfo.erotype)
        return equip in eqstr

    def s20_add_location_moves(self):
        nextpt = self.get_incoming_point()
        equip = self.get_incoming_equip()
        minute = self.get_incoming_minute()

        for delta in [(-1, 0), (+1, 0), (0, -1), (0, +1)]:
            probe = (nextpt[0]+delta[0], nextpt[1]+delta[1], equip)
            heapq.heappush(self.incoming, (minute+1, probe))

    def s22_add_equipment_changes(self):
        nextpt = self.get_incoming_point()
        minute = self.get_incoming_minute()

        # It's a bit inefficient to not check for repetition here, but it's not going to hurt anything
        for tchar in ['G', 'N', 'T']:
            probe = (nextpt[0], nextpt[1], tchar)
            heapq.heappush(self.incoming, (minute+7, probe))


    def s28_log_exploration(self):
        minute = self.get_incoming_minute()
        tple = self.get_incoming_tuple()
        self.explores[tple] = minute
        #print("Logging exploration of {} at time {}".format(tple, minute))

    def s29_reached_finish(self):
        return self.get_time2_target() != None

    def s30_poll_incoming_queue(self):
        minute = self.get_incoming_minute()
        tple = self.get_incoming_tuple()

        #print("Polling queue for {} at minute {}, queue size is {}-1".format(tple, minute, len(self.incoming)))
        heapq.heappop(self.incoming)

    def s40_success_complete(self):
        pass

def run_tests():

    pmach = PMachine()
    pmach.target = (10, 10)
    pmach.depth = 510
    pmach.run2_completion()

    assert pmach.get_result() == 45
    print("Test successful!!")


    