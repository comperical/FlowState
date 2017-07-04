#!/usr/bin/python

import re, os, sys, fileinput, DiaComp

 	
def runClass(extrainfo):
	
	runcall = "java -cp %s lifedesign.diagram.DiagramCli %s" % (DiaComp.getBatchClassPath(), extrainfo)
	
	print runcall
	
	os.system(runcall)
		

if __name__ == "__main__":

	extrainfo = " ".join(sys.argv)
	
	runClass(extrainfo)


