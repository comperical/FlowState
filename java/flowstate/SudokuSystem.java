
package net.danburfoot.flowstate; 

import java.util.*;

import net.danburfoot.shared.Util;
import net.danburfoot.shared.Pair;
import net.danburfoot.shared.CollUtil;
import net.danburfoot.shared.FileUtils;
import net.danburfoot.shared.Util.*;
import net.danburfoot.shared.FiniteState.*;

/**
 * This code is a Sudoku solver. It is based on Peter Norvig's solution, written in Python:
 * http://norvig.com/sudoku.html
 * The point of this implementation is to demonstrate the FlowState programming tool.
 * The solver is composed of 2 Finite State Machines:
 * - SudokuGridMachine checks a specific grid for contradictions
 * - SudokuSearchMachine searches through the space of grids, looking for one that is a solution.
 */
public class SudokuSystem
{
	// Full list of all the squares
	static List<SudokuPos> SQUARE_LIST = Util.vector();
	
	// List of all the UNIT sets
	static List<Set<SudokuPos>> UNIT_LIST = Util.vector();

	static Map<SudokuPos, List<Set<SudokuPos>>> UNIT_MAP = Util.treemap();
	
	static Map<SudokuPos, Set<SudokuPos>> PEER_MAP = Util.treemap();
	
	static Map<Character, Integer> ATOI_MAP = Util.hashmap();
	
	static 
	{
		String alphastr = "ABCDEFGHI";
				
		for(int i : Util.range(1, 10))
		{
			for(int j : Util.range(1, 10))
			{
				SudokuPos s = new SudokuPos(alphastr.charAt(i-1), j);
				SQUARE_LIST.add(s);
				
				UNIT_MAP.put(s, new Vector<Set<SudokuPos>>());
				PEER_MAP.put(s, new TreeSet<SudokuPos>());
			}
		}
		
		for(int i : Util.range(1, 10))
		{
			char c = (i+"").charAt(0);
			
			ATOI_MAP.put(c, i);
		}
		
		for(int i : Util.range(1, 10))
		{
			// Row units
			{
				char r = alphastr.charAt(i-1);
				Set<SudokuPos> rowunit = Util.filter2set(SQUARE_LIST, s -> s.Row == r);
				UNIT_LIST.add(rowunit);
			}
			
			// Column units
			{
				Set<SudokuPos> colunit = Util.filter2set(SQUARE_LIST, s -> s.Col == i);
				UNIT_LIST.add(colunit);
			}			
		}
		
		for(String charblock : Util.listify("ABC", "DEF", "GHI"))
		{
			for(int div : Util.range(3))
			{
				Set<SudokuPos> boxunit = Util.filter2set(SQUARE_LIST, s -> charblock.indexOf(s.Row) > -1 && (s.Col-1) / 3 == div);
				UNIT_LIST.add(boxunit);				
			}
		}
		
		for(Set<SudokuPos> oneunit : UNIT_LIST)
		{
			for(SudokuPos s : oneunit)
				{ UNIT_MAP.get(s).add(oneunit); }	
		}
		
		// Initialize the Peer Map. 
		// PeerSet for A is all the positions that share a Unit with A. 
		for(SudokuPos a : UNIT_MAP.keySet())
		{
			for(Set<SudokuPos> peerset : UNIT_MAP.get(a))
			{
				for(SudokuPos b : peerset)
				{ 
					if(a.compareTo(b) == 0)
						{ continue; }
					
					PEER_MAP.get(a).add(b);
				}
			}
		}		
	}
	
	// Simple representation of a Sudoku position
	// Suitable for putting in a TreeMap
	public static class SudokuPos implements Comparable<SudokuPos>
	{
		public final char Row;
		
		public final int Col;
		
		public final String strForm;
		
		public SudokuPos(char r, int c)
		{
			Row = r;
			Col = c;
			
			strForm = Row+""+Col;
		}
		
		public String toString()
		{
			return strForm;	
		}
		
		public int compareTo(SudokuPos that)
		{
			if(this.Row != that.Row)
				{ return that.Row - this.Row; }
			
			return that.Col - this.Col;
		}
	}
	
	public enum SdGridState implements StringCodeStateEnum
	{
		InitGrid,	
		
		// Any more items in elimination stack?
		HaveMoreElimItem("F->HMAI"),
		
		// Is the next item in elimination stack relevant?
		IsNextElimRelevant("F->PES"),
		
		// Run next elimination
		DoNextElimination,
		
		// Did we just eliminate the last option?
		EliminatedLastOpt("T->CC"),			
		
		// If we eliminated down to last result, then add eliminate options for peers
		MaybeAddPeerElim, 
		
		HaveUnitContradiction("T->CC"),
		
		DoUnitAssign,
		
		// Poll elimination stack
		PollElimStack("HMEI"),			
		
		// Do we have any more assign ops?
		HaveMoreAssignItem("F->OC"),
		
		// Do the next assignation
		DoNextAssign("HMEI"),		
		
		OkayComplete("0"),
		ContradictComplete;
		
		public final String tCode;
		
		SdGridState() 			{  tCode  = ""; }	
		SdGridState(String tc) 		{  tCode = tc; }	
		
		public String getTransitionCode()  { return tCode; }		
	}		
	
	
	public static class SudokuGridMachine extends FiniteStateMachineImpl
	{
		// Map representing possible values for each position
		// The String is really a Set<Integer>
		// Eg if all values are possible, the string will be "123456789"
		private Map<SudokuPos, String> _valMap = Util.treemap();
		
		// Stack of position x value combinations to be ELIMINATED
		private LinkedList<Pair<SudokuPos, Integer>> _elimStack = Util.linkedlist();		
		
		// Stack of positions waiting to be ASSIGNED
		private LinkedList<Pair<SudokuPos, Integer>> _assignStack = Util.linkedlist();
		
		public SudokuGridMachine()
		{
			super(SdGridState.InitGrid);
			
			for(SudokuPos s : SQUARE_LIST)
			{
				// Set<Integer> initset = Util.setify(1, 2, 3, 4, 5, 6, 7, 8, 9);
				_valMap.put(s, "123456789");
			}
		}
		
		// Build a new Grid machine as a copy of a previous one.
		public SudokuGridMachine(Map<SudokuPos, String> copymap)
		{
			super(SdGridState.InitGrid);
			
			_valMap.putAll(copymap);
		}			
		
		
		public SudokuGridMachine(String gridstring)
		{
			this();
			
			Util.massert(gridstring.length() == 81, 
				"Grid size should be 9x9=81");
			
			for(int i : Util.range(81))
			{
				char c = gridstring.charAt(i);
				
				if(c == '0' || c == '.')
					{ continue; }
				
				int d = ATOI_MAP.get(c);
				
				initAssign(SQUARE_LIST.get(i), d);
			}
		}		
		
		public void initGrid() {} 	

		public void initAssign(SudokuPos spos, int d)
		{
			Util.massert(getState() == SdGridState.InitGrid,
				"You can only add values in the InitGrid state");
			
			_assignStack.add(Pair.build(spos, d));
		}
		
		public void pollElimStack()
		{ 
			_elimStack.poll(); 
		}			
		
		public boolean haveMoreAssignItem()
		{
			return !_assignStack.isEmpty();
		}
		
		public boolean haveMoreElimItem()
		{
			return !_elimStack.isEmpty();
		}
		
		// If the position is not in the valid set anyway, it is not relevant.
		public boolean isNextElimRelevant()
		{
			return _valMap.get(nextElimPos()).contains(nextElimVal()+"");
		}
		
		// Actually remove the value from the position-valid set.
		public void doNextElimination()
		{
			SudokuPos nextpos  = nextElimPos();
			Integer nextval = nextElimVal();
			
			// Set removal as string operation
			String newvalstr = _valMap.get(nextpos).replace(nextval+"", "");
			
			_valMap.put(nextpos, newvalstr);
		}
		
		// Did we kill off last possible value for the position?
		public boolean eliminatedLastOpt()
		{
			return _valMap.get(nextElimPos()).isEmpty();			
		}		
		
		public void maybeAddPeerElim()
		{
			String valstr = _valMap.get(nextElimPos());
			
			if(valstr.length() != 1)
				{ return; }
			
			// Okay, this is the selected value.
			int d2 = ATOI_MAP.get(valstr.charAt(0));
			
			// Util.massert(d2 <= 9, "Out of range new elim %d", d2);
			
			// This value cannot exist in any of the peer positions of S
			for(SudokuPos s2 : PEER_MAP.get(nextElimPos()))
			{	
				_elimStack.add(Pair.build(s2, d2));
			}
		}		
		
		private SudokuPos nextElimPos()
		{
			return _elimStack.peek()._1;	
		}
		
		private Integer nextElimVal()
		{
			return _elimStack.peek()._2;	
		}
				
		public void doNextAssign()
		{
			Pair<SudokuPos, Integer> next = _assignStack.poll();
			
			// Util.massert(next._2 <= 9, "Out of range value %d", next._2);
			
			// Util.pf("Doing assign %s\n", next);
			
			String dstr = _valMap.get(next._1);
			
			Util.massert(dstr.contains(next._2+""), 
				"Attempt to assign value %d to position %s, but allowed set is %s",
				next._2, next._1, dstr);
			
			// Util.pf("DSet is %s, estack is %d\n", dset, _elimStack.size());
			
			for(char c : dstr.toCharArray())
			{
				int dp = ATOI_MAP.get(c);
				
				if(dp == next._2)
					{ continue; } 
				
				_elimStack.add(Pair.build(next._1, dp));
			}
			
			// Util.pf("ElimStack size is %d\n", _elimStack.size());
		}
		
		public boolean haveUnitContradiction()
		{
			String d = nextElimVal()+"";
			
			for(Set<SudokuPos> oneunit : UNIT_MAP.get(nextElimPos()))
			{
				List<SudokuPos> dplist = Util.filter2list(oneunit, s -> _valMap.get(s).contains(d));
				
				if(dplist.isEmpty())
					{ return true; }
			}
			
			return false;
		}
		
		public void doUnitAssign()
		{
			int d = nextElimVal();
			
			// Util.massert(d <= 9, "Out of range D=%d", d);
			
			for(Set<SudokuPos> oneunit : UNIT_MAP.get(nextElimPos()))
			{
				List<SudokuPos> dplist = Util.filter2list(oneunit, s -> _valMap.get(s).contains(d+""));
				
				// If there's only one place that D can be assigned, send it there.
				if(dplist.size() == 1)
				{
					_assignStack.add(Pair.build(dplist.get(0), d));
				}
			}
		}
		
		public boolean isFailed()
		{
			Util.massert(isComplete(), 
				"Attempt to query result status, but state is %s", getState());
			
			return getState() == SdGridState.ContradictComplete;
		}
		
		public boolean isSolved()
		{
			if(isFailed())
				{ return false; }
			
			// These are "bad" value sets, that are not yet fully determined
			List<String> undetlist = Util.filter2list(_valMap.values(), dstr -> dstr.length() > 1);
			
			// If no undetermineds, then we've solved it
			return undetlist.isEmpty();
		}
		
		SudokuPos getMinPossibilityPos()
		{
			List<Pair<Integer, SudokuPos>> targlist = _valMap.entrySet()
										.stream()
										.map(me -> Pair.build(me.getValue().length(), me.getKey()))
										.filter(pr -> pr._1 > 1)
										.sorted()
										.collect(CollUtil.toList());
			
			Util.massert(!targlist.isEmpty(),
					"This grid is either solved or failed, you must check before calling");
			
			return targlist.get(0)._2;
		}
		
		public void printGrid()
		{
			for(int i : Util.range(9))
			{
				for(int j : Util.range(9))
				{
				
					SudokuPos s = SQUARE_LIST.get(i*9+j);
				
					String dstr = _valMap.get(s);
				
					if(dstr.length() == 1)
						{ Util.pf("%s", dstr); } 
					else 
						{ Util.pf("."); }
				
				}
				
				Util.pf("\n");
			}
		}
	}	
	
	public enum SearcherState implements StringCodeStateEnum
	{
		HaveAnotherGrid,
		PollCurGrid,
		RunGridMachine,
		GridFailed, 
		GridSolved,
		QueueNextGrid,
		
		SolvedComplete,
		FailComplete;
		
		public String getTransitionCode()
		{
			switch(this)
			{
				case HaveAnotherGrid:	return "F->FC";
				
				case GridFailed:	return "T->HAG";
				case GridSolved: 	return "T->SC";
					
				case QueueNextGrid: 	return "HAG";
					
				case SolvedComplete:	return "0";
				default: 		return "";
			}
		}
	}
	
	
	public static class SudokuSearchMachine extends FiniteStateMachineImpl
	{
		private LinkedList<SudokuGridMachine> _gridList = Util.linkedlist();
		
		private SudokuGridMachine _curGrid;
		
		private int _gridCheckTotal = 0;
		
		
		public SudokuSearchMachine()
		{
			this("003020600900305001001806400008102900700000008006708200002609500800203009005010300");
		}		
		
		public SudokuSearchMachine(String gridstring)
		{
			super(SearcherState.HaveAnotherGrid);	
			
			_gridList.add(new SudokuGridMachine(gridstring));
		}				
		
		public void runGridMachine()
		{
			_curGrid.run2Completion();	
			
			_gridCheckTotal++;
			
		}				
		
		public void pollCurGrid()
		{
			_curGrid = _gridList.poll();
		}	
		
		public boolean gridFailed()
		{
			return _curGrid.isFailed();			
		}
		
		public boolean gridSolved()
		{
			return _curGrid.isSolved();
		}

		public void queueNextGrid()
		{
			SudokuPos minpos = _curGrid.getMinPossibilityPos();
			
			// Util.pf("Probing position %s, possibilities are %s\n", minpos, _curGrid._valMap.get(minpos));
			
			// _curGrid.printGrid();
			
			for(char c : _curGrid._valMap.get(minpos).toCharArray())
			{
				SudokuGridMachine nextgrid = new SudokuGridMachine(_curGrid._valMap);
				
				// Util.pf("Probing assignment of %d to %s\n", d, minpos);
				
				nextgrid.initAssign(minpos, ATOI_MAP.get(c));
				
				// nextgrid.run2Completion();
				
				// Util.pf("-----------\nNextGrid:\n");
				
				// nextgrid.printGrid();
				
				// We're adding the successor grids FIRST : this is depth-first search.
				_gridList.addFirst(nextgrid);
			}
		}		
		
		public boolean haveAnotherGrid()
		{
			return !_gridList.isEmpty();	
		}
		
		public void printResult()
		{
			Util.massert(isComplete(), "Search is not complete");
			
			if(getState() == SearcherState.FailComplete)
			{
				Util.pf("Search failed -- puzzle is impossible\n");
				return;
			}
			
			_curGrid.printGrid();
		}
	}
	
	public static class RunSudokuMachine extends ArgMapRunnable
	{
		
		public void runOp()
		{
			String grid = "003020600900305001001806400008102900700000008006708200002609500800203009005010300";
			
			SudokuGridMachine sgmachine = new SudokuGridMachine(grid);
			
			sgmachine.run2Completion();
			
			sgmachine.printGrid();
			
		}
	}	
	
	public static class RunSudokuSearch extends ArgMapRunnable
	{
		
		public void runOp()
		{
			// Scanner sc = new Scanner(System.in);
			
			// Util.pf("Enter Sudoku Grid: ");
			
			// String grid = "4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......";
			
			String grid = "....7..8...6...5...2...3.61.1...7..2..8..534.2..9.......2......58...6.3.4...1....";
			
			// sc.close();
			
			SudokuSearchMachine ssmachine = new SudokuSearchMachine(grid);
			
			ssmachine.run2Completion();
			
			ssmachine.printResult();
		}
	}		
	
	
	public static class RunSearchFromFile extends ArgMapRunnable
	{
		public void runOp()
		{
			String srcfile = _argMap.getStr("srcfile");
			int loop2run = _argMap.getInt("loop2run", 1);
			
			List<String> gamelist = FileUtils.getReaderUtil()
								.setFile(srcfile)
								.readLineListE();
						
								
			double startup = Util.curtime();
								
			for(int loop : Util.range(loop2run))
			{
				for(String onegame : gamelist)
				{
					SudokuSearchMachine ssmachine = new SudokuSearchMachine(onegame);
					
					ssmachine.run2Completion();
					
					Util.massert(ssmachine.getState() == SearcherState.SolvedComplete,
						"Search failed for game\n%s", onegame);
				}
			}
			
			double timesec = (Util.curtime()-startup)/1000;
			
			Util.pf("Solved %d games, took %.03f sec total, %.01f HZ\n", 
					gamelist.size(), timesec, gamelist.size()/timesec);
		}
	}
	
	
	
	
	public static class TestBasicSetup extends ArgMapRunnable
	{
		public void runOp()
		{
			Util.massert(SQUARE_LIST.size() == 81);
			
			SudokuPos testpos = new SudokuPos('C', 2);
			
			Util.pf("%s\n", UNIT_MAP.get(testpos));
			
			for(List<Set<SudokuPos>> unitlist : UNIT_MAP.values())
			{
				Util.massertEqual(3, unitlist.size(),
					"Expected %d-length list, but found %d");
				
				Set<Integer> sizeset = Util.map2set(unitlist, spset -> spset.size());
				
				Util.massert(sizeset.size() == 1 && sizeset.contains(9),
					"Size set should be [9], got %s", sizeset); 
			}
			
			Util.pf("%s\n", PEER_MAP.get(testpos));
			
			{
				Set<Integer> psizeset = Util.map2set(PEER_MAP.values(), pset -> pset.size());
				
				Util.massert(psizeset.size() == 1 && psizeset.contains(20), 
					"Peer sizes should all be 24, got %s", psizeset);
			}
		}
	}		
}
