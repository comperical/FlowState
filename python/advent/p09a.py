import json
import string
from collections import deque, Counter

import utility as U
from finite_state import *

KNOWN_DATA = { 
        (10, 1618): 8317,
        (13, 7999): 146373,
        (17, 1104): 2764,
        (21, 6111): 54718,
        (30, 5807): 37305,
        # Puzzles
        (424, 71482): -1,
        (424, 7148200): -1
}

#10 players; last marble is worth 1618 points: high score is 8317
##13 players; last marble is worth 7999 points: high score is 146373
#17 players; last marble is worth 1104 points: high score is 2764
#21 players; last marble is worth 6111 points: high score is 54718
#30 players; last marble is worth 5807 points: high score is 37305


class MarbleLink: 


    def __init__(self, mc, after=None):
        self.mcount = mc
        self.leftlink = self
        self.rghtlink = self

        if after != None:
            befor = after.rghtlink
            after.mark_new_rght(self)
            befor.mark_new_left(self)

    def mark_new_left(self, nleft):
        assert nleft != None
        self.leftlink = nleft
        nleft.rghtlink = self

    def mark_new_rght(self, nrght):
        assert nrght != None
        self.rghtlink = nrght
        nrght.leftlink = self

    def remove_me(self):
        self.leftlink.mark_new_rght(self.rghtlink)

        self.leftlink = None
        self.rghtlink = None

class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "IST" : "T:SP",
            "BP" : "IT",
            "GO" : "F:IST"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        
        self.player_turn = 0

        self.current_marble = MarbleLink(0)

        #self.current_marble = 0

        self.marble_count = 1

        self.num_players = None
        self.max_marble = None

        self.scores = {}

        self.chain_size = 1

    def get_result(self):
        return max([c for k,c in self.scores.items()])

    def configure(self, players=10, maxmarble=30):
        self.num_players = players
        self.max_marble = maxmarble

    def s1_init_machine(self):
        assert self.num_players != None, "You must call configure(..) before running machine"

    def s3_is_special_turn(self):
        return self.marble_count % 23 == 0

    def s4_basic_place(self):

        newmarble = MarbleLink(self.marble_count, self.current_marble.rghtlink)
        self.current_marble = newmarble

        #placepos = (self.current_marble + 1) % len(self.marbles)
        #self.marbles.insert(placepos+1, self.marble_count)
        #print("marbles={}".format(self.marbles))
        #self.current_marble = placepos+1

        self.chain_size += 1

        #self.sanity_check()

    def add2_current_player(self, pts):
        self.scores.setdefault(self.player_turn, 0)
        self.scores[self.player_turn] += pts

    def s7_special_place(self):

        # Current player scores current marble
        self.add2_current_player(self.marble_count)

        for _ in range(7):
            self.current_marble = self.current_marble.leftlink

        nextmarb = self.current_marble.rghtlink
        self.current_marble.remove_me()

        self.add2_current_player(self.current_marble.mcount)
        #print("removed marble count {}".format(self.marble_count+removed))
        #print("removed marble at {}::{}".format(remover, removed))
        self.current_marble = nextmarb
        self.chain_size -= 1

        #self.sanity_check()

    def sanity_check(self):

        gimp = self.current_marble
        rlist = []

        for _ in range(self.chain_size):
            rlist.append(gimp.mcount)
            gimp = gimp.rghtlink

        assert gimp == self.current_marble
        llist = []

        for _ in range(self.chain_size):
            llist.append(gimp.mcount)
            gimp = gimp.leftlink

        assert gimp == self.current_marble

    def s10_increment_turn(self):

        #self.show_game_state()

        self.marble_count += 1
        self.player_turn = (self.player_turn + 1) % self.num_players

    def show_game_state(self):

        mystr = "[{}]".format(self.player_turn+1)

        g = self.current_marble
        while g.mcount != 0:
            g = g.leftlink

        for idx in range(self.chain_size):

            m = g.mcount
            g = g.rghtlink

            if m == self.current_marble.mcount:
                mystr = mystr + "({})".format(m)
            else:
                mystr = mystr + " {} ".format(m)

        print(mystr)

    def marbles(self, stepleft=True):
        g = self.current_marble
        for _ in range(self.chain_size):
            yield g.mcount
            g = g.leftlink if stepleft else g.rghtlink


    def s15_game_over(self):
        #return self.marble_count > 30

        #return any([c >= 8317 for k, c in self.scores.items()])
        return self.marble_count > self.max_marble


    def s30_success_complete(self):
        pass    

        
        
    