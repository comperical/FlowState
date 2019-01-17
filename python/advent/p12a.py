import json
import string
from functools import reduce
from collections import deque, Counter

import utility as U
from finite_state import *

def status2_code(statstr):
    assert len(statstr) == 5
    assert statstr.replace('#', '').replace('.', '') == ''

    binform = statstr.replace('#', '1').replace('.', '0')
    return int(binform, 2)


class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {   
            "HAI" : "F:CG",
            "HAG" : "T:PPI",
            "NGC" : "HAI"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        
        self.curgen = set()
        self.nxtgen = set()

        self.curidx = -3

        self.generation = 0
        self.max_generation = 1000000

        self.is_test = False

    def get_result(self):
        return sum(self.curgen)

    def get_window_status(self, anidx):

        def plantstr(p):
            return '#' if p in self.curgen else '.'

        return "".join([plantstr(d+anidx) for d in range(-2, +3)])

    def load_initial_state(self, inline):
        assert inline.startswith("initial state:")
        marks = inline[len("initial state:"):].strip()

        for idx, c in enumerate(marks):
            assert c in ['.', '#']
            if c == '#':
                self.curgen.add(idx)

        #print("Cur gen is {}".format(self.curgen))


    def load_plants_grow(self, inputs):

        def procline(s):
            codestr, result = s.split("=>")
            codeint = status2_code(codestr.strip())            
            assert result.strip() in ['#', '.']
            return codeint, result.strip() == '#'

        self.plants_grow = dict([procline(inp) for inp in inputs])

        for code in range(0, 32):
            if not code in self.plants_grow:
                assert self.is_test
                self.plants_grow[code] = False

        print(self.plants_grow)

    def s1_init_machine(self):

        inputfile = 'p12test' if self.is_test else 'p12'
        inputs = U.read_input_deque(inputfile)

        self.load_initial_state(inputs.popleft())
        blankstr = inputs.popleft()
        assert blankstr.strip() == ''

        self.load_plants_grow(inputs)

    def s3_print_plant_info(self):


        assert len(self.curgen) > 0, "Generation died!!!"

        #minidx = min(self.curgen)-3
        #maxidx = max(self.curgen)+3


        minidx = -3 if self.is_test else min(self.curgen)-3
        maxidx = 37 if self.is_test else max(self.curgen)+3

        print("{0: <2}: ".format(self.generation), end='')

        for idx in range(minidx, maxidx):
            c = '#' if idx in self.curgen else '.'
            print(c, end='')

        print("")

    def s5_reset_index(self):
        self.curidx = min(self.curgen)-3

    def s10_have_another_index(self):
        return self.curidx < max(self.curgen)+3

    def s11_increment_index(self):
        self.curidx += 1

    def s12_next_gen_calc(self):
        
        winstat = self.get_window_status(self.curidx)
        wincode = status2_code(winstat)

        grow = self.plants_grow.get(wincode, None)
        assert grow != None 

        if grow:
            self.nxtgen.add(self.curidx)


    def s15_cycle_generation(self):
        self.curgen = self.nxtgen
        self.nxtgen = set()

        self.generation += 1

    def s16_have_another_generation(self):
        return self.generation < self.max_generation

    def s30_success_complete(self):
        pass    

        

def run_tests():

    statmap = {'.....': 0, '#####' : 31, '..#..': 4, '#.#..': 20 }

    for k, v in statmap.items():
        assert status2_code(k) == v
        print("confirmed K={} --> V={}".format(k, v))

    pmod = PMachine()
    pmod.is_test = True
    pmod.run2_completion()
    assert pmod.get_result() == 325
    print("Confirmed test result of {}".format(pmod.get_result()))



    """
    testdata = [[122, 79, 57, -5], [217,196,39,0], [101,153,71,4]]

    for xval, yval, snum, expect in testdata:

        pmachine = PMachine()
        pmachine.serial_number = snum
        pmachine.run2_completion()
        assert pmachine.values[xval][yval] == expect
    
        print("Got value {} as expected".format(expect))   
    

    nextdata = [[21, 61, 42, 30], [33,45, 18, 29]]

    for xval, yval, snum, expect in nextdata:

        pmachine = PMachine()
        pmachine.serial_number = snum
        pmachine.run2_completion()
        result = pmachine.calc_square_total(xval, yval, showsquare=True)
        assert result == expect
        print("Got value {}={} as expected".format(result, expect))  
    """     


