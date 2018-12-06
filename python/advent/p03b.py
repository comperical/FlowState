import json
from collections import deque

import utility as U
from finite_state import *

class Claim:

    def __init__(self, crec):

        cidstr, diminfo = crec.split("@")
        self.cid = int(cidstr[1:])
        posinfo, sizeinfo = diminfo.split(":")

        def split2int(thestr, delim):
            astr, bstr = thestr.split(delim)
            return int(astr), int(bstr)

        self.xpt, self.ypt = split2int(posinfo, ",")
        self.wdth, self.hite = split2int(sizeinfo, "x")

    def reform(self):
        return "#{} @ {},{} : {}x{}".format(self.cid, self.xpt, self.ypt, self.wdth, self.hite)

    def check_orig(self, origstr):
        def flatten(s):
            return s.replace(' ', '')

        assert flatten(self.reform()) == flatten(origstr)

    def __str__(self):
        return "CID={}   x={}, y={}, wd={}, ht={}".format(self.cid, self.xpt, self.ypt, self.wdth, self.hite)

class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "HAC" : "F:FC",
            "PC" : "HAC"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        self.inputdata = deque([])
        self.cidset = set([])
        self.biggrid = []
        for x in range(1000):
            self.biggrid.append([])
            for _ in range(1000):
                self.biggrid[x].append([])

    def get_result(self):
        print(self.cidset)
        return list(self.cidset)[0]

    def s1_init_machine(self):
        self.inputdata = U.read_input_deque('p03')

        #while len(self.inputdata) > 10:
        #    self.inputdata.popleft()

    def s8_have_another_claim(self):
        return len(self.inputdata) > 0

    def s10_process_claim(self):
        claimstr = self.inputdata.popleft()
        claim = Claim(claimstr)
        self.cidset.add(claim.cid)

        for x in range(claim.xpt, claim.xpt+claim.wdth):
            for y in range(claim.ypt, claim.ypt+claim.hite):
                self.biggrid[x][y].append(claim.cid)


    def s14_final_count(self):
        for x in range(1000):
            for y in range(1000):
                if len(self.biggrid[x][y]) > 1:
                    for badcid in self.biggrid[x][y]:
                        self.cidset.discard(badcid)


    def s20_success_complete(self):
        pass    

        
        
    