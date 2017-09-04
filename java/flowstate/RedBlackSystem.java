
package net.danburfoot.flowstate; 

import java.util.*;

import net.danburfoot.shared.Util;
import net.danburfoot.shared.Util.*;
import net.danburfoot.shared.FiniteState.*;

public class RedBlackSystem
{
	// GENERAL UTILITY METHODS {{{
	
	
	private static <T extends Comparable<T>> void rotate(RedBlackNode<T> N, boolean isleft)
	{
		if(isleft)
			{ rotateLeft(N); }
		else 
			{ rotateRght(N); }
	}
	
	private static <T extends Comparable<T>> void rotateUp(RedBlackNode<T> K)
	{
		rotate(K.getParent(), !K.isLeftKid());
	}    
	
	private static <T extends Comparable<T>> boolean isNullOrBlack(RedBlackNode<T> A)
	{
		return A == null || !A.isRed;
	}
	
	private static <T extends Comparable<T>> void swapColor(RedBlackNode<T> A, RedBlackNode<T> B)
	{
		boolean ac = !isNullOrBlack(A);
		boolean bc = !isNullOrBlack(B);
		
		if(A != null)
			{ A.isRed = bc; }
		
		if(B != null)
			{ B.isRed = ac; }
	}
	
	private static <T extends Comparable<T>> void rotateLeft(RedBlackNode<T> N)
	{
		Util.massert(N.rghtKid != null, "Attempt to rotate left with null right-side child");
		
		RedBlackNode<T> P = N.getParent();
		RedBlackNode<T> K = N.rghtKid;
		RedBlackNode<T> X = K.leftKid;
		
		if(P != null)
		{ 
			if(N.isLeftKid())
				{ P.setLeftKid(K); }
			else
				{ P.setRghtKid(K); }
		} else {
			K.thePrnt = null;
		}
		
		K.setLeftKid(N);
		N.setRghtKid(X);
	}
	
	private static <T extends Comparable<T>> void rotateRght(RedBlackNode<T> N)
	{
		Util.massert(N.leftKid != null, "Attempt to rotate right with null left-side child");
		
		RedBlackNode<T> P = N.getParent();
		RedBlackNode<T> K = N.leftKid;
		RedBlackNode<T> X = K.rghtKid;
		
		if(P != null)
		{ 
			if(N.isLeftKid())
				{ P.setLeftKid(K); }
			else
				{ P.setRghtKid(K); }
		} else {
			K.thePrnt = null;
		}
		
		K.setRghtKid(N);
		N.setLeftKid(X);
	}		
	
	// }}}
	
	public static class RedBlackNode<T extends Comparable<T>>
	{
		// {{{
		
		private T theItem;
		
		RedBlackNode<T> thePrnt;
		
		RedBlackNode<T> leftKid;
		RedBlackNode<T> rghtKid;
		
		// All new nodes start life as red
		public boolean isRed = true;
		
		public RedBlackNode(T ti)
		{
			this(ti, null);
		}		
		
		public RedBlackNode(T ti, RedBlackNode<T> prnt)
		{
			theItem = ti;	
			
			thePrnt = prnt;
		}
		
		public RedBlackNode(T ti, RedBlackNode<T> prnt, RedBlackMachine<T> mach)
		{
			theItem = ti;	
			
			thePrnt = prnt;
		}		
		
		
		public RedBlackNode<T> add(T newitem)
		{
			int comp = theItem.compareTo(newitem);
			
			// Already have the item, nothing to do
			if(comp == 0)
				{ return null; }
			
			if(comp > 0)
			{
				if(leftKid == null)
				{
					leftKid = new RedBlackNode<T>(newitem, this);
					return leftKid;
				}
				
				return leftKid.add(newitem);
				
			} else {
				
				if(rghtKid == null)
				{
					rghtKid = new RedBlackNode<T>(newitem, this);
					return rghtKid;
				}
				
				return rghtKid.add(newitem);
			}
		}
		
		private void popList(LinkedList<T> listform)
		{
			if(leftKid != null)
				{ leftKid.popList(listform); }
			
			listform.addLast(theItem);
			
			if(rghtKid != null)
				{ rghtKid.popList(listform); }
		}
		
		public RedBlackNode<T> find(T lookup)
		{
			int comp = theItem.compareTo(lookup);
			
			// Found it
			if(comp == 0)
				{ return this; }
			
			RedBlackNode<T> relkid = comp > 0 ? leftKid : rghtKid;
			
			return relkid == null ? null : relkid.find(lookup);		    
		}
		
		public RedBlackNode<T> maxTreeNode()
		{
			return rghtKid == null ? this : rghtKid.maxTreeNode();
		}
		
		public RedBlackNode<T> minTreeNode()
		{
			return leftKid == null ? this : leftKid.minTreeNode();
		}		
		
		public boolean contains(T probeitem)
		{
			return find(probeitem) != null;
		}
		
		public RedBlackNode<T> getParent()
		{
			return thePrnt;	
		}
		
		public T getItem()
		{
			return theItem;   
		}
		
		public RedBlackNode<T> getGrandParent()
		{
			Util.massert(thePrnt != null,
				"Attempt to get grandparent with null parent, you must check before calling");
			
			return thePrnt.getParent();
		}
		
		public RedBlackNode<T> getUncle()
		{
			RedBlackNode<T> prnt = getParent();
			RedBlackNode<T> gpar = getGrandParent();
			
			Util.massert(gpar != null, "Attempt to get Uncle with null GrandParent");
			
			return gpar.leftKid == prnt ? gpar.rghtKid : gpar.leftKid;
		}		
		
		public RedBlackNode<T> getSibling()
		{
			RedBlackNode<T> prnt = getParent();
			
			Util.massert(prnt != null, "Attempt to get Sibling with null parent");
			
			return isLeftKid() ? prnt.rghtKid : prnt.leftKid;		
		}
		
		public RedBlackNode<T> getInnerNephew()
		{
			RedBlackNode<T> s = getSibling();
			
			return isLeftKid() ? s.rghtKid : s.leftKid;
		}
		
		int getCheckBlackHeight()
		{
			int lblack = leftKid == null ? 0 : leftKid.getCheckBlackHeight();
			int rblack = rghtKid == null ? 0 : rghtKid.getCheckBlackHeight();
			
			Util.massert(lblack == rblack,
				"Black height imbalance for %s", this);
			
			return lblack + (isRed ? 0 : 1);
		}
		
		public boolean isLeftKid()
		{
			Util.massert(thePrnt != null, 
				"Attempt to query isLeftKid on node without parent, must check first");
			
			return thePrnt.leftKid == this;
		}
		
		public void setLeftKid(RedBlackNode<T> newkid)
		{	
			leftKid = newkid;
			
			if(newkid != null)
				{ newkid.thePrnt = this; }
		}
		
		public void setRghtKid(RedBlackNode<T> newkid)
		{
			rghtKid = newkid;
			
			if(newkid != null)
				{ newkid.thePrnt = this; }
		}		
		
		void checkRef(Set<T> itemset, int depth)
		{
			//Util.pf("Checking ref for node %s::%s at depth %d\n",
			//		(isRed ? "R" : "B"), theItem, depth);
			
			Util.massert(!itemset.contains(theItem),
				"Found item %s already in itemset %s", theItem, itemset);
			
			itemset.add(theItem);
			
			if(leftKid != null)
				{ leftKid.checkRef(itemset, depth+1); }
			
			if(rghtKid != null)
				{ rghtKid.checkRef(itemset, depth+1); }
			
		}
		
		public String toString()
		{
			return Util.sprintf("%s::%s", isRed ? "R" : "B", theItem);	
		}
		
		public void print()
		{
			TreePrinter tp = new TreePrinter();
			printSub(tp, 0, 0);
			tp.print();
		}
		
		private void printSub(TreePrinter tp, int depth, int midpt)
		{
			String todisp = toString();
			
			tp.addInfo(depth, midpt-todisp.length()/2, todisp);
			
			if(leftKid != null)
			{
				tp.addInfo(depth+1, midpt-3, "//");	
				
				leftKid.printSub(tp, depth+2, midpt-6);
			}
			
			if(rghtKid != null)
			{
				tp.addInfo(depth+1, midpt+3, "\\\\");	
				
				rghtKid.printSub(tp, depth+2, midpt+6);
			}
		}
		
		
		void checkInvariant()
		{
			Util.massert(thePrnt != null || !isRed,
				"Root node should always be black");
			
			Util.massert(this != leftKid && this != rghtKid, "Circular references!!!");
			
			if(leftKid != null)
			{ 
				Util.massert(theItem.compareTo(leftKid.theItem) > 0,
					"Parent item %s is below Left Kid Item %s", 
					theItem, leftKid.theItem);
				
				Util.massert(Util.AimpliesB(isRed, !leftKid.isRed),
					"Node %s has red=%b, but left kid %s has red=%b", 
					theItem, isRed, leftKid.theItem, leftKid.isRed);
				
				leftKid.checkInvariant();
			}			
			
			if(rghtKid != null)
			{ 
				Util.massert(theItem.compareTo(rghtKid.theItem) < 0,
					"Parent item %s is above right Kid Item %s", 
					theItem, rghtKid.theItem);	
				
				
				Util.massert(Util.AimpliesB(isRed, !rghtKid.isRed),
					"Node %s has red=%b, but left kid %s has red=%b", 
					theItem, isRed, rghtKid.theItem, rghtKid.isRed);
				
				rghtKid.checkInvariant();
			}			
		}
		
		
		
		private static <T extends Comparable<T>> void singleDelete(RedBlackNode<T> killnode)
		{
			deleteReplace(killnode, null);
		}
		
		private static <T extends Comparable<T>> void deleteReplace(RedBlackNode<T> killnode, RedBlackNode<T> replace)
		{
			// Util.pf("Replacing killnode %s with replacement %s\n", killnode, replace);
			
			RedBlackNode<T> prnt = killnode.getParent();
			
			// TODO: what if Parent is null?
			
			if(prnt == null)
				{ return; }
			
			if(killnode.isLeftKid())
				{ prnt.setLeftKid(replace); }
			else
				{ prnt.setRghtKid(replace); }
		}
		// }}}
	}
	
	public enum RedBlackState implements StringCodeStateEnum
	{
		// {{{
		
		InsertStart,
		DoesCnodeHaveParent("T->ICPR"),
		SetCnodeBlack("RC"),
		
		IsCnodeParentRed("F->RC"),
		
		IsCnodeUncleRed("F->ICIC"),
		SwapUpperNodeColor,
		Bounce2GrandParent("IS"),
		
		IsCnodeInnerChild("F->PCP"),
		RotateInner2Outer,
		
		PromoteCnodeParent("RC"),
		ReadyComplete;
		
		public final String tCode;
		
		RedBlackState() 		{  tCode  = ""; }	
		RedBlackState(String tc) 	{  tCode = tc; }	
		
		public String getTransitionCode()  { return tCode; }
		
		// }}}
	}	
	
	public enum DeleteState implements StringCodeStateEnum
	{
		// {{{
		DeleteStart,
		TargetHasAnyKid("T->FTH"),
		JustDeleteTarget("DC"),
		
		FindTargetHeir,
		SwapTargetHeirValue,
		HeirHasKid("T->HIB"),
		JustDeleteHeir("DC"),
		
		HeirIsBlack("F->SRC"),
		HeirKidIsRed("F->RRB"),
		TurnHeirKidBlack("SRC"),
		SimpleReplaceCase("DC"),
		
		ReplaceReBalance,

		IsParentNull("T->DC"),
		
		IsSiblingRed("F->ISFB"),
		SwapSiblingParentColor("RSU"),
		
		IsSiblingFamilyBlack("F->IINR"),		
		IsParentBlack("F->SPBSR"),
		SetSiblingRed,
		BounceToParent("IPN"),
		
		SetParentBlackSiblingRed("DC"),
		
		
		
		IsInnerNephewRed("F->RSU"),
		SwapNephewSiblingColor,
		RotateInnerNephewUp,
		
		RotateSiblingUp,		
		DeleteComplete;
		
		public final String tCode;
		
		DeleteState() 			{  tCode  = ""; }	
		DeleteState(String tc) 	{  tCode = tc; }	
		
		public String getTransitionCode()  { return tCode; }
		
		// }}}
	}		
	
	public static class RbDeleteMachine<T extends Comparable<T>> extends FiniteStateMachineImpl
	{
		// {{{
		
		RedBlackNode<T> _trgNode;
		
		RedBlackNode<T> _curNode;
		
		RbDeleteMachine()
		{
			this(null);
		}
		
		RbDeleteMachine(RedBlackNode<T> thenode)
		{
			super(DeleteState.DeleteStart);	
			
			_trgNode = thenode;
		}		
		
		// Dummy state for delete start
		public void deleteStart()  {} 
				
		public boolean targetHasAnyKid()
		{
			return _trgNode.leftKid != null || _trgNode.rghtKid != null;   
		}
		
		public void justDeleteTarget()
		{
			RedBlackNode.singleDelete(_trgNode);   
		}
		
		public void findTargetHeir()
		{
			// Util.pf("Target is %s, left is %s, rght is %s\n", _trgNode, _trgNode.leftKid, _trgNode.rghtKid);
			
			_curNode = _trgNode.leftKid == null ?
			_trgNode.rghtKid.minTreeNode() :
			_trgNode.leftKid.maxTreeNode() ;
			
		}
		
		public void swapTargetHeirValue()
		{
			T gimp = _curNode.theItem;
			
			_curNode.theItem = _trgNode.theItem;
			_trgNode.theItem = gimp;
		}
		
		public boolean heirHasKid()
		{
			return _curNode.leftKid != null || _curNode.rghtKid != null;
		}
		
		public void justDeleteHeir()
		{
			RedBlackNode.singleDelete(_curNode);
		}
		
		public boolean heirIsBlack()
		{
			return !_curNode.isRed;
		}
		
		private RedBlackNode<T> getHeirKid()
		{
			Set<Boolean> checkset = Util.setify(_curNode.leftKid == null, _curNode.rghtKid == null);
			
			Util.massert(checkset.size() == 2, 
				"This method should only be called when the heir (=curNode) has exactly one kid");
			
			return _curNode.leftKid == null ? _curNode.rghtKid : _curNode.leftKid;
		}
		
		public boolean heirKidIsRed()
		{
			return getHeirKid().isRed;
		}
		
		public void turnHeirKidBlack()
		{
			getHeirKid().isRed = false;			
			
			// Util.pf("Turned heir kid black, its now %s\n", getHeirKid());
		}
		
		public void simpleReplaceCase()
		{
			// Util.pf("calling simple replace case with %s --> %s\n",
			//		_curNode, getHeirKid());
			
			RedBlackNode.deleteReplace(_curNode, getHeirKid());
		}	
		
		public void replaceReBalance()
		{
			Util.pf("Calling complex rebalance condition\n");
			
			RedBlackNode<T> heirkid = getHeirKid();
			
			RedBlackNode.deleteReplace(_curNode, heirkid);
			
			_curNode = heirkid;
		}
		
		public boolean isParentNull()
		{
			return _curNode.getParent() == null;
		}
		
		public void setSiblingRed()
		{
			_curNode.getSibling().isRed = true;
		}
		
		public void swapSiblingParentColor()
		{
			swapColor(_curNode.getParent(), _curNode.getSibling());
		}
		
		public void setParentBlackSiblingRed()
		{
			_curNode.getParent().isRed = false;
			_curNode.getSibling().isRed = true;
		}		
		
		public void rotateSiblingUp()
		{
			Util.massert(_curNode.getSibling() != null,
				"Attempt to rotate NULL sibling up, curnode is %s", _curNode);
			
			rotateUp(_curNode.getSibling());
		}
		
		public void bounceToParent()
		{
			_curNode = _curNode.getParent();
		}
		
		public boolean isParentBlack()
		{
			return !_curNode.getParent().isRed;
		}
		
		public boolean isSiblingRed()
		{
			return _curNode.getSibling() == null || _curNode.getSibling().isRed;
		}
		
		public boolean isSiblingFamilyBlack()
		{
			RedBlackNode<T> s = _curNode.getSibling();

			return isNullOrBlack(s) && isNullOrBlack(s.leftKid) && isNullOrBlack(s.rghtKid);
			
			// return !s.isRed && !s.leftKid.isRed && !s.rghtKid.isRed;
		}
		
		public boolean isInnerNephewRed()
		{
			return _curNode.getInnerNephew().isRed;
		}
		
		public void swapNephewSiblingColor()
		{
			swapColor(_curNode.getSibling(), _curNode.getInnerNephew());
		}
		
		public void rotateInnerNephewUp()
		{
			RedBlackNode<T> nephew = _curNode.getInnerNephew();
			
			rotateUp(nephew);
		}
		
		// }}}
	}
	
	public static class RedBlackMachine<T extends Comparable<T>> extends FiniteStateMachineImpl
	{
		// {{{
		private RedBlackNode<T> _rootNode;
		
		private RedBlackNode<T> _curNode;
		
		public RedBlackMachine()
		{
			super(RedBlackState.ReadyComplete);	
		}
		
		public LinkedList<T> toList()
		{
			LinkedList<T> ilist = Util.linkedlist();
			
			if(_rootNode != null)
			{ 
				_rootNode.popList(ilist);
			}
			
			return ilist;
		}
		
		public boolean add(T newitem)
		{
			if(_rootNode == null)
			{
				_rootNode = new RedBlackNode<T>(newitem);
				_rootNode.isRed = false;
				return true;
			}
			
			_curNode = _rootNode.add(newitem);	
			
			boolean didadd = _curNode != null;
			
			if(didadd)
			{ 
				setState(RedBlackState.InsertStart);
				run2Completion();
				
				int bouncecount = 0;
				
				for( ; _rootNode.getParent() != null; bouncecount++)
				{
					_rootNode = _rootNode.getParent();						
				}
				
				Util.massert(bouncecount <= 1, "Did %d root bounce operatinos", bouncecount);
			}
			
			return didadd;
		}
		
		public boolean remove(T killitem)
		{
			RedBlackNode<T> killnode = _rootNode == null ? null : _rootNode.find(killitem);
			
			if(killnode == null)
				{ return false; }
			
			RbDeleteMachine<T> delmach = new RbDeleteMachine<T>(killnode);
			
			delmach.run2Completion();
			
			return true;
		}
		
		public boolean contains(T probeitem)
		{
			return _rootNode == null ? false : _rootNode.contains(probeitem);	
			
		}
		
		public void checkInvariant()
		{
			if(_rootNode == null)
				{ return; }
			
			_rootNode.checkInvariant();
		}
		
		// Dummy state for insertion start
		public void insertStart() {}
		
		public boolean doesCnodeHaveParent()
		{
			return _curNode.getParent() != null;
		}
		
		public void setCnodeBlack()
		{
			_curNode.isRed = false;	
		}
		
		public boolean isCnodeParentRed()
		{
			return _curNode.getParent().isRed;	
		}
		
		public boolean isCnodeUncleRed()
		{
			RedBlackNode<T> uncle = _curNode.getUncle();
			
			return uncle != null && uncle.isRed;
		}
		
		public void swapUpperNodeColor()
		{
			// Util.pf("Swapping node colors...\n");
			
			_curNode.getParent().isRed = false;
			_curNode.getUncle().isRed  = false;
			
			_curNode.getGrandParent().isRed  = true;
			
			
			// Util.pf("Parent is %s\n", _curNode.getParent());
			// Util.pf("Uncle  is %s\n", _curNode.getUncle());
			// Util.pf("GParent is %s\n", _curNode.getGrandParent());
			// Util.pf("Current is %s\n", _curNode);
		}		
		
		public void commLineResult(String inputstr)
		{
			if(inputstr.startsWith("A"))
			{	
				String sub = inputstr.substring(1);
				T betterbeint = Util.cast(Integer.valueOf(sub));
				add(betterbeint);
			}
		}
		
		public void bounce2GrandParent()
		{
			_curNode = _curNode.getGrandParent();	
		}
		
		public boolean isCnodeInnerChild()
		{
			boolean a = _curNode.isLeftKid();
			boolean b = _curNode.getParent().isLeftKid();
			
			return a != b;			
		}
		
		public void rotateInner2Outer()
		{
			RedBlackNode<T> p = _curNode.getParent();
			
			rotateUp(_curNode);
			
			_curNode = p;
		}
		
		public void promoteCnodeParent()
		{
			RedBlackNode<T> p = _curNode.getParent();
			RedBlackNode<T> g = p.getParent();
			
			Util.massert(p.isRed && !g.isRed,
				"Expected parent to be red, grandparent to be black, found pred=%b, gpred=%b", p.isRed, g.isRed);
			
			p.isRed = false;
			g.isRed = true;
			
			rotateUp(p);
		}
		
		// }}}
	}
	
	
	public static class TestInsertLogic extends ArgMapRunnable
	{
		
		public void runOp()
		{
			int treesize = _argMap.getInt("size", 100);
			int seedid = _argMap.getInt("seedid", -1);
			
			RedBlackMachine<Integer> rbm = new RedBlackMachine<Integer>();
			
			List<Integer> mylist = Util.range(treesize);
			
			if(seedid > -1)
			{
				Random myrand = new Random(seedid);	
				Collections.shuffle(mylist, myrand);
			} else {
				
				Collections.shuffle(mylist);
			}
			
			Set<Integer> curset = Util.treeset();
			
			for(int oneinsert : mylist)
			{ 
				rbm.add(oneinsert);
				
				try {
					rbm._rootNode.getCheckBlackHeight();
				} catch (Exception ex) {
					
					rbm._rootNode.print();
					throw ex;
				}
			}
			
			// rbm._rootNode.print();
			
			for(int probe : mylist)
			{
				Util.massert(rbm._rootNode.contains(probe),
					"Failed to find probe node %d in tree", probe);
			}
			
			Util.pf("Success\n");
		}
	}
	
	public static class TestDeleteLogic extends ArgMapRunnable
	{
		
		public void runOp()
		{
			int treesize = _argMap.getInt("size", 100);
			int seedid = _argMap.getInt("seedid", -1);
			Random myrand = new Random(seedid);
			
			RedBlackMachine<Integer> rbm = new RedBlackMachine<Integer>();
			

			
			for(int i : Util.range(treesize))
				{ rbm.add(i); }
			
			for(int probe : Util.range(treesize))
			{
				Util.massert(rbm._rootNode.contains(probe),
					"Failed to find probe node %d in tree", probe);
			}
			
			// rbm._rootNode.print();
			
			List<Integer> mylist = Util.range(treesize);
			
			Collections.shuffle(mylist, myrand);
			
			for(int remove : mylist)
			{
				Util.pf("Going to delete node %d\n", remove);
				
				if(remove == 1)
				{
					rbm._rootNode.print();	
				}
				
				rbm.remove(remove);
				
				try {
					rbm._rootNode.getCheckBlackHeight();
				} catch (Exception ex) {
					
					rbm._rootNode.print();
					throw ex;
				}				
				
				
				// Util.massert(
				
				// rbm._rootNode.print();
			}
		}
	}	
	
	public static class FullSystemCheck extends ArgMapRunnable
	{
		Random _genRand;
		Random _prbRand;
		
		Integer _maxRange;
		Integer _addPercent;
		
		TreeSet<Integer> _referenceSet = null;
		RedBlackMachine<Integer> _rbMachine = new RedBlackMachine<Integer>();
		
		public void runOp()
		{
			int maxstep = _argMap.getInt("maxstep", 1_000_000);
			boolean useref = _argMap.getBit("useref", true);
			
			_maxRange = _argMap.getInt("maxrange", 1_000_000);
			_addPercent = _argMap.getInt("addpercent", 60);
			
			int genseed = _argMap.getInt("genseed");
			int prbseed = _argMap.getInt("probeseed", 1000);

			_genRand = new Random(genseed);
			_prbRand = new Random(prbseed);
			
			if(useref)
				{ _referenceSet = Util.treeset(); }
			
			for(int i : Util.range(maxstep))
			{
				oneOperation();
				
				probeEqual();
			}
		}
		
		private void oneOperation()
		{	
			boolean doadd = _genRand.nextInt(100) < _addPercent;
			int nextval = _genRand.nextInt(_maxRange);
			
			Boolean result = doadd ? _rbMachine.add(nextval) : _rbMachine.remove(nextval);

			

			if(_referenceSet != null)
			{
				Boolean refresult = doadd ? _referenceSet.add(nextval) : _referenceSet.remove(nextval);

				Util.massert(result.equals(refresult),
					"Reference set reported add=%b , rbm reported add=%b, for nextval=%d",
					refresult, result, nextval);				
			}
		}
		
		private void probeEqual()
		{
			if(_referenceSet == null)
				{ return; }
			
			if(_referenceSet.size() < 100)
			{	
				List<Integer> alist = Util.vector(_referenceSet);
				List<Integer> blist = _rbMachine.toList();
				
				Util.massert(alist.equals(blist),
					"AList/BList: \n\t%s\n\t%s", alist, blist);
			}
			
			for(int i : Util.range(10))
			{
				int checkval = _prbRand.nextInt(_maxRange);	
				
				boolean a = _rbMachine.contains(checkval);
				boolean b = _referenceSet.contains(checkval);
				
				Util.massert(a == b,
					"RBMachine reports contains=%b  but refset reports contains=%b for checkval=%d",
					a, b, checkval);
			}
		}
	}		
}
