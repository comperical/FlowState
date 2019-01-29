import json
import copy
import sys

from collections import deque
import utility as U

sys.path.append("..")
from finite_state import *


import p23reddit

def mdist2origin(pt):
    assert len(pt) == 3
    return sum([abs(x) for x in pt])


COUNT_LOG = deque()

def clear_count_log():
    global COUNT_LOG
    assert len(COUNT_LOG) == 0
    COUNT_LOG.clear()

def log_count_operation(scode, pt):

    assert scode in ['original', 'machine']

    global COUNT_LOG
    if scode == 'original':
        COUNT_LOG.append(pt)
        return

    logpt = COUNT_LOG.popleft()
    assert logpt == pt, "Logged point is {}, but machine tried {}".format(logpt, pt)


class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {   
            "HAP" : "F:FC",
            "FET" : "T:SC",
            "ANT" : "HAP"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))

        self.nanobots = None

        self.forced_count = None

        # These are x/y/z/dist tuples
        self.probes = deque([])

        self.newtargets = []


    def initialize(self, bots, fcount):

        self.nanobots = bots

        self.forced_check = fcount


    def get_result(self):
        if len(self.newtargets) == 0:
            assert len(self.probes) == 0
            return None, None

        x, y, z, dist, cnt, mandist = self.newtargets[0]
        assert dist == 0
        return mandist, cnt

    def s1_init_machine(self):

        assert self.nanobots != None and self.forced_check != None

        assert len(self.probes) == 1, "Must add a single probe point"

        #assert self.nanobots != None, "You must set the nanobots externally"


    def s8_have_another_probe(self):
        return len(self.probes) > 0

    def s10_check_new_targets(self):
        xp, yp, zp, dist = self.probes[0]

        ntargs = []

        for x in [xp, xp+dist]:
            for y in [yp, yp+dist]:
                for z in [zp, zp+dist]:

                    # See how many bots are possible
                    count = p23reddit.count_for_point(self.nanobots, x, y, z, dist)

                    log_count_operation('machine', (x, y, z, dist))

                    if count >= self.forced_check:
                        #print("Got count ={} point {}, {}, {}, {}".format(count, x, y, z, dist))

                        ntargs.append((x, y, z, dist // 2, count, abs(x) + abs(y) + abs(z)))


        # This can often be empty
        self.newtargets = sorted(ntargs, key=lambda x: x[5])


    def s14_poll_probe_stack(self):
        self.probes.popleft()


    def s16_found_exact_target(self):
        if len(self.newtargets) == 0:
            return False

        _, _, _, dist, _, _ = self.newtargets[0]
        return dist == 0

    def s20_add_new_targets(self):
        for x, y, z, dist, _, _ in reversed(self.newtargets):
            self.probes.appendleft((x, y, z, dist))


    def s30_success_complete(self):
        pass

    def s31_fail_complete(self):
        pass



def machine_find(bots, xs, ys, zs, dist, forced_check):

    mach = PMachine()
    mach.initialize(bots, forced_check)
    mach.probes.append((min(xs), min(ys), min(zs), dist))
    mach.run2_completion()
    return mach.get_result()

def calc2(bots):
    # Find the range of the bots
    xs = [x[0] for x in bots] + [0]
    ys = [x[1] for x in bots] + [0]
    zs = [x[2] for x in bots] + [0]

    # Pick a starting resolution big enough to find all of the bots
    dist = 1
    while dist < max(xs) - min(xs) or dist < max(ys) - min(ys) or dist < max(zs) - min(zs):
        dist *= 2

    # And some offset values so there are no strange issues wrapping around zero
    ox = -min(xs)
    oy = -min(ys)
    oz = -min(zs)

    xs = xs + [min(xs)+dist+1]
    ys = ys + [min(ys)+dist+1]
    zs = zs + [min(zs)+dist+1]

    # Try to find all of the bots, backing off with a binary search till
    # we can find the most bots
    span = 1
    while span < len(bots):
        span *= 2
    forced_check = 1
    tried = {}

    best_val, best_count = None, None

    while True:

        print("Trying forced_count = {}, span = {}, |Tried|={}".format(forced_check, span, len(tried)))

        # We might try the same value multiple times, save some time if we've seen it already
        if forced_check not in tried:
            clear_count_log()
            test_val, test_count = find(bots, xs, ys, zs, dist, forced_check)            
            print("Size of count log is {}".format(len(COUNT_LOG)))
            mach_val, mach_count = machine_find(bots, xs, ys, zs, dist, forced_check)

            if test_val != mach_val or mach_count != test_count:
                print("Got test_val={}, mach_val={}, tcount={}, mcount={}".format(test_val, mach_val, test_count, mach_count))
                assert False

            #tried[forced_check] = find(bots, xs, ys, zs, dist, forced_check)
            tried[forced_check] = (test_val, test_count)


        test_val, test_count = tried[forced_check]
        print("Found test_val={}, count={} for forced_check={}".format(test_val, test_count, forced_check))


        if test_val is None:
            # Nothing found at this level, so go back
            if span > 1:
                span = span // 2
            forced_check = max(1, forced_check - span)
        else:
            # We found something, so go forward
            if best_count is None or test_count > best_count:
                best_val, best_count = test_val, test_count
            if span == 1:
                # This means we went back one, and it was empty, so we're done!
                break
            forced_check += span

    print("The max count I found was: " + str(best_count))
    return best_val


def find(bots, xs, ys, zs, dist, forced_count):
    at_target = []

    #print("Have {} subboxes".format(len(mysubs)))

    #print("Checking xpts {}".format(list(range(min(xs), max(xs)+1, dist))))


    for x in range(min(xs), max(xs)+1, dist):
        for y in range(min(ys), max(ys)+1, dist):
            for z in range(min(zs), max(zs)+1, dist):

                # See how many bots are possible
                count = p23reddit.count_for_point(bots, x, y, z, dist)

                log_count_operation("original", (x, y, z, dist))

                if count >= forced_count:
                    at_target.append((x, y, z, count, abs(x) + abs(y) + abs(z)))
                    #at_target.append((x, y, x), count)

    at_target = sorted(at_target, key=lambda x: x[4])

    while len(at_target) > 0:
        """
        best = []
        best_i = None

        # Find the best candidate from the possible boxes
        for i in range(len(at_target)):
            if best_i is None or at_target[i][4] < best[4]:
                best = at_target[i]
                best_i = i
        """

        best = at_target[0]

        if dist == 1:
            # At the end, just return the best match
            return best[4], best[3]
        else:
            # Search in the sub boxes, see if we find any matches
            xs = [best[0], best[0] + dist//2]
            ys = [best[1], best[1] + dist//2]
            zs = [best[2], best[2] + dist//2]
            a, b = find(bots, xs, ys, zs, dist // 2, forced_count)
            if a is None:
                # This is a false path, remove it from consideration and try any others
                #at_target.pop(best_i)
                at_target = at_target[1:]
            else:
                # We found something, go ahead and let it bubble up
                return a, b

    # This means all of the candidates yeild false paths, so let this one
    # be treated as a false path by our caller
    return None, None





if __name__ == "__main__":

    bots = p23reddit.get_bots()
    calc2(bots)

    print("Have {} bots".format(len(bots)))