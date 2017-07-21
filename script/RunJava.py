#!/usr/bin/python

import re, os, sys, fileinput, CompJava

def getMainInner(basedir, targetclass):
	
	pathlist = findPathList(basedir, targetclass)
	
	assert len(pathlist) > 0, "Found no paths corresponding to %s" % (targetclass)
	assert len(pathlist) == 1, "Found multiple paths corresponding to %s :: %s" % ( targetclass, pathlist )
	
	return mungeFull2MainInner(basedir, pathlist[0])

def mungeFull2MainInner(basedir, fullpath):

	assert fullpath.startswith(basedir), "Full path should start with basedir %s, found %s" % (basedir, fullpath)
	
	thepath = fullpath[len(basedir)+1:]
	thepath = thepath[:-len(".class")]
		
	thepath = thepath.replace("/", ".")
		
	return thepath.split("$")

	
def findPathList(basedir, innerclass):
	
	hitlist = []
	
	completename = "%s.class" % (innerclass)
	innersuff = "$%s.class" % (innerclass)
	
	for (dirpath, dirnames, filenames) in os.walk("../jclass"):
		for onefile in filenames:
			if onefile == completename or onefile.endswith(innersuff):
				hitlist.append("%s/%s" % (dirpath, onefile))
				
	return hitlist
 	
def runClass(outerclass, innerclass, extrainfo):
	
	innerstr = ""
	
	if len(innerclass) > 0:
		innerstr = "innerclass=%s" % (innerclass)
	
	runcall = "java -cp ../jclass net.danburfoot.flowstate.EntryPoint %s %s %s" % (outerclass, innerstr, extrainfo)

	print runcall
	
	os.system(runcall)
		

if __name__ == "__main__":

	extrainfo = " ".join(sys.argv[2:])
	
	innerclass = sys.argv[1]
	
	# outerclass = findOuterClass(innerclass)
	
	[outerclass, innerclass] = getMainInner("../jclass", innerclass)
	
	runClass(outerclass, innerclass, extrainfo)


