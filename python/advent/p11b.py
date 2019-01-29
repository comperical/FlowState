import json
import string
from collections import deque, Counter

import utility as U
from finite_state import *


class IntgImage:

    def __init__(self, values):

        S = len(values)
        assert S == len(values[0]), "Only works for squares"

        #self.image = [[0] * S] * S

        self.image = []

        while len(self.image) < S:
            self.image.append([None] * S)

        self.store = values

        self.query_lookup_result(S-1, S-1)


    def query_lookup_result(self, idx, jdx):

        if idx < 0 or jdx < 0:
            return 0

        if self.image[idx][jdx] == None:
            left = 0 if jdx == 0 else self.query_lookup_result(idx, jdx-1)
            lowr = 0 if idx == 0 else self.query_lookup_result(idx-1, jdx)
            rduc = 0 if (idx == 0 or jdx == 0) else self.query_lookup_result(idx-1, jdx-1)
            vlue = self.store[idx][jdx]
            self.image[idx][jdx] = left+lowr-rduc+vlue

        return self.image[idx][jdx]


    def show_image(self, myinfo):

        if len(myinfo) == 0:
            print("EMPTY")

        for imrow in myinfo:
            print(imrow, end='')

            #print(", ".join([str(c) for c in imrow]), end='')
            print("")

    def fast_calc(self, lowpt, xwidth, ywidth):

        A = self.get_integ_value(lowpt[0]-1, lowpt[1]-1)
        B = self.get_integ_value(lowpt[0]-1+xwidth, lowpt[1]-1)
        C = self.get_integ_value(lowpt[0]-1, lowpt[1]-1+ywidth)
        D = self.get_integ_value(lowpt[0]+xwidth-1, lowpt[1]+ywidth-1)

        return D + A - B - C

    def get_integ_value(self, idx, jdx):
        if idx < 0 or jdx < 0:
            return 0
        return self.image[idx][jdx]


    def slow_calc(self, lowpt, xwidth, ywidth):

        csum = 0

        for idx in range(lowpt[0], lowpt[0]+xwidth):
            for jdx in range(lowpt[1], lowpt[1]+ywidth):
                csum += self.store[idx][jdx]

        return csum


class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {   
            "HAR" : "F:BII",
            "HAC": "T:SIP",
            "PXV" : "HAC",
            "PYV" : "HAR"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        
        self.xvals = None
        self.yvals = None

        self.serial_number = 2568

    def get_result(self):
        
        results = []

        for idx in range(1, 301):
            for jdx in range(1, 301):
                for sze in range(1, 301):
                    if idx + sze > 301 or jdx + sze > 301:
                        continue

                    thesum = self.intimage.fast_calc((idx, jdx), sze, sze)
                    results.append(((idx, jdx, sze), thesum))

        results = sorted(results, key=lambda x: -x[1])
        return results[0][0]

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
        self.values = []

        while len(self.values) < 301:
            onerow = [-12345678 for _ in range(301)]
            self.values.append(onerow)

        #self.values = [[-12345678 for _ in range(301)] for _ in range(301)]

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

    def s18_build_intregral_image(self):
        self.intimage = IntgImage(self.values)

    def s30_success_complete(self):
        pass    


def mini_image_test():

    values = [[1, 1], [1, 1]]

    iimage = IntgImage(values)

    print(iimage.image)

    assert iimage.image[1][1] == 4


def integ_image_test():

    import random

    S = 100

    values = []
    for _ in range(S):
        values.append([0] * S)

    for idx in range(S):
        for jdx in range(S):
            values[idx][jdx] = random.randint(0, 100)
            #values[idx][jdx] = 1


    iimage = IntgImage(values)

    for n in range(1000):
        lowpt = (random.randint(0, S/2), random.randint(0, S/2))
        width = random.randint(0, S/2-1)
        hight = random.randint(0, S/2-1)

        #print("Calculating for pt={}, width={}, hight={}".format(lowpt, width, hight))
        fcalc = iimage.fast_calc(lowpt, width, hight)
        scalc = iimage.slow_calc(lowpt, width, hight)

        assert fcalc == scalc, "Fast calc produced {}, but slow produced {}".format(fcalc, scalc)

        
    print("Checked {} queries".format(1000))


def run_tests():

    #mini_image_test()

    #integ_image_test()

    testdata = [(18, (90, 269, 16)), (42, (232, 251, 12))]

    for snum, expect in testdata:

        pmachine = PMachine()
        pmachine.serial_number = snum
        pmachine.run2_completion()

        result = pmachine.get_result()
        print("For serial={}, expected {}, observed {}".format(snum, expect, result))
        assert result == expect
    




