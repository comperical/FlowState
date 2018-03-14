#!/usr/bin/python

from __future__ import print_function

import sys, json
from collections import deque

from finite_state import *

def next_collatz(n):
	
	assert n > 0, "N must be >= 0, found {}".format(n)
	
	if (n % 2) == 0:
		return n / 2
		
	return 3*n+1

class CollSeqMachine(FiniteStateMachine):
	
	
	def __init__(self, tvalue):
		
		statemap = """
		{
			"NQIC" : "F:AQTS",
			"ARTC" : "PQS",
			"AQTS" : "NQIC",
			
			"QSE" : "F:NQIC",
			"INAT" : "F:ANPTS"
		}
		"""
		
		FiniteStateMachine.__init__(self, json.loads(statemap))
		
		self.cache_map = {}
		
		self.not_in_cache = set()
		
		self.query_stack = deque()
		
		self.target_value = tvalue

	def s1_init_machine(self):
		
		self.cache_map[1] = 1
		
		for p in range(2, self.target_value+1000):
			self.not_in_cache.add(p)
		
	
	def s2_add_next_probe_to_stack(self):
		self.query_stack.append(self.get_next_probe_val())

	def get_next_probe_val(self):
		return min(self.not_in_cache)
	
	def s3_next_query_in_cache(self):
		nextcol = next_collatz(self.query_stack[0])
		return nextcol in self.cache_map

	def s4_add_result_to_cache(self):
		query = self.query_stack[0]
		nextcol = next_collatz(query)
		cacheval = self.cache_map[nextcol]
		
		#print("Cache hit: adding result {} for query {} to cache".format(cacheval+1, query))
		
		self.cache_map[query] = cacheval + 1
		
		if query in self.not_in_cache:
			self.not_in_cache.remove(query)
		

	def s5_add_query_to_stack(self):
		nextcol = next_collatz(self.query_stack[0])
		self.query_stack.appendleft(nextcol)
		
	def s6_poll_query_stack(self):
		popval = self.query_stack.popleft()
	
	def s7_query_stack_empty(self):
		# Python style: empty collections are False!!
		return not self.query_stack
	
	def s8_is_next_above_target(self):
		return self.get_next_probe_val() > self.target_value
	
	def s9_calc_complete(self):
		pass
	
	def get_max_collatz(self):
		"""
		This is the actual answer
		"""
		assert self.cur_state_func == self.s9_calc_complete
		
		resultlist = sorted(list(self.cache_map.items()), key=lambda x: -x[1])
		
		for i in range(5):
			print("First result is {}".format(resultlist[i]))
		
		return resultlist[0]


if __name__ == "__main__":
		
	if sys.argv[1] == 'diagram':
		create_diagram(CollSeqMachine(100), sys.argv[2], keepgv=True)
		quit()
		
		
	targetvalue = int(sys.argv[1])
	print("Running CollSeqMachine for targetvalue {}".format(targetvalue))
		
	cseqmachine = CollSeqMachine(targetvalue)
	cseqmachine.run2_completion()
	
	cseqmachine.get_max_collatz()
	