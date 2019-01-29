import json
import copy
import sys

from collections import deque
import utility as U

from finite_state import *

def mdist2origin(pt):
    assert len(pt) == 3
    return sum([abs(x) for x in pt])


def get_bots():

    values = U.read_input_deque('p23')

    r = re.compile("pos=<([0-9-]+),([0-9-]+),([0-9-]+)>, r=([0-9]+)")
    bots = []
    for cur in values:
        m = r.search(cur)
        if m is None:
            print(cur)
        bots.append([int(x) for x in m.groups()])
    return bots


def count_for_point(bots, x, y, z, dist):

    count = 0
    for bx, by, bz, bdist in bots:

        calc = abs(x - bx) + abs(y - by) + abs(z - bz)

        if dist == 1:
            if calc <= bdist:
                count += 1
        else:
            # The minus three is to include the current box 
            # in any bots that are near it
            if calc // dist - 3 <= (bdist) // dist:
                count += 1

    return count    


class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {   
            "BC" : "T:SC",
            "HAP" : "F:SF",
            "FET" : "T:SS",
            "ANT" : "HAP",
            "DUB" : "BC",
            "ILB" : "BC"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))

        self.nanobots = get_bots()

        # These are x/y/z/dist tuples
        self.probes = None

        self.newtargets = []

        self.achieved_lower_bound = 1
        self.unachieved_upper_bound = 1000

    def get_result(self):
        return mdist2origin(self.best_point)

    def s1_init_machine(self):
        pass

    def s5_bounds_converged(self):
        return self.achieved_lower_bound + 1 == self.unachieved_upper_bound

    def initialize_probes(self):
        xs = [x[0] for x in self.nanobots]
        ys = [x[1] for x in self.nanobots]
        zs = [x[2] for x in self.nanobots]

        # Pick a starting resolution big enough to find all of the bots
        dist = 1
        while dist < max(xs) - min(xs) or dist < max(ys) - min(ys) or dist < max(zs) - min(zs):
            dist *= 2

        initpt = (min(xs), min(ys), min(zs), dist)
        self.probes = deque([initpt])

    def s6_setup_partition_search(self):

        bound_gap = self.unachieved_upper_bound - self.achieved_lower_bound
        assert bound_gap > 1
        self.attempt_reqd_count = self.achieved_lower_bound + bound_gap // 2

        print("searching with bounds={}/{}, attempt={}".format(self.achieved_lower_bound, self.unachieved_upper_bound, self.attempt_reqd_count))
        self.initialize_probes()

    def s8_have_another_probe(self):
        return len(self.probes) > 0

    def s10_check_new_targets(self):
        xp, yp, zp, dist = self.probes[0]

        ntargs = []

        for x in [xp, xp+dist]:
            for y in [yp, yp+dist]:
                for z in [zp, zp+dist]:

                    # See how many bots are possible
                    count = count_for_point(self.nanobots, x, y, z, dist)

                    if count >= self.attempt_reqd_count:
                        ntargs.append((x, y, z, dist // 2, count))

        # This can often be empty
        self.newtargets = sorted(ntargs, key=lambda x: mdist2origin((x[0], x[1], x[2])))


    def s14_poll_probe_stack(self):
        self.probes.popleft()

    def s16_found_exact_target(self):
        if len(self.newtargets) == 0:
            return False

        _, _, _, dist, _ = self.newtargets[0]
        return dist == 0

    def s20_add_new_targets(self):
        for x, y, z, dist, _ in reversed(self.newtargets):
            self.probes.appendleft((x, y, z, dist))


    def s30_search_success(self):
        x, y, z, dist, cnt = self.newtargets[0]
        assert dist == 0
        self.best_point = (x, y, z)
        self.best_count = cnt

        print("Successful search at attempted_count={}, best point is {}, count is {}, mdist={}".format(self.attempt_reqd_count, self.best_point, self.best_count, mdist2origin(self.best_point)))

    def s31_increase_lower_bound(self):
        self.achieved_lower_bound = self.attempt_reqd_count

    def s32_search_failed(self):
        print("Search failed at attempted_count={}".format(self.attempt_reqd_count))

    def s33_decrease_upper_bound(self):
        self.unachieved_upper_bound = self.attempt_reqd_count

    def s36_success_complete(self):
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


def run_tests():
    pass


if __name__ == "__main__":

    bots = p23reddit.get_bots()
    calc2(bots)

    print("Have {} bots".format(len(bots)))