#!/usr/bin/python

import re, os, sys, fileinput

from shutil import copyfile

def getSrcFileList():
	return ["Util", "FiniteState", "Pair", "DiagramUtil", "ArgMap", "CollUtil", "FileUtils"]
	
def clearSharedDir():
	
	delcall = "rm /userdata/external/FlowState/java/shared/*.java"
	
	os.system(delcall)
	
def copyCode2Dir():
	
	for onesrc in getSrcFileList():
		
		farrpath = "/userdata/crm/src/java/shared/%s.java" % (onesrc)
		nearpath = "/userdata/external/FlowState/java/shared/%s.java" % (onesrc)
		
		print "Going to copy %s ---> %s" % (farrpath, nearpath)
		
		# Change file to writable
		#chmodcall = "chmod 644 %s" % (nearpath)
		#os.system(chmodcall)		
		
		copyfile(farrpath, nearpath)
		
		# Change file back to read-only
		#chmodcall = "chmod 444 %s" % (nearpath)
		#os.system(chmodcall)	
	
	


if __name__ == "__main__":
	
	#clearSharedDir()

	#copyCode2Dir()

	dirlist = ["flowstate"]
	#dirlist = ["shared"]

	for onedir in dirlist:
	
		jcompcall = "javac -Xlint:unchecked -d ../jclass/ -cp ../jclass ../java/%s/*.java" % (onedir)
	
		print jcompcall
	
		os.system(jcompcall)
	
