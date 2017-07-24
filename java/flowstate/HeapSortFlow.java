
package net.danburfoot.flowstate; 

import java.util.*;

import net.danburfoot.shared.Util;
import net.danburfoot.shared.FiniteState.*;

public class HeapSortFlow
{
	public enum HeapSortMachineState implements StringCodeStateEnum
	{
		InitMachine,
		HaveAnotherNewItem("F->HR"),
		
		AddNewItem,
		CursorBelowParent("F->HANI"),
		SwapCursorWithParent,
		MoveCursorUp("CBP"),
		
		HeapReady,
		
		IsHeapEmpty("T->SC"),
		AddHeapTop2Result,
		SetCursorToZero,

		CursorPosHasKid("F->IHE"),
		HaveLeftKid("F->SDR"),
		HaveRghtKid("F->SDL"),
		LeftBelowRght("T->SDL,F->SDR"),
		
		SwapDownLeft,
		MoveCursorDownLeft("CPHK"),
		
		SwapDownRght,
		MoveCursorDownRght("CPHK"),
				
		SortComplete;
		
		public final String tCode;
		
		HeapSortMachineState() 			{  tCode  = ""; }	
		HeapSortMachineState(String tc) 	{  tCode = tc; }	
		
		public String getTransitionCode()  { return tCode; }
	}
	
	
	public  static class HeapSortMachine<T extends Comparable<T>> extends FiniteStateMachineImpl
	{
		private ArrayList<T> _heapList = new ArrayList<T>();
		
		// This is both the original input list and the storage place for the result.
		private final List<T> _origList;
		
		// Keep track of where in the list we are adding to
		private int _curAddIndex;
		
		// This is the index in the heap that we are "studying" 
		private int _cursorPosition = -1;
		
		public HeapSortMachine()
		{
			this(Collections.emptyList());
		}	
		
		public HeapSortMachine(List<T> olist)
		{
			super(HeapSortMachineState.InitMachine);
			
			Util.massert(olist instanceof RandomAccess,
				"The list provided to this machine must be random access, found %s", olist.getClass().getName());
			
			_origList = olist;
			
			_curAddIndex = 0;
		}	
		
		public void initMachine() {}
		
		public void addNewItem()
		{
			T newitem = _origList.get(_curAddIndex++);
						
			_cursorPosition = _heapList.size();
			
			_heapList.add(newitem);
		}
		
		public boolean haveAnotherNewItem()
		{	
			return _curAddIndex < _origList.size();			
		}
		
		public void heapReady()
		{
			_origList.clear();
		}
		
		// Binary array math to give the parent position from the kid position
		private  int getParentPosition()
		{
			return (_cursorPosition-1)/2;
		}
		
		public int getLeftKidPos()
		{
			return 2*_cursorPosition+1;	
		}
		
		public  int getRghtKidPos()
		{
			return 2*_cursorPosition+2;	
		}
		
		public void showInfo()
		{
			Util.pf("%s\n", _heapList);	
		}
		
		public boolean cursorBelowParent()
		{
			T kid = _heapList.get(_cursorPosition);
			T par = _heapList.get(getParentPosition());
			
			// true of the current kid is out of order compared to parent	
			return kid.compareTo(par) < 0;
		}
				
		public void swapCursorWithParent()
		{
			swapPosition(getParentPosition());
		}
		
		private void swapPosition(int otherpos)
		{
			T a = _heapList.get(_cursorPosition);
			T b = _heapList.get(otherpos);
			
			_heapList.set(_cursorPosition, b);
			_heapList.set(otherpos, a);			
		}
		
		public void moveCursorUp()
		{
			_cursorPosition = getParentPosition();
		}
		
		public boolean isHeapEmpty()
		{
			return _heapList.isEmpty() || _heapList.get(0) == null;	
		}
		
		public void addHeapTop2Result()
		{
			// Add the top of the heap to the result.
			_origList.add(_heapList.get(0));
			
			// Prepare for sift-down operations
			_heapList.set(0, null);
		}
		
		public void setCursorToZero()
		{
			_cursorPosition = 0;
		}
		
		public boolean cursorPosHasKid()
		{
			// Util.pf("Have LKid=%b, Rkid=%b\n", haveLeftKid(), haveRghtKid());
			
			return haveLeftKid() || haveRghtKid();
		}
		
		public boolean haveLeftKid()
		{
			return getOrNull(getLeftKidPos()) != null;
		}
		
		public boolean haveRghtKid()
		{
			return getOrNull(getRghtKidPos()) != null;
		}
		
		public void swapDownLeft()
		{
			swapPosition(getLeftKidPos());
		}
		
		public void swapDownRght()
		{
			swapPosition(getRghtKidPos());
		}
		
		public void moveCursorDownRght()
		{
			_cursorPosition = getRghtKidPos();	
		}
		
		public void moveCursorDownLeft()
		{
			_cursorPosition = getLeftKidPos();	
		}		
		
		public boolean leftBelowRght()
		{
			T leftkid = _heapList.get(getLeftKidPos());
			T rghtkid = _heapList.get(getRghtKidPos());
			
			return leftkid.compareTo(rghtkid) < 0;
		}
		
		private T getOrNull(int idx)
		{
			return idx < _heapList.size() ? _heapList.get(idx) : null;
		}
	}
	
}
