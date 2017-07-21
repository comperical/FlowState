#!/usr/bin/python

import re, os, sys, fileinput, CompJava

 	
def runClass(extrainfo):
	
	runcall = "java -cp %s lifedesign.diagram.DiagramCli %s" % (CompJava.getBatchClassPath(), extrainfo)
	
	print runcall
	
	os.system(runcall)
		

if __name__ == "__main__":

	extrainfo = " ".join(sys.argv)
	
	runClass(extrainfo)


