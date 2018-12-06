
package net.danburfoot.flowstate; 

import java.util.*;

import net.danburfoot.shared.Util;
import net.danburfoot.shared.Util.*;
import net.danburfoot.shared.FileUtils;

import net.danburfoot.shared.FiniteState.*;

public class PaperCutter
{
	public static class PaperData
	{
		final int A1;
		final int A2;
		final int A3;
		final int A4;
		final int A5;
		
		final String strKey;
		
		final double _total;
		
		private Double _theValue;
		
		PaperData(int a1, int a2, int a3, int a4, int a5)
		{
			A1 = a1;
			A2 = a2;
			A3 = a3;
			A4 = a4;
			A5 = a5;
			
			strKey = Util.varjoin(",", A1, A2, A3, A4, A5);
			
			_total = A1 + A2 + A3 + A4 + A5;
		}
		
		private int intrinsicValue()
		{
			return A1 + A2 + A3 + A4 + A5 == 1 ? 1 : 0;
		}
		
		void setExtraValue(double x)
		{
			Util.massert(_theValue == null);
			_theValue = x + intrinsicValue();
			
			Util.pf("Set value for state %s to %.03f=%d+%.06f\n", strKey, _theValue, intrinsicValue(), x);
		}
		
		double getValue()
		{
			Util.massert(_theValue != null);
			return _theValue;
		}
		
		public int totalArea()
		{
			return A5 + A4*2 + A3*4 + A2*8 + A1*16;	
		}
		
		public List<PaperData> getOneStepList()
		{
			return Util.vector(getStepMap().values());
		}
		
		public double getProb4Step(int stepnum)
		{
			double initprob = getCount4Step(stepnum);
			return initprob / _total;
		}
		
		private int getCount4Step(int stepnum)
		{
			switch(stepnum)
			{
				case 1:	return A1;	
				case 2: return A2;
				case 3: return A3;
				case 4: return A4;
				case 5: return A5;
				default: throw new RuntimeException("BAd step num");
			}			
		}
		
		
		public Map<Integer, PaperData> getStepMap()
		{
			Map<Integer, PaperData> gimpmap = Util.treemap();
			
			gimpmap.put(1, new PaperData(A1-1, A2+1, A3+1, A4+1, A5+1));
			gimpmap.put(2, new PaperData(A1  , A2-1, A3+1, A4+1, A5+1));
			gimpmap.put(3, new PaperData(A1  , A2  , A3-1, A4+1, A5+1));
			gimpmap.put(4, new PaperData(A1  , A2  , A3  , A4-1, A5+1));
			gimpmap.put(5, new PaperData(A1  , A2  , A3  , A4  , A5-1));
			
			Map<Integer, PaperData> stepmap = Util.treemap();
			
			for(int stepkey : gimpmap.keySet())
			{
				PaperData onestep = gimpmap.get(stepkey);
				
				if(onestep.isValid())
					{ stepmap.put(stepkey, onestep); }
			}
				
			return stepmap;
		}
		
		public boolean isValid()
		{
			List<Integer> alist = Util.listify(A1, A2, A3, A4, A5);
			return Util.countPred(alist, anum -> anum < 0) == 0;
		}
	
	}
	
	
	public enum PaperMachineState implements StringCodeStateEnum
	{
		InitState,
		BuildCandidateList,
		HaveAnyNew("F->CVFS"),
		AddCandidates("BCL"),
		
		CalcValueForStage,
		AtMaxStage("T->CC"),
		IncrementStageCount("CVFS"),
		
		CalcComplete;
		
		public final String tCode;
		
		PaperMachineState() 			{  tCode  = ""; }	
		PaperMachineState(String tc) 		{  tCode = tc; }	
		
		public String getTransitionCode()  	{ return tCode; }		
	}
	
	public static class PaperCutMachine extends FiniteStateMachineImpl
	{
		private Map<String, PaperData> _stateMap = Util.treemap();
		
		private LinkedList<PaperData> _candList;
		
		private int _stageCount = 1;
		
		public PaperCutMachine()
		{
			super(PaperMachineState.InitState);	
		}
		
		public void initState()
		{
			PaperData basic = new PaperData(1, 0, 0, 0, 0);
			_stateMap.put(basic.strKey, basic);
		}
		
		public void buildCandidateList()
		{
			_candList = Util.linkedlist();
			
			for(PaperData pdata : _stateMap.values())
				{ _candList.addAll(pdata.getOneStepList()); }
		}
		
		public boolean haveAnyNew()
		{	
			int newcount = Util.countPred(_candList, pdata -> !_stateMap.containsKey(pdata.strKey));
			return newcount > 0;
		}
		
		public void addCandidates()
		{
			for(PaperData pdata : _candList)
				{ _stateMap.put(pdata.strKey, pdata); }
		}
		
		public void calcValueForStage()
		{
			List<PaperData> stagelist = Util.filter2list(_stateMap.values(), pdata -> pdata.totalArea() == _stageCount);

			for(PaperData pdata : _stateMap.values())
			{
				if(pdata.totalArea() != _stageCount)
					{ continue; }
				
				if(_stageCount == 1)
				{
					pdata.setExtraValue(0D);	
					continue;	
				}
				
				double expval = 0D;
				double sanity = 0D;
				
				for(Map.Entry<Integer, PaperData> next : pdata.getStepMap().entrySet())
				{
					double prob = pdata.getProb4Step(next.getKey());
					sanity += prob;
					
					PaperData realdata = _stateMap.get(next.getValue().strKey);
					Util.massert(realdata != null, "Step neighbor %s not found", next.getValue().strKey);
					Util.massert(realdata.getValue() > -0.5, "Real Data has bad value");
					
					double stepval = prob * realdata.getValue();
					expval += stepval;
					
					Util.pf("Got stepvalue %.03f=%.03f*%.03f from step %s->%s\n",
						stepval, prob, realdata.getValue(), pdata.strKey, realdata.strKey);
				}
				
				Util.massert(Math.abs(sanity - 1) < .0001);
				pdata.setExtraValue(expval);
			}
		}
		
		public void incrementStageCount()
		{
			_stageCount++;
		}
		
		public boolean atMaxStage()
		{
			return _stageCount > (new PaperData(1, 0, 0, 0, 0)).totalArea();
		}

	}
	
	public static class RunPaperCutter extends ArgMapRunnable
	{
		
		public void runOp()
		{
			Util.pf("Going to run paper cutter\n");
			PaperCutMachine pcmachine = new PaperCutMachine();
			pcmachine.run2Completion();
			
		}
	}	
	
	
}
