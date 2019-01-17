import json
import string
from collections import deque, Counter

import utility as U
from finite_state import *





class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {   
            "HAR" : "F:SC",
            "HAC": "T:SIP",
            "PXV" : "HAC",
            "PYV" : "HAR"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        
        self.xvals = None
        self.yvals = None

        self.serial_number = 57

    def get_result(self):
        
        results = []

        for xpt in range(1, 301):
            for ypt in range(1, 301):
                results.append((xpt, ypt, self.calc_square_total(xpt, ypt)))


        results = sorted(results, key=lambda x: -x[2])

        print(results[0])

        return results[0]


    def calc_square_total(self, xpt, ypt, showsquare=False):

        total = 0

        for yd in range(3):
            for xd in range(3):
                try: 
                    theval = self.values[xpt+xd][ypt+yd]
                    total += theval

                    if showsquare:
                        print("{0: >4}".format(theval), end='')
                        
                except IndexError:
                    pass

            if showsquare:
                print("")

        return total



    def s1_init_machine(self):

        assert self.serial_number != None, "You must set the serial number"

        # Use 301 here so that we don't have to futz around with 0/1 indexing
        # Use magic number so you know you screwed up if you try to index it
        self.values = [[-12345678 for _ in range(301)] for _ in range(301)]

        self.yvals = deque(range(1, 301))


    def s3_have_another_row(self):
        return len(self.yvals) > 0



    def s4_prepare_column(self):
        self.xvals = deque(range(1, 301))


    def s5_have_another_col(self):
        return len(self.xvals) > 0

    def s6_poll_y_value(self):
        self.yvals.popleft()



    def get_current_rack_id(self):
        return self.xvals[0] + 10

    def s8_set_initial_power(self):
        self.power = self.get_current_rack_id() * self.yvals[0]

    def s9_add_serial_number(self):
        self.power += self.serial_number

    def s10_multiply_by_rack_id(self):
        self.power *= self.get_current_rack_id()

    def s11_keep_hundreds_digit(self):
        pstr = str(self.power)
        assert len(pstr) >= 3

        # Sweet negative indexing technology
        hundreds = pstr[-3:-2]
        self.power = int(hundreds)

    def s12_subtract_five(self):
        self.power -= 5

    def s13_set_result(self):
        
        # This is the final result
        self.values[self.xvals[0]][self.yvals[0]] = self.power

    def s14_poll_x_value(self):
        # Poll xval Q
        self.xvals.popleft()

    def s30_success_complete(self):
        pass    

        

def run_tests():

    """
    testdata = [[122, 79, 57, -5], [217,196,39,0], [101,153,71,4]]

    for xval, yval, snum, expect in testdata:

        pmachine = PMachine()
        pmachine.serial_number = snum
        pmachine.run2_completion()
        assert pmachine.values[xval][yval] == expect
    
        print("Got value {} as expected".format(expect))   
    """     
    

    nextdata = [[21, 61, 42, 30], [33,45, 18, 29]]

    for xval, yval, snum, expect in nextdata:

        pmachine = PMachine()
        pmachine.serial_number = snum
        pmachine.run2_completion()
        result = pmachine.calc_square_total(xval, yval, showsquare=True)
        assert result == expect
        print("Got value {}={} as expected".format(result, expect))     

