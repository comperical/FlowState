import json
import time
from collections import deque

import utility as U
from finite_state import *

import p24a


def result_at_boost(boost, tcode, verbose=False):
    alpha = time.time()
    submachine = p24a.PMachine()
    submachine.test_code = tcode
    submachine.verbose = verbose
    submachine.run_until(lambda mach: len(mach.groups) > 0)


    for grp in submachine.groups.values():
        if grp.is_immune():
            grp.attpower += boost

    submachine.run2_completion()
    print("Ran calculation with tcode={}, boost={}, took {} sec".format(tcode, boost, time.time()-alpha))

    if submachine.is_battle_draw():
        print("Got DRAW")
        return False, -10000000

    return submachine.immune_wins(), submachine.get_result()


class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "IIV" : "T:PC",
            "IB" : "IIV"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        
        self.boost_probe = 0

        self.test_code = None

    def get_result(self):
        immwin, fresult = result_at_boost(self.boost_probe, self.test_code)
        assert immwin
        return fresult

    def s1_init_machine(self):
        pass

    def s16_is_immune_victory(self):
        immwin, _ = result_at_boost(self.boost_probe, self.test_code)
        if immwin:
            print("Found immune system win at boost={}".format(self.boost_probe))

        return immwin

    def s20_increment_boost(self):
        self.boost_probe += 1


    def s30_problem_complete(self):
        pass    
    

        
        
def run_tests():
    
    """
    boosts = { 1569: (False, 139), 1570: (True, 51 ) }

    for boost in boosts:
        expwin, exprslt = boosts[boost]

        immunewin, finalresult = result_at_boost(boost, 'A')
        print("For boost={}, have win={}, result={}".format(boost, immunewin, finalresult))        
        assert expwin == immunewin
        assert exprslt == finalresult
    """

    regular = [27]

    for boost in regular:
        immunewin, finalresult = result_at_boost(boost, None)
        print("For boost={}, have win={}, result={}".format(boost, immunewin, finalresult))        


    