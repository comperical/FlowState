
package net.danburfoot.flowstate; 

import java.util.*;

import net.danburfoot.shared.Util;
import net.danburfoot.shared.Util.*;
import net.danburfoot.shared.FiniteState.*;

public class AvlTreeSystem
{
	
	private static AvlNode rotateLeft(AvlNode anode)
	{
		AvlNode rghtkid = (AvlNode) anode.rght;
		
		AvlNode newleft = new AvlNode(anode.theVal, anode.left, rghtkid.left);
		
		return new AvlNode(rghtkid.theVal, newleft, rghtkid.rght);
	}
	
	private static AvlNode rotateRght(AvlNode anode)
	{
		AvlNode leftkid = (AvlNode) anode.left;
		
		AvlNode newrght = new AvlNode(anode.theVal, leftkid.rght, anode.rght);
		
		return new AvlNode(leftkid.theVal, leftkid.left, newrght);
	}	
	
	private static AvlTree delete(AvlTree thetree, int theval)
	{
		return AvlTreeOpMachine.getMachine(AvlTreeOpState.DeleteStart, thetree, theval).runGetResult();
	}
	
	private static AvlTree insert(AvlTree thetree, int theval)
	{
		return AvlTreeOpMachine.getMachine(AvlTreeOpState.InsertStart, thetree, theval).runGetResult();
	}
	
	private static AvlTree calcDeleteResult(AvlNode anode)
	{
		boolean leftisleaf = anode.left.isLeaf();
		boolean rghtisleaf = anode.rght.isLeaf();
		
		// If the node to delete has NO children, we just return a leaf.
		if(leftisleaf && rghtisleaf)
		{ 
			return new AvlLeaf();
		}
		
		// If the node to delete has a single child, we return it.
		if(leftisleaf || rghtisleaf)
		{
			return leftisleaf ? anode.rght : anode.left;
		}
		
		// Complex case: have both left and right children
		// We find the max-successor of the node,
		// And create a new tree with the root as the maxsucc,
		// and the result of deleting the maxsucc from the left tree.
		int maxsucc = ((AvlNode) anode.left).max();
		
		return new AvlNode(maxsucc, delete(anode.left, maxsucc), anode.rght);			
	}	
	
	public static abstract class AvlTree
	{
		public final int height;
		
		private AvlTree(int h)
		{
			height = h;	
		}
		
		public int getSlope() 
		{
			return 0;	
		}
		
		public boolean isLeaf()
		{
			return height == 0;	
		}
				
		public LinkedList<Integer> getList() 
		{
			return new LinkedList<Integer>();
		}
		
		public boolean contains(int x) 
		{
			return false;	
		}

		void checkInvariant() {}
	}
	
	public static class AvlNode extends AvlTree
	{
		final int theVal;
		
		private final AvlTree left;
		private final AvlTree rght;
		
		private AvlNode(int tv, AvlTree L, AvlTree R)
		{
			super(1 + (L.height > R.height ? L.height : R.height));
			
			theVal = tv;
			
			left = L;
			rght = R;
		}
		
		// The "slope" of the tree, also called the imbalance factor
		@Override
		public int getSlope()
		{
			return left.height - rght.height;	
		}	
		
		public int max()
		{
			return rght.isLeaf() ? theVal : ((AvlNode) rght).max();	
		}
		
		@Override
		public LinkedList<Integer> getList()
		{
			LinkedList<Integer> leftlist = left.getList();
			leftlist.add(theVal);
			leftlist.addAll(rght.getList());
			return leftlist;
		}
		
		@Override 
		public boolean contains(int x)
		{
			if(theVal == x)
				{ return true; }
			
			return (x < theVal ? left.contains(x) : rght.contains(x));
		}
		
		@Override
		void checkInvariant()
		{
			int s = getSlope();
			
			Util.massert(-1 <= s && s <= 1, "Slope is out of range: s=%d", s);
			
			left.checkInvariant();
			rght.checkInvariant();
		}
	}
	
	public static class AvlLeaf extends AvlTree
	{
		private AvlLeaf()
		{
			super(0);	
		}
	}
	
	public enum AvlTreeOpState implements StringCodeStateEnum
	{
		DeleteStart,
		DIsTargetLeaf("T->OC"),
		FoundDeleteTarget("F->DTBV"),
		ComposeDeleteResult("OC"),
		
		DTargetBelowValue("F->RDR"),
		RecDeleteLeft("BS"),
		RecDeleteRght("BS"),
		
		InsertStart,
		IIsTargetLeaf("F->FIT"),
		ComposeNewNode("OC"),
		
		FoundInsertTarget("T->OC"),
		ITargetBelowValue("F->RIR"),
		RecInsertLeft("BS"),
		RecInsertRght("BS"),
		
		BalanceStart,
		HaveStrongImbalance("F->OC"),
		MainTreeSlopeUp("F->RKSU"),
		
		LeftKidSlopeDown("F->BRR"),
		RotateLeftKidLeft,
		BasicRotateRght("OC"),		

		RghtKidSlopeUp("F->BRL"),
		RotateRghtKidRght,
		BasicRotateLeft("OC"),
		
		OpComplete;
		
		public final String tCode;
		
		AvlTreeOpState() 		{  tCode  = ""; }	
		AvlTreeOpState(String tc) 	{  tCode = tc; }	
		public String getTransitionCode()  { return tCode; }			
	}
	
	public static class AvlTreeOpMachine extends FiniteStateMachineImpl
	{
		private AvlTree _resultTree;
		
		private int _opVal;
		
		AvlTreeOpMachine()
		{
			super(AvlTreeOpState.OpComplete);
		}
		
		public AvlTree runGetResult()
		{
			run2Completion();
			
			return _resultTree;
		}
		
		public boolean dIsTargetLeaf()
		{
			return _resultTree.isLeaf();
		}
		
		public boolean iIsTargetLeaf()
		{
			return _resultTree.isLeaf();
		}
			
		public void composeNewNode()
		{
			_resultTree = new AvlNode(_opVal, new AvlLeaf(), new AvlLeaf());	
		}
		
		public void recDeleteLeft()
		{
			replaceLeft(delete(targAsNode().left, _opVal));
		}
		
		public void recDeleteRght()
		{
			replaceRght(delete(targAsNode().rght, _opVal));
		}
		
		public boolean dTargetBelowValue()
		{	
			return _opVal < targAsNode().theVal;
		}
		
		public boolean iTargetBelowValue()
		{
			return _opVal < targAsNode().theVal;	
		}		
		
		public boolean foundDeleteTarget()
		{
			return _opVal == targAsNode().theVal;	
		}
		
		public boolean foundInsertTarget()
		{
			return _opVal == targAsNode().theVal;
		}		
		
		public void recInsertLeft()
		{
			replaceLeft(insert(targAsNode().left, _opVal));
		}
		
		public void recInsertRght()
		{
			replaceRght(insert(targAsNode().rght, _opVal));
		}
		
		public void composeDeleteResult()
		{
			_resultTree = calcDeleteResult(targAsNode());
		}
		
		private AvlNode targAsNode()
		{
			Util.massert(_resultTree instanceof AvlNode);
			
			return Util.cast(_resultTree);
		}
		
		public void balanceStart() {}
		
		public void deleteStart() {}
		
		public void insertStart() {}
		
		public boolean haveStrongImbalance()
		{
			int s = targAsNode().getSlope();
			
			// -2 or +2
			return s * s == 4;
		}
		
		public boolean mainTreeSlopeUp()
		{
			return targAsNode().getSlope() > 0;
		}

		public boolean leftKidSlopeDown()
		{
			return targAsNode().left.getSlope() == -1;
		}
		
		public boolean rghtKidSlopeUp()
		{
			return targAsNode().rght.getSlope() == +1;
		}
		
		public void basicRotateLeft()
		{
			_resultTree = rotateLeft(targAsNode());
		}
		
		public void basicRotateRght()
		{
			_resultTree = rotateRght(targAsNode());
		}		
		
		public void rotateLeftKidLeft()
		{
			replaceLeft(rotateLeft((AvlNode) targAsNode().left));
		}
		
		public void rotateRghtKidRght()
		{
			replaceRght(rotateRght((AvlNode) targAsNode().rght));
		}		
		
		private void replaceLeft(AvlTree newleft)
		{
			_resultTree = new AvlNode(targAsNode().theVal, newleft, targAsNode().rght);
		}
		
		private void replaceRght(AvlTree newrght)
		{
			_resultTree = new AvlNode(targAsNode().theVal, targAsNode().left, newrght);
		}
		
		// This is just a hacky cache mechanism that helps with performance. 
		// When you create an FSM, it needs to do some initialization stuff,
		// This is fast in absolute terms but slow if you do it millions of times. 
		// So this trick allows us to reuse the machines.
		private static List<AvlTreeOpMachine> _OP_POOL = Util.vector();
		
		private static AvlTreeOpMachine getMachine(AvlTreeOpState thestate, AvlTree targtree, int op)
		{
			AvlTreeOpMachine opmachine = null;			
			
			for(AvlTreeOpMachine mach : _OP_POOL)	
			{ 
				if(mach.getState() == AvlTreeOpState.OpComplete)
				{ 
					opmachine = mach; 
					break;
				}
			}
			
			if(opmachine == null)
			{
				opmachine = new AvlTreeOpMachine();
				_OP_POOL.add(opmachine);
			}
			
			opmachine.setState(thestate);
			opmachine._resultTree = targtree;
			opmachine._opVal = op;	
			return opmachine;
		}	
	}
	
	public static class FullAvlTreeCheck extends ArgMapRunnable
	{
		Random _genRand;
		Random _prbRand;
		
		Integer _maxRange;
		Integer _addPercent;
		
		TreeSet<Integer> _referenceSet = null;
		// RedBlackMachine<Integer> _rbMachine = new RedBlackMachine<Integer>();
		AvlTree _theTree = new AvlLeaf();
		
		
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
			
			Boolean result = (doadd ? !_theTree.contains(nextval) : _theTree.contains(nextval));
			
			_theTree = (doadd ? insert(_theTree, nextval) : delete(_theTree, nextval));
						
			_theTree.checkInvariant();
			
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
				List<Integer> blist = _theTree.getList();
				
				Util.massert(alist.equals(blist),
					"AList/BList: \n\t%s\n\t%s", alist, blist);
			}
			
			for(int i : Util.range(10))
			{
				int checkval = _prbRand.nextInt(_maxRange);	
				
				boolean a = _theTree.contains(checkval);
				boolean b = _referenceSet.contains(checkval);
				
				Util.massert(a == b,
					"RBMachine reports contains=%b  but refset reports contains=%b for checkval=%d",
					a, b, checkval);
			}
		}
	}		
}
