import json
import copy
import hashlib

from functools import reduce
from collections import deque
from collections import Counter

import utility as U
from finite_state import *

class ReBlock:

    def __init__(self, btype, prnt=None, step=None):

        assert btype in ['OR', 'AND', 'S']
        assert (btype == 'S') == (step != None)

        self.btype = btype
        self.step = step
        self.kids = None if btype == 'S' else []

        self.parent = prnt

    def new_kid(self, btype, step=None):
        assert self.btype != 'S'
        nkid = ReBlock(btype, prnt=self, step=step)
        self.kids.append(nkid)
        return nkid

    def countpaths(self):
        if self.btype == 'S':
            return 1

        kidpaths = [k.countpaths() for k in self.kids]

        # Sum
        if self.btype == 'OR':
            return sum(kidpaths)

        # Product
        return reduce(lambda a,b : a*b, kidpaths, 1)


    def enumerate(self):

        if self.btype == 'S':
            return self.step

        if self.btype == 'OR':
            for k in self.kids:
                for sub in k.enumerate():
                    yield sub

            return





    def serialize(self):

        if self.btype == 'S':
            return self.step

        kidser = [k.serialize() for k in self.kids]

        if self.btype == 'AND':
            return "".join(kidser)

        return '(' + "|".join(kidser) + ')'


class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {

        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))

        self.test_code = None


    def get_result(self):
        pass

    def s1_init_machine(self):

        infile = 'p20test' + self.test_code if self.test_code != None else 'p20'
        lines = U.read_input_deque(infile)

        self.regexstr = lines[0]
        assert self.regexstr[0] == '^' and self.regexstr[-1] == '$'

        self.tokens = deque([c for c in self.regexstr])
        self.tokens.popleft()
        self.tokens.pop()

        self.curblock = ReBlock('AND')

    def s6_have_another_input(self):
        return len(self.tokens) > 0

    def s10_next_is_open(self):
        return self.tokens[0] == '('


    def s11_handle_open(self):
        self.curblock = self.curblock.new_kid('OR')
        self.curblock = self.curblock.new_kid('AND')

    def s14_next_is_close(self):
        return self.tokens[0] == ')'


    def s15_handle_close(self):
        assert self.curblock.btype == 'AND'
        self.curblock = self.curblock.parent

        assert self.curblock.btype == 'OR'
        self.curblock = self.curblock.parent


    def s18_next_is_pipe(self):
        return self.tokens[0] == '|'

    def s19_handle_pipe(self):
        assert self.curblock.parent.btype == 'OR'
        self.curblock = self.curblock.parent.new_kid('AND')

    def s20_handle_basic_move(self):
        assert self.curblock.btype == 'AND'
        self.curblock.new_kid('S', step=self.tokens[0])


    def s22_poll_input_token(self):
        self.tokens.popleft()


    def s28_input_sanity_check(self):
        #assert not self.curblock.is_leaf(), "Somehow ended up on an input leaf"
        assert self.curblock.parent == None, "Failed to return to root node"
        resultstr = '^' + self.curblock.serialize() + '$'

        assert resultstr == self.regexstr

        if self.test_code != None:
            print("Result is:\n{}".format(resultstr))


        totalpaths = self.curblock.countpaths()
        print("Have {} total paths through maze".format(totalpaths))

    def s30_success_complete(self):
        pass


def run_tests():
    
    for tcode in 'ABCDE':
        pmach = PMachine()
        pmach.test_code = tcode
        pmach.run2_completion()
    