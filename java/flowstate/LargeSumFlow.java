
package net.danburfoot.flowstate; 

import java.util.*;

import net.danburfoot.shared.Util;
import net.danburfoot.shared.Util.*;
import net.danburfoot.shared.FileUtils;

import net.danburfoot.shared.FiniteState.*;

public class LargeSumFlow
{
	
	public enum LargeSumState implements StringCodeStateEnum
	{
		InitState,
		ReadTestData,
		
		HaveAnotherNumber("F->SC"), // Another record of input data?
		HaveAnotherDigit("T->ACD"), // Another digit in current record?
		
		Setup4NextNumber("HAN"), // Poll the input list
		
		HaveOverFlow("F->HAD"), // Are we overflowing?
		FixSingleOverFlow("HOF"), //
		
		AddCurDigit("HOF"), // Add the current digit to the sum
		
		SumComplete;
		
		public final String tCode;
		
		LargeSumState() 			{  tCode  = ""; }	
		LargeSumState(String tc) 		{  tCode = tc; }	
		
		public String getTransitionCode()  	{ return tCode; }		
	}
	
	public static class LargeSumMachine extends FiniteStateMachineImpl
	{
		public LargeSumMachine()
		{
			super(LargeSumState.InitState);	
		}
		
		// Queue of input data, in string form, yet to handle.
		private LinkedList<String> _inputNumberList = Util.linkedlist();
		
		// This is a map of digit position to digit value
		// If one of the keys is > 0, we have an overflow problem marked
		private Map<Integer, Integer> _bigSumMap = Util.treemap();
		
		private TreeSet<Integer> _overFlowSet = Util.treeset();
		
		private int _digitIndex = 0;
		
		public void initState()
		{
			for(int i : Util.range(1000))
				{ _bigSumMap.put(i, 0); }	
		}
		
		public void readTestData()
		{
			List<String> testdata = FileUtils.getReaderUtil()
								.setFile("../data/LargeSumData.txt")
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
		
		// Poll off the previous input, reset digit index to 0
		public void setup4NextNumber()
		{
			_inputNumberList.poll();
			
			_digitIndex = 0;
		}
		
		public boolean haveAnotherDigit()
		{
			return _digitIndex < _inputNumberList.peek().length();
		}
		
		public boolean haveOverFlow()
		{
			return !_overFlowSet.isEmpty();
		}
		
		// Shuffle numbers up to higher significance, to fix overflow
		public void fixSingleOverFlow()
		{
			int opos = getOverFlowIndex();
			
			int a = _bigSumMap.get(opos+0);
			int b = _bigSumMap.get(opos+1);
			
			placeNumberAtIndex(opos+0, a-10);
			placeNumberAtIndex(opos+1, b+1 );
		}
		
		// Put the given number at the given index, and mark as overflow if appropriate, or clear 
		private void placeNumberAtIndex(int idx, int thenumber)
		{
			_bigSumMap.put(idx, thenumber);
			
			if(thenumber >= 10)
				{ _overFlowSet.add(idx); }
			else 
				{ _overFlowSet.remove(idx); }
		}
		
		private int getOverFlowIndex()
		{
			Util.massert(!_overFlowSet.isEmpty(), 
				"Do not call this method when overFlowSet is empty");
			
			return _overFlowSet.first();	
		}
		
		public void addCurDigit()
		{
			String curnum = _inputNumberList.peek();
			
			int x = Integer.valueOf(curnum.charAt(_digitIndex)+"");
			
			int p = _bigSumMap.get(_digitIndex);
			
			placeNumberAtIndex(_digitIndex, p+x);
			
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
}
