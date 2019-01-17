import json
import copy
import hashlib

from functools import reduce
from collections import deque
from collections import Counter
from itertools import permutations, combinations

import utility as U
from finite_state import *

ORIENTATIONS = [
    (-1, -1, -1), # = 0
    (-1, -1, +1), 
    (-1, +1, -1), # = 2
    (-1, +1, +1),
    (+1, -1, -1), # = 4
    (+1, -1, +1),
    (+1, +1, -1), # = 6
    (+1, +1, +1)  # = 7
]

def good_orient_triple(olist):

    assert len(set(olist)) == 3

    def neighbors(ornt1, ornt2):
        return sum([o[0] != o[1] for o in zip(ornt1, ornt2)]) == 1

    return neighbors(olist[0], olist[1]) and neighbors(olist[0], olist[2])


def get_plane_intersections(planes):

        # orienttation to plane
        plmap = { p.O : p for p in planes }
        assert len(plmap) == 8, "Require all 8 plane orientations, got {}".format(len(plmap))

        vertset = set([])

        for orientset in get_plane_orient_sets():
            pl3list = [plmap[ornt] for ornt in orientset]
            intersect = find_plane_intersection(pl3list)

            for pln in pl3list:
                assert pln.point_on_plane(intersect), "Point {} is not on plane {}".format(intersect, pln)

            vertset.add(intersect)

        assert len(vertset) == 6
        return vertset



def planes_intersect(olist):

    assert len(olist) == 3

    if len(set(olist)) != 3:
        return False    

    def opposes(o1, o2):
        return all([s[0] == - s[1] for s in zip(o1, o2)])

    return not opposes(olist[0], olist[1]) and not opposes(olist[0], olist[2]) and not opposes(olist[1], olist[2])

def get_plane_orient_sets():

    return [otrp for otrp in combinations(ORIENTATIONS, 3) if good_orient_triple(otrp)]


def find_plane_intersection(planes):

    assert len(planes) == 3
    assert planes_intersect((planes[0].O, planes[1].O, planes[2].O))

    #print("-----------\nStudying Planes: ")
    #for pln in planes:
    #    print("\t{}".format(pln))

    idx1, val1 = planes[0].find_intersection_coord(planes[1])
    idx2, val2 = planes[0].find_intersection_coord(planes[2])

    assert idx1 != idx2

    #print("{} --> {}".format(idx1, val1))
    #print("{} --> {}".format(idx2, val2))

    idx3 = [idx for idx in range(3) if idx not in [idx1, idx2]][0]
    val3 = planes[0].R - (planes[0].O[idx1] * val1) - (planes[0].O[idx2] * val2)
    val3 *= planes[0].O[idx3] 

    lstres = sorted([(idx1, val1), (idx2, val2), (idx3, val3)])
    frslt = tuple([lr[1] for lr in lstres])
    #print(frslt)
    return frslt

class Plane:

    def __init__(self, orient, R):
        assert all([c in [-1,+1] for c in orient]), "Orientation should be vector of form (+-1, +-1, +-1)"

        self.R = R
        self.O = tuple([o for o in orient])

    @staticmethod
    def read_from_string(pstr):
        toks = pstr.split("<=")
        assert len(toks) == 2

        ostr = toks[0].strip()
        def pm2int(oidx):
            c = ostr[oidx]
            assert c in ['-','+']
            return int(c+'1')

        orient = [pm2int(oidx) for oidx in [0, 2, 4]]
        rpower = int(toks[1].strip())
        return Plane(orient, rpower)

    def convert_origin(self, neworgn):
        shift = sum([x[0]*x[1] for x in zip(self.O, neworgn)])
        self.R += shift

    def distance_to_point(self, pt):
        shift = sum([x[0]*x[1] for x in zip(self.O, pt)])
        #print("PT is {}, O is {}, shift is {}, R is {}, R-shift={}".format(pt, self.O, shift, self.R, self.R-shift))
        return self.R - shift

    def accept(self, pt):
        return self.distance_to_point(pt) >= 0

    def find_intersection_coord(self, other):
        assert (self.R + other.R) % 2 == 0, "Bad intersection for {} vs {}".format(self, other)

        sameidxes = [idx for idx in range(3) if self.O[idx] == other.O[idx]]
        diffidxes = [idx for idx in range(3) if self.O[idx] != other.O[idx]]

        if len(sameidxes) == 1:
            rsum = (self.R + other.R)//2
            rsum = -rsum if self.O[sameidxes[0]] == -1 else rsum
            return sameidxes[0], rsum 

        if len(diffidxes) == 1:
            rdff = (self.R - other.R)//2
            rdff = -rdff if self.O[diffidxes[0]] == -1 else rdff
            return diffidxes[0],  rdff

        assert False, "Must have either one diffidxes or one sameidxes"


    def point_on_plane(self, pt):
        return self.distance_to_point(pt) == 0

    def __str__(self):

        def pminus(ornt):
            return "-" if ornt == -1 else "+"

        return "{}x{}y{}z <= {}".format(pminus(self.O[0]), pminus(self.O[1]), pminus(self.O[2]), self.R)


class Nanobot:

    def __init__(self, s):
        
        alpha = s.find("=<")
        omega = s.find(">,")

        self.coords = [int(cs) for cs in s[alpha+2:omega].split(",")]
        assert len(self.coords) == 3

        rpos = s.find("r=")
        self.rpower = int(s[rpos+2:])


    def get_cutting_planes(self):
        for ornt in ORIENTATIONS:
            p = Plane(ornt, self.rpower)
            p.convert_origin(self.coords)
            yield p

    def can_see_point(self, ptcoords):

        def mdist(idx):
            return abs(self.coords[idx] - ptcoords[idx])

        netdist = sum([mdist(idx) for idx in range(3)])
        return netdist <= self.rpower

    def can_see_nbot(self, nbot):
        return self.can_see_point(nbot.coords)

    def diamond_vertices(self):
        for dlt in [-self.rpower, +self.rpower]:
            yield (self.coords[0]+dlt, self.coords[1], self.coords[2])
            yield (self.coords[0], self.coords[1]+dlt, self.coords[2])
            yield (self.coords[0], self.coords[1], self.coords[2]+dlt)

    def __str__(self):
        cstr = ",".join([str(c) for c in self.coords])
        return "pos=<{}>, r={}".format(cstr, self.rpower)


    def plane_check(self):

        planes = list(self.get_cutting_planes())

        for vt in self.diamond_vertices():

            onplanes = [p for p in planes if p.distance_to_point(vt) == 0]

            if len(onplanes) != 4:
                for p in planes:
                    dist = p.distance_to_point(vt)
                    print("Distance for plane {} to vertex {} is {}".format(p, vt, dist))

                assert False

            acplanes = [p for p in planes if p.accept(vt)]

            if len(acplanes) != 8:
                for p in planes:
                    accpt = p.accept(vt)
                    dist = p.distance_to_point(vt)                    
                    print("Plane {} has accept={}, dist={} for vt={}".format(p, accpt, dist, vt))

                assert False


    def recalc_vertices(self):
        vertset = get_plane_intersections(list(self.get_cutting_planes()))
        assert all([diam in vertset for diam in self.diamond_vertices()])


class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "SV": "HAV",
            "HAV" : "F:FBD",
            "CWTB": "F:SC",
            "WTB" : "CWTB"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))

        self.is_test = False

        self.nanobots = []

        # queue of vertices to score
        self.unscored = deque()

        # (pt, #nano) pairs
        self.scored = []

        self.currentbest = None


    def get_result(self):
        return sum([abs(p) for p in self.currentbest])

    def s1_init_machine(self):
        infile = 'p23testB' if self.is_test else 'p23'
        lines = U.read_input_deque(infile)

        for s in lines:
            nbot = Nanobot(s)
            assert str(nbot) == s.strip(), "Got nbot={} but orig={}".format(nbot, s)
            self.nanobots.append(nbot)

            nbot.plane_check()

            nbot.recalc_vertices()


        self.nanobots = [Nanobot(s) for s in lines]
        print("Read {} Nano bots".format(len(self.nanobots)))


    def score_point(self, pt):
        return sum([nbot.can_see_point(pt) for nbot in self.nanobots])

    def s4_generate_diamond_vertices(self):
        
        ptset = set()

        for nbot in self.nanobots:
            for vertex in nbot.diamond_vertices():
                assert nbot.can_see_point(vertex)
                ptset.add(vertex)

        self.unscored.extend(ptset)
        print("Have {} diamond vertices to score".format(len(ptset)))

    def s6_have_another_vertex(self):
        return len(self.unscored) > 0


    def s8_score_vertex(self):
        vertex = self.unscored.popleft()
        score = self.score_point(vertex)
        self.scored.append((vertex, score))

    def s10_find_best_diamonds(self):
        self.bestscore = max(self.scored, key=lambda x: x[1])[1]

        bestverts = [pt for pt, score in self.scored if score == self.bestscore]

        print("Found {} vertices with score = {}".format(len(bestverts), self.bestscore))

        for bv in bestverts:
            print("Vertex={}".format(bv))

        self.currentbest = bestverts[0]


    def s11_find_supporting_planes(self):

        planemap = {}

        for nbot in self.nanobots:

            if not nbot.can_see_point(self.currentbest):
                continue

            for splane in nbot.get_cutting_planes():
                assert splane.accept(self.currentbest)

                planemap.setdefault(splane.O, [])
                planemap[splane.O].append(splane)


        print("For current best = {}".format(self.currentbest))
        for ornt, splanes in planemap.items():
            minplane = min(splanes, key=lambda pln: pln.distance_to_point(self.currentbest))
            dist2pln = minplane.distance_to_point(self.currentbest)
            print("Found minplane {} at distance {}".format(minplane, dist2pln))


    def closer_points(self):

        def delta(vl):
            if vl == 0:
                return 0

            return +1 if vl < 0 else -1

        yield (self.currentbest[0]+delta(self.currentbest[0]), self.currentbest[1], self.currentbest[2])
        yield (self.currentbest[0], self.currentbest[1]+delta(self.currentbest[1]), self.currentbest[2])
        yield (self.currentbest[0], self.currentbest[1], self.currentbest[2]+delta(self.currentbest[2]))

    def find_closer_point(self):
        
        for pt in self.closer_points():
            if pt == self.currentbest:
                continue

            newscore = self.score_point(pt)
            assert newscore <= self.bestscore

            print("Score for point {} is {}".format(pt, newscore))

            if newscore == self.bestscore:
                return pt

        return None


    def s16_can_walk_to_better(self):        
        betterpt = self.find_closer_point()
        print("Found better point = {} at current {}".format(betterpt, self.currentbest))
        return betterpt != None

    def s18_walk_to_better(self):
        self.currentbest = self.find_closer_point()

    def s30_success_complete(self):
        pass


def test_plane_intersection():

    planestr = """
    -x-y-z <= -85761536
    -x-y+z <= -34004690
    -x+y-z <= -28210764
    -x+y+z <= 23546082
    +x-y-z <= -16612679
    +x-y+z <= 30944267
    +x+y-z <= 38204597
    +x+y+z <= 85761546
    """

    planes = [Plane.read_from_string(pstr) for pstr in planestr.split("\n") if len(pstr.strip()) > 0]

    for pln in planes:
        print("Plane is {}".format(pln))

    vertices = get_plane_intersections(planes)

    for vrt in vertices:
        print(vrt)


def run_tests():
    

    pmach = PMachine()
    pmach.is_test = True
    pmach.run2_completion()
    assert pmach.get_result() == 36

    #test_plane_intersection()

