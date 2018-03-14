#!/usr/bin/python

from __future__ import print_function

import os, copy

GV_NODE_SHAPE_LIST = ["box", "diamond", "ellipse"]

class GraphVizTool:
	
	def __init__(self):
		
		self.node_set = set()
		self.edge_set = set()
		
		self.node_shape_map = {}
		self.edge_label_map = {}
		
		self.prop_map = {}
		
		self.prop_map["graphname"] = "MyGraphName"
		self.prop_map["graphlabel"] = "MyGraphLabel"
		self.prop_map["defnodeshape"] = "box"
		self.prop_map["fontsize"] = str(12)
	

	def set_property(self, propname, propval):
		
		assert propname in self.prop_map, "Unknown property name {}".format(propname)
		self.prop_map[propname] = propval
		
	def add_node(self, nodecode, dupokay=False, nodeshape="box"):
		assert not nodecode in self.node_set or dupokay, "Already have node {}".format(nodecode)
		self.node_set.add(nodecode)
		self.node_shape_map[nodecode] = nodeshape
		
		
	def add_edge(self, srcnode, dstnode, label=None, dupokay=False):
		assert srcnode in self.node_set, "Bad Node {}".format(srcnode)
		assert dstnode in self.node_set, "Bad Node {}".format(dstnode)
		assert dupokay or not (srcnode, dstnode) in self.edge_set, "Already have edge {} {}".format(srcnode, dstnode)
		
		self.edge_set.add((srcnode, dstnode))
		
		if label is not None:
			self.edge_label_map[(srcnode, dstnode)] = label
				
	def get_node_list4_shape(self, gvshape):
		return [k for (k,v) in self.node_shape_map.items() if v == gvshape]
		
	def get_gv_line_output(self):
		
		dgline = "digraph {} ".format(self.prop_map["graphname"]) + "{"
		yield dgline
		
		for nodeshape in GV_NODE_SHAPE_LIST:
			nodelist = self.get_node_list4_shape(nodeshape)
			yield "node [shape={}] {}".format(nodeshape, "; ".join(nodelist))
		
		for (srcnode, dstnode) in self.edge_set:
			labelstr = self.edge_label_map.get((srcnode, dstnode), "")
			labelstr = "" if not labelstr else "[label={}]".format(labelstr)			
			yield "{}->{} {};".format(srcnode, dstnode, labelstr)
		
		yield "overlap=false"
		yield "label={}".format(self.prop_map.get("graphlabel"))
		yield "fontsize={}".format(int(self.prop_map.get("fontsize")))
		yield "}"
