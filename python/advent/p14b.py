import json
import time
import sys
from collections import deque

import utility as U
from finite_state import *


class Recipe:


    def __init__(self, rval):
        self.value = rval

        self.idxpos = None
        self.next = None
        self.prev = None

        self.fast_jump = None

    def fastappend(self, nextrec):
        assert nextrec.next == None
        assert self.next == None
        self.next = nextrec

        nextrec.idxpos = self.idxpos+1
        nextrec.prev = self

class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "SPCS" : "F:PRI",
            "FPCS" : "T:SC",
            "HTNR" : "F:ABR"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))

        self.is_test = False
        self.target_sequence = "760221"

        self.recipe_head = Recipe(3)
        self.recipe_head.idxpos = 0
        self.recipe_tail = self.recipe_head
        self.append_recipe(7)

        self.elf1 = self.recipe_head
        self.elf2 = self.recipe_tail


    def recipe_count(self):
        return self.recipe_tail.idxpos + 1

    def get_result(self):
        self.print_recipes()

        return self.recipe_count() - len(self.target_sequence)

    def s1_init_machine(self):
        self.tseq_list = [int(c) for c in self.target_sequence]

    def s3_print_recipe_info(self):
        self.print_recipes()

    def print_recipes(self):
        if self.recipe_tail.idxpos >= 30 or not self.is_test:
            return

        ptr = self.recipe_head

        while ptr != None:
            sp = " {} ".format(ptr.value)
            if ptr == self.elf1:
                sp = "({})".format(ptr.value)
            elif ptr == self.elf2:
                sp = "[{}]".format(ptr.value)
            print(sp, end='')

            ptr = ptr.next

        print("")


    def s4_have_two_new_recipes(self):
        rsum = self.elf1.value + self.elf2.value
        return rsum >= 10

    def s5_add_first_recipe(self):
        rsum = self.elf1.value + self.elf2.value
        self.append_recipe(rsum // 10)


    def s8_first_pass_check_solution(self):
        return self.fast_prefix_check()


    def s10_add_basic_recipe(self):
        rsum = self.elf1.value + self.elf2.value
        self.append_recipe(rsum % 10)



    def append_recipe(self, rc):
        newnode = Recipe(int(rc))
        self.recipe_tail.fastappend(newnode)
        self.recipe_tail = self.recipe_tail.next


    def jump_to_next(self, orig):
        if orig.fast_jump != None:
            return orig.fast_jump

        cycled = False
        gimp = orig
        #numstep = orig.idxpos + orig.value + 1  
        numstep = orig.value + 1      

        for _ in range(numstep):
            if gimp.next != None:
                gimp = gimp.next
                continue

            gimp = self.recipe_head
            cycled = True


        if not cycled:
            # Log the jump result, IF we didn't cycle
            orig.fast_jump = gimp

        return gimp


    def s18_advance_elves(self):

        #self.elf1 = newpos(self.elf1)
        #self.elf2 = newpos(self.elf2)

        self.elf1 = self.jump_to_next(self.elf1)
        self.elf2 = self.jump_to_next(self.elf2)

        #self.elf1 = self.slow_index_jump(self.elf1)
        #self.elf2 = self.slow_index_jump(self.elf2)

    def slow_index_jump(self, elf):
        np = elf.idxpos + elf.value + 1
        np = np % (self.recipe_tail.idxpos+1)
        return self.slow_index_lookup(np)

    def slow_index_lookup(self, idx):
        ptr = self.recipe_head

        for _ in range(idx):
            ptr = ptr.next

        return ptr


    def get_current_suffix(self):

        ptr = self.backup_from_tail(len(self.target_sequence)-1)
        suffix = ""

        for _ in range(len(self.target_sequence)):
            suffix += str(ptr.value)

            if ptr.next == None:
                break 

            ptr = ptr.next

        return suffix


    def slow_suffix_check(self):    
        return self.get_current_suffix() == self.target_sequence


    def backup_from_tail(self, numstep):
        ptr = self.recipe_tail

        for _ in range(numstep):
            if ptr.prev == None:
                break 
            ptr = ptr.prev

        return ptr

    def fast_prefix_check(self):


        if self.recipe_count() < len(self.tseq_list):
            return False

        ptr = self.recipe_tail
        checkseq = copy.copy(self.tseq_list)
        checkseq.reverse()

        for idx, cseq in enumerate(checkseq):
            if cseq != ptr.value:
                return False

            if idx == len(self.tseq_list)-2:
                csuffix = self.get_current_suffix()
                print("Have {} recipes, current suffix is {}".format(self.recipe_count(), csuffix))

            ptr = ptr.prev

        return True

    def s20_second_pass_check_solution(self):
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



    