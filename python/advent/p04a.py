import json
from collections import deque, Counter

import utility as U
from finite_state import *

class LogEntry:

    def __init__(self, crec):
        self.orig = crec

        tcount = sum(cfunc() for cfunc in [self.is_guard_change, self.is_wake_up, self.is_fall_asleep])
        assert tcount == 1, "Unknown type for input record {}".format(crec)

    def is_guard_change(self):
        return "Guard" in self.orig

    def get_guard_id(self):
        assert self.is_guard_change()
        hashidx = self.orig.find("#")
        begnidx = self.orig.find("begins")
        return int(self.orig[hashidx+1:begnidx].strip())

    def get_isodate(self):
        return self.orig[1:1+len("1518-07-19")]

    def get_hour(self):
        prevlen = len("[1518-07-19 ")
        return int(self.orig[prevlen:prevlen+2])

    def get_minute(self):
        prevlen = len("[1518-07-19 00:")
        return int(self.orig[prevlen:prevlen+2])

    def is_wake_up(self):
        return "wakes" in self.orig

    def is_fall_asleep(self):
        return "asleep" in self.orig

    def __str__(self):
        return self.orig

class PMachine(FiniteStateMachine):
    
    
    def __init__(self):
        
        statemap = """
        {
            "HAE" : "F:CR",
            "IND" : "F:IGC",
            "IGC" : "F:IFA",
            "IFA" : "F:UW",
            "UGI" : "PE",
            "US" : "PE",
            "UW" : "PE",
            "PE": "HAE"
        }
        """
        
        FiniteStateMachine.__init__(self, json.loads(statemap))
        self.inputdata = deque([])

        self.current_date = None

        self.cur_guard_id = None

        # Moment when the guard fell asleep
        self.sleep_moment = None

        # Guard ID to pair [sleep, wake]
        self.guard2_sleep_wake = {}

    def get_result(self):
        bestminute = self.sleepy_counter(self.sleepiest_guard).most_common(1)[0][0]
        return self.sleepiest_guard * int(bestminute)

    def get_p2_result(self):

        def bestmin4guard(gid):
            mincountpr = self.sleepy_counter(gid).most_common(1)[0]
            return [gid, mincountpr[0], mincountpr[1]]

        timetuples = [bestmin4guard(gid) for gid in self.guard2_sleep_wake]
        timetuples = sorted(timetuples, key=lambda x: -x[2])

        for idx in range(10):
            print(timetuples[idx])

        besttup = timetuples[0]
        return besttup[0] * besttup[1]


    def s1_init_machine(self):
        initial = sorted(U.read_input_deque('p04'))

        for rec in initial:
            self.inputdata.append(LogEntry(rec))


        for idx in range(5):
            print(self.inputdata[idx])



    def s8_have_another_entry(self):
        return len(self.inputdata) > 0

    def s9_is_new_date(self):
        return self.current_date == None or self.inputdata[0].get_isodate() != self.current_date

    def s10_update_date(self):

        #newdate = self.inputdata[0].get_isodate()
        #print("Updating to new date {}".format(newdate))

        assert self.sleep_moment == None
        self.current_date = self.inputdata[0].get_isodate()


    def s11_is_guard_change(self):
        return self.inputdata[0].is_guard_change()

    def s12_update_guard_info(self):
        self.cur_guard_id = self.inputdata[0].get_guard_id()


    def s14_is_fall_asleep(self):
        return self.inputdata[0].is_fall_asleep()

    def s15_update_sleep(self):
        self.sleep_moment = self.inputdata[0]

    def s17_update_wake(self):
        assert self.cur_guard_id != None
        assert self.sleep_moment != None

        self.guard2_sleep_wake.setdefault(self.cur_guard_id, [])

        swpair = [self.sleep_moment, self.inputdata[0]]
        self.guard2_sleep_wake[self.cur_guard_id].append(swpair)

        self.sleep_moment = None


    def s19_poll_entry(self):
        self.inputdata.popleft()


    def total_guard_sleep_time(self, gid):
        return sum([c for _, c in self.sleepy_counter(gid).items()])

    def sleepy_counter(self, gid):
        scounter = Counter()
        for alpha, omega in self.guard2_sleep_wake[gid]:
            amin = alpha.get_minute()
            omin = omega.get_minute()
            assert omin > amin
            scounter.update(range(amin, omin))
        return scounter


    def s27_compute_result(self):
        guardtime = [(gid, self.total_guard_sleep_time(gid)) for gid in self.guard2_sleep_wake.keys()]
        guardtime = sorted(guardtime, key=lambda x: -x[1])
        print(guardtime)
        self.sleepiest_guard = guardtime[0][0]


    def s30_success_complete(self):
        pass    

        
        
    