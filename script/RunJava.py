#!/usr/bin/python

import re, os, sys, fileinput, CompJava

def findOuterClass(innerclass):
	
	targsuffix = "%s.class" % (innerclass)
	
	for (dirpath, dirnames, filenames) in os.walk("../jclass"):
		
		for onefile in filenames:
			if not onefile.endswith(targsuffix):
				continue
				
			print "OneFile is %s" % (onefile)
			
			return onefile.split("$")[0]
			
			
	assert False, "Could not found inner class with name %s" % (innerclass)
		
	
 	
def runClass(outerclass, innerclass, extrainfo):
	
	runcall = "java -cp ../jclass net.danburfoot.flowstate.EntryPoint %s %s %s" % (outerclass, innerclass, extrainfo)

	print runcall
	
	os.system(runcall)
		

if __name__ == "__main__":

	extrainfo = " ".join(sys.argv[2:])
	
	innerclass = sys.argv[1]
	
	outerclass = findOuterClass(innerclass)
	
	runClass(outerclass, innerclass, extrainfo)


