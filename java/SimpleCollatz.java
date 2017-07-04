
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

public class SimpleCollatz
{
	public enum CollStateEnum implements StringCodeStateEnum
	{
		InitMachine,
		NextProbeVal,
		ProbeInCache,
		AddToStack,
		PollStack,
		StackEmpty,
		IsCalcComplete;
		
		// TODO: need to refactor this.
		/*
			Map<String, String> tmap = Util.treemap();
			tmap.put("ICZ", "T->IC,F->DC");
			
			tmap.put("PIC", "F->ATS,T->ATC");
			tmap.put("ATS", "PIC");
			tmap.put("SE", "T->ICC,F->PIC");
			tmap.put("ICC", "T->1,F->NPV");	
		*/
		
		
		public final String tCode;
		
		CollStateEnum() 		{  tCode  = ""; }	
		CollStateEnum(String tc) 	{  tCode = tc; }	
		
		public String getTransitionCode()  { return tCode; }
	}
	
	
	public static class CollSeqMachine extends FiniteStateMachineImpl
	{
		private TreeMap<Long, Long> _lenMap = Util.treemap();
		
		private TreeSet<Long> _notInCache = Util.treeset();
		
		private LinkedList<Pair<Long, Long>> _stackList = Util.linkedlist();
		
		private long _targetValue = 100000L;
		
		public Enum[] getEnumStateList()
		{
			return CollStateEnum.values();	
		}
		
		public CollSeqMachine()
		{
			super(CollStateEnum.InitMachine);
		}	
		
		public CollSeqMachine(int maxn)
		{
			this();
			_targetValue = maxn;
		}			
		
		public Map<Long, Long> getLengthMap()
		{
			return Collections.unmodifiableMap(_lenMap);	
		}
		
		public Map<String, String> getCodedTransMap()
		{
			Map<String, String> tmap = Util.treemap();
			tmap.put("ICZ", "T->IC,F->DC");
			
			tmap.put("PIC", "F->ATS,T->ATC");
			tmap.put("ATS", "PIC");
			tmap.put("SE", "T->ICC,F->PIC");
			tmap.put("ICC", "T->1,F->NPV");
			return tmap;
		}
		
		public void initMachine()
		{
			_lenMap.put(1L, 1L);
			
			for(long p = 2L; p < _targetValue+100; p++)
				{ _notInCache.add(p); }
		}			
		
		public void nextProbeVal()
		{
			// Gotcha: this doesn't work!!
			// int probe = _lenMap.lastKey()+1;
			long probe = getNextProbeVal();
			
			_stackList.add(Pair.build(probe, nextCollatz(probe)));
			
			// Util.pf("Probing %s\n", _stackList.peek());
		}	
		
		private long getNextProbeVal()
		{
			return _notInCache.first();
		}
				
		public boolean probeInCache()
		{
			Pair<Long, Long> probepair = _stackList.peek();
			// Util.pf("Probing pair %s\n", probepair);
			return _lenMap.containsKey(probepair._2);
		}
		
		public void addToStack()
		{
			Pair<Long, Long> probepair = _stackList.peek();
			_stackList.addFirst(Pair.build(probepair._2, nextCollatz(probepair._2)));
		}
		
		public void addToCache()
		{
			Pair<Long, Long> probepair = _stackList.peek();
			long cacheval = _lenMap.get(probepair._2);
			_lenMap.put(probepair._1, cacheval+1);
			_notInCache.remove(probepair._1);
		}				
		
		public void pollStack()
		{
			_stackList.poll();	
		}
		
		public boolean stackEmpty()
		{
			return _stackList.isEmpty();	
		}
		
		public boolean isCalcComplete()
		{
			return getNextProbeVal() > _targetValue;	
		}

		public Pair<Long, Long> getResult()
		{
			long maxlen = -1;
			long maxkey = -1;
			
			for(Map.Entry<Long, Long> lenpair : _lenMap.entrySet())
			{
				if(lenpair.getValue() > maxlen)
				{
					maxkey = lenpair.getKey();
					maxlen = lenpair.getValue();
				}
			}
			
			return Pair.build(maxkey, maxlen);
		}
		
		@Override
		public List<String> getDiagnosticInfo()
		{
			List<String> mylist = Util.vector();
			mylist.add(Util.sprintf("Cache Size: %d", _lenMap.size()));
			mylist.add(Util.sprintf("Top Cache Value: %d", _lenMap.isEmpty() ? -1 : _lenMap.lastKey()));
			mylist.add(Util.sprintf("Stack Size: %d", _stackList.size()));
			mylist.add(Util.sprintf("Stack: %s", _stackList));
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
	
}
