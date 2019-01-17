import json
import heapq
from collections import deque

import utility as U
from finite_state import *

# Very important: this is in READING ORDER
#STEP_LIST = ((0, -1), (-1, 0), (+1, 0), (0, +1))

STEP_LIST = ((0, -1), (-1, 0), (+1, 0), (0, +1))


def reading_order(pt):
    return pt[1] * 100000 + pt[0]

def min_and_max(coords):
    return min(coords), max(coords)

def adjacents(pt):
    for step in STEP_LIST:
        newpt = (pt[0]+step[0], pt[1]+step[1])
        yield newpt, step


def find_path(obstacles, targets, startpt):

    def successors(pt):
        return [npt for npt, _ in adjacents(pt) if npt not in obstacles]

    def isgoal(pt):
        return any([npt in targets for npt, _ in adjacents(pt)])

    goal, parents = U.state_search(startpt, successors, isgoal, breadth=True)

    if goal == None:
        return None

    path = U.extract_path(goal, parents)

    return path

class Creature:

    def __init__(self, cid, cc, xp, yp, elf_boost=0):
        assert cc in ['G', 'E']

        self.cid = cid
        self.xpos = xp
        self.ypos = yp
        self.ccode = cc

        self.health = 200
        self.attack_pow = 3

        # Modification for problem B
        if self.ccode == 'E':
            self.attack_pow += elf_boost


    def get_position(self):
        return (self.xpos, self.ypos)

    def enemy_code(self):
        return 'G' if self.ccode == 'E' else 'E'

    def get_priority(self):
        return reading_order((self.xpos, self.ypos))

    def single_step(self, step):
        assert step in STEP_LIST, "Invalid step {}".format(step)
        self.xpos += step[0]
        self.ypos += step[1]


    def step2_point(self, pt):
        assert abs(pt[0] - self.xpos) + abs(pt[1] - self.ypos) == 1
        self.xpos = pt[0]
        self.ypos = pt[1]

    def distance_to_creature(self, other):
        return abs(self.xpos - other.xpos) + abs(self.ypos - other.ypos)

    def attack_enemy(self, enemy):
        assert self.ccode != enemy.ccode,  "Friendly fire!!!"
        enemy.health -= self.attack_pow


class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "ECM" : "ACM",
            "HAC" : "F:ET",
            "EIR" : "T:AE",
            "HDC" : "F:ECM",
            "HAT" : "F:ECM",
            "RD" : "ECM",
            "AE" : "HDC",
            "ET" : "ITO",
            "ACM" : "F:BO",
            "BO" : "F:HAC"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))

        # Set of (x,y) tuples
        self.walls = set()

        # (Cid) --> Creature
        self.creatures = {}

        self.turn_order = deque([])

        self.test_code = None

        self.full_round = 0

        self.elf_boost = 0

    def get_result(self):
        allhealth = sum([c.health for c in self.creatures.values() ])
        return self.full_round * allhealth

    def get_current_creature(self):
        return self.creatures[self.turn_order[0]]

    def get_current_target(self):
        crnt = self.get_current_creature()
        targets = [t for t in self.creatures.values() if t.ccode != crnt.ccode and crnt.distance_to_creature(t) == 1]

        if len(targets) == 0:
            return None

        # Sort by health, filter down to only those in top health bracket, then sort by priority
        targets = sorted(targets, key=lambda t: t.health)
        targets = [t for t in targets if t.health == targets[0].health]
        targets = sorted(targets, key=lambda t: t.get_priority())
        return targets[0]

    def find_dead_creature(self):
        deadies = [t for t in self.creatures.values() if t.health <= 0]
        assert len(deadies) <= 1
        return None if len(deadies) == 0 else deadies[0]

    def process_input_code(self, xpt, ypt, ccode):
        
        if ccode == '#':
            self.walls.add((xpt, ypt))
            return

        if ccode in 'GE':
            newcid = len(self.creatures)
            self.creatures[newcid] = Creature(newcid, ccode, xpt, ypt, elf_boost=self.elf_boost)
            return

        assert ccode == '.', "Bad input character code {}".format(ccode)


    def s1_init_machine(self):
        infile = 'p15'
        infile += '' if self.test_code == None else 'test'+self.test_code
        inlist = U.read_input_deque(infile)

        for yidx, line in enumerate(inlist):
            line = line.strip()
            for xidx in range(len(line)):
                ccode = line[xidx]
                self.process_input_code(xidx, yidx, ccode)

        print("Read input data, have {} walls and {} creatures".format(len(self.walls), len(self.creatures)))

    def s4_init_turn_order(self):
        clist = list(self.creatures.values())
        clist = sorted(clist, key=lambda c: c.get_priority())
        self.turn_order = deque([c.cid for c in clist])

    def s10_have_another_creature(self):
        return len(self.turn_order) > 0

    def s14_enemy_in_range(self):
        return self.get_current_target() != None

    def get_obstacle_set(self):
        return set(list(self.walls) + [c.get_position() for c in self.creatures.values()])

    def get_target_set(self, enemycode):
        return set([c.get_position() for c in self.creatures.values() if c.ccode == enemycode])

    def s16_step_toward_enemy(self):

        creat = self.get_current_creature()
        bestpath = find_path(self.get_obstacle_set(), self.get_target_set(creat.enemy_code()), creat.get_position())

        #print("For CID={}, bestpath={}".format(creat.cid, bestpath))

        # Okay, well, actually still have to check.
        if bestpath != None:
            assert bestpath[0] == creat.get_position()
            creat.step2_point(bestpath[1])

    def s17_have_attack_target(self):
        return self.get_current_target() != None

    def s20_attack_enemy(self):
        self.get_current_creature().attack_enemy(self.get_current_target())

    def s26_end_turn(self):
        pass


        #print("------------\nSituation after {} full rounds".format(self.full_round))
        #self.print_board()
        #print("Health: " + ",".join(self.get_health_status()))


    def get_health_status(self, encode=True):
        clist = sorted(list(self.creatures.values()), key=lambda c: c.get_priority())

        if encode:
            return ["{}{}".format(c.ccode, c.health) for c in clist]

        return [(c.ccode, c.health) for c in clist]


    def print_board(self):
        print(self.get_board_string())

    def get_board_string(self):

        c2posmap = { c.get_position() : c for c in self.creatures.values() }

        xbounds = min_and_max([w[0] for w in self.walls])
        ybounds = min_and_max([w[1] for w in self.walls])

        chars = []

        for ypt in range(ybounds[0], ybounds[1]+1):
            for xpt in range(xbounds[0], xbounds[1]+1):
                pt = (xpt, ypt)
                bchar = '.'

                if pt in self.walls:
                    bchar = '#'

                if pt in c2posmap:
                    bchar = c2posmap[pt].ccode

                chars.append(bchar)
            chars.append('\n')

        return "".join(chars)

    def s28_have_dead_creature(self):
        return self.find_dead_creature() != None

    def s29_resolve_death(self):
        deadid = self.find_dead_creature().cid
        self.creatures.pop(deadid)

        # Filter dead creature out of turn order
        self.turn_order = deque([cid for cid in self.turn_order if cid != deadid])


    def s30_end_creature_move(self):
        lastid = self.turn_order.popleft()
        #print("Ending turn for creature {}".format(lastid))


    def s31_all_creatures_moved(self):
        return len(self.turn_order) == 0

    def s32_increment_round_count(self):
        self.full_round += 1


    def s34_battle_over(self):
        codeset = set([crt.ccode for crt in self.creatures.values()])
        return len(codeset) == 1

    def s36_success_complete(self):
        pass    


def stripspace(s):
    return s.replace('\n', '').replace(' ', '')

def checkboard(pmach, testboard):
    machboard = pmach.get_board_string()
    assert stripspace(testboard) == stripspace(machboard), "Test Board is \n{}\n but machine gave {}\n".format(testboard, machboard)

def test_examples():

    scores = {}
    knowns = {}

    scores['C'] = 36334
    scores['D'] = 39514
    scores['E'] = 27755
    scores['F'] = 28944
    scores['G'] = 18740

    knowns['C'] = """
        #######
        #...#E#
        #E#...#
        #.E##.#
        #E..#E#
        #.....#
        #######
    """

    knowns['D'] = """
        #######
        #.E.E.#
        #.#E..#
        #E.##.#
        #.E.#.#
        #...#.#
        ####### 
    """

    knowns['E'] = """
        #######
        #G.G#.#
        #.#G..#
        #..#..#
        #...#G#
        #...G.#
        #######
    """

    knowns['F'] = """
        #######
        #.....#
        #.#G..#
        #.###.#
        #.#.#.#
        #G.G#G#
        #######
    """

    knowns['G'] = """
        #########
        #.G.....#
        #G.G#...#
        #.G##...#
        #...##..#
        #.G.#...#
        #.......#
        #.......#
        #########
    """

    for tcode in knowns:
        print("Running test code {}".format(tcode))
        pmach = PMachine()
        pmach.test_code = tcode
        pmach.run2_completion()      
        checkboard(pmach, knowns[tcode])
        assert pmach.get_result() == scores[tcode], "Machine reported {}, but expected {}".format(pmach.get_result(), scores[tcode])
        print("Test successful for tcode={}".format(tcode))  


def run_tests():
    
    pmach = PMachine()
    pmach.test_code = 'A'

    knownboard = {}

    knownboard[1] = """
            #########
            #.G...G.#
            #...G...#
            #...E..G#
            #.G.....#
            #.......#
            #G..G..G#
            #.......#
            #########
    """

    knownboard[2] = """
        #########
        #..G.G..#
        #...G...#
        #.G.E.G.#
        #.......#
        #G..G..G#
        #.......#
        #.......#
        #########
    """

    knownboard[3] = """
        #########
        #.......#
        #..GGG..#
        #..GEG..#
        #G..G...#
        #......G#
        #.......#
        #.......#
        #########
    """

    knownboard[4] = """
        #########
        #.......#
        #..GGG..#
        #..GEG..#
        #G..G...#
        #......G#
        #.......#
        #.......#
        #########
    """



    for turn, knownstr in knownboard.items():
        pmach.run_until(lambda x: x.full_round == turn)
        checkboard(pmach, knownstr)


    test_examples()



    