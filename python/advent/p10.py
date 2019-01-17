import json
import string
from collections import deque, Counter

import utility as U
from finite_state import *


def parse_pull(r):

    alpha = r.find("<")
    omega = r.find(">")

    xs, ys = r[alpha+1:omega].split(",")
    return (int(xs), int(ys)), r[omega+1:]

class Star:

    def __init__(self, rec):

        self.orig = rec

        self.parse_data()

    def parse_data(self):

        self.pos, subr = parse_pull(self.orig)
        self.vel, _ = parse_pull(subr)
        #print("Got position={}, velocity={}".format(self.pos, self.vel))

    def update_pos(self):
        self.pos = (self.pos[0] + self.vel[0], self.pos[1] + self.vel[1])


class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {   
            "IIP" : "F:SSS",
            "DI" : "F:CT",
            "CT": "IIP",
            "SSP" : "IIP",
            "SSS" : "F:DSP",
            "DSP" : "F:CT"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        
        self.stars = []

        self.seconds = 0

        self.dispersion_log = []

        self.best_dispersion = None

    def get_result(self):
        pass

    def s1_init_machine(self):

        self.load_star_data()

        #print("Read inputs: {}".format(self.inputs))

    def load_star_data(self):

        self.stars = [Star(r) for r in U.read_input_deque('p10')]

    def s3_is_initial_pass(self):
        return self.best_dispersion is None

    def s6_log_dispersion(self):
        self.dispersion_log.append(self.calc_dispersion())

    def s7_dispersion_increasing(self):
        return len(self.dispersion_log) > 100 and self.dispersion_log[-1] > self.dispersion_log[-100]

    def s8_start_second_pass(self):

        self.best_dispersion = min(self.dispersion_log)
        print("Starting second pass, found best dispersion of {}".format(self.best_dispersion))

        self.seconds = 0
        self.load_star_data()


    def s10_clock_tick(self):
        self.seconds += 1

        for s in self.stars:
            s.update_pos()


    def calc_dispersion(self):

        ys = [ s.pos[1] for s in self.stars ]
        xs = [ s.pos[0] for s in self.stars ]

        width = (max(xs) - min(xs))
        hight = (max(ys) - min(ys))

        return width * hight


    def s12_should_show_stars(self):
        curdisp = self.calc_dispersion()
        return abs(curdisp - self.best_dispersion) < 4


    def s13_show_stars(self):

        print("Going to show for second={}:".format(self.seconds))

        posmap = { s.pos : True for s in self.stars }

        ys = [ s.pos[1] for s in self.stars ]
        xs = [ s.pos[0] for s in self.stars ]

        for y in range(min(ys)-5, max(ys)+5):
            for x in range(min(xs)-5, max(xs)+5):
                c = '#' if (x, y) in posmap else '.'
                print(c, end='')
            print("")


    def s20_done_second_pass(self):
        return self.seconds > len(self.dispersion_log)

    def s30_success_complete(self):
        pass    

        
        
    