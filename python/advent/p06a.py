import json
import string
from collections import deque, Counter

import utility as U
from finite_state import *

class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "HANE" : "F:SC,T:SNTC",
            "HACE" : "F:HANE",
            "PCE"  : "HACE"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        
        # set([ptx, pty])
        self.next_expands = set()

        # deque([ptx, pty])
        self.crnt_expands = None

        # {(ptx, pty) : dist to nearest seed }
        self.distances = {}

        # {(ptx, pty) : [] nearest seeds}
        self.closests = {}


    def get_result(self):
        return self.get_region_size_counter().most_common(1)[0][1]

    def s1_init_machine(self):
        
        def getxy(istr):
            xs, ys = istr.split(",")
            return (int(xs), int(ys))

        inlist = U.read_input_deque('p06')

        for idx, istr in enumerate(inlist):
            pt = getxy(istr)
            self.distances[pt] = 0
            self.closests[pt] = set([idx])
            self.next_expands.add(pt)

    def s2_calc_boundaries(self):

        xpts = [pt[0] for pt in self.closests]
        ypts = [pt[1] for pt in self.closests]

        self.minx = min(xpts)
        self.maxx = max(xpts)

        self.miny = min(ypts)
        self.maxy = max(ypts)

        print("X in {}/{} Y is {}/{}".format(self.minx, self.maxx, self.miny, self.maxy))

    def is_inner_pt(self, ptx, pty):
        return self.minx <= ptx and ptx <= self.maxx and self.miny <= pty and pty <= self.maxy

    def is_outer_pt(self, ptx, pty):
        return self.minx-5 <= ptx and ptx <= self.maxx+5 and self.miny-5 <= pty and pty <= self.maxy+5


    def get_region_size_counter(self, translate=False):
        """
        Get a counter of { regid : size } for non-infinite regions
        """
        infregs = self.get_infinite_regions()
        scounter = Counter()

        for pt, dist in self.distances.items():

            closeids = self.closests[pt]
            onehit = list(closeids)[0]

            if len(closeids) > 1 or onehit in infregs:
                continue

            kc = self.get_display_str(onehit) if translate else onehit
            #print("KC is {}".format(kc))
            scounter.update([kc])

        return scounter



    def get_infinite_regions(self, translate=False):
        infset = set()
        for pt in self.distances:
            if self.is_inner_pt(pt[0], pt[1]):
                continue

            closeids = self.closests[pt]
            if len(closeids) > 1:
                continue

            if self.is_outer_pt(pt[0], pt[1]):
                for ptid in closeids:
                    infset.add(ptid)

        if translate:
            return [self.get_display_str(ptid) for ptid in infset]

        return infset

    def print_inner_region(self):

        for y in range(0, self.maxy+1):
            for x in range(0, self.maxx+2):
                pstr = '?'
                pnt = (x, y)
                if pnt in self.distances:
                    closeids = self.closests[pnt]
                    if len(closeids) > 1:
                        pstr = '.'
                    else:
                        ptid = list(closeids)[0]
                        pstr = self.get_display_str(ptid)

                        if self.distances[pnt] == 0:
                            pstr = pstr.upper()

                print("{}".format(pstr), end='')
            print("")


    def get_display_str(self,ptid):
        modid = ptid % len(string.ascii_lowercase)
        return list(string.ascii_lowercase)[modid]

    def s4_swap_next_to_current(self):
        self.crnt_expands = deque(self.next_expands)
        self.next_expands = set([])

    def s5_have_another_current_expand(self):
        return len(self.crnt_expands) > 0

    def s6_register_neighbors(self):
        thepnt = self.crnt_expands[0]
        thedst = self.distances[thepnt]
        thecls = self.closests[thepnt]

        for newpt in self.neighbors(thepnt):
            if not self.is_outer_pt(newpt[0], newpt[1]):
                continue

            curdst = self.distances.get(newpt, None)
            if curdst == None:
                self.distances[newpt] = thedst+1
                self.closests[newpt] = set(thecls)
                self.next_expands.add(newpt)
            elif curdst == thedst+1:
                for ptid in thecls:
                    self.closests[newpt].add(ptid)

    def neighbors(self, apt):

        for dx in [-1, +1]:
            yield (apt[0]+dx, apt[1])

        for dy in [-1, +1]:
            yield (apt[0], apt[1]+dy)

    def s7_poll_current_expand(self):
        self.crnt_expands.popleft()

    def s12_have_any_next_expand(self):
        return len(self.next_expands) > 0

    def s30_success_complete(self):
        pass    

        
        
    