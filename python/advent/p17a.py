import json
import copy
from collections import deque

import utility as U
from finite_state import *

def boundaries(coords, pad=False):
    padding = 4 if pad else 0
    return min(coords) - padding, max(coords) + padding

class ClayRecord:

    def __init__(self, pstr):
        assert pstr.startswith("x=") or pstr.startswith("y=")
        self.xvaries = pstr.startswith("y=")

        tokens = pstr.split(",")
        self.minmax = self.parse_min_max(tokens[1])
        self.single = self.parse_single(tokens[0])


    def parse_min_max(self, s):
        eqidx = s.find('=')
        elidx = s.find('..')

        rmin = int(s[eqidx+1:elidx])
        rmax = int(s[elidx+2:])
        return (rmin, rmax)

    def parse_single(self, s):
        eqidx = s.find("=")
        return int(s[eqidx+1:])

    def get_clay_points(self):

        for varpt in range(self.minmax[0], self.minmax[1]+1):
            if self.xvaries:
                yield (varpt, self.single)
            else:
                yield (self.single, varpt)



class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "HAP" : "F:RSS",
            "PPP" : "CNB",
            "HW" : "F:WA",
            "WA" : "T:MNW",
            "MNW" : "PPP",
            "PIS" : "T:PPP,F:SOL",
            "SWN" : "F:PPP",
            "SOL" : "F:SOR",
            "SOR" : "F:PPP",
            "PPP" : "HAP",
            "RSS" : "T:SC,F:ROWN",
            "ROWN" : "CNB"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))

        self.test_code = None

        self.clays = set()

        # point --> N =  1, 2... 7 (never 4 or 6)
        # 1 = unsupported water,
        # & 2 = left support
        # & 4 = rght support
        self.board = {}

        # Copy and updated version of board
        self.newbrd = {}

        self.probes = deque()

        self.iteration = 0


    def get_result(self):
        
        ybnd = boundaries([cpt[1] for cpt in self.clays])

        def okayy(pt):
            y = pt[1]
            return ybnd[0] <= y and y <= ybnd[1]

        basics = [pt for pt in self.board if okayy(pt)]
        settld = [pt for pt, bv in self.board.items() if okayy(pt) and bv == 7]
        return len(basics), len(settld)

    def s1_init_machine(self):
        infile = 'p17'
        infile += '' if self.test_code is None else 'test' + self.test_code
        inlist = U.read_input_deque(infile)

        for line in inlist:
            crec = ClayRecord(line)
            for cpt in crec.get_clay_points():
                self.clays.add(cpt)

        print("Read {} lines of input, have {} clay points".format(len(inlist), len(self.clays)))

        self.xbounds = boundaries([cpt[0] for cpt in self.clays], pad=True)
        self.ybounds = boundaries([cpt[1] for cpt in self.clays], pad=True)

        # Do this or else you won't be able to see the spigot!!!
        if self.ybounds[0] > -2:
            self.ybounds = (-2, self.ybounds[1])

        print("Boundaries are x={} , y={}".format(self.xbounds, self.ybounds))

        assert not (500, 0) in self.clays

        # add initial water point
        self.board[(500, 0)] = 1

        self.change_list = [(500, 0)]

    def basic_bound_okay(self, pt):

        if not (self.xbounds[0] <= pt[0] and pt[0] <= self.xbounds[1]):
            return False

        if not (self.ybounds[0] <= pt[1] and pt[1] <= self.ybounds[1]):
            return False

        return True

    def s4_copy_new_board(self):
        self.newbrd = copy.copy(self.board)

    def s5_print_board(self):
        if self.test_code != None:
            #if self.iteration % 4 == 0:
            self.print_board()

    def print_board(self):
        print("Board situation at iteration {}".format(self.iteration))
        print(self.get_board_string(simple=True, bounded=True))

    def s6_setup_probe_list(self):

        prbset = set()
        for pt in self.change_list:
            for xdelta in [-1, 0, +1]:
                for ydelta in [-1, 0, +1]:
                    prbset.add((pt[0]+xdelta, pt[1]+ydelta))

        def prbokay(prb):
            return (not prb in self.clays) and self.basic_bound_okay(prb)

        self.probes = deque([prb for prb in sorted(prbset) if prbokay(prb)])

    def s7_clear_change_list(self):
        self.change_list = []

    def s10_have_another_probe(self):
        return len(self.probes) > 0

    def current_value(self):
        return self.board.get(self.probes[0], 0)

    def s14_has_water(self):
        return self.current_value() > 0

    def s15_position_is_settled(self):
        return self.current_value() == 7

    def s18_water_above(self):
        curpt = self.probes[0]
        abvpt = (curpt[0], curpt[1]-1)
        return self.board.get(abvpt, 0) > 0

    def s20_supported_water_neighbor(self):
        
        curpt = self.probes[0]
        for xd in [-1, +1]:
            # immediate neighbor
            sidept = (curpt[0]+xd, curpt[1])
            # point supporting neighbor
            sidelow = (sidept[0], sidept[1]+1)

            # if the neighbor has any water, and the lower point is fully supported, okay
            if self.board.get(sidept, 0) > 0 and (sidelow in self.clays or self.board.get(sidelow, 0) == 7):
                return True

        return False

    def s22_mark_new_water(self):

        if self.test_code == None:
            pass
            #print("Marking new water at {}".format(self.probes[0]))

        self.newbrd[self.probes[0]] = 1

        # At this point, we are guaranteed that the board has changed.
        self.change_list.append(self.probes[0])

    def s30_supported_on_left(self):
        return self.check_support(-1, 2)

    def s31_mark_left_support(self):
        self.turn_on_support(2)

    def s32_supported_on_right(self):
        return self.check_support(+1, 4)

    def s33_mark_right_support(self):
        self.turn_on_support(4)

    def check_support(self, xdelta, thebit):
        curpt = self.probes[0]
        nxtpt = (curpt[0]+xdelta, curpt[1])
        return nxtpt in self.clays or (self.board.get(nxtpt, 0) & thebit) > 0

    def turn_on_support(self, thebit):
        curpt = self.probes[0]
        oldval = self.newbrd.get(curpt, 0)
        assert oldval > 0
        self.newbrd[curpt] |= thebit

        if self.newbrd[curpt] != oldval:
            self.change_list.append(curpt)

    def get_board_char(self, pt, simple):

        if pt == (500, 0):
            return '+'

        if pt in self.clays:
            return '#'

        bval = self.board.get(pt, 0)

        if bval == 0:
            return '.'

        if bval == 1:
            return '|'

        if bval == 7:
            return '~'

        if bval == 3:
            # 1 + 2
            return '|' if simple else '{'

        if bval == 5:
            return '|' if simple else '}'

        assert False, 'Bad board value: {}'.format(bval)


    def get_board_string(self, simple=False, bounded=False):
        lines = []

        for ypt in range(self.ybounds[0], self.ybounds[1]):
            chars = [(xpt, self.get_board_char((xpt, ypt), simple)) for xpt in range(self.xbounds[0], self.xbounds[1])]

            if bounded: 
                #if not (-5 <= ypt and ypt <= 35):
                #    continue

                chars = [(x,c) for x,c in chars if 480 <= x and x <= 580]

            lines.append("".join([c for _, c in chars]))

        return "\n".join(lines)

    def s36_poll_probe_point(self):
        self.probes.popleft()

    def s40_reached_steady_state(self):
        return len(self.change_list) == 0


    def s42_replace_old_with_new(self):
        self.board = copy.copy(self.newbrd)
        self.iteration += 1

    def s50_success_complete(self):
        pass




def run_tests():
    
    testmap = {'A': (57, 29) }

    for code, expect in testmap.items():
        pmach = PMachine()
        pmach.test_code = code
        pmach.run2_completion()
        assert pmach.get_result() == expect, "Got result {} but expected {} for problem {}".format(pmach.get_result(), expect, code)
        print("Confirmed correct result")

    