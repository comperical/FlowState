import json
from collections import deque

import utility as U
from finite_state import *

class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "HER" : "F:PRI"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        self.is_test = False
        self.recipe_goal = 760221

        self.recipes = [3, 7]

        self.elf1 = 0
        self.elf2 = 1


    def get_result(self):
        return self.get_result_at(self.recipe_goal)

    def get_result_at(self, tg):
        assert tg + 10 < len(self.recipes), "Requested TG={} but only have {} recipes".format(tg, len(self.recipes))
        return "".join([str(r) for r in self.recipes[tg:tg+10]])

    def s1_init_machine(self):
        pass

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


    def s15_have_enough_recipes(self):
        return len(self.recipes) > self.recipe_goal + 20

    def s30_success_complete(self):
        pass    
    


def run_tests():
    
    testmap = { 9 : "5158916779", 5: "0124515891", 18: "9251071085", 2018:  "5941429882" }
    pmod = PMachine()
    pmod.is_test = True
    pmod.recipe_goal = 4000
    pmod.run2_completion()    

    for tg, expd in testmap.items():
        rslt = pmod.get_result_at(tg)
        print("For TG={} expected {} and got {}".format(tg, expd, rslt))
        assert expd == rslt

    