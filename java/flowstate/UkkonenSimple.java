
package net.danburfoot.flowstate; 

import java.util.*;

import net.danburfoot.shared.Util;
import net.danburfoot.shared.Util.*;
import net.danburfoot.shared.FiniteState.*;

// This is a solution to Problem 14, "Longest Collatz sequence", of Project Euler
// https://projecteuler.net/problem=14
public class UkkonenSimple
{
	public enum StrieUpdateEnum implements StringCodeStateEnum
	{
		InitBoundaryNode,
		
		HaveTransition("T->CLSL"),

		CreateNewNode,
		CreateNewTransition,
		
		IsCurNodeTop("T->URP"),
		CreateNewSuffixLink,
		UpdateRPrime,
		FollowSuffixLink("HT"),

		
		CreateLastSuffixLink,
		UpdateTopNode,
		UpdateComplete;
		
		public final String tCode;
		StrieUpdateEnum() 		{  tCode  = ""; }	
		StrieUpdateEnum(String tc) 	{  tCode = tc; }	
		public String getTransitionCode()  { return tCode; }		
	}
	
	
	public static class StrieUpdateMachine extends FiniteStateMachineImpl
	{
		final SuffixTrie _theTrie;
		
		final Character _nextChar;
		
		private StrieNode _curNode;
		
		private LinkedList<StrieNode> _rprimeList = Util.linkedlist();
		
		public StrieUpdateMachine()
		{
			this(null, null);
		}
		
		public StrieUpdateMachine(SuffixTrie strie, Character nextchar)
		{
			super(StrieUpdateEnum.InitBoundaryNode);	
			
			_theTrie = strie;
			
			_nextChar = nextchar;
			
			_rprimeList.add(null);
		}		
				
		public void initBoundaryNode()
		{
			_curNode = _theTrie.getTopNode();
		}
		
		public boolean haveTransition()
		{
			// Util.pf("CurNode %s has transition for Ti=%c ? %b\n",
			//	_curNode.getLabel(), _nextChar, _curNode.haveTransition(_nextChar));
			
			return _curNode.haveTransition(_nextChar);
		}
		
		public void createNewNode()
		{
			StrieNode rprime = new StrieNode(_nextChar);
			
			// Util.pf("Created new node with char=%c\n", _nextChar);
			
			_rprimeList.addLast(rprime);
		}
		
		public void createNewTransition()
		{
			_curNode.setTransition(_nextChar, _rprimeList.getLast());
		}
		
		public boolean isCurNodeTop()
		{
			return _theTrie.getTopNode() == _curNode;
		}
		
		public void createNewSuffixLink()
		{
			Util.massertEqual(2, _rprimeList.size(), 
				"Expect RPrime List size %d here, got %d");
			
			_rprimeList.getFirst().setSuffixLink(_rprimeList.getLast());
		}
		
		public void updateRPrime()
		{
			_rprimeList.pollFirst();	
		}
		
		public void followSuffixLink()
		{
			// Util.pf("Following suffix link %s -> %s\n", 
			//	_curNode.getLabel(), _curNode.getSuffixLink().getLabel());
			
			_curNode = _curNode.getSuffixLink();	
		}
		
		public void createLastSuffixLink()
		{
			_rprimeList.getFirst().setSuffixLink(_curNode.getTransition(_nextChar));
		}
		
		public void updateTopNode()
		{
			StrieNode newtop = _theTrie.getTopNode().getTransition(_nextChar);
			
			_theTrie.setTopNode(newtop);
		}
	}

	public static class StrieNode
	{
		public final Character inChar;
		
		private final Map<Character, StrieNode> _transMap = Util.treemap();
		
		private StrieNode _suffixLink;
		
		public StrieNode(Character incoming)
		{
			inChar = incoming;
		}		
		
		public boolean haveTransition(Character c)
		{
			return _transMap.containsKey(c);
		}
		
		public StrieNode getTransition(Character c)
		{
			return _transMap.get(c);	
		}
		
		public boolean isFinal()
		{
			return _transMap.isEmpty();	
		}
		
		void setTransition(Character tchar, StrieNode nextnode)
		{
			Util.massert(!_transMap.containsKey(tchar),
				"Transition map already contains transition for %s", tchar);
			
			_transMap.put(tchar, nextnode);
		}
		
		StrieNode getSuffixLink()
		{
			Util.massert(_suffixLink != null,
				"Attempt to get suffix link, but it has not yet been set, char=%s", inChar);
			
			return _suffixLink;
		}
		
		void setSuffixLink(StrieNode sufflink)
		{
			Util.massert(_suffixLink == null,
				"Node already has suffix link");
			
			_suffixLink = sufflink;	
		}
		
		public boolean accept(String s, int pos)
		{
			if(pos == s.length())
				{ return isFinal(); }
			
			char c = s.charAt(pos);
			
			if(haveTransition(c))
				{ return getTransition(c).accept(s, pos+1); }
			
			return false;
		}
		
		public String toString()
		{
			return Util.sprintf("%s->[%s]", getLabel(), Util.join(_transMap.keySet(), ","));	
		}
		
		public String getLabel()
		{
			return inChar == null ? "SIGMA" : inChar +"";	
		}
		
		void popNodeList(List<StrieNode> kidlist)
		{
			kidlist.add(this);
			
			for(StrieNode kidnode : _transMap.values())
			{
				kidnode.popNodeList(kidlist);
			}
		}
	}
	
	static class DummyNode extends StrieNode
	{
		final StrieNode rootNode;
		
		DummyNode(StrieNode rnode)
		{
			super(null);	
			
			rootNode = rnode;
		}
		
		public boolean haveTransition(Character c)
		{
			return true;
		}
		
		public StrieNode getTransition(Character c)
		{
			return rootNode;
		}
		
		void setTransition(Character tchar, StrieNode nextnode)
		{
			Util.massert(false, 
				"Attempt to set transition of dummy node");
		}
		
		StrieNode getSuffixLink()
		{
			Util.massert(false, "Attempt to get suffix link on dummy node");
			return null;
		}
		
		void setSuffixLink(StrieNode sufflink)
		{
			Util.massert(false, "Attempt to set suffix link of Dummy Node");
		}		
		
		public String toString()
		{
			return getLabel();
		}
		
		public String getLabel()
		{
			return "DUMMY";	
		}
		
	}
	
	
	
	public static class SuffixTrie
	{
		private StrieNode _topNode;
		
		private StrieNode _rootNode;
		
		private DummyNode _dummyNode;
		
		public SuffixTrie()
		{
			_rootNode = new StrieNode(null);
			
			_dummyNode = new DummyNode(_rootNode);

			// I have a bad feeling about this...
			_rootNode.setSuffixLink(_dummyNode);
			
			_topNode = _rootNode;
		}
		
		public String longestSubstring(LinkedList<Character> llist)
		{
			
			return "";			
			
		}
		
		public boolean isSuffix(String s)
		{
			return _rootNode.accept(s, 0);
		}		
		
		public StrieNode getTopNode()
		{
			return _topNode;
		}
		
		public void setTopNode(StrieNode newtop)
		{
			_topNode = newtop;
		}
		
		public List<StrieNode> getNodeList()
		{
			List<StrieNode> nodelist = Util.vector();
			_rootNode.popNodeList(nodelist);
			return nodelist;
		}
		
		public void showSuffixInfo()
		{
			Util.pf("------------\n");
			Util.pf("Suffix Info:\n");	
			
			for(StrieNode onenode : getNodeList())
			{
				Util.pf("\t%s --> %s\n", onenode.getLabel(), onenode.getSuffixLink().getLabel());	
			}
			
			Util.pf("------------\n");
		}
	}
	
	public static class BuildSimpleTrie extends ArgMapRunnable
	{
		
		public void runOp()
		{
			String thestr = _argMap.getStr("thestr");
			String suffix = _argMap.getStr("suffix");
			
			SuffixTrie thetrie = new SuffixTrie();
						
			for(int i : Util.range(thestr.length()))
			{
				Character c = thestr.charAt(i);
				
				StrieUpdateMachine sumach = new StrieUpdateMachine(thetrie, c);
				
				sumach.run2Completion();
				
				// Util.pf("Extended trie for char=%c\n", c);
				
				
				// thetrie.showSuffixInfo();
			}
			
			
			Util.pf("String %s suffix of %s ? %b \n", suffix, thestr, thetrie.isSuffix(suffix));
		}
		
	}
	
}
