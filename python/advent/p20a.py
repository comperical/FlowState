import json
import copy
import hashlib

from functools import lru_cache

from collections import deque
from collections import Counter

import utility as U
from finite_state import *

CARDINAL = { 'N' : -1j, 'S': +1j, 'E' : +1, 'W': -1 }

def full_range(coords, padding=0):
    minc = min(coords) - padding
    maxc = max(coords) + padding
    return range(minc, maxc+1)

def path2delta(steps):
    return sum([CARDINAL.get(stp) for stp in steps])


class AndBlock:

    def __init__(self, head):
        self.head = head
        self.tail = None

    def append(self, expr):

        if self.tail == None:
            self.tail = AndBlock(expr)
            return

        self.tail.append(expr)

    def size(self):
        return 1 if self.tail == None else 1 + self.tail.size()


    def allpaths(self):
        if self.tail == None:
            yield from self.head.allpaths()
            return

        for hpath in self.head.allpaths():
            for tpath in self.tail.allpaths():
                yield hpath + tpath

    def apply(self, doormap, curpt):

        if not doormap.haveblock(self, curpt):
            self.head.apply(doormap, curpt)

            if self.tail != None:
                for hpath in self.head.allpaths():
                    self.tail.apply(doormap, curpt+path2delta(hpath))

            if self.tail == None:
                # We will have already placed this in the log, when calling self.head.apply(...)
                assert doormap.haveblock(self, curpt)
            else:
                doormap.logapply(self, curpt)

    @lru_cache(maxsize=1)
    def __str__(self):

        gimp = self
        s = str(self.head)

        while gimp.tail != None:
            gimp = gimp.tail
            s += str(gimp.head)

        return s


class OrBlock:

    def __init__(self):
        self.kids = []

    def add_kid(self, expr):
        self.kids.append(expr)


    def allpaths(self):
        for kid in self.kids:
            yield from kid.allpaths()

    def apply(self, doormap, curpt):

        if not doormap.haveblock(self, curpt):
            #print("Applying OR block {} at {}".format(str(self), curpt))

            for kid in self.kids:
                kid.apply(doormap, curpt)

            doormap.logapply(self, curpt)

    @lru_cache(maxsize=1)
    def __str__(self):        
        return "(" + "|".join([str(kid) for kid in self.kids]) + ")"


class SBlock:

    def __init__(self, steps):
        assert all([s in CARDINAL for s in steps])
        self.steps = steps

    def allpaths(self):
        yield self.steps


    def apply(self, doormap, curpt):

        if not doormap.haveblock(self, curpt):
            #print("Applying S block {} at {}".format(str(self), curpt))
            doormap.markpath(curpt, self.steps)
            doormap.logapply(self, curpt)


    @lru_cache(maxsize=1)
    def __str__(self):        
        return "".join(self.steps)


class DoorMap:

    def __init__(self):
        
        self.applied = set()

        # set of positions with doors to the west 
        self.door2west = set()

        # Doors to the north
        self.door2nrth = set()

    def haveblock(self, block, curpt):
        #print("Applied set is {}".format(self.applied))
        return (str(block), curpt) in self.applied

    def logapply(self, block, curpt):
        probe = (str(block), curpt)
        assert not probe in self.applied, "Already have point {}".format(probe)
        self.applied.add(probe)

    def mark_block_slow(self, curpt, block):
        for path in block.allpaths():
            self.markpath(curpt, path)

    def markpath(self, curpt, steps):
        thept = curpt
        for stp in steps:
            self.marksingle(thept, stp)
            thept += CARDINAL.get(stp)

    def room_distance_stats(self):

        def successors(pt):
            if pt in self.door2nrth:
                yield pt - 1j

            if (pt + 1j) in self.door2nrth:
                yield pt + 1j

            if pt in self.door2west:
                yield pt - 1

            if (pt + 1) in self.door2west:
                yield pt + 1

        # Explore all the rooms!!!
        def isgoal(pt):
            return False

        _, parents = U.state_search(0, successors, isgoal)

        def length2root(pt):
            g = pt
            d = 0

            while g != 0:
                g = parents[g]
                d += 1

            return d

        alldist = [length2root(pt) for pt in parents]
        maxdist = max(alldist)
        longpth = sum([dist >= 1000 for dist in alldist])

        return maxdist, longpth

    def marksingle(self, curpt, onestep):

        if onestep == 'N':
            self.door2nrth.add(curpt)
        elif onestep == 'S':
            self.door2nrth.add(curpt + CARDINAL.get('S'))
        elif onestep == 'W':
            self.door2west.add(curpt)
        elif onestep == 'E':
            self.door2west.add(curpt + CARDINAL.get('E'))
        else:
            assert False, "Unknown step code: {}".format(onestep)

    def allpoints(self):
        yield from self.door2west
        yield from self.door2nrth

    def hight(self):
        return max([pt.imag for pt in self.allpoints()])

    def width(self):
        return max([pt.real for pt in self.allpoints()])

    def anydoor(self, pt):

        if pt in self.door2nrth or pt in self.door2west:
            return True

        if pt+CARDINAL.get('E') in self.door2west:
            return True

        if pt+CARDINAL.get('S') in self.door2nrth:
            return True

        return False

    def get_y_range(self):

        def coords():
            for pt in self.door2west:
                yield int(pt.imag)

            for pt in self.door2nrth:
                yield int(pt.imag)
                yield int(pt.imag)-1

        miny = min(coords())
        maxy = max(coords())
        return range(miny, maxy+1)

    def get_x_range(self):
        def coords():
            for pt in self.door2west:
                yield int(pt.real)-1
                yield int(pt.real)

            for pt in self.door2nrth:
                yield int(pt.real)

        minx = min(coords())
        maxx = max(coords())
        return range(minx, maxx+1)

    def get_board_string(self):
        #print("D2North: " + str(self.door2nrth))
        #print("D2West : " + str(self.door2west))

        rows = []
        for y in self.get_y_range():
            oldrow = ['#']
            newrow = ['#']
            for x in self.get_x_range():
                prb = complex(x, y)

                nrthdoor = (prb + CARDINAL.get('S')) in self.door2nrth
                westdoor = (prb + CARDINAL.get('E')) in self.door2west

                # okay, point is the upper/left cornder.
                roomtok = 'X' if (x == 0 and y == 0) else '.'

                if roomtok == '.' and not self.anydoor(prb):
                    roomtok = '#'

                oldrow.append(roomtok)
                oldrow.append('|' if westdoor else '#')

                newrow.append('-' if nrthdoor else '#')
                newrow.append('#')

            rows.append("".join(oldrow))
            rows.append("".join(newrow))

        toprow = ['#' * len(rows[0])]
        rows.insert(0, "".join(toprow))

        return "\n".join(rows)


class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "EOI" : "T:ISC",
            "IMT" : "F:POT",
            "SSB" : "EOI",
            "IPT" : "F:PCT",
            "SOB" : "EOI",
            "IET" : "T:ISC",
            "PPT" : "ROC"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))

        self.test_code = None

        self.regexstr = None

        self.tokens = None

        self.mainblock = None

    def get_result(self):
        doormap = self.get_doormap_result()
        return doormap.room_distance_stats()


    def get_result_block(self):
        return SBlock([]) if self.mainblock == None else self.mainblock

    def set_external_input(self, restr, docheck=True):

        assert self.tokens == None and self.regexstr == None

        self.regexstr = restr.strip()
        assert not docheck or (self.regexstr[0] == '^' and self.regexstr[-1] == '$')

        self.tokens = deque([c for c in self.regexstr])
        self.tokens.popleft()
        self.tokens.pop()


    def set_external_queue(self, tq):
        assert self.regexstr == None
        self.tokens = tq

    def get_doormap_result(self):
        fastdoor = DoorMap()
        self.mainblock.apply(fastdoor, 0)
        return fastdoor

    def s1_init_machine(self):

        if self.tokens == None:
            lines = U.read_input_deque('p20')
            self.set_external_input(lines[0])

        #self.curblock = ReBlock('AND')


    def s2_end_of_input(self):
        return len(self.tokens) == 0


    def s3_is_ending_token(self):
        return self.tokens[0] in '|)'

    def s4_is_move_token(self):
        return self.tokens[0] in 'NEWS'


    def ship_expression(self, expr):

        if self.mainblock != None:
            #print("Appending to main block, size is {}".format(self.mainblock.size()))
            self.mainblock.append(expr)
            return

        self.mainblock = AndBlock(expr)

    def s5_slurp_ship_basic(self):
        
        steps = []
        while len(self.tokens) > 0 and self.tokens[0] in 'NEWS':
            steps.append(self.tokens.popleft())

        self.ship_expression(SBlock(steps))


    def s11_poll_open_token(self):
        openc = self.tokens.popleft()
        assert openc == '('


    def s12_begin_or_block(self):
        
        self.or_block = OrBlock()

    def s14_recursive_or_call(self):
        
        subm = PMachine()
        subm.set_external_queue(self.tokens)
        subm.run2_completion()

        self.or_block.add_kid(subm.get_result_block())

    def s18_is_pipe_token(self):
        return self.tokens[0] == '|'

    def s20_poll_pipe_token(self):
        nextc = self.tokens.popleft()
        assert nextc == '|'


    def s23_poll_close_token(self):
        nextc = self.tokens.popleft()
        assert nextc == ')'

    def s24_ship_or_block(self):
        self.ship_expression(self.or_block)
        self.or_block = None




    def s29_input_sanity_check(self):

        if self.regexstr != None:
            checkstr = '^' + str(self.mainblock) + '$'
            assert checkstr == self.regexstr, "Check string is {}, original is {}".format(checkstr, self.regexstr)
            printstr = checkstr[:100] + "..." if len(checkstr) > 100 else checkstr
            print("Checked sanity for input RE {}".format(printstr))




    def s30_success_complete(self):
        pass



def get_day20_test_data(testnum):

    fullpath = "{}/day20/test{}.txt".format(U.get_data_dir(), testnum)
    indeq = deque([line for line in open(fullpath, 'r')])

    def readfrombreak(mydeq):
        assert "----" in mydeq[0]
        mydeq.popleft()

        lines = []
        while len(mydeq) > 0 and not "----" in mydeq[0]:
            lines.append(mydeq.popleft().strip())

        return lines


    restr = indeq.popleft()
    paths = readfrombreak(indeq)
    board = readfrombreak(indeq)
    return restr, paths, board


def run_tests():
    
    def joinpath(pths):
        return "".join(pths)

    def checkboard(astr, bstr):
        assert astr.replace('\n', '').replace(' ', '') == bstr.replace('\n', '').replace(' ', '')

    for testidx in range(1, 9):
        restr, knownpaths, board = get_day20_test_data(testidx)
        print("read RE string {}".format(restr))
        pmach = PMachine()
        pmach.set_external_input(restr)
        pmach.run2_completion()

        checkpaths = [joinpath(pth) for pth in pmach.mainblock.allpaths()]

        if knownpaths != checkpaths:

            print("Expected: ")
            for kp in knownpaths:
                print("\t{}".format(kp))

            print("Obtained: ")
            for cp in checkpaths:
                print("\t{}".format(cp))

            assert False


        print("Checked {} paths for test input {}".format(len(checkpaths), testidx))

        doormap = DoorMap()
        doormap.mark_block_slow(0, pmach.mainblock)
        print(doormap.get_board_string())

        checkboard(doormap.get_board_string(), "\n".join(board))

        fastdoor = DoorMap()
        pmach.mainblock.apply(fastdoor, 0)

        #print("FastDoor:")
        #print(fastdoor.get_board_string())
        assert doormap.get_board_string() == fastdoor.get_board_string()




    