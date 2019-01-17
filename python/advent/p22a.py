import json
import copy
from collections import deque

import utility as U
from finite_state import *

EROSION_TYPE = { 0: 'rocky', 1: 'wet', 2: 'narrow'}

ERO_CHARS = { 'rocky': '.', 'wet': '=', 'narrow' : '|' }


class CaveInfo:

    def __init__(self, gindex, depth):
        self.geoindex = gindex
        self.erosion = (gindex + depth) % 20183
        self.erotype = EROSION_TYPE.get(self.erosion % 3)

    def get_risk(self):
        return self.erosion % 3        


class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "HMR" : "F:SC",
            "AHR" : "T:PRQ",
            "RIO" : "T:ZGA",
            "RIT" : "F:IZY",
            "ZGA" : "PRQ",
            "PRQ" : "HMR",
            "IZY" : "F:IZX",
            "ZYA" : "PRQ",
            "ZXA" : "PRQ",
            "IZX" : "F:HLNI",
            "HLNI" : "F:SLR",
            "HANI" : "F:SAR",
            "SLR" : "PRQ",
            "NBA" : "PRQ"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))

        self.depth = 10914

        self.target = (9, 739)

        self.caveinfo = {}

        self.requests = deque()

        self.request_padding = 6


    def get_result(self):
        
        def cinfogen():
            for x in range(0, self.target[0]+1):
                for y in range(0, self.target[1]+1):
                    cinfo = self.caveinfo.get((x, y), None)
                    assert cinfo != None
                    yield cinfo

        return sum([ci.get_risk() for ci in cinfogen()])

    def s1_init_machine(self):

        print("Target is : {}".format(self.target))

        for x in range(0, self.target[0]+self.request_padding):
            for y in range(0, self.target[1]+self.request_padding):
                self.requests.append((x, y))


    def external_submit_request(self):
        

    def s4_pause_new_requests(self):
        pass

    def submit_answer(self, gindex):
        self.caveinfo[self.requests[0]] = CaveInfo(gindex, self.depth)

    def s8_have_more_requests(self):
        return len(self.requests) > 0

    def s9_already_have_request(self):
        return self.requests[0] in self.caveinfo

    def s10_request_is_origin(self):
        return self.requests[0] == (0, 0)

    def s11_request_is_target(self):
        return self.requests[0] == self.target

    def s12_zero_geo_answer(self):
        self.submit_answer(0)        

    def s14_is_zero_yboundary(self):
        return self.requests[0][1] == 0

    def s15_zero_yboundary_answer(self):
        gindex = self.requests[0][0] * 16807
        self.submit_answer(gindex)

    def s16_is_zero_xboundary(self):
        return self.requests[0][0] == 0

    def s17_zero_xboundary_answer(self):
        gindex = self.requests[0][1] * 48271
        self.submit_answer(gindex)

    def s20_have_left_neighbor_info(self):
        leftpt = (self.requests[0][0] - 1, self.requests[0][1])
        return leftpt in self.caveinfo

    def s23_have_above_neighbor_info(self):
        abovpt = (self.requests[0][0], self.requests[0][1]-1)
        return abovpt in self.caveinfo

    def s26_neighbor_based_answer(self):
        leftinfo = self.caveinfo[(self.requests[0][0]-1, self.requests[0][1])]
        abovinfo = self.caveinfo[(self.requests[0][0], self.requests[0][1]-1)]

        gindex = leftinfo.erosion * abovinfo.erosion
        self.submit_answer(gindex)

    def s38_submit_left_request(self):
        curpt = self.requests[0]
        self.appendleft((curpt[0]-1, curpt[1]))

    def s39_submit_above_request(self):
        curpt = self.requests[0]
        self.appendleft((curpt[0], curpt[1]-1))

    def s40_poll_request_queue(self):
        self.requests.popleft()

    def s50_success_complete(self):
        pass

    def get_board_char(self, pt):

        if pt == (0, 0):
            return 'M'

        if pt == self.target:
            return 'T'

        cinfo = self.caveinfo.get(pt, None)
        if cinfo == None:
            return '?'

        etype = cinfo.erotype
        return ERO_CHARS[etype]

    def get_board_str(self):

        def boardchars():
            for y in range(0, self.target[1]+6):
                for x in range(0, self.target[0]+6):
                    yield self.get_board_char((x, y))
                yield '\n'

        return "".join(boardchars())

    def print_board(self):
        print(self.get_board_str())


def run_tests():

    resultstr = """
        M=.|=.|.|=.|=|=.
        .|=|=|||..|.=...
        .==|....||=..|==
        =.|....|.==.|==.
        =|..==...=.|==..
        =||.=.=||=|=..|=
        |.=.===|||..=..|
        |..==||=.|==|===
        .=..===..=|.|||.
        .======|||=|=.|=
        .===|=|===T===||
        =|||...|==..|=.|
        =.=|=.=..=.||==|
        ||=|=...|==.=|==
        |=.=||===.|||===
        ||.|==.|.|.||=||
        """

    def stripboard(bs):
        return bs.replace('\n', '').replace(' ', '')

    pmach = PMachine()
    pmach.target = (10, 10)
    pmach.depth = 510
    pmach.run2_completion()

    assert pmach.get_result() == 114
    assert stripboard(pmach.get_board_str()) == stripboard(resultstr)
    print("Test successful!!")



    