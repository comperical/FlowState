#!/usr/bin/python

import re, os, sys, fileinput

def getCrmClassPath():
	return "/userdata/crm/compiled/jclass"
	
	

if __name__ == "__main__":

	# TODO: 
	jcompcall = "javac -d ../jclass/ -cp %s ../java/*.java" % (getCrmClassPath())
	
	print jcompcall
	
	os.system(jcompcall)
	
