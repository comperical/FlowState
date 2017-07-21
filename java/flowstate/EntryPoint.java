
package net.danburfoot.flowstate; 

import java.io.*;
import java.util.*;

import net.danburfoot.shared.*;
import net.danburfoot.shared.Util.*;
import net.danburfoot.shared.DiagramUtil.*;

import net.danburfoot.shared.FiniteState.*;

import net.danburfoot.flowstate.MinTreeSystem.*;
import net.danburfoot.flowstate.SimpleCollatz.*;
import net.danburfoot.flowstate.HeapSortFlow.*;
import net.danburfoot.flowstate.MergeSortFlow.*;
import net.danburfoot.flowstate.SudokuSystem.*;

public class EntryPoint
{
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
				new SudokuGridMachine(),
				new SudokuSearchMachine()
				// new MergeSortMachine()
			);
		}
	}
	 
	
	public static void main(String[] args) throws Exception
	{
		// {{{
		ArgMap amap = ArgMap.getClArgMap(args);
		
		String outerclass = args[0];
		String innerclass = args[1]; 
		String fullclass = Util.sprintf("net.danburfoot.flowstate.%s$%s", outerclass, innerclass); 
		
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
