
package net.danburfoot.flowstate; 

import java.io.*;
import java.util.*;
import java.util.regex.*;
import java.util.stream.*;
import java.sql.*;


import net.danburfoot.shared.*;
import net.danburfoot.shared.Util.*;
import net.danburfoot.shared.DiagramUtil.*;
import net.danburfoot.shared.InspectUtil.*;

import net.danburfoot.shared.FiniteState.*;

import lifedesign.basic.*;

import net.danburfoot.flowstate.MinTreeSystem.*;
import net.danburfoot.flowstate.SimpleCollatz.*;
import net.danburfoot.flowstate.HeapSortFlow.*;
import net.danburfoot.flowstate.MergeSortFlow.*;


// CLI interface to all the Diagram tools.
public class DiagramCli
{
	public static class RunSimpleColl extends ArgMapRunnable
	{
		public void runOp()
		{
			int maxn = _argMap.getInt("maxn", 10000);
			
			CollSeqMachine csm = new CollSeqMachine(maxn);
			csm.run2Completion();
			
			Util.pf("result = %s\n", csm.getResult());
			
			/*
			Map<Integer, Integer> lenmap = csm.getLengthMap();
			
			for(int start : lenmap.keySet())
			{
				int directlen = SimpleCollatz.directLengthCalc(start);
				
				Util.pf("Start Pt %d --> %d --> %d\n", start, lenmap.get(start), directlen);	
			}
				
			*/
		}
	}
	
	public static class TestEntryCode extends ArgMapRunnable
	{
		public void runOp()
		{
			Util.pf("Hello, Flow State\n");	
		}
	}
	
	public static class RunMinTree4File extends ArgMapRunnable
	{
		public void runOp()
		{
			boolean isbig = _argMap.getBit("isbig", false);
			
			String filename = Util.sprintf("i%d.in", (isbig ? 2 : 1));
			
			LinkedList<String> mainlist = Util.cast(
							FileUtils.getReaderUtil()
								.setFile("/userdata/lifecode/datadir/ipsc/2008/" + filename)
								.useLinkedList(true)
								.readLineListE());
									
			int numproblem = Integer.valueOf(mainlist.poll());
			
			for(int i : Util.range(numproblem))
			{
				List<String> oneprob = readProblemDesc(mainlist);	
				
				
				MinTreeCalcMachine mtcm = new MinTreeCalcMachine();
				mtcm.setInputData(oneprob);
				
				mtcm.run2Completion();
				
				Util.pf("%d\n", mtcm.getResult());
			}
			
		}
		
		private List<String> readProblemDesc(LinkedList<String> gimplist)
		{
			Util.massert(gimplist.peek().trim().isEmpty());
			
			gimplist.poll();
			
			int nodecount = Integer.valueOf(gimplist.peek().trim());
			
			List<String> plist = Util.vector();
			
			while(plist.size() < nodecount)
				{ plist.add(gimplist.poll()); }
				
			Util.massert(gimplist.isEmpty() || gimplist.peek().trim().isEmpty());
			
			return plist;
		}
	}	
	
	
	public static class RunMinTree extends ArgMapRunnable
	{
		public void runOp()
		{
			// MinTreeCalcMachine rmachine = MinTreeSystem.getSing();
			// CommLineFsmRunner crunner = new CommLineFsmRunner(rmachine);
			// crunner.runFromCommLine();
		}
	}	
	
	
	public static class RunCommLine extends ArgMapRunnable
	{
		public void runOp()
		{
			FiniteStateMachineImpl fsm = getMachine();
			CommLineFsmRunner clrunner = new CommLineFsmRunner(getMachine());
			clrunner.runFromCommLine();
		}
		
		private FiniteStateMachineImpl getMachine()
		{
			String s = _argMap.getStr("machine");
			
			switch(s)
			{
				// case "mintree": 	return new MinTreeCalcMachine();
				//case "simplecoll":	return new CollSeqMachine(10000);
				
				default: throw new RuntimeException("Unknown machine name: " + s);
			}
		}
	}	
	
	public static class RunCollatzMachine extends ArgMapRunnable
	{
		
		public void runOp()
		{
			int maxvalue = _argMap.getInt("maxvalue", 100);
			
			CollSeqMachine csmach = new CollSeqMachine(maxvalue);
			
			csmach.run2Completion();
			
			Pair<Long, Long> respair = csmach.getResult();
			
			Util.pf("Result is %d::%d\n", respair._1, respair._2);
			
			Util.pf("%s\n", SimpleCollatz.getSequenceString(respair._1));
			
		}
	}
	
	
	public static class CreateDiagramList extends ArgMapRunnable
	{
		
		public void runOp()
		{
			File outputdir = new File(_argMap.getStr("outputdir"));
			
			Util.massert(outputdir.exists() && outputdir.isDirectory(),
				"Problem with output directory %s", outputdir);
			
			for(FiniteStateMachineImpl fsmi : getMachineList())
			{
				FsDiagramCreator.build()
						.setOutputDir(outputdir)
						.setMachine(fsmi)
						.runProcess();
			}
		}
		
		private List<FiniteStateMachineImpl> getMachineList()
		{
			return Util.listify(
				// new MinTreeCalcMachine(),
				new CollSeqMachine()
				// new HeapSortMachine()
				// new MergeSortMachine()
			);
		}
	}
	 
	
	public static class HeapSortTest extends ArgMapRunnable
	{
		public void runOp()
		{
			int listsize = _argMap.getInt("listsize", 100);
			
			List<Integer> datalist = getDataList(listsize);
			
			List<Integer> sortlist = Util.arraylist(datalist);
			Collections.sort(sortlist);
			
			// Collections.shuffle(rlist);
			
			double startup = Util.curtime();
			
			HeapSortMachine<Integer> hsm = new HeapSortMachine<Integer>();
			
			for(int r : datalist)
				{ hsm.add(r); }	
			
			List<Integer> reslist = hsm.getResult();
			
			double sorttime = Util.curtime() - startup;
			
			Util.massert(reslist.equals(sortlist), "Sorting mistake");
			
			Util.pf("Sorted %d elements okay, took %.03f sec\n", reslist.size(), sorttime/1000);
		}
		
		
		private List<Integer> getDataList(int n)
		{
			Random r = new Random();
			
			List<Integer> dlist = Util.vector();
			
			while(dlist.size() < n)
				{ dlist.add(r.nextInt()); }	
			
			return dlist;
		}
	}
	
	public static class MergeSortTest extends ArgMapRunnable
	{
		public void runOp()
		{
			int listsize = _argMap.getInt("listsize", 100);
			
			ArrayList<Integer> datalist = getDataList(listsize);
			
			List<Integer> sortlist = Util.arraylist(datalist);
			Collections.sort(sortlist);
			
			// Collections.shuffle(rlist);
			
			double startup = Util.curtime();
			
			List<Integer> reslist = MergeSortFlow.runMergeSort(datalist);
			
			double sorttime = Util.curtime() - startup;
			
			// Util.pf("%s\n%s\n", sortlist, reslist);
			
			Util.massert(reslist.equals(sortlist), "Sorting mistake");
			
			Util.pf("Sorted %d elements okay, took %.03f sec\n", reslist.size(), sorttime/1000);
		}
		
		
		private ArrayList<Integer> getDataList(int n)
		{
			Random r = new Random();
			
			ArrayList<Integer> dlist = Util.arraylist();
			
			while(dlist.size() < n)
				{ dlist.add(r.nextInt()); }	
			
			return dlist;
		}
	}	
	
	
	
	public static void main(String[] args) throws Exception
	{
		
		// {{{
		ArgMap amap = ArgMap.getClArgMap(args);
		
		String simpleclass = args[0];
		String fullclass = Util.sprintf("%s$%s", DiagramCli.class.getName(), simpleclass);
		
		ArgMapRunnable amr;
		
		try {
			amr = (ArgMapRunnable) Class.forName(fullclass).newInstance();
			
		} catch (Exception ex) {
			
			Util.pferr("Error creating ArgMapRunnable from class %s\n", fullclass);
			Util.pferr("%s\n", ex.getMessage());
			return;
		}
		
		amr.initFromArgMap(amap);
		amr.runOp();
		
		// }}}
	}
		

}
