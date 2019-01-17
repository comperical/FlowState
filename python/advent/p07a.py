import json
import string
from collections import deque, Counter

import utility as U
from finite_state import *

class Prereq:

    # Step C must be finished before step A can begin.
    def __init__(self, pr):
        self.prec = pr.strip()

    def get_precond(self):
        return self.extract("Step ")

    def get_pstcond(self):
        return self.extract("Step C must be finished before step ")

    def extract(self, prefix):
        alpha = len(prefix)
        return self.prec[alpha:alpha+1]



class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {   
            "AR" : "F:FC",
            "HAC" : "F:AAD",
            "IAR" : "F:PCL",
            "PCL" : "HAC",
            "AAD" : "F:AR,T:SC"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        
        # precondition --> list of postconditions
        self.pre2pst = {}

        # list of preconditions for each item
        self.pst2pre = {}

        self.allitems = set([])

        self.ready_list = []

        self.completed = []

        self.check_list = None

    def get_result(self):
        return "".join(self.completed)

    def s1_init_machine(self):
        
        inlist = U.read_input_deque('p07')

        for prec in inlist:
            req = Prereq(prec)

            self.pre2pst.setdefault(req.get_precond(), [])
            self.pre2pst[req.get_precond()].append(req.get_pstcond())

            self.pst2pre.setdefault(req.get_pstcond(), [])
            self.pst2pre[req.get_pstcond()].append(req.get_precond())            

            self.allitems.add(req.get_precond())
            self.allitems.add(req.get_pstcond())

            print("{} --> {}".format(req.get_precond(), req.get_pstcond()))

        print("{}".format(self.pre2pst))
        print("{}".format(self.pst2pre))
        print("{}".format(self.allitems))


    def s2_find_initial_ready(self):

        for item in self.allitems:
            if len(self.pst2pre.get(item, [])) == 0:
                print("Initiall ready item ={}".format(item))
                self.ready_list.append(item)

    def s3_any_ready(self):
        return len(self.ready_list) > 0

    def s4_emit_action(self):

        topitem = sorted(self.ready_list)[0]
        print("emitting action {}".format(topitem))

        self.check_list = deque(self.pre2pst.get(topitem, []))

        assert not topitem in self.completed, "Already have item {} in completed list {}".format(topitem, self.completed)
        self.completed.append(topitem)
        self.ready_list.remove(topitem)

    def s5_have_another_check(self):
        return len(self.check_list) > 0


    def s6_is_action_ready(self):
        nextitem = self.check_list[0]
        return all([prec in self.completed for prec in self.pst2pre.get(nextitem, [])])

    def s7_add_to_ready_list(self):
        nextitem = self.check_list[0]
        assert not nextitem in self.ready_list
        self.ready_list.append(nextitem)

    def s8_poll_check_list(self):
        self.check_list.popleft()

    def s27_all_actions_done(self):
        return len(self.completed) == len(self.allitems)

    def s29_fail_complete(self):
        pass    

    def s30_success_complete(self):
        pass    

        
        
    