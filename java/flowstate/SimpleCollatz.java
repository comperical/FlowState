
package net.danburfoot.flowstate; 

import java.util.*;

import net.danburfoot.shared.Util;
import net.danburfoot.shared.Util.*;
import net.danburfoot.shared.FiniteState.*;

// This is a solution to Problem 14, "Longest Collatz sequence", of Project Euler
// https://projecteuler.net/problem=14
public class SimpleCollatz
{
	public enum CollStateEnum implements StringCodeStateEnum
	{
		InitMachine,
		AddNextProbeToStack,
		NextQueryInCache("F->AQTS"),
		AddResultToCache("PQS"),
		AddQueryToStack("NQIC"),
		PollQueryStack,
		QueryStackEmpty("F->NQIC"),
		IsNextAboveTarget("F->ANPTS"),
		
		CalcComplete;
		
		public final String tCode;
		
		CollStateEnum() 		{  tCode  = ""; }	
		CollStateEnum(String tc) 	{  tCode = tc; }	
		
		public String getTransitionCode()  { return tCode; }
	}
	
	
	public static class CollSeqMachine extends FiniteStateMachineImpl
	{
		// Cache of previously obtained result:
		// Number --> Length of Collatz Sequence
		private TreeMap<Long, Long> _cacheMap = Util.treemap();
		
		// Numbers < TargetValue that have not yet been calculated
		private TreeSet<Long> _notInCache = Util.treeset();
		
		// Stack of queries. When we try to calculate a number that's not in the cache,
		// we put it on this stack and then try the next Collatz value.
		// If that's not in the cache either, we push it onto the stack and continue
		// the process until we get a hit.
		private LinkedList<Long> _queryStack = Util.linkedlist();
		
		private final long _targetValue;
		
		public Enum[] getEnumStateList()
		{
			return CollStateEnum.values();	
		}
		
		public CollSeqMachine()
		{
			this(-1);
		}	
		
		public CollSeqMachine(int maxn)
		{
			super(CollStateEnum.InitMachine);
			_targetValue = maxn;
		}			
		
		public Map<Long, Long> getLengthMap()
		{
			return Collections.unmodifiableMap(_cacheMap);	
		}
		
		public void initMachine()
		{
			_cacheMap.put(1L, 1L);
			
			for(long p = 2L; p < _targetValue+100; p++)
				{ _notInCache.add(p); }
		}			
		
		public void addNextProbeToStack()
		{
			long probe = getNextProbeVal();
			
			_queryStack.add(probe);
		}	
		
		private long getNextProbeVal()
		{
			return _notInCache.first();
		}
				
		public boolean nextQueryInCache()
		{
			long nextcol = nextCollatz(_queryStack.peek());
			
			return _cacheMap.containsKey(nextcol);
		}
		
		public void addQueryToStack()
		{
			_queryStack.addFirst(nextCollatz(_queryStack.peek()));
		}
		
		public void addResultToCache()
		{
			long query = _queryStack.peek();
			long nextcol = nextCollatz(query);
			long cacheval = _cacheMap.get(nextcol);
			
			_cacheMap.put(query, cacheval+1);
			_notInCache.remove(query);
		}				
		
		public void pollQueryStack()
		{
			_queryStack.poll();	
		}
		
		public boolean queryStackEmpty()
		{
			return _queryStack.isEmpty();	
		}
		
		public boolean isNextAboveTarget()
		{
			return getNextProbeVal() > _targetValue;	
		}

		public long getMaxCollatz()
		{
			long maxlen = -1;
			long maxkey = -1;
			
			for(Map.Entry<Long, Long> lenpair : _cacheMap.entrySet())
			{
				if(lenpair.getValue() > maxlen)
				{
					maxkey = lenpair.getKey();
					maxlen = lenpair.getValue();
				}
			}
			
			return maxkey;
		}
		
		@Override
		public List<String> getDiagnosticInfo()
		{
			List<String> mylist = Util.vector();
			mylist.add(Util.sprintf("Cache Size: %d", _cacheMap.size()));
			mylist.add(Util.sprintf("Top Cache Value: %d", _cacheMap.isEmpty() ? -1 : _cacheMap.lastKey()));
			mylist.add(Util.sprintf("Stack Size: %d", _queryStack.size()));
			mylist.add(Util.sprintf("Stack: %s", _queryStack));
			return mylist;
		}
	}
	
	public static long nextCollatz(long n)
	{
		Util.massert(n > 0, "Attempt to calculate collatz for negative number %d\n", n);
		
		if((n % 2) == 0)
			{ return n/2; }
		
		return 3*n+1;
	}	
	
	
	public static long directLengthCalc(long n)
	{
		if(n == 1)
			{ return 1; }
		
		return 1 + directLengthCalc(nextCollatz(n));
		
	}
	
	public static String getSequenceString(long n)
	{
		if(n == 1)
			{ return "1"; }
		
		return n + "->" + getSequenceString(nextCollatz(n));
	}
	
	
	public static class RunCollatzMachine extends ArgMapRunnable
	{
		
		public void runOp()
		{
			int maxvalue = _argMap.getInt("maxvalue", 100);
			
			CollSeqMachine csmach = new CollSeqMachine(maxvalue);
			
			csmach.run2Completion();
			
			long maxcoll = csmach.getMaxCollatz();
			
			Util.pf("Result is %d\n", maxcoll);
			
			Util.pf("%s\n", SimpleCollatz.getSequenceString(maxcoll));
			
		}
	}
}
