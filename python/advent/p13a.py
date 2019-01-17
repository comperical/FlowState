import json
from collections import deque

import utility as U
from finite_state import *

TRACKS = """
/\-|+
""".strip()

MOVE_MAP = { 
    '^' : (0, -1), 
    'v' : (0, +1),
    '>' : (+1, 0),
    '<' : (-1, 0)
}

FORWARD_SLASH_TURN = {
    '^' : '>',
    '<' : 'v',
    'v' : '<',
    '>' : '^'
}

LEFT_TURN_MAP = {
    '^' : '<',
    '<' : 'v',
    'v' : '>',
    '>' : '^'
}

class Cart:

    def __init__(self, hd, xp, yp):
        
        self.xpos = xp
        self.ypos = yp

        self.head = hd

        self.turncode = 0

    def get_priority(self):
        return self.ypos * 1000000 + self.xpos

    def update_position(self):
        xup, yup = MOVE_MAP.get(self.head)
        self.xpos += xup
        self.ypos += yup

    def basic_turn(self, trk):

        assert trk == '/' or trk == '\\'
        self.head = FORWARD_SLASH_TURN.get(self.head)

        # Reverse is two left turns
        if trk == '\\':
            for _ in range(2):
                self.left_turn()

    def left_turn(self):
        self.head = LEFT_TURN_MAP.get(self.head)


    def intersection_turn(self):
        assert self.turncode in [0, 1, 2]

        if self.turncode == 0:
            self.left_turn()

        if self.turncode == 2:
            for _ in range(3):
                self.left_turn()

        self.turncode += 1
        self.turncode = 0 if self.turncode == 3 else self.turncode



class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "HAC" : "F:NR",
            "IBB" : "F:II",
            "BCT" : "PCI",
            "PCI" : "HAC",
            "IT" : "PCI",
            "TMR" : "F:SBS",
            "II" : "F:PCI",
            "CC" : "T:SCI"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        self.is_test = False


    def get_result(self):
        ccart = self.get_current_cart()
        return ccart.xpos, ccart.ypos

    def s1_init_machine(self):
        
        self.carts = {}
        self.track = []

        # Call these "rounds" because "turn" already in use
        self.round_count = 0

    def s2_read_input(self):
        
        inputfile = 'p13test' if self.is_test else 'p13'
        inputs = U.read_input_deque(inputfile, dostrip=False)

        while len(inputs) > 0:
            gridline = inputs.popleft()
            gridline = gridline.replace('\n', '')
            row = []

            if len(gridline.strip()) == 0:
                continue

            for c in gridline:

                if c == ' ' or c in TRACKS:
                    row.append(c)
                    continue

                if c in 'v^<>':

                    self.carts[len(self.carts)] = Cart(c, len(row), len(self.track))

                    track = '|' if c in 'v^' else '-'
                    row.append(track)
                    continue

                assert False, "Bad track character _{}_".format(c)

            self.track.append(row)



        checkset = set([len(r) for r  in self.track])
        assert len(checkset) == 1, "Have length set {}".format(checkset)


    def s5_show_board_state(self):
        self.print_board_info()

    def print_board_info(self):

        if not self.is_test:
            return 

        print("Board state on round {}".format(self.round_count))

        for y in range(len(self.track)):
            for x in range(len(self.track[0])):

                c = self.track[y][x]
                hits = [cart for cart in self.carts.values() if cart.xpos == x and cart.ypos == y]

                assert len(hits) <= 2, "Got MORE THAN 2 carts at x/y={}/{}".format(x, y)

                if len(hits) == 2:
                    c = 'X'
                if len(hits) == 1:
                    c = hits[0].head

                print(c, end='')
            print("")

    def get_current_cart(self):
        return self.carts[self.cart_ids[0]]

    def get_current_track(self):
        curcart = self.get_current_cart()
        trk = self.track[curcart.ypos][curcart.xpos]
        assert trk in TRACKS, "Bad track code _{}_ for cart at {}/{}".format(trk, curcart.xpos, curcart.ypos)
        return trk        

    def s6_init_cart_ids(self):

        ids = [idx for idx in self.carts]
        ids = sorted(ids, key=lambda id: self.carts[id].get_priority())
        self.cart_ids = deque(ids)

    def s8_have_another_cart(self):
        return len(self.cart_ids) > 0


    def s10_update_cart_pos(self):
        self.get_current_cart().update_position()

    def s11_check_collision(self):
        priset = set([cart.get_priority() for cart in self.carts.values()])
        return len(priset) < len(self.carts)


    def s12_is_basic_bend(self):
        trk = self.get_current_track()
        return trk == '/' or trk == '\\'

    def s13_basic_cart_turn(self):
        trk = self.get_current_track()        
        self.get_current_cart().basic_turn(trk)

    def s16_is_intersection(self):
        return self.get_current_track() == '+'

    def s17_intersection_turn(self):
        self.get_current_cart().intersection_turn()

    def s18_poll_cart_id(self):
        self.cart_ids.popleft()

    def s22_next_round(self):
        self.round_count += 1

    def s23_too_many_rounds(self):
        return self.round_count > 10000

    def s29_fail_complete(self):
        pass 

    def s30_show_collision_info(self):
        self.print_board_info()

    def s31_success_complete(self):
        pass    
    
   


def run_tests():
    
    pmod = PMachine()
    pmod.is_test = True
    pmod.run2_completion()
    assert pmod.get_result() == (7, 3)

        
        
    