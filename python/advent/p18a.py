import json
import copy
from collections import deque
from collections import Counter

import utility as U
from finite_state import *


class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "CT" : "SBI",
            "REP" : "T:SC"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))

        # list of lists
        self.geography = []

        self.minute = 0

        self.target_minute = 10

        self.is_test = False

    def get_result(self):

        rcounter = Counter([c for row in self.geography for c in row])
        return rcounter['|'] * rcounter['#']

    def s1_init_machine(self):

        infile = 'p18test' if self.is_test else 'p18'
        lines = U.read_input_deque(infile)

        for line in lines:
            georow = []
            for c in line:
                georow.append(c)

            self.geography.append(georow)


    def s4_show_board_info(self):

        if not self.is_test:
            return

        print("After minute {}: ".format(self.minute))

        for row in self.geography:
            rowstr = "".join(row)
            print(rowstr)




    def s5_reached_end_point(self):
        return self.minute >= self.target_minute


    def get_adjacency_count(self, idx, jdx):

        tcount = Counter()

        for di in range(-1, +2):
            for dj in range(-1, +2):
                if di == 0 and dj == 0:
                    continue

                if idx+di < 0 or jdx+dj < 0:
                    continue

                try: 
                    terrain = self.geography[idx+di][jdx+dj]
                    tcount.update(terrain)
                except IndexError:
                    pass

        if idx == 0 or jdx == 0:
            assert sum(tcount.values()) <= 5

        return tcount


    def compute_new_state(self, idx, jdx):
        adjcount = self.get_adjacency_count(idx, jdx)
        current = self.geography[idx][jdx]

        #if idx == 2 or idx == 1:
        #    print("For position i={}, j={}, current={}, adjacency={}".format(idx, jdx, current, adjcount))


        if current == '.':
            return '|' if adjcount['|'] >= 3 else '.'

        if current == '|':
            return '#' if adjcount['#'] >= 3 else '|'

        if current == '#':
            acond = adjcount['#'] >= 1 and adjcount['|'] >= 1
            return '#' if acond else '.'

        assert False


    def s10_compose_new_geo(self):

        self.new_geo = [copy.copy(row) for row in self.geography]

        for idx in range(len(self.geography)):
            for jdx in range(len(self.geography[0])):
                newstat = self.compute_new_state(idx, jdx)
                self.new_geo[idx][jdx] = newstat




    def s12_replace_old_with_new(self):

        self.geography = self.new_geo

    def s20_clock_tick(self):
        self.minute += 1

    def s30_success_complete(self):
        pass


def run_tests():
    
    pmachine = PMachine()
    pmachine.is_test = True
    pmachine.run2_completion()
    assert pmachine.get_result() == 1147
    