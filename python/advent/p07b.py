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
            "FIR" : "AR",
            "AR" : "F:CT",
            "HIW": "F:CT",
            "HAC" : "F:AAD",
            "ATW" : "AR",
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

        self.check_list = deque([])

        self.clocktime = -1

        # clocktime -> [task ids complete then]
        self.completion_sched = {}

        # Worker ID -> task ID
        self.worker_task = {}

        self.testmode = False

        self.num_workers = 2 if self.testmode else 5

    def get_result(self):
        return "".join(self.completed)

    def s1_init_machine(self):
        
        inlist = U.read_input_deque('p07test' if self.testmode else 'p07')

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
                self.ready_list.append(item)
                print("Initial ready item ={}".format(item))



    def s3_clock_tick(self):

        self.clocktime += 1
        #print("Clock tick, time is {}".format(self.clocktime))

    def s4_mark_completed_tasks(self):

        #print("Schedule is {}".format(self.completion_sched))

        for topitem in self.completion_sched.get(self.clocktime, []):

            workers = [wkid for wkid, task in self.worker_task.items() if task == topitem]
            assert len(workers) == 1

            print("Marking task {} complete at time {}, completed by worker {} ".format(topitem, self.clocktime, workers[0]))
            self.check_list.extend(self.pre2pst.get(topitem, []))
            #print("Check list is {}".format(self.check_list))

            assert not topitem in self.completed, "Already have item {} in completed list {}".format(topitem, self.completed)
            self.completed.append(topitem)
            self.worker_task.pop(workers[0])


    def s5_have_another_check(self):
        return len(self.check_list) > 0

    def s6_is_action_ready(self):
        nextitem = self.check_list[0]
        isready = all([prec in self.completed for prec in self.pst2pre.get(nextitem, [])])
        print("Item {} is ready={} at time {}".format(nextitem, isready, self.clocktime))
        return all([prec in self.completed for prec in self.pst2pre.get(nextitem, [])])

    def s7_add_to_ready_list(self):
        nextitem = self.check_list[0]
        assert not nextitem in self.ready_list
        self.ready_list.append(nextitem)

    def s8_poll_check_list(self):
        self.check_list.popleft()

    def s10_any_ready(self):
        return len(self.ready_list) > 0

    def get_idle_worker(self):
        idlers = [wkid for wkid in range(self.num_workers) if wkid not in self.worker_task]
        return None if len(idlers) == 0 else idlers[0]

    def s11_have_idle_worker(self):
        return self.get_idle_worker() is not None

    def s15_assign_task2_worker(self):

        idler = self.get_idle_worker()
        topitem = sorted(self.ready_list)[0]
        comptime = self.clocktime + 1 + string.ascii_uppercase.find(topitem)
        comptime += 0 if self.testmode else 60

        print("Assigning action {} to worker {}, completing on {}".format(topitem, idler, comptime))

        self.worker_task[idler] = topitem
        self.completion_sched.setdefault(comptime, [])
        self.completion_sched[comptime].append(topitem)
        self.ready_list.remove(topitem)


    def s27_all_actions_done(self):
        return len(self.completed) == len(self.allitems)

    def s30_success_complete(self):
        pass    

        
        
    