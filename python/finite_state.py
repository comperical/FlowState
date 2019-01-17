#!/usr/bin/python

from __future__ import print_function

import os, re, copy
import sys

from diagram_util import GraphVizTool

STATE_FUNCTION_RE = r's(\d{1,3})_(.*)'

def get_basic_name(functionref):
	return re.match(STATE_FUNCTION_RE, functionref.__name__).group(2)

def get_acro_name(functionref):
	return basic2_acro(get_basic_name(functionref))

def get_camel_name(functionref):
	return basic2_camel(get_basic_name(functionref))

def basic2_acro(basicname):
	# Split on underscores
	fclist = [tok[0] for tok in basicname.split("_")]
	return "".join(fclist).upper()

def basic2_camel(basicname):
	# Split on underscores
	fclist = [tok[0].upper() + tok[1:] for tok in basicname.split("_")]
	return "".join(fclist)
	
def is_end_state_name(functionref):
	return any([get_basic_name(functionref).endswith(suffstr) for suffstr in ["_complete", "_end"]])

def create_diagram(fsmachine, outputdir, keepgv=False):
	
	assert os.path.exists(outputdir) and os.path.isdir(outputdir), "Problem with output directory {}".format(outputdir)

	print("Going to create diagram in director {}".format(outputdir))
	
	gvtool = fsmachine.get_gv_tool()
	
	gvpath = os.path.join(outputdir, "StateThing.gv")
	pngpath = os.path.join(outputdir, "StateThing.png")
	
	with open(os.path.join(outputdir, "StateThing.gv"), 'w') as fh:
		for oneline in gvtool.get_gv_line_output():
			fh.write(oneline + "\n")
			
	dotcall = "dot -Tpng -O {}".format(gvpath)
	print(dotcall)
	os.system(dotcall)



class FiniteStateMachine:
		
	def __init__(self, smap):
			
		self.state_list = []
		self.acro2_func_map = {}
		self.name2_func_map = {}	
		
		self.transition_map = {}
		
		
		self.exact_visit_map = {}
		self.max_visit_map = {}
			
		self.step_count = 0

		self.__init_state_info()
				
		self.build_transition_map(smap)

		self.show_transition_map()
		
		self.cur_state_func = self.state_list[0]
		
		self.state_visit_count = dict([(sfunc, 0) for sfunc in self.state_list])

	def build_transition_map(self, smap):
		
		
		for key in smap:
			assert key in self.acro2_func_map or key in self.name2_func_map, "No function found for state {}".format(key)
		
		
		for (idx, statefunc) in enumerate(self.state_list):
			
			default_next = None if idx >= len(self.state_list)-1 else self.state_list[idx+1]
			
			#if default_next is not None:
			#	print("For state {}, default next is {}".format(get_acro_name(statefunc), get_acro_name(default_next)))
			
			for codeword in [get_acro_name(statefunc), get_basic_name(statefunc)]:
				if codeword in smap:
					self.transition_map[statefunc] = self.interpret_transition_code(smap[codeword], default_next)
			
			if is_end_state_name(statefunc):
				self.transition_map[statefunc] = 0
			
			if not statefunc in self.transition_map:
				assert default_next is not None, "No default available for state {}".format(get_acro_name(statefunc))
				self.transition_map[statefunc] = default_next

		def statetype(trans):
			if trans == 0:
				return "end"
			if type(trans) == dict:
				return "query"
			return "op"

		self.state_type_map = { sfunc : statetype(trns) for sfunc, trns in self.transition_map.items() }
				
			
	def interpret_transition_code(self, strcode, default_next):
		
		if not ("," in strcode or ":" in strcode):
			return self.lookup_state_name(strcode)
			
		transmap = {} 
			
		for onepair in strcode.split(","):
			tfcode, codename = onepair.split(":")
			assert tfcode.upper() in ['T', 'F'], "Bad true/false code {}, expected T or F".format(tfcode)
			tfval = { 'T' : True, 'F' : False}.get(tfcode.upper())
			transmap[tfval] = self.lookup_state_name(codename)
			
		assert len(transmap) >= 1
		
		for tfdef in [True, False]:
			if not tfdef in transmap:
				transmap[tfdef] = default_next
				
		return transmap
		
	def lookup_state_name(self, strcode):
		
		for amap in [self.acro2_func_map, self.name2_func_map]:
			if strcode in amap:
				return amap[strcode]
			
		assert False, "No state found corresponding to strcode {}".format(strcode)
						
				
	def __init_state_info(self):
		
		slist = []
		
		for oneitem in dir(self):
						
			matchdata = re.match(STATE_FUNCTION_RE, oneitem)
			
			if matchdata == None: 
				continue
				
			functionref = getattr(self, oneitem)
			functionidx = int(matchdata.group(1))
			basicname = matchdata.group(2)
			
			slist.append((functionidx, functionref))
			self.name2_func_map[basicname] = functionref
			self.acro2_func_map[basic2_acro(basicname)] = functionref
				

		idxes = [idx for idx, _ in slist]
		if len(set(idxes)) < len(idxes):
			for prbidx in idxes:
				if len([myidx for myidx in idxes if myidx == prbidx]) > 1:
					print("Error: Have repeated function index: {}".format(prbidx), file=sys.stderr)
			assert False, "Repeated function indexes"


		for (fidx, fref) in sorted(slist, key=lambda pr: pr[0]):
			self.state_list.append(fref)

				
	def show_transition_map(self):
		
		#print("--------\nTransition Map:")
		
		for functionref in self.state_list:
			
			transition = self.transition_map[functionref]			
			#print("For state {}".format(get_acro_name(functionref)), end='')
			
			if type(transition) == type({}):
				#print("\t query transition T:{}, F:{}".format(get_acro_name(transition[True]), get_acro_name(transition[False])))
				continue
				
			if transition == 0:
				#print("\tmachine complete")
				continue
				
			#print("\tOp transition {}".format(get_acro_name(transition)))
	
	def set_max_allowed_visit(self, statecode, numvisit):
		
		assert type(statecode) == type("x"), "Use string codes for the method"
				
		for namemap in [self.acro2_func_map, self.name2_func_map]:
			if statecode in namemap:
				self.max_visit_map[namemap[statecode]] = numvisit
				return

		assert False, "StateCode {} not found in either basic or ACRO state map".format(statecode)
	
	def set_exact_visit_count(self, statecode, numvisit):
		
		self.set_max_allowed_visit(statecode, numvisit)

		for namemap in [self.acro2_func_map, self.name2_func_map]:
			if statecode in namemap:
				self.exact_visit_map[namemap[statecode]] = numvisit
	
	def set_state(self, statefunc):
		
		assert statefunc in self.state_map, "Unknown state function {}".format(statefunc.__name__)
	
		self.cur_state_func = statefunc
	
	def get_state(self):
		return self.cur_state_func.__name__
		
	def get_state_type(self, statefunc):
		return self.state_type_map[statefunc]

	def run_until(self, conditfunc):

		while True:
			if conditfunc(self):
				break

			self.run_one_step()

	def run_one_step(self):
		
		statetype = self.get_state_type(self.cur_state_func)
		
		# Log the state visit
		self.state_visit_count[self.cur_state_func] += 1
		
		for (sfunc, maxvisit) in self.max_visit_map.items():
			assert self.state_visit_count[sfunc] <= maxvisit, "Visited state {} too many times".format(get_basic_name(sfunc))		
		
		assert statetype is not "end", "Attempt to run end state {}, should check for complete before calling".format(self.cur_state_func.__name__)
		
		myreturn = self.cur_state_func()
		
		#print("Ran curstate {}, statetype is {}, return value is {}".format(curbasic, statetype, myreturn))
				
		if statetype == "op":
			assert myreturn == None, "Got return value of {} in op state {}, op state should return None".format(myreturn, self.cur_state_func.__name__)
			nextstate = self.transition_map[self.cur_state_func]
		else:
			assert myreturn in [True, False], "Got return value of {} in query state {}, query state should return True/False".format(myreturn, self.cur_state_func.__name__)
			nextstate = self.transition_map[self.cur_state_func][myreturn]
		
		#print("\t {} --> {}".format(curbasic, get_basic_name(nextstate)))
		
		self.cur_state_func = nextstate

		self.step_count += 1


	def run2_step_count(self, stepnum):
		while self.step_count != stepnum:			
			self.run_one_step()

	
	def run2_completion(self):
		while self.get_state_type(self.cur_state_func) != "end":
			self.run_one_step()
			
		for (sfunc, expvisit) in self.exact_visit_map.items():
			assert self.state_visit_count[sfunc] == self.exact_visit_map[sfunc], (
				"Visited state {} {} times, but expected {}".format(get_basic_name(sfunc), self.state_visit_count[sfunc], expvisit))
			
			
	def get_gv_tool(self, graphlabel="FsMachine"):
		
		gvtool = GraphVizTool()
		gvtool.set_property("graphlabel", graphlabel)
		
		type2shape = { "op" : "box", "query" : "ellipse", "end" : "diamond" }
		
		for statefunc in self.state_list:
			statetype = self.get_state_type(statefunc)			
			gvtool.add_node(get_camel_name(statefunc), nodeshape=type2shape[statetype])
			
		for statefunc in self.state_list:
			
			statetype = self.get_state_type(statefunc)
			
			if statetype == "end":
				continue
			if statetype == "op":
				nextstate = self.transition_map[statefunc]
				gvtool.add_edge(get_camel_name(statefunc), get_camel_name(nextstate))
				continue
				
			# Now we're dealing with a query state
			for (istrue, nextstate) in self.transition_map[statefunc].items():
				labelstr = str(istrue)[0]
				gvtool.add_edge(get_camel_name(statefunc), get_camel_name(nextstate), label=labelstr)
	
		return gvtool


