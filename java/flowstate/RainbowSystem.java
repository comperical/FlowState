
package net.danburfoot.flowstate; 

import java.util.*;


import net.danburfoot.shared.*;
import net.danburfoot.shared.Util.*;
import net.danburfoot.shared.DiagramUtil.*;
import net.danburfoot.shared.FiniteState.*;

public class RainbowSystem
{
	/*
	
	public static class CityId implements Comparable<CityId>
	{	
		public final int C;
		
		public CityId(int c)
		{
			C = c;
		}
		
		public int compareTo(CityId that)
		{
			return this.C - that.C;	
		}
		
		public boolean equals(CityId that)
		{
			return this.C == that.C;	
		}
		
		public String toString()
		{
			return C+"";
		}	
		
	}
	
	
	public enum RainbowState implements StringCodeStateEnum
	{
		// {{{
		
		InitProblemSetup,	
		
		BuildPath2Root,
		
		// Did we successfully finish the graph?
		IsGraphComplete, 
		
		HaveAnotherUpdate,
		
		GetFullPath2Root,
		
		PeelPathOverLap,
		
		UpdateAndCount,
		
		ClearUpdateInfo,
		
		GraphFailComplete, // Failed to complete the graph, bad input
		QueryComplete;
		
		
		public String getTransitionCode()
		{
			switch(this)
			{
				case IsGraphComplete:		return "F->GFC";
					
				case HaveAnotherUpdate:		return "F->QC";
					
				case ClearUpdateInfo:		return "HAU";
					
				case GraphFailComplete:		return "0";
					
				default:			return ""; 
			}
		}
		
		// }}}
	}			
	
	
	
	public static class RainbowMachine extends FiniteStateMachineImpl
	{
		// {{{
		
		// This is PROVIDED by the caller code.
		private SortedMap<CityId, Set<CityId>> _linkMap = Util.treemap();
		
		private LinkedList<Triple<CityId, CityId, String>> _updateList = Util.linkedlist();
		
		// Used during construction of path2Root
		private LinkedList<CityId> _linkProcList = Util.linkedlist();
		
		private Vector<List<City>> _path2RootList = Util.vector();
		// private Map<CityId, List<CityId>> _path2RootMap = Util.treemap();
		
		// These are null normally, and get cleared on the clear update info step
		private LinkedList<CityId> _leftPath = null;
		private LinkedList<CityId> _rghtPath = null;
		
		// Count of color updates
		private Map<String, Integer> _colorUpdateMap = Util.linkedhashmap();
		
		// Current color of links
		private Map<Pair<CityId, CityId>, String> _curColorMap = Util.treemap();
		
		
		public RainbowMachine()
		{
			super(RainbowState.InitProblemSetup);
			
			for(String color : Util.listify("red", "orange", "yellow", "green", "blue", "indigo", "violet"))
			{
				_colorUpdateMap.put(color, 0);	
			}	
		}
		
		public void initProblemSetup()
		{
			
		}
		
		void loadSingleProblem(String fpath)
		{
			List<String> datalist = FileUtils.getReaderUtil()
								.setFile(fpath)
								.readLineListE();
				
			setInputData(datalist);		
		}		
		
		void setInputData(List<String> datalist)
		{
			Util.massertEqual(getState(), RainbowState.InitProblemSetup,
				"Current state is %s, but this method can only be called in state %s");
			
			
			LinkedList<String> gimplist = Util.linkedlistify(datalist);
			
			int numcity = Integer.valueOf(gimplist.poll().trim());
			
			for(int nl : Util.range(numcity-1))
			{
				String gimprec = gimplist.poll();
				String[] linkrec = gimprec.trim().split(" ");
				
				// Util.pf("Record is %s\n", gimprec);
				
				CityId a = new CityId(Integer.valueOf(linkrec[0]));
				CityId b = new CityId(Integer.valueOf(linkrec[1]));
				
				_linkMap.putIfAbsent(a, new TreeSet<CityId>());
				_linkMap.putIfAbsent(b, new TreeSet<CityId>());
				
				_linkMap.get(a).add(b);
				_linkMap.get(b).add(a);
				
				_curColorMap.put(getLinkPair(a, b), "grey");
			}
			
			int numupdate = Integer.valueOf(gimplist.poll().trim());
			
			for(int nu : Util.range(numupdate))
			{
				String gimprec = gimplist.poll();
				
				String[] toklist = gimprec.trim().split(" ");
				
				CityId a = new CityId(Integer.valueOf(toklist[0]));
				CityId b = new CityId(Integer.valueOf(toklist[1]));
				
				Util.massert(_linkMap.containsKey(a) && _linkMap.containsKey(b));
				
				_updateList.add(Triple.build(a, b, toklist[2].trim()));
			}
			
		}
		
		public void buildPath2Root()
		{
			CityId rootcity = _linkMap.firstKey();
			
			// Root node has 1-element list pointing to itself.
			_path2RootMap.put(rootcity, new Vector<CityId>());
			_path2RootMap.get(rootcity).add(rootcity);
			
			LinkedList<CityId> pq = Util.linkedlist();
			pq.add(rootcity);
			
			SimpleTimer stimer = SimpleTimer.buildAndStart();
			
			while(!pq.isEmpty())
			{
				CityId nextcity = pq.poll();
				List<CityId> rootpath = _path2RootMap.get(nextcity);
				
				// Sanity check of setup				
				{
					Util.massert(rootpath != null && !rootpath.isEmpty(),
						"Found null or empty rootpath for city %d", nextcity.C);
				
					Util.massert(rootpath.get(0).equals(nextcity),
						"By convention source city is element 0 of path2root list");
					
					Util.massert(Util.getLast(rootpath).equals(rootcity),
						"By convention root city is last element of path2root list");
				}
				
				for(CityId linkcity : _linkMap.get(nextcity))
				{
					// This might actually be an error
					if(_path2RootMap.containsKey(linkcity))
						{ continue; }
					
					List<CityId> newpath = Util.listify(linkcity);
					newpath.addAll(rootpath);
					
					_path2RootMap.put(linkcity, newpath);
					
					pq.add(linkcity);
				}
				
				if(_path2RootMap.size() % 1000 == 0)
				{
					Util.pf("Root map size is %d, took %.03f sec\n", 
						_path2RootMap.size(), stimer.getTimeSinceStartSec());
					
				}
			}
		}
		
		private void showPath2Root()
		{
			Util.pf("Path 2 Root Map: \n");
			
			for(CityId onecity : _path2RootMap.keySet())
			{
				Util.pf("\t%d --> %s\n", onecity.C, _path2RootMap.get(onecity));	
			}
		}
		
		public void getFullPath2Root()
		{
			_leftPath = Util.linkedlistify(_path2RootMap.get(_updateList.peek()._1));
			_rghtPath = Util.linkedlistify(_path2RootMap.get(_updateList.peek()._2));
		}		
		
		public void peelPathOverLap()
		{
			while(true)
			{
				CityId left = _leftPath.pollLast();
				CityId rght = _rghtPath.pollLast();
				
				// Util.pf("Polled Left=%d and Rght=%d from pathlist\n", left.C, rght.C);
				
				Util.massertEqual(left.C, rght.C,
					"Left City is %d, but Rght is %d");
				
				if(_leftPath.isEmpty() || _rghtPath.isEmpty())
				{
					_leftPath.addLast(left);
					break;
				}
				
				CityId nextleft = _leftPath.peekLast();
				CityId nextrght = _rghtPath.peekLast();
				
				if(nextleft.C != nextrght.C)
				{
					//Util.pf("Have NextLeft=%d but NextRght=%d\n",
					//			nextleft.C, nextrght.C);
					
					_leftPath.addLast(left);
					break;					
				}
			}
		}
		
		List<CityId> composeSrc2DstPath()
		{
			if(_leftPath == null)
				{ return null; }
			
			List<CityId> src2dst = Util.vector();
			
			List<CityId> revrght = Util.vector(_rghtPath);
			Collections.reverse(revrght);
			
			src2dst.addAll(_leftPath);
			src2dst.addAll(revrght);
			
			return src2dst;
		}
		
		private Pair<CityId, CityId> getLinkPair(CityId a, CityId b)
		{
			return a.C < b.C ? 
					Pair.build(a, b) : 
					Pair.build(b, a) ;
		}
		
		
		public void updateAndCount()
		{
			Triple<CityId, CityId, String> update = _updateList.peek();
			
			List<CityId> pathlist = composeSrc2DstPath();
			
			Util.massert(pathlist.get(0).equals(update._1));
			Util.massert(Util.getLast(pathlist).equals(update._2));
			
			for(int i : Util.range(pathlist.size()-1))
			{
				CityId a = pathlist.get(i+0);
				CityId b = pathlist.get(i+1);
				
				Pair<CityId, CityId> linkpair = getLinkPair(a, b);
				
				String curcolor = _curColorMap.get(linkpair);
				
				Util.massert(curcolor != null,
					"Path Link %d -> %d is not a valid path", a.C, b.C);
				
				if(!curcolor.equals(update._3))
				{
					Util.incHitMap(_colorUpdateMap, update._3);	
					
					_curColorMap.put(linkpair, update._3);
				}
				
			}
			
		}		
		
		public void clearUpdateInfo()
		{
			_leftPath = null;
			_rghtPath = null;
			
			_updateList.poll();
		}				
		
		
		public boolean isGraphComplete()
		{
			return _linkMap.size() == _path2RootMap.size();	
		}		
		
		public boolean haveAnotherUpdate()
		{
			return !_updateList.isEmpty();	
		}				
		
		@Override
		public List<String> getDiagnosticInfo()
		{
			List<String> reclist = Util.vector();
			
			reclist.add(Util.sprintf("Remaining Updates: %d", _updateList.size()));
			
			reclist.add(Util.sprintf("NextUpdate: %s", _updateList.isEmpty() ? "---" : _updateList.peek()));

			reclist.add(Util.sprintf("Left-Path: %s", _leftPath));
			reclist.add(Util.sprintf("Rght-Path: %s", _rghtPath));
			
			reclist.add(Util.sprintf("Src2Dst path: %s", composeSrc2DstPath()));
			
			reclist.add(Util.sprintf("Graph-Complete?: %b", isGraphComplete()));
			reclist.add(Util.sprintf("LinkMapSize: %d", _linkMap.size()));
			reclist.add(Util.sprintf("Path2Root Size: %d", _path2RootMap.size()));			
			
			reclist.add(Util.sprintf("%s", _colorUpdateMap));
			
			if(_curColorMap.size() < 10)
			{
				reclist.add(Util.sprintf("%s", _curColorMap));	
			}
			
			
			return reclist;
		}
		
		
		
		
		
		// }}}
	}
	
	private static RainbowMachine _SING = null;
	
	public static RainbowMachine getSing()
	{
		if(_SING == null)
		{
			_SING = new RainbowMachine();
			_SING.loadSingleProblem("/userdata/lifecode/datadir/euler/SingleRainbow.txt");
		}
		
		return _SING;
	}
	
	public static void reloadSing()
	{
		_SING = new RainbowMachine();
		_SING.loadSingleProblem("/userdata/lifecode/datadir/euler/SingleRainbow.txt");
	}
		
	
	

	

	public static class RunSingleTest extends ArgMapRunnable
	{
		public void runOp()
		{
			
			RainbowMachine rmach = RainbowSystem.getSing();
						
			rmach.run2State(RainbowState.IsGraphComplete);
			
			rmach.showPath2Root();
		}
		
	}
	
	public static class CreateDiagram extends ArgMapRunnable
	{
		public void runOp()
		{
			// Build the finite state machine
			(new FsmGraphWrapper(new RainbowMachine())).runOp();		
		}
	}			
	
	public static class RunFromCommLine extends ArgMapRunnable
	{
		public void runOp()
		{
			RainbowMachine rmachine = getSing();
			
			CommLineFsmRunner crunner = new CommLineFsmRunner(rmachine);
			crunner.runFromCommLine();
		}
	}	
	
	public static class BigTestRunner extends ArgMapRunnable
	{
		LinkedList<String> _bigRecordList = Util.linkedlistify();
		
		List<String> _outputList = Util.vector();
		
		public void runOp()
		{
			readTestData();
			
			int numproblem = Integer.valueOf(_bigRecordList.poll());
			
			for(int np : Util.range(numproblem))
			{
				List<String> oneproblist = pollProblemData();	
				
				Util.pf("Got %d records for problem %d\n", oneproblist.size(), np);
				
				RainbowMachine rmachine = new RainbowMachine();
				rmachine.setInputData(oneproblist);
				
				SimpleTimer stime = SimpleTimer.buildAndStart();
				
				rmachine.run2State(RainbowState.IsGraphComplete);
				
				Util.pf("Constructed graph, took %.03f sec\n",
						stime.getTimeSinceStartSec());
			}
		}
		
		private List<String> pollProblemData()
		{
			String breakline = _bigRecordList.poll();
			
			Util.massert(breakline.trim().isEmpty(),
						"Didn't find an empty line between problems");			
				
			List<String> datalist = Util.vector();
			
			while(!_bigRecordList.isEmpty() && !_bigRecordList.peek().trim().isEmpty())
			{
				datalist.add(_bigRecordList.poll());
			}
			
			return datalist;
			
		}
		
		private void readTestData()
		{
			String datapath = _argMap.getStr("datapath");
			
			List<String> datalist = FileUtils.getReaderUtil()
								.setFile(datapath)
								.setTrim(false)
								.readLineListE();
								
			Util.pf("Read %d data records from path %s\n", datalist.size(), datapath);
			
			_bigRecordList.addAll(datalist);
		}
	}			
	
	
	
	public static void main(String[] args) throws Exception
	{
		
		// {{{
		ArgMap amap = ArgMap.getClArgMap(args);
		
		String simpleclass = args[1];
		String fullclass = Util.sprintf("%s$%s", RainbowSystem.class.getName(), simpleclass);
		
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
	
	*/

}
