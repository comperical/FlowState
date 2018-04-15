
package net.danburfoot.flowstate; 

import java.util.*;

import net.danburfoot.shared.Util;
import net.danburfoot.shared.FiniteState.*;

public class MonsterDance
{
	public enum StepDir
	{
		north,
		east, 
		west, 
		south;
	}
	
	public enum MDanceState implements StringCodeStateEnum
	{
		StartDance,
		
		DanceLoop,
		IsPlayerNear("F->ISQE"),
		Step2Player("TAS"),
		
		IsStepQueueEmpty("F->PSQ"),
		AddStepToQueue,
		
		PollStepQueue,
		TakeActualStep("DL");
		
		
		public final String tCode;
		
		MDanceState() 		{  tCode  = ""; }	
		MDanceState(String tc) 	{  tCode = tc; }	
		
		public String getTransitionCode()  { return tCode; }
	}
	
	public static class MDanceMachine extends FiniteStateMachineImpl
	{
		private StepDir _nextDir;
		
		private Random _myRandom;
		
		private LinkedList<StepDir> _stepQueue = Util.linkedlistify();
		
		// Use for diagram purposes only
		public MDanceMachine()
		{
			super(MDanceState.StartDance);
		}
		
		public void startDance()
		{
			// Maybe initialize Dance info	
		}
		
		public void danceLoop()
		{
			// dummy state for dance loop	
			
		}
		
		public boolean isPlayerNear()
		{
			return _myRandom.nextDouble() < 0.1;	
		}
		
		public void step2Player()
		{
			int stepint = _myRandom.nextInt(StepDir.values().length);
			_nextDir = StepDir.values()[stepint];
		}
		
		public boolean isStepQueueEmpty()
		{
			return _stepQueue.isEmpty();
		}
		
		public void addStepToQueue()
		{
			for(StepDir sd : StepDir.values())
				{ _stepQueue.add(sd); }
		}
		
		public void pollStepQueue()
		{
			_nextDir = _stepQueue.poll();
		}
		
		public void takeActualStep()
		{
			Util.pf("Stepping towards %s\n", _nextDir);	
			
		}
	}
}
