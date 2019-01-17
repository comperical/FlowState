import json
import copy
from collections import deque

import utility as U
from finite_state import *

# Re-use function opcodes
import p16b


def dumbfactors(mynumber):

    for f in range(1, mynumber+1):
        if mynumber % f == 0:
            yield f

def numpairs(r4):

    """
    hit = 0

    for idx in range(1, r4+1):
        for jdx in range(1, r4+1):
            if idx * jdx == r4:
                print("got hit i={} * j={} = {}".format(idx, jdx, r4))
                hit += idx

    return hit
    """

    return sum(dumbfactors(r4))


class Instruction:

    def __init__(self, istr):

        toks = istr.split()
        self.opcode = toks[0].strip()
        assert self.opcode in p16b.MAIN_OP_MAP

        self.aval = int(toks[1])
        self.bval = int(toks[2])
        self.cval = int(toks[3])

    def __str__(self):
        return "{} {} {} {}".format(self.opcode, self.aval, self.bval, self.cval)


    def execute(self, registers):
        opfunc = p16b.MAIN_OP_MAP[self.opcode]
        newc = opfunc(registers, self.aval, self.bval)
        registers[self.cval] = newc

class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "IIP" : "PT",
            "PT" : "T:SC",
            "SFC" : "T:SSFI"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))

        self.registers = [0] * 6

        self.ip_binding = 1

        self.instr_ptr = 0

        self.instructions = []

        self.is_test = False


    def get_result(self):
        return self.registers[0]


    def s1_init_machine(self):

        infile = 'p19test' if self.is_test else 'p19'

        lines = U.read_input_deque(infile)

        binding = lines.popleft()
        assert binding.startswith("#ip")
        self.ip_binding = int(binding[3:])

        # remaining lines are the instructions
        for ln in lines:
            inst = Instruction(ln)
            assert str(inst) == ln
            self.instructions.append(inst)

        print("Got IP binding = {} and {} lines of instructions".format(self.ip_binding, len(self.instructions)))

        for idx, inst in enumerate(self.instructions):
            print("{} --> {}".format(idx, inst))



    def s4_program_terminates(self):
        return self.instr_ptr < 0 or self.instr_ptr >= len(self.instructions)


    def s5_smart_fast_check(self):
        return self.step_count > 1e6 and self.instr_ptr == 8

    def s6_copy_iptr2_register(self):
        self.registers[self.ip_binding] = self.instr_ptr

    def s7_execute_instruction(self):
        logline = "ip={} {} ".format(self.instr_ptr, str(self.registers))

        curinst = self.instructions[self.instr_ptr]
        logline += str(curinst)

        curinst.execute(self.registers)
        logline += " " + str(self.registers)

        #print(logline)

    def s8_copy_register2_iptr(self):
        self.instr_ptr = self.registers[self.ip_binding]


    def s12_increment_inst_ptr(self):
        self.instr_ptr += 1


    def s25_set_smart_fast_info(self):

        print("Registers are {}, setting smart fast".format(self.registers))

        assert self.registers[0] == 0, "Expected nothing in register 0"
        r4 = self.registers[4]

        npairs = numpairs(r4)

        print("Got value of {} for npair r4={}".format(npairs, r4))
        self.registers[0] = npairs

    def s30_success_complete(self):
        pass


def run_tests():
    
    assert list(dumbfactors(8)) == [1, 2, 4, 8]
    assert list(dumbfactors(9)) == [1, 3, 9]
    assert list(dumbfactors(12)) == [1, 2, 3, 4, 6, 12]
    assert list(dumbfactors(25)) == [1, 5, 25]
    assert list(dumbfactors(100)) == [1, 2, 4, 5, 10, 20, 25, 50, 100]

    assert numpairs(970) == 1764


    pmachine = PMachine()
    pmachine.is_test = True
    pmachine.run2_completion()
    assert pmachine.get_result() == 6
    