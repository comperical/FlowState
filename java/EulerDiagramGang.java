
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

public class EulerDiagramGang
{
	
	public enum SudokuState implements FiniteStateEnumSimple
	{
		InitPuzzle;	
		
		public Object getBasicTransition()
		{
			switch(this)
			{
				case InitPuzzle: 		return null;
					
				default: 
					throw new RuntimeException("No transition specified for state: " + this);
			}
			
		}
	}
	
	
	public static class SudokuMachine extends FiniteStateMachineImpl
	{
		public Enum[] getEnumStateList()
		{
			return SudokuState.values();	
		}
		
		public SudokuMachine()
		{
			super(SudokuState.InitPuzzle);	
		}		
		
	}
	
	
	
	public enum LargeSumState implements FiniteStateEnumSimple
	{
		InitState,
		ReadTestData,
		
		HaveAnotherNumber, // Another record of input data?
		HaveAnotherDigit, // Another digit in current record?
		
		Setup4NextNumber, // Poll the input list
		
		HaveOverFlow, // Are we overflowing?
		FixSingleOverFlow, //
		
		AddCurDigit, // Add the current digit to the sum
		
		SumComplete;

		public Object getBasicTransition()
		{
			switch(this)
			{
				case InitState: 		return ReadTestData;
				case ReadTestData: 		return HaveAnotherNumber;
					
				case AddCurDigit:		return HaveOverFlow;
				case HaveOverFlow:		return Util.listify(FixSingleOverFlow, HaveAnotherDigit);
					
				case FixSingleOverFlow:		return HaveOverFlow;	
					
				case Setup4NextNumber:		return HaveAnotherNumber;
					
				case HaveAnotherNumber:		return Util.listify(HaveAnotherDigit, SumComplete);
				case HaveAnotherDigit: 		return Util.listify(AddCurDigit, Setup4NextNumber);
				case SumComplete: 		return null;
					
				default: 
						throw new RuntimeException("Transition not specified for state: " + this);
			}
		}
	}
	
	public static class LargeSumMachine extends FiniteStateMachineImpl
	{
		
		public Enum[] getEnumStateList()
		{
			return LargeSumState.values();	
		}
		
		public LargeSumMachine()
		{
			super(LargeSumState.InitState);	
		}
		
		private LinkedList<String> _inputNumberList = Util.linkedlist();
		
		private Map<Integer, Integer> _bigSumMap = Util.treemap();
		
		private int _digitIndex = 0;
		
		public void initState()
		{
			for(int i : Util.range(1000))
			{
				_bigSumMap.put(i, 0);	
			}
		}
		
		public void readTestData()
		{
			List<String> testdata = FileUtils.getReaderUtil()
								.setFile("/userdata/lifecode/datadir/euler/LargeSumData.txt")
								.readLineListE();
			
								
			for(String rec : testdata)
			{
				addReverseInput(rec.trim());	
			}
		}
		
		private void addReverseInput(String s)
		{
			_inputNumberList.add(new StringBuilder(s).reverse().toString());			
		}
		
		public boolean haveAnotherNumber()
		{
			return !_inputNumberList.isEmpty();
		}
		
		
		public void setup4NextNumber()
		{
			_inputNumberList.poll();
			
			_digitIndex = 0;
		}
		
		public boolean haveAnotherDigit()
		{
			String curnum = _inputNumberList.peek();
			
			return _digitIndex < curnum.length();
		}
		
		public boolean haveOverFlow()
		{
			return findOverFlowIndex().isPresent();
		}
		
		public void fixSingleOverFlow()
		{
			int opos = findOverFlowIndex().get();
			
			int a = _bigSumMap.get(opos+0);
			int b = _bigSumMap.get(opos+1);
			
			_bigSumMap.put(opos  , a-10);
			_bigSumMap.put(opos+1, b+1 );
		}
		
		private Optional<Integer> findOverFlowIndex()
		{
			return _bigSumMap.entrySet()
						.stream()
						.filter(me -> me.getValue() >= 10)
						.map(me -> me.getKey())
						.findAny();
		}
		
		public void addCurDigit()
		{
			String curnum = _inputNumberList.peek();
			
			int x = Integer.valueOf(curnum.charAt(_digitIndex)+"");
			
			int p = _bigSumMap.get(_digitIndex);
			
			_bigSumMap.put(_digitIndex, p+x);
			
			_digitIndex++;
		}
		
		TreeMap<Integer, Integer> getTopNzMap()
		{
			TreeMap<Integer, Integer> copymap = new TreeMap<Integer, Integer>(_bigSumMap);
			
			while(copymap.lastEntry().getValue() == 0)
				{ copymap.pollLastEntry(); }
			
			return copymap;
		}
		
		public void showResult()
		{
			TreeMap<Integer, Integer> nzmap = getTopNzMap();
			
			while(!nzmap.isEmpty())
			{
				Map.Entry<Integer, Integer> toprec = nzmap.pollLastEntry();	
				
				Util.pf("\tPos=%d\t\tVal=%d\n", toprec.getKey(), toprec.getValue());
			}
		}
		
		public void showTop(int n)
		{
			TreeMap<Integer, Integer> nzmap = getTopNzMap();
			
			StringBuffer sb = new StringBuffer();
			
			while(!nzmap.isEmpty() && sb.length() < n)
			{
				Map.Entry<Integer, Integer> toprec = nzmap.pollLastEntry();	

				int d = toprec.getValue();
				
				Util.massert(0 <= d && d < 10, "Digit out of bounds: %d", d);
				
				sb.append(d);
			}
			
			Util.pf("GRAND RESULT: %s\n", sb.toString());
		}
		
		
		
		
	}
	

	
	public static class CreateDiagram extends ArgMapRunnable
	{
		
		public void runOp()
		{
			// Build the finite state machine
			(new FsmGraphWrapper(new LargeSumMachine())).runOp();			
		}
		
	}		
	
	
	public static class RunSumMachine extends ArgMapRunnable
	{
		
		public void runOp()
		{
			LargeSumMachine lsm = new LargeSumMachine();
			
			lsm.run2Completion();
			
			lsm.showResult();
			
			lsm.showTop(10);
		}
		
	}	
	
	
	
	public static void main(String[] args) throws Exception
	{
		
		// {{{
		ArgMap amap = ArgMap.getClArgMap(args);
		
		String simpleclass = args[1];
		String fullclass = Util.sprintf("%s$%s", EulerDiagramGang.class.getName(), simpleclass);
		
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
