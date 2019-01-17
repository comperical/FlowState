import json
import copy
from collections import deque

import utility as U
from finite_state import *

# Re-use function opcodes
import p16b

from p21a import Instruction


def get_result_alternate():

    mysim = elf_code_sim()
    foundokay = False
    rlog = {}

    for _ in range(1000000):
        iptr, regs = next(mysim)
        item = tuple(regs + [iptr])

        if item in rlog:
            print("Found cycle after {} yields".format(len(rlog)))
            foundokay = True
            break

        rlog[item] = len(rlog)

    assert foundokay, "Failed to find cycle"

    r4map = {}
    lastobserve = None
    for item in rlog:
        if item[-1] != 28:
            continue

        r4val = item[4]
        if r4val not in r4map:
            r4map[r4val] = len(r4map)
            lastobserve = r4val
            print("Last observed r4 is {}".format(r4val))

    return lastobserve


def elf_code_sim():

    r0 = 0
    r1 = 0
    r2 = 0
    r3 = 0 
    r4 = 0
    r5 = 0

    doinitial = True
    r4 = 0 

    while True: # Line 5

        if doinitial:
            r3 = r4 | 65536
            r4 = 10552971
            doinitial = False

        yield (8, [r0, r1, r2, r3, r4, r5])

        r5 = 255 & r3 # line 8
        r4 += r5

        r4 &= 16777215
        r4 *= 65899
        r4 &= 16777215

        yield (13, [r0, r1, r2, r3, r4, r5])

        if 256 > r3:

            # This is the line that matters, in terms of the actual solution output.
            # the solution will be the LATEST value of r4 that appears here, before a cycle occurs.
            yield (28, [r0, r1, r2, r3, r4, r5])
            if r4 == r0:
                return (-1, [])

            r5 = 0
            doinitial = True
            continue

        r5 = 0        
        while True:
            if (r5+1)*256 > r3:
                r2 = 1
                break

            r5 += 1

        r3 = r5

        yield (27, [r0, r1, r2, r3, r4, r5])



class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "HLP" : "F:PT",
            "IIP" : "HLP",
            "PT" : "T:SC",
            "CAS" : "CSL",
            "CSL" : "T:SC",
            "MSL" : "PT"

        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))

        self.registers = [0] * 6

        self.ip_binding = 1

        self.instr_ptr = 0

        self.instructions = []

        self.is_test = False

        self.log_points = [8, 13, 27]

        self.simulator = elf_code_sim()

        self.hash_log = set()

    def get_result(self):
        return self.registers[4]


    def s1_init_machine(self):

        #infile = 'p19test' if self.is_test else 'p19'
        infile = 'p21'

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

        #for idx, inst in enumerate(self.instructions):
        #    print("{} --> {}".format(idx, inst))



    def s2_hit_log_point(self):

        return self.instr_ptr in self.log_points


    def s3_check_against_sim(self):

        instpt, regs = next(self.simulator)
        regs[1] = self.registers[1]

        #print("Simulator gave: IP={}, regs={}".format(instpt, regs))
        #print("Machine    has: IP={}, regs={}".format(self.instr_ptr, self.registers))

        assert self.instr_ptr == instpt and self.registers == regs


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


    def compute_state_hash(self):
        return hash(tuple(self.registers))

    def s16_check_state_log(self):
        shash = self.compute_state_hash()
        if shash in self.hash_log:
            print("Success, found state cycle")

        return shash in self.hash_log

    def s18_mark_state_log(self):
        shash = self.compute_state_hash()
        self.hash_log.add(shash)

        if len(self.hash_log) % 100 == 0:
            print("Hash Log size is {}".format(len(self.hash_log)))


    def s30_success_complete(self):
        pass


def run_tests():
    
    pass
    