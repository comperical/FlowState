import json
import time
import sys
from collections import deque

import utility as U
from finite_state import *

class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "FTS" : "F:PRI"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        self.is_test = False
        self.target_sequence = "760221"

        self.recipes = bytearray([3, 7])

        self.elf1 = 0
        self.elf2 = 1


    def get_result(self):
        return len(self.recipes) - len(self.target_sequence)

    def get_result_at(self, tg):
        assert tg + 10 < len(self.recipes), "Requested TG={} but only have {} recipes".format(tg, len(self.recipes))
        return "".join([str(r) for r in self.recipes[tg:tg+10]])

    def s1_init_machine(self):
        self.tseq_list = [int(c) for c in self.target_sequence]

    def s3_print_recipe_info(self):

        if len(self.recipes) >= 30 or not self.is_test:
            return

        for idx, r in enumerate(self.recipes):
            sp = " {} ".format(r)
            if idx == self.elf1:
                sp = "({})".format(r)
            elif idx == self.elf2:
                sp = "[{}]".format(r)
            print(sp, end='')

        print("")

    def s4_add_new_recipes(self):

        rsum = self.recipes[self.elf1] + self.recipes[self.elf2]

        for c in str(rsum):
            self.recipes.append(int(c))


    def s6_advance_elves(self):
        def newpos(p):
            np = p + self.recipes[p] + 1
            return np % len(self.recipes)

        self.elf1 = newpos(self.elf1)
        self.elf2 = newpos(self.elf2)

    def get_current_suffix(self):
        suffix = self.recipes[-len(self.target_sequence):]
        return "".join([str(r) for r in suffix])

    def slow_suffix_check(self):    
        return self.get_current_suffix() == self.target_sequence

    def fast_prefix_check(self):
        for d in range(len(self.tseq_list)):
            p = len(self.recipes)-len(self.tseq_list) + d

            if p < 0:
                return False

            if self.recipes[p] != self.tseq_list[d]:
                return False

            if d == 3 and not self.is_test:
                csuff = self.get_current_suffix()
                print("Got suffix {}, target is {}, #recipe={}, memory={}".format(csuff, self.target_sequence, len(self.recipes), sys.getsizeof(self.recipes)))

        return True


    def s15_found_target_sequence(self):
        return self.fast_prefix_check()

    def s30_success_complete(self):
        pass    
    


def run_tests():
    
    testmap = { '51589' : 9, '01245': 5, '92510': 18, '59414': 2018 }

    for tseq, expd in testmap.items():
        pmod = PMachine()
        pmod.is_test = True
        pmod.target_sequence = tseq
        pmod.run2_completion()
        rslt = pmod.get_result()
        print("For Tseq={}, expected {} and got {}".format(tseq, expd, rslt))

    """
    scount = 10000000
    alpha = time.time()
    timemod = PMachine()
    timemod.run2_step_count(scount)
    print("Ran {} steps, took {:.03f} secs".format(scount, time.time()-alpha))
    """



    