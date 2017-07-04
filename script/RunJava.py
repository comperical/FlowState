#!/usr/bin/python

import re, os, sys, fileinput, DiaComp

 	
def runClass(extrainfo):
	
	runcall = "java -cp %s:../jclass net.danburfoot.flowstate.DiagramCli %s" % (DiaComp.getCrmClassPath(), extrainfo)
	
	print runcall
	
	os.system(runcall)
		

if __name__ == "__main__":

	extrainfo = " ".join(sys.argv[1:])
	
	runClass(extrainfo)


