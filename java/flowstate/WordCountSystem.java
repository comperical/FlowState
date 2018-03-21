
package net.danburfoot.flowstate; 

import java.util.*;
import java.io.*;

import net.danburfoot.shared.*;
import net.danburfoot.shared.Util.*;
import net.danburfoot.shared.FileUtils.*;
import net.danburfoot.shared.FiniteState.*;

public class WordCountSystem
{
	/**
	* This is an implementation of the problem used in the book 
	* "Exercises in Programming Style" by Cristina Vidiera Lopes.
	* https://www.amazon.com/Exercises-Programming-Style-Cristina-Videira/dp/1482227371/
	* https://github.com/crista/exercises-in-programming-style
	*/
	
	public enum WordCountState implements StringCodeStateEnum
	{
		StartMachine,
		ReadInputFile,
		ReadStopWordData,
		HaveAnotherChar("F->SWQ"),
		IsAlphaNumeric("F->AWS"),
		AddLowerCase("PCQ"),
		AddWhiteSpace("PCQ"),
		PollCharQueue("HAC"),
	
		SetupWordQueue,
		HaveAnotherWord("F->SAS"),
		IsStopWord("T->PWQ"),
		IsSingleLetter("T->PWQ"),
		IncrementFrequency,
		PollWordQueue("HAW"),
		
		SortAndShow,
		CountComplete;

		public final String tCode;
		
		WordCountState() 		{  tCode  = ""; }	
		WordCountState(String tc) 	{  tCode = tc; }	
		
		public String getTransitionCode()  { return tCode; }
		
	}
	
	public  static class WordCountMachine extends FiniteStateMachineImpl
	{
		private LinkedList<Character> _charQ;
		
		private LinkedList<String> _wordQ;
		
		private Set<String> _stopSet;
		
		private StringBuffer _filterString = new StringBuffer();
				
		private Map<String, Integer> _freqMap = Util.treemap();
		
		public WordCountMachine()
		{
			super(WordCountState.StartMachine);	
		}
				
		public void startMachine()
		{
			
		}
		
		public void readInputFile()
		{
			String datafile = "../data/pride-and-prejudice.txt";
			
			List<String> linelist = FileUtils.getReaderUtil()
								.setFile(datafile)
								.setTrim(false)
								.readLineListE();
			_charQ = Util.linkedlist();					
								
			for(String oneline : linelist)
			{
				for(int i : Util.range(oneline.length()))
					{ _charQ.add(oneline.charAt(i)); }
				
				_charQ.add('\n');
			}
		}
		
		public void readStopWordData()
		{
			_stopSet = Util.treeset();
			
			String stopfile = "../data/stop_words.txt";
			
			String filedata = FileUtils.getReaderUtil()
							.setFile(stopfile)
							.readSingleStringE();
							
			for(String stopword : filedata.split(","))
				{ _stopSet.add(stopword); }
			
		}
		
		private Character nextChar()
		{
			return _charQ.peek();	
		}
		
		public boolean haveAnotherChar()
		{
			return !_charQ.isEmpty();
		}
		
		public boolean isAlphaNumeric()
		{
			return Character.isLetterOrDigit(nextChar());
		}
		
		public void addLowerCase()
		{
			_filterString.append(Character.toLowerCase(nextChar()));
		}
		
		public void pollCharQueue()
		{	
			_charQ.poll();
		}
		
		public void addWhiteSpace()
		{
			_filterString.append(" ");
		}
		
		public void setupWordQueue()
		{
			_wordQ = Util.linkedlist();
			
			for(String word : _filterString.toString().split(" "))
				{ _wordQ.add(word); }
		}
		
		public boolean haveAnotherWord()
		{
			return !_wordQ.isEmpty();
		}
		
		public boolean isStopWord()
		{
			return _stopSet.contains(nextWord());
		}
		
		public boolean isSingleLetter()
		{
			return nextWord().length() <= 1;
		}		
		
		
		private String nextWord()
		{
			return _wordQ.peek();	
		}
		
		public void incrementFrequency()
		{
			int pval = _freqMap.containsKey(nextWord()) ? _freqMap.get(nextWord()) : 0;
			_freqMap.put(nextWord(), pval+1);
		}
		
		public void pollWordQueue()
		{
			_wordQ.poll();
		}
		
		public void sortAndShow()
		{
			TreeSet<Pair<Integer, String>> topset = Util.treeset();
			
			for(String word : _freqMap.keySet())
			{
				topset.add(Pair.build(_freqMap.get(word), word));
				
				while(topset.size() > 25)
					{ topset.pollFirst();} 
			}
			
			while(!topset.isEmpty())
			{
				Pair<Integer, String> top = topset.pollLast();
				
				Util.pf("%s -- %d\n", top._2, top._1);
			}
		}
	}
}
