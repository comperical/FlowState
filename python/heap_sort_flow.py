#!/usr/bin/python

from __future__ import print_function

import sys, json, random, math
from collections import deque

from finite_state import *

def next_collatz(n):
	
	assert n > 0, "N must be >= 0, found {}".format(n)
	
	if (n % 2) == 0:
		return n / 2
		
	return 3*n+1

class HeapSortMachine(FiniteStateMachine):
	
	
	def __init__(self, olist):
		
		statemap = """
		{
			"HANI" : "F:HR",
			"CBP"  : "F:HANI",
			
			"MCU"  : "CBP",
			"IHE"  : "T:SC",
			
			"CPHK" : "F:IHE",
			"HLK"  : "F:SDR",
			"HRK"  : "F:SDL",
			"LBR"  : "T:SDL,F:SDR",
			
			"MCDL" : "CPHK",
			"MCDR" : "CPHK"
		}
		"""
		
		FiniteStateMachine.__init__(self, json.loads(statemap))
		
		self.heap_list = []
		self.orig_list = olist
		
		self.cur_add_idx = 0
		self.cursor_position = -1
		
		self.set_exact_visit_count("ANI", len(olist))
		self.set_exact_visit_count("AHT2R", len(olist))
		
		self.set_max_allowed_visit("CPHK", math.ceil(len(olist)*math.log(len(olist),2)))
	
	def get_parent_position(self):
		return (self.cursor_position-1)/2
		
	def get_left_kid_pos(self):
		return 2*self.cursor_position+1
		
	def get_rght_kid_pos(self):
		return 2*self.cursor_position+2
	
	def get_or_none(self, idx):
		return self.heap_list[idx] if idx < len(self.heap_list) else None
	
	def s1_init_machine(self):
		pass
	
	def s2_have_another_new_item(self):
		return self.cur_add_idx < len(self.orig_list)
	
	def s3_add_new_item(self):
		self.heap_list.append(self.orig_list[self.cur_add_idx])
		self.cur_add_idx += 1
	
	def s4_move_cursor_2_new_leaf(self):
		self.cursor_position = len(self.heap_list)-1
	
	def s5_cursor_below_parent(self):
		
		kiditem = self.heap_list[self.cursor_position]
		paritem = self.heap_list[self.get_parent_position()]
		
		return kiditem < paritem
	
	def s6_swap_cursor_with_parent(self):
		
		self.__swap_position(self.get_parent_position())
	
	def __swap_position(self, otherpos):
		aitem = self.heap_list[self.cursor_position]
		bitem = self.heap_list[otherpos]
		
		self.heap_list[self.cursor_position] = bitem
		self.heap_list[otherpos] = aitem
	
	def s7_move_cursor_up(self):
		
		self.cursor_position = self.get_parent_position()
	
	def s8_heap_ready(self):
		
		self.orig_list[:] = []
	
	def s9_is_heap_empty(self):
		
		return len(self.heap_list) == 0 or self.heap_list[0] == None
	
	def s10_add_heap_top_2_result(self):
		
		self.orig_list.append(self.heap_list[0])
		
		self.heap_list[0] = None
	
	def s11_set_cursor_to_zero(self):
		self.cursor_position = 0
	
	def s12_cursor_pos_has_kid(self):
		return self.s13_have_left_kid() or self.s14_have_rght_kid()
		
	def s13_have_left_kid(self):
		return self.get_or_none(self.get_left_kid_pos()) != None
	
	def s14_have_rght_kid(self):
		return self.get_or_none(self.get_rght_kid_pos()) != None
	
	def s15_left_below_rght(self):
		
		leftkid = self.heap_list[self.get_left_kid_pos()]
		rghtkid = self.heap_list[self.get_rght_kid_pos()]
		
		return leftkid < rghtkid
	
	def s16_swap_down_left(self):
		self.__swap_position(self.get_left_kid_pos())
	
	def s18_swap_down_rght(self):
		self.__swap_position(self.get_rght_kid_pos())
	
	def s17_move_cursor_down_left(self):
		self.cursor_position = self.get_left_kid_pos()
	
	def s19_move_cursor_down_rght(self):
		self.cursor_position = self.get_rght_kid_pos()
	
	def s20_sort_complete(self):
		assert len(self.orig_list) == len(self.heap_list), "Mismatch is list sizes"
	

if __name__ == "__main__":
		
	if len(sys.argv) >= 2 and sys.argv[1] == 'diagram':
		create_diagram(HeapSortMachine(), sys.argv[2], keepgv=True)
		quit()
		
		
	mylist = range(10000)
	random.shuffle(mylist)
	
	hsmachine = HeapSortMachine(mylist)
	hsmachine.run2_completion()
	
	
	
		
		
	