
package net.danburfoot.flowstate; 

import java.io.*;
import java.util.*;
import java.util.regex.*;
import java.util.stream.*;
import java.sql.*;


import net.danburfoot.shared.*;
import net.danburfoot.shared.Util.*;
import net.danburfoot.shared.DiagramUtil.*;

import net.danburfoot.shared.FiniteState.*;

import net.danburfoot.flowstate.MinTreeSystem.*;
import net.danburfoot.flowstate.SimpleCollatz.*;
import net.danburfoot.flowstate.HeapSortFlow.*;
import net.danburfoot.flowstate.MergeSortFlow.*;
import net.danburfoot.flowstate.SudokuSystem.*;
import net.danburfoot.flowstate.LargeSumFlow.*;


// CLI interface to all the Diagram tools.
public class EntryPoint
{
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
				// new CollSeqMachine()
				// new SudokuGridMachine(),
				// new SudokuSearchMachine()
				//new LargeSumMachine()
				// new MergeSortMachine()
				new HeapSortMachine()
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
					
			double startup = Util.curtime();
			
			HeapSortMachine<Integer> hsm = new HeapSortMachine<Integer>(datalist);
			hsm.run2Completion();						
			
			double sorttime = Util.curtime() - startup;
			
			Util.massert(datalist.equals(sortlist), 
				"Sorting mistake, data is %s, sorted is %s", datalist, sortlist);
			
			Util.pf("Sorted %d elements okay, took %.03f sec\n", datalist.size(), sorttime/1000);
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
		
		// The first argument is the outer class
		String fullclass = args[0];

		// Optionally specify an inner class
		if(amap.containsKey("innerclass"))
			{ fullclass = fullclass + "$" + amap.getStr("innerclass"); }
				
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
