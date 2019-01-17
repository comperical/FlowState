import json
import copy
from collections import deque

import utility as U
from finite_state import *

# Re-use function opcodes
import p16b

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
            "PT" : "T:SC"

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


    def s30_success_complete(self):
        pass


def run_tests():
    
    pmachine = PMachine()
    pmachine.is_test = True
    pmachine.run2_completion()
    assert pmachine.get_result() == 6
    