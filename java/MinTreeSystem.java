
package net.danburfoot.flowstate; 

import java.io.*;
import java.util.*;
import java.util.regex.*;
import java.util.stream.*;
import java.sql.*;

import lifedesign.basic.*;
import lifedesign.basic.LifeUtil.*;

import net.danburfoot.shared.*;
import net.danburfoot.shared.Util.*;
import net.danburfoot.shared.DiagramUtil.*;
import net.danburfoot.shared.InspectUtil.*;
import net.danburfoot.shared.FiniteState.*;

// Code to solve the IPSC 2008 Problem I
// https://ipsc.ksp.sk/2008/real/problems/i.html
// Inventing Test Data
public class MinTreeSystem
{
	public enum MinTreeCalcState implements StringCodeStateEnum
	{
		SetupEdgeList,
		
		InitComponentMap,
		
		HaveAnotherMstEdge,
		
		CalcEdgeContribution,
		
		UpdateComponentMap, 
		
		CheckInvariant,
		
		PollMstEdge,
		
		CalcComplete;

		public String getTransitionCode()
		{
			switch(this)
			{
				case HaveAnotherMstEdge: 	return "F->CC"; 
					
				case PollMstEdge:		return "HAME";

				default: 			return "";
			}
		}
	}
	
	public static class MinTreeCalcMachine extends FiniteStateMachineImpl
	{
		// Same format as in input: node A, node B, weight
		private LinkedList<List<Integer>> _edgeList = null;
		
		private int _nodeCount = -1;
		
		private Map<Integer, Integer> _componentMap = Util.treemap();
		
		private long _minGraphResult = 0L;
		
		public Enum[] getEnumStateList()
		{
			return MinTreeCalcState.values();	
		}
		
		public MinTreeCalcMachine()
		{
			super(MinTreeCalcState.SetupEdgeList);
		}				
		
		// Call this method externally to add the input data to the machine.
		public void setInputData(List<String> datalist)
		{
			LinkedList<String> gimplist = Util.linkedlistify(datalist);
			
			_nodeCount = Integer.valueOf(gimplist.poll().trim());
			
			_edgeList = Util.linkedlist();
			
			while(!gimplist.isEmpty())
			{
				String[] tok = gimplist.poll().trim().split(" ");
				
				List<Integer> edgerec = Util.listify(
						Integer.valueOf(tok[0])-1,
						Integer.valueOf(tok[1])-1,
						Integer.valueOf(tok[2])
					);
				
				_edgeList.add(edgerec);
			}
			
		}
		
		// Read in input, create list, sort it
		public void setupEdgeList()
		{
			Util.massert(_edgeList != null, "You must call setInputData(..) first");
			
			// Canonical MST sort operation, by weight.
			CollUtil.sortListByFunction(_edgeList, erec -> erec.get(2));
			
			_minGraphResult = _edgeList.stream()
							.map(erec -> erec.get(2))
							.collect(CollUtil.summingInt(x -> x));
			
		}
		
		public void initComponentMap()
		{
			for(int i : Util.range(_nodeCount))
				{ _componentMap.put(i, i); }
		}		
		
		long getResult()
		{
			return _minGraphResult;	
		}
		
		public void updateComponentMap()
		{
			int leftcomp = getCurComponent(true );
			int rghtcomp = getCurComponent(false);
			
			List<Integer> rghtlist = _componentMap
							.entrySet()
							.stream()
							.filter(me -> me.getValue() == rghtcomp)
							.map(me -> me.getKey())
							.collect(CollUtil.toList());
			
			rghtlist.stream().forEach(id -> _componentMap.put(id, leftcomp));
		}
		
		public void pollMstEdge()
		{
			_edgeList.poll();
		}
		
		private int getCurComponent(boolean isleft)
		{
			int nodeid = _edgeList.peek().get(isleft ? 0 : 1);
			
			Integer compid = _componentMap.get(nodeid);
			
			Util.massert(compid != null, "No component ID set for Node ID %d", nodeid);
			
			return compid;
		}
		
		// Utility method for debugging
		private Set<Integer> getComponentSet(int compid)
		{
			return Util.filter2set(_componentMap.keySet(), nodeid -> _componentMap.get(nodeid) == compid);	
		}
		
		public void calcEdgeContribution()
		{
			int leftcomp = getCurComponent(true );
			int rghtcomp = getCurComponent(false);
			
			int N = 0, M = 0;
			
			for(int compid : _componentMap.values())
			{
				if(compid == leftcomp)
					{ N++; }
				
				if(compid == rghtcomp)
					{ M++; }
			}
			
			int W = _edgeList.peek().get(2);
			
			_minGraphResult += (N*M - 1) * (W+1);
		}
		
		public boolean haveAnotherMstEdge()
		{
			return !_edgeList.isEmpty();
		}
		


		public void checkInvariant()
		{
			/*
			
			for(int a : Util.range(_nodeCount))
			{
				for(int b : Util.range(a+1, _nodeCount))
				{
					int acomp = _componentMap.get(a);
					int bcomp = _componentMap.get(b);
					
					if(acomp == bcomp)
						{ checkSameComponentPair(a, b); }
					else
						{ checkDiffComponentPair(a, b); }
				}
			}
			
			*/
		}
		
		private void checkSameComponentPair(int anode, int bnode)
		{
			Util.massertEqual(_componentMap.get(anode), _componentMap.get(bnode),
				"Subnode is component %d, but linknode is component %d, for a=%d, b=%d", anode, bnode);
		}
		
		private void checkDiffComponentPair(int anode, int bnode)
		{
			Util.massert(_componentMap.get(anode) != _componentMap.get(bnode),
				"Subnode is component %d, but linknode is component %d, for a=%d, b=%d", anode, bnode);
		}		
		
		@Override
		public List<String> getDiagnosticInfo()
		{
			List<String> dlist = Util.listify(
					Util.sprintf("MST Edge size is %d, first is %s", _edgeList.size(), (_edgeList.isEmpty() ? "--" : _edgeList.peek())),
					Util.sprintf("Component map is %s", _componentMap) 
			);
			
			
			if(!_componentMap.isEmpty() && !_edgeList.isEmpty())
			{
				dlist.add(Util.sprintf("Left Component Set is %s", getComponentSet(getCurComponent(true ))));
				dlist.add(Util.sprintf("Rght Component Set is %s", getComponentSet(getCurComponent(false))));
				
			};
			
			dlist.add(Util.sprintf("Min Graph Result: %d\n", _minGraphResult));
			
			
			
			return dlist;
		}
		
		
		private static void addMatrixData(List<String> dlist, int[][] matrixdata)
		{
			for(int i : Util.range(matrixdata.length))
			{
				List<Integer> row = Util.vector();
				
				for(int j : Util.range(matrixdata[i].length))
					{ row.add(matrixdata[i][j]); }
				
				dlist.add("\t" + Util.join(row, "  "));
			}			
		}
	}
	
	private static MinTreeCalcMachine _SING = null;
	
	public static MinTreeCalcMachine getSing()
	{
		if(_SING == null)
			{ reloadSing(); }
		
		return _SING;
	}	
	
	
	public static void reloadSing()
	{
		_SING = new MinTreeCalcMachine();
		
		List<String> flist = FileUtils.getReaderUtil()
							.setFile("/userdata/lifecode/datadir/ipsc/2008/SingleProblem.txt")
							.readLineListE();
		
		_SING.setInputData(flist);		
	}
}
