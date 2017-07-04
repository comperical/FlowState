
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

public class HeapSortFlow
{
	public enum HeapSortMachineState implements StringCodeStateEnum
	{
		AddItemState,
		KidOutOfOrder("F->RC"),
		SwapKidParent,
		Bounce2Parent("KOOO"),
		
		PollItemState,
		HolePosHasKid("F->RC"),
		SwapSiftDown("HPHK"),	
		
		ReadyComplete;
		public final String tCode;
		
		HeapSortMachineState() 			{  tCode  = ""; }	
		HeapSortMachineState(String tc) 	{  tCode = tc; }	
		
		public String getTransitionCode()  { return tCode; }
	}
	
	
	public  static class HeapSortMachine<T extends Comparable<T>> extends FiniteStateMachineImpl
	{
		private ArrayList<T> _theList = new ArrayList<T>();
		
		// This is the index of the state we are looking at. 
		// The study operation could be the result of either a poll() or an add()
		private int _studyPosition = -1;
		
		public Enum[] getEnumStateList()
		{
			return HeapSortMachineState.values();	
		}
		
		public HeapSortMachine()
		{
			super(HeapSortMachineState.ReadyComplete);
		}	
		
		public void add(T newitem)
		{
			requireState(HeapSortMachineState.ReadyComplete);
			
			_studyPosition = _theList.size();
			
			_theList.add(newitem);
			
			setState(HeapSortMachineState.AddItemState);
			
			run2State(HeapSortMachineState.ReadyComplete);
		}
		
		public void initMachine() {}
		
		// Dummy state, set here after we add an item
		public void addItemState() {}
		
		// Dummy state, set after we poll an item
		public void pollItemState() {}
		
		// Binary array math to give the parent position from the kid position
		private static int getParentPosition(int n)
		{
			return (n-1)/2;
		}
		
		// Binary Array math: get the kid positions from the parent position
		public static int[] getKidPosition(int n)
		{
			return new int[] { 2*n+1, 2*n+2 };
		}		
		
		public void showInfo()
		{
			Util.pf("%s\n", _theList);	
		}
		
		public boolean kidOutOfOrder()
		{
			T kid = _theList.get(_studyPosition);
			T par = _theList.get(getParentPosition(_studyPosition));
			
			// true of the current kid is out of order compared to parent	
			return kid.compareTo(par) < 0;
		}
		
		public void swapKidParent()
		{
			swapPosition(getParentPosition(_studyPosition));
		}
		
		private void swapPosition(int otherpos)
		{
			T a = _theList.get(_studyPosition);
			T b = _theList.get(otherpos);
			
			_theList.set(_studyPosition, b);
			_theList.set(otherpos, a);			
		}
		
		public void bounce2Parent()
		{
			_studyPosition = getParentPosition(_studyPosition);
		}
		
		public boolean isEmpty()
		{
			return _theList.isEmpty() || _theList.get(0) == null;	
		}
		
		public T poll()
		{
			T presult = _theList.get(0);
			
			_theList.set(0, null);
			_studyPosition = 0;
			
			setState(HeapSortMachineState.PollItemState);
			run2Completion();
			
			return presult;
		}
		
		// Does the hole position have kids?
		public boolean holePosHasKid()
		{
			int[] kidposition = getKidPosition(_studyPosition);	
			
			T leftkid = getOrNull(kidposition[0]);
			T rghtkid = getOrNull(kidposition[1]);			
			
			return leftkid != null || rghtkid != null;
		}
		
		public void swapSiftDown()
		{
			int[] kidposition = getKidPosition(_studyPosition);	
			
			T leftkid = getOrNull(kidposition[0]);
			T rghtkid = getOrNull(kidposition[1]);
			
			Util.massert(leftkid != null || rghtkid != null,
				"We should never enter this state with both kids null");
			
			boolean swapleft = leftkid == null ? false :
						(rghtkid == null ? true : leftkid.compareTo(rghtkid) < 0);

			int swaptarget = kidposition[swapleft ? 0 : 1];
			
			swapPosition(swaptarget);
			
			// Now we bounce down to study the swap target
			_studyPosition = swaptarget;
		}
		
		private T getOrNull(int idx)
		{
			return idx < _theList.size() ? _theList.get(idx) : null;
		}
		
		public List<T> getResult()
		{
			List<T> reslist = Util.arraylist();
			
			while(!isEmpty())
				{ reslist.add(poll()); }
			
			return reslist;
		}
	}
	
}
