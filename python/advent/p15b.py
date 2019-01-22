import json
from collections import deque

import utility as U
from finite_state import *

import p15a

class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "ZED" : "T:SC",
            "IB" : "BSM"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        
        self.eboost = 0

        self.test_code = None

    def get_result(self):
        return self.submachine.get_result()

    def s1_init_machine(self):
        pass


    def get_elf_count(self, pmach):
        return sum([creat.ccode == 'E' for creat in pmach.creatures.values() ])

    def s3_calc_initial_elf_count(self):
        calcmachine = p15a.PMachine()
        calcmachine.test_code = self.test_code
        calcmachine.run_until(lambda x: len(x.creatures) > 0)
        self.init_elf_count = self.get_elf_count(calcmachine)
        print("Calculated initial elf count={} for testcode={}".format(self.init_elf_count, self.test_code))

    def s4_build_sub_machine(self):
        
        self.submachine = p15a.PMachine()
        self.submachine.test_code = self.test_code
        self.submachine.elf_boost = self.eboost

    def s6_run_sub_machine(self):
        self.submachine.run2_completion()


    def s10_zero_elf_deaths(self):
        survivors = self.get_elf_count(self.submachine)
        #print("Status is: {}".format(self.submachine.get_health_status()))
        #print("For boost={}, have {} survivors, vs {} initial".format(self.eboost, survivors, self.init_elf_count))
        return self.get_elf_count(self.submachine) == self.init_elf_count

    def s15_increment_boost(self):
        self.eboost += 1


    def s20_success_complete(self):
        pass    
        
        
    
def run_tests():
    
    scores = {}
    knowns = {}
    rpower = {}

    rpower['B'] = 15
    rpower['D'] = 4
    rpower['E'] = 15

    scores['B'] = 4988
    scores['D'] = 31284
    scores['E'] = 3478


    knowns['B'] = """
        #######
        #..E..#
        #...E.#
        #.#.#.#
        #...#.#
        #.....#
        #######
    """

    knowns['D'] = """
        #######
        #.E.E.#
        #.#E..#
        #E.##E#
        #.E.#.#
        #...#.#
        #######
    """

    knowns['E'] = """
        #######
        #.E.#.#
        #.#E..#
        #..#..#
        #...#.#
        #.....#
        #######
    """



    for tcode in scores: 
        pmach = PMachine()
        pmach.test_code = tcode
        pmach.run2_completion()

        p15a.checkboard(pmach.submachine, knowns[tcode])
        #print(pmach.submachine.get_board_string())

        assert pmach.get_result() == scores[tcode], "Machine reported outcome {}, but expected {}".format(pmach.get_result(), scores[tcode])
        assert pmach.eboost+3 == rpower[tcode], "Discrepancy in power for tcode={}".format(tcode)
        print("Test successful for TC={}".format(tcode))


