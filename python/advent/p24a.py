import json
import time
import sys
from collections import deque

import utility as U
from finite_state import *

SPECIALS = ['fire', 'radiation', 'cold', 'bludgeoning', 'slashing']


def pointafter(record, tagstr):
    idx = record.find(tagstr)
    assert idx != -1, "Failed to find tag string {} ".format(tagstr)
    return idx + len(tagstr)

def read_hit_points(rstr):
    alpha = pointafter(rstr, "each with")
    omega = rstr.index("hit points")
    return int(rstr[alpha:omega])


def readinit(record):
    alpha = pointafter(record, "at initiative")
    return int(record[alpha+1:])

def read_unit_count(rstr):
    unitp = rstr.index("units each")
    return int(rstr[:unitp])

def read_specials(rstr):

    imms = []
    vulns = []

    if "(" in rstr:
        alpha = rstr.find("(")
        omega = rstr.find(")")

        specstr = rstr[alpha+1:omega]
        subtokens = specstr.split(";")

        for sub in subtokens:
            isimmune, items = read_spec_sub(sub)
            if isimmune:
                imms.extend(items)
            else:
                vulns.extend(items)

    return imms, vulns

def read_spec_sub(substr):
    isweak = "weak to" in substr
    isimmn = "immune to" in substr
    assert isweak or isimmn
    items = [s for s in SPECIALS if s in substr]
    return isimmn, items

def read_attack(record):
    alpha = pointafter(record, "attack that does")
    omega = record.index("damage at")
    substr = record[alpha:omega].strip()
    apower, atype = substr.split()
    assert atype in SPECIALS
    return int(apower), atype


class BioGroup:

    def __init__(self, record, grpid):
        self.units = read_unit_count(record)
        self.hpoints = read_hit_points(record)
        self.imms, self.vulns = read_specials(record)

        self.attpower, self.attkind = read_attack(record)
        self.initiative = readinit(record)

        self.group_id = grpid

        """
        print("Initiative is {}".format(self.initiative))
        print("Attack is {}--{}".format(self.attpower, self.attkind))

        print("Immunes are {}".format(self.imms))
        print("Vulners are {}".format(self.vulns))
        """

    def is_immune(self):
        return self.group_id[0]

    def effective_power(self):
        return self.units * self.attpower


    def damage_estimate(self, defender):

        # immune!!
        if self.attkind in defender.imms:
            return 0

        damage = self.effective_power()
        damage *= 2 if self.attkind in defender.vulns else 1
        return damage

    def attack(self, defender, verbose):
        
        damage = self.damage_estimate(defender)
        numkilled = damage // defender.hpoints
        numkilled = min(defender.units, numkilled)
        defender.units -= numkilled

        strongattack = self.attkind in defender.vulns

        if verbose:
            groupstr = "Immune System" if self.is_immune() else "Infection"
            print("{} group {} attacks defending group {}, killing {} units".format(groupstr, self.group_id[1], defender.group_id[1], numkilled))
       
        #print("Damage={}, hpoints={}, Attack is strong={}".format(damage, defender.hpoints, strongattack))

        #Immune System group 2 attacks defending group 1, killing 4 units
        #Infection group 1 attacks defending group 2, killing 144 units

        return numkilled


    def __str__(self):
        #1466 units each with 7549 hit points (weak to fire, bludgeoning) with an attack that does 49 fire damage at initiative 1

        specs = []
        if self.imms:
            specs.append("immune to " + ", ".join(self.imms))
        if self.vulns:
            specs.append("weak to " + ", ".join(self.vulns))

        specstr = "" if len(specs) == 0 else "(" + "; ".join(specs) + ")"

        return """
            {} units each with {} hit points {} with an attack that does {} {} damage at initiative {}
        """.format(self.units, self.hpoints, specstr, self.attpower, self.attkind, self.initiative).strip()



class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "IM" : "STSD",
            "HAS" : "F:SAD",
            "HDG" : "F:PAQ",
            "ST" : "PSQ",
            "PSQ" : "HAS",
            "RDG" : "BO",
            "BO" : "T:SC",
            "HAT" : "F:PAQ",
            "HAA" : "F:IBS",
            "PAQ" : "HAA",
            "IBS" : "T:DC"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))

        self.groups = {}

        self.selectors = None

        self.attackers = None

        self.targets = {}

        self.test_code = None

        self.verbose = True

    def get_result(self):

        assert len(set([g.group_id[0] for g in self.groups.values()])) == 1
        return sum([g.units for g in self.groups.values()])

    def immune_wins(self):
        if self.is_battle_draw():
            return False

        glist = [g.is_immune() for g in self.groups.values() ]
        assert len(set(glist)) == 1, "No winner yet!!"
        return glist[0]


    def is_battle_draw(self):
        return "draw" in self.get_state().lower()

    def get_groups_of_type(self, isimmune):
        return [g for g in self.groups.values() if g.is_immune() == isimmune]

    def new_group_id(self, isimm):
        return (isimm, len(self.get_groups_of_type(isimm))+1)

    def s1_init_machine(self):
        infile = 'p24'
        infile += '' if self.test_code == None else 'test' + self.test_code
        lines = U.read_input_deque(infile)

        for isimmune in [True, False]:
            header = lines.popleft()
            expect = "Immune System" if isimmune else "Infection"
            assert expect in header

            while len(lines) > 0:

                nextline = lines.popleft()
                if len(nextline.strip()) == 0:
                    break

                grpid = self.new_group_id(isimmune)
                bgroup = BioGroup(nextline, grpid)
                self.groups[grpid] = bgroup

                #print("Read/reconst:\t\n{}\t\n{}".format(nextline.strip(), bgroup))

                #assert str(bgroup) == nextline.strip()
                #print("Read BioGroup  {}".format(bgroup))

        #print("Read {} biogroups".format(len(self.groups)))


    def print_group_status(self):

        if self.verbose:
            print("")

            for isimm in [True, False]:
                printgroups = sorted([g for g in self.get_groups_of_type(isimm)], key=lambda g: g.group_id)

                print(("Immune System:" if isimm else "Infection:"))
                for pg in printgroups:
                    print("Group {} contains {} units".format(pg.group_id[1], pg.units))


            print("")

    def s9_is_battle_stalemate(self):

        return self.killed_in_round == 0


    def s10_setup_target_selector_data(self):

        self.print_group_status()

        self.killed_in_round = 0

        self.targets = {}

        def orderkey(grpid):
            g = self.groups[grpid]
            return g.is_immune(), -g.effective_power(), -g.initiative
        
        self.selectors = sorted([grpid for grpid in self.groups], key=orderkey)
        self.selectors = deque(self.selectors)


    def s16_have_another_selector(self):
        return len(self.selectors) > 0


    def s18_select_target(self):
        
        attacker = self.groups[self.selectors[0]]

        def targeting_key(g):
            return (-attacker.damage_estimate(g), -g.effective_power(), -g.initiative)

        #print("Targets are: {}".format(self.targets))

        enemies = self.get_groups_of_type(not attacker.is_immune())
        enemies = [g for g in enemies if not g.group_id in self.targets.values()]
        enemies = sorted(enemies, key=targeting_key)

        if self.verbose: 
            printlist = sorted(enemies, key=lambda g: g.group_id)

            for en in printlist:
                groupstr = "Immune System" if attacker.is_immune() else "Infection"
                print("{} group {} would deal defending group {} {} damage".format(groupstr, attacker.group_id[1], en.group_id[1], attacker.damage_estimate(en)))
            #Infection group 1 would deal defending group 1 185832 damage
            # print("Enemy group has tkey {} ".format(targeting_key(en)))


        if len(enemies) > 0 and attacker.damage_estimate(enemies[0]) > 0:
            self.targets[attacker.group_id] = enemies[0].group_id


    def s19_poll_select_queue(self):
        self.selectors.popleft()

    def s20_setup_attack_data(self):

        if self.verbose:
            print("")

        def attackorder(grpid):
            group = self.groups[grpid]
            return -group.initiative

        self.attackers = sorted([g.group_id for g in self.groups.values() ], key=attackorder)
        self.attackers = deque(self.attackers)

    def s24_have_another_attacker(self):
        return len(self.attackers) > 0

    def s26_have_attack_target(self):
        return self.attackers[0] in self.targets

    def s28_attack_enemy_group(self):
        attacker = self.groups[self.attackers[0]]

        defender = self.groups[self.targets[self.attackers[0]]]

        self.killed_in_round += attacker.attack(defender, self.verbose)

    def s30_have_dead_group(self):
        return any([g.units <= 0 for g in self.groups.values()])

    def s32_remove_dead_group(self):
        
        self.groups = { g.group_id : g for g in self.groups.values() if g.units > 0 }

        self.attackers = deque([grpid for grpid in self.attackers if grpid in self.groups ])


    def s34_battle_over(self):
        for isimm in [True, False]:
            if len(self.get_groups_of_type(isimm)) == 0:
                return True

        return False

    def s35_poll_attack_queue(self):
        self.attackers.popleft()

    def s36_success_complete(self):
        pass    
    

    def s37_draw_complete(self):
        pass


def run_tests():
    
    pass


    