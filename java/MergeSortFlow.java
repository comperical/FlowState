
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

public class MergeSortFlow
{
	public enum MergeSortState implements StringCodeStateEnum
	{
		StartMachine,
		IsTrivialSort("F->SSL"),
		DoTrivialSort("SC"),
		
		SetupSubList,
		HaveAnotherLeft("F->DFR"),
		HaveAnotherRght("F->DFL"),
		
		IsLeftLower("F->PFR"),
		
		PollFromLeft("HAL"),
		PollFromRght("HAL"),

		DrainFromLeft("SC"),
		DrainFromRght("SC"),
		
		SortComplete;

		public final String tCode;
		
		MergeSortState() 			{  tCode  = ""; }	
		MergeSortState(String tc) 	{  tCode = tc; }	
		
		public String getTransitionCode()  { return tCode; }
	}
	
	
	public static <T extends Comparable<T>> LinkedList<T> runMergeSort(ArrayList<T> thelist)
	{
		return runMergeSort(thelist, 0, thelist.size());	
	}
	
	public static <T extends Comparable<T>> LinkedList<T> runMergeSort(ArrayList<T> thelist, int alpha, int omega)
	{
		MergeSortMachine<T> mgm = new MergeSortMachine<T>(thelist, alpha, omega);
		mgm.run2Completion();
		return mgm.getResult();
	}
	
	public  static class MergeSortMachine<T extends Comparable<T>> extends FiniteStateMachineImpl
	{
		private ArrayList<T> _theList = new ArrayList<T>();
		
		private final int Alpha;
		private final int Omega;
		
		private LinkedList<T> _leftSub;
		private LinkedList<T> _rghtSub;
		
		private LinkedList<T> _theResult = Util.linkedlist();
		
		public Enum[] getEnumStateList()
		{
			return MergeSortState.values();	
		}
		
		// Use for diagram purposes only
		public MergeSortMachine()
		{
			this(null, -1, -1);
		}
		
		public MergeSortMachine(ArrayList<T> arglist, int a, int o)
		{
			super(MergeSortState.StartMachine);
			
			_theList = arglist;
			
			Alpha = a;
			Omega = o;
				
			// Util.massert(Omega - Alpha >= 1);
		}		
		
		public void startMachine()  {}
		
		public boolean isTrivialSort()
		{
			return Omega - Alpha <= 2;	
		}
		
		public void doTrivialSort()
		{
			// 1-element list
			if(Omega - Alpha == 1)
			{ 
				_theResult.add(_theList.get(Alpha));
				return;
			}
			
			T a = _theList.get(Alpha);
			T b = _theList.get(Alpha+1);
			
			if(b.compareTo(a) < 0)
			{ 
				T gimp = b;
				b = a;
				a = gimp;
			}
			
			_theResult.add(a);
			_theResult.add(b);
		}
		
		
		public void setupSubList()
		{
			int midpt = Alpha + (Omega-Alpha)/2;
			
			_leftSub = runMergeSort(_theList, Alpha, midpt);
			_rghtSub = runMergeSort(_theList, midpt, Omega);
		}
		
		public boolean haveAnotherLeft()
		{
			return !_leftSub.isEmpty();
		}
		
		public boolean haveAnotherRght()
		{
			return !_rghtSub.isEmpty();
		}
		
		public boolean isLeftLower()
		{
			T left = _leftSub.peek();
			T rght = _rghtSub.peek();
			
			return left.compareTo(rght) < 0;
		}
		
		public void pollFromLeft()
		{
			_theResult.add(_leftSub.poll());
			
		}
		
		public void pollFromRght()
		{
			_theResult.add(_rghtSub.poll());
		}
		
		public void drainFromLeft()
		{
			drainSrc2Dst(_leftSub, _theResult);
		}
		
		public void drainFromRght()
		{
			drainSrc2Dst(_rghtSub, _theResult);
			
		}
		
		private static <T> void drainSrc2Dst(LinkedList<T> src, LinkedList<T> dst)
		{
			while(!src.isEmpty())
				{ dst.add(src.poll()); }
		}
		
		
		public LinkedList<T> getResult()
		{
			return _theResult;	
		}
	}
}
