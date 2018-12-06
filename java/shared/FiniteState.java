
package net.danburfoot.shared; 

// IMPORTS {{{
import java.util.*; 
import java.io.*; 

import java.lang.reflect.*;

import net.danburfoot.shared.Util.*;
import net.danburfoot.shared.DiagramUtil.*;
// }}}


public class FiniteState
{ 
	// Final is Java keyword
	public enum StateType { querystate, endstate, opstate };
	
	// This is included here to avoid dependence on StringUtil
	public static String getAcroForm(String fullstr)
	{
		StringBuilder sb = new StringBuilder();	
		
		for(int i : Util.range(fullstr.length()))
		{
			char c = fullstr.charAt(i);
			
			if(Character.isUpperCase(c))
				{ sb.append(c); }
		}
		
		return sb.toString();
	}
	
	public interface FiniteStateEnum
	{
		// {{{
		public List<? extends Enum> getTransitionList();
		
		public default StateType getStateType()
		{
			int numtrans = getTransitionList().size();
			
			switch(numtrans)
			{
				case 0: return StateType.endstate;
				case 1: return StateType.opstate;
				case 2: return StateType.querystate;
				
				default: throw new RuntimeException("Too many transitions: " + numtrans);
			}
			
		}
		// }}}
	}
	
	public interface FiniteStateEnumSimple extends FiniteStateEnum
	{
		// {{{
		public Object getBasicTransition();
		
		public default List<? extends Enum> getTransitionList()
		{
			List<Enum> tlist = Util.vector();
			
			Object bt = getBasicTransition();
			
			if(bt == null)
			{
				; 	
			} else if(bt instanceof Enum) {
				tlist.add((Enum) bt);
			} else if(bt instanceof List) {
				for(Object en : ((List) bt))
					{ tlist.add((Enum) en); }
			} else {
				
				Util.massert(false, 
					"Return type of getBasicTransition must be null, single enum, or List of enums, found %s", bt);	
			}
				
			
			return tlist;
		}
		
		public default Object getDefaultTransition()
		{
			Enum curenum = (Enum) this;
			
			Object[] peerenum = curenum.getClass().getEnumConstants();
			
			// In this case, the argument is the LAST enum of the list
			if(curenum.ordinal() == peerenum.length-1)
				{ return null; }
			
			// Return the direct successor to the argument enum.
			return peerenum[curenum.ordinal()+1];
		}
		
		
		public default Object defaultPlus(boolean istrue, Enum otherenum)
		{
			List<Object> mylist = Util.vector();

			mylist.add(otherenum);
			mylist.add(getDefaultTransition());
			
			if(!istrue)
				{ Collections.reverse(mylist); }
			
			return mylist;
		}		
		// }}}
	}	
	
	public interface StringCodeStateEnum extends FiniteStateEnum
	{
		// {{{
		public String getTransitionCode();
		
		// Can take this out, just want to keep it around for a little while longer
		public default List<? extends Enum> getTransitionList()
		{
			List<? extends Enum> tlist = getTransitionListSub();
			
			// Util.pf("Got transition list %s for %s\n", tlist, this);
			
			return tlist;
		}
		
		public default List<? extends Enum> getTransitionListSub()
		{
			String tcode = getTransitionCode().trim();
			
			Enum def = getDefaultTransition();
			
			// 0 is code for completion state.
			// Also if the transition code isEmpty, and the default is null, return []
			if(tcode.equals("0") || (tcode.isEmpty() && def == null)) 
				{ return Collections.emptyList(); }			
			
			// Empty string, just return default transition 
			if(tcode.isEmpty())
				{ return Util.listify(def); }

			Map<String, Enum> codemap = getCode2EnumMap(this.getClass());
			
			// Util.pf("CodeMap is %s\n", codemap);
			
			// This is an explicit specification of a single transition, override the default.
			// if(tcode.equals(tcode.toUpperCase()))
			if(!tcode.contains("->"))
			{
 				Util.massert(codemap.containsKey(tcode),
 					"No state enum corresponding to code %s found for origin state %s", tcode, this);
				
 				return Util.listify(codemap.get(tcode));
			}
			
			String[] commatok = tcode.split(",");
			
			Util.massert(commatok.length <= 2,
				"Can only specify one or two transitions, found %d for code %s", commatok.length, tcode);
			
			// Here we specify one branch of the transition explicitly, and use the default for the other one.
			if(commatok.length == 1)
			{
				Pair<Boolean, Enum> ptc = parseBranchCode(codemap, tcode);	
				
				List<Enum> tlist = Util.vector();
				
				tlist.add(ptc._2);
				tlist.add(def);

				if(!ptc._1)
					{ Collections.reverse(tlist); }
				
				return tlist;
			}
			
			// Okay, here we are specifying two different branches explicitly, ignore the default.
			if(commatok.length == 2)
			{
				Map<Boolean, Enum> resmap = Util.treemap();
				
				for(String onetok : commatok)
				{
					Pair<Boolean, Enum> ptc = parseBranchCode(codemap, onetok);
					resmap.put(ptc._1, ptc._2);
				}
				
				Util.massert(resmap.size() == 2, 
					"Found resmap %s, must specify two different T/F values, tcode=%s", tcode);
				
				
				List<Enum> tlist = Util.vector(resmap.values());
				
				Collections.reverse(tlist);
				
				return tlist;
			}
			
			throw new RuntimeException("Should never occur");
		}
		
		public default Enum getDefaultTransition()
		{
			Enum curenum = (Enum) this;
			
			Object[] peerenum = curenum.getClass().getEnumConstants();
			
			// In this case, the argument is the LAST enum of the list
			if(curenum.ordinal() == peerenum.length-1)
				{ return null; }
			
			// Return the direct successor to the argument enum.
			return (Enum) peerenum[curenum.ordinal()+1];
		}
		// }}}
	}		
	
	public static Pair<Boolean, Enum> parseBranchCode(Map<String, Enum> codemap, String tcode)
	{
		// {{{
		Util.massert(tcode.indexOf("->") > -1,
			"Branch code must have arrow (->) symbol, found %s", tcode);
		
		String[] tf_code = tcode.split("->");

		Util.massert(Util.setify("T", "F").contains(tf_code[0].trim()),
			"First token of branch code should be T/F, found %s", tf_code[0]);
		
		Boolean branch = tf_code[0].trim().equals("T");
		
		Enum result = codemap.get(tf_code[1].trim());
		
		Util.massert(result != null,
				"Could not find branch code %s in codemap", tf_code[1]);
		
		return Pair.build(branch, result);
		
		// }}}
	}
	
	public static Map<String, Enum> getCode2EnumMap(Class enumclass)
	{
		// {{{
		List<Object> oblist = Util.listify(enumclass.getEnumConstants());
	
		return Util.map2map(oblist, ob -> getAcroForm(ob.toString()), ob -> (Enum) ob);
		// }}}
	}
	
	public interface FiniteStateMachine 
	{
		// {{{
		abstract Map<Enum, List<? extends Enum>> getStateTransMap();
		
		abstract Map<Enum, Method> getQrStateMap();
		abstract Map<Enum, Method> getOpStateMap();
		abstract Set<Enum> getEndStateSet();
		
		public abstract void setState(Enum methname);
		public abstract Enum getState(); 
		
		public default Set<Enum> getStateSet()
		{
			return getStateTransMap().keySet();	
		}
		
		public default void requireState(Enum reqstate)
		{
			Util.massert(reqstate == getState(),
				"Required to be in state %s, but machine is now in state %s",  reqstate, getState());
		}
		
		public default void doStateOp()
		{
			Enum statename = getState();
			
			Method statemeth = getOpStateMap().get(statename);			
			Util.massert(statemeth != null,
				"Attempt to do operation in non-op state %s", statename);
			
			try { statemeth.invoke(this); }
			catch (Exception ex) { throw new RuntimeException(ex); }			
		}
		
		public default StateType getTypeOfState(Enum statename) 
		{
			if(getOpStateMap().containsKey(statename))
				{ return StateType.opstate; }
			
			if(getQrStateMap().containsKey(statename))
				{ return StateType.querystate; }
			
			if(getEndStateSet().contains(statename))
				{ return StateType.endstate; }
			
			Util.massert(false, "Could not find state method for %s", statename);
			return null;
		}		
		
		public default void logStep(Enum astate, Enum bstate) {}
		
		public default int getStepCount()
		{
			return -1;	
		}
		
		public default boolean getStateQueryResult()
		{
			Enum statename = getState();
			
			Method statemeth = getQrStateMap().get(statename);
			Util.massert(statemeth != null,
				"Attempt to do operation in non-op state %s", statename);
			
			try {
				Boolean qval = (Boolean) statemeth.invoke(this);
				return qval;
			} catch (Exception ex) { 
				throw new RuntimeException(ex);
			}
		}
		
		public default String stateName2MethName(String onestate)
		{
			// Decapitalized naming convention
			String methname = onestate.toString();
			return methname.substring(0, 1).toLowerCase() + methname.substring(1);
		}
		
		public default String meth2StateName(Method onemeth)
		{
			String methname = onemeth.getName();
			return methname.substring(0, 1).toUpperCase() + methname.substring(1);
		}
		
		public default Method getMethodFromName(String onestate)
		{
			String methname = stateName2MethName(onestate);
			Method statemeth = null;
			
			try { statemeth = getClass().getDeclaredMethod(methname); }
			catch (Exception ex) { ; }
			
			if(statemeth == null)
			{
				try { statemeth = getClass().getMethod(methname); }
				catch (Exception ex) { ; }
			}			
			
			return statemeth;
		}
		
		public default void run2State(Enum targstate)
		{
			while(getState() != targstate)
			{
				runOneStep();	
			}			
		}
		
		public default void run2Completion()
		{
			while(true)
			{
				// Util.pf("CurState is %s\n", getState());
				
				StateType curstatetype = getTypeOfState(getState());
				
				if(curstatetype == StateType.endstate)
					{ break; }

				runOneStep();				
			}
		}
		
		public default void runOneStep()
		{
			boolean qres = true;
			
			if(getTypeOfState(getState()) == StateType.querystate)
			{
				qres = getStateQueryResult();
			}
			
			runOneStep(qres);
		}	
		
		public default boolean isComplete()
		{
			return getTypeOfState(getState()) == StateType.endstate;	
		}
		
		// This method enables you to run the FSM without using its internal stateQuery mechanism,
		// say from a state transition log.
		public default void runOneStep(boolean qres)
		{
			Enum curstate = getState();
			StateType curstatetype = getTypeOfState(curstate);

			// Util.incHitMap(_visitMap, curstate.

			if(curstatetype == StateType.endstate)
				{ return; }

			Enum nextstate = null;

			if(curstatetype == StateType.querystate)
			{
				nextstate = getQueryNextState(curstate, qres);
			} else {

				doStateOp();
				nextstate = getOpNextState(curstate);
			}
			
			logStep(curstate, nextstate);

			setState(nextstate);
		}			
		
		public default void run2StepCount(int targstep)
		{
			while(true)
			{
				int sc = getStepCount();
				
				Util.massert(sc != -1, "This FSM interface does not provide step count feature");
				
				if(sc == targstep)
					{ break; }
				
				runOneStep();
			}
		}
		
		default void runPastState(Enum afterstate)
		{
			while(true)
			{
				Enum prvstate = getState();
				
				runOneStep();
				
				if(prvstate == afterstate)
					{ break; }
				
				Util.massert(getTypeOfState(getState()) != StateType.endstate,
					"Encountered endstate %s but wanted to run to %s",
					getState(), afterstate);
			}			
		}
		
		default Enum getQueryNextState(Enum curstate, boolean qres)
		{
			return getStateTransMap().get(curstate).get(qres ? 0 : 1);
		}
		
		default Enum getOpNextState(Enum curstate)
		{
			return getStateTransMap().get(curstate).get(0);
		}
		
		default List<String> getDiagnosticInfo()
		{
			return Util.listify("No diagnostic info available, override getDiagnosticInfo()");	
		}
		
		default void commLineResult(String argline)
		{
			Util.massert(false, "Must override commLineResult(..) method for this to work");	
		}
		
		// }}}
	}
	
	public static abstract class FiniteStateMachineImpl implements FiniteStateMachine
	{
		// {{{
		protected Map<Enum, List<? extends Enum>> _stateTransMap = Util.treemap();
		
		private Map<Enum, Method> _qrStateMap;
		private Map<Enum, Method> _opStateMap;
		private Set<Enum> _endStateSet;
		
		private Enum _curState;
		
		private int _stepCount = 0;
		
		protected FiniteStateMachineImpl(Enum initstate)
		{
			_curState = initstate;
			
			popStateTransMap();
			
			maybeInitState2MethMap();
		}
		
		public void setState(Enum methname) 
		{
			_curState = methname;	
		}
		
		public Enum getState()
		{
			return _curState; 	
		}
		
		public Map<Enum, Method> getOpStateMap()
		{
			return Collections.unmodifiableMap(_opStateMap);			
		}
		
		public Map<Enum, Method> getQrStateMap()
		{
			return Collections.unmodifiableMap(_qrStateMap);	
		}		
		
		public Set<Enum> getEndStateSet()
		{
			return _endStateSet;	
		}
		
		@Override
		public void logStep(Enum astate, Enum bstate)
		{
			_stepCount++;	
		}
		
		@Override
		public int getStepCount()
		{
			return _stepCount;
		}
		
		// Subclasses override to change state transition behavior
		protected void popStateTransMap()
		{
			List<Enum> slist = Util.vector();
			{
				Class enumclass = _curState.getClass();
				
				for(Object o : enumclass.getEnumConstants())
					{ slist.add((Enum) o); }				
			}
			
			for(Enum onestate : slist)
			{			
				FiniteStateEnum fstate = (FiniteStateEnum) onestate; 
				_stateTransMap.put(onestate, fstate.getTransitionList());
			}
		}
		
		public Map<Enum, List<? extends Enum>> getStateTransMap()
		{
			return 	Collections.unmodifiableMap(_stateTransMap);
		}
		
		
		private synchronized void maybeInitState2MethMap()
		{
			if(_opStateMap != null)
				{ return; }
			
			_opStateMap = Util.treemap();
			_qrStateMap = Util.treemap();
			_endStateSet = Util.treeset();
						
			for(Enum onestate : _stateTransMap.keySet())
			{
				Method statemeth = getMethodFromName(onestate.toString());
				
				int trancount = _stateTransMap.get(onestate).size();
				
				if(trancount == 0)
				{
					Util.massert(onestate.toString().endsWith("Complete") || 
						onestate.toString().endsWith("End"),
						"No state method found for %s,  end state names must end with -End or -Complete", onestate);
					
					Util.massert(statemeth == null,
						"Found expected method for EndState %s", onestate);
					
					_endStateSet.add(onestate);
					continue;
				}
				
				Util.massert(statemeth != null, 
					"Could not find method named %s for state name %s",
					stateName2MethName(onestate.toString()), onestate);
				
				Class returnclass = statemeth.getReturnType();
				
				if(trancount == 1)
				{
					Util.massert(returnclass.toString().equals("void"),
						"Found non-void return class %s for state method %s, op states must return void",
						returnclass, onestate);
					
					_opStateMap.put(onestate, statemeth); 
					continue;					
				}
				
				if(trancount == 2)
				{
					Util.massert(returnclass.toString().equals("boolean"),
						"Found non-boolean return type %s for query state %s", 
						returnclass, onestate);
					
					_qrStateMap.put(onestate, statemeth);					
				}				
			}
		}	
		// }}}
	}
	
	public static class CommLineFsmRunner
	{
		// {{{
		
		public final FiniteStateMachine theMachine;
		
		public CommLineFsmRunner(FiniteStateMachine fsm)
		{
			theMachine = fsm;
		}
		
		public void runFromCommLine()
		{
			Scanner sc = new Scanner(System.in);
			
			while(true)
			{	
				Util.pf("Current state is %s, step count is %d\n",
						theMachine.getState(), theMachine.getStepCount());
				
				for(String onerec : theMachine.getDiagnosticInfo())
				{
					Util.pf("\t%s\n", onerec);
				}
				
				Util.pf("Command [(S)tep, # for stepcount, (Q)uit, +(...)] : ");
				
				String resp = sc.nextLine().trim().toLowerCase();
				
				if(resp.startsWith("+"))
				{
					theMachine.commLineResult(resp.substring(1));	
					continue;
				}
				
				if(resp.equals("s"))
				{
					theMachine.runOneStep();	
					continue;
				}
				
				if(resp.equals("q"))
					{ break; }	
				
				try {
					int stepcount = Integer.valueOf(resp);
					theMachine.run2StepCount(stepcount);
					continue;
					
				} catch (NumberFormatException nfex) {
					
					// 
				}
				
				Util.pf("Invalid command __%s__ try again\n", resp);
			}
		}
		// }}}
	}
	
	public static class FiniteStateGraphGen
	{
		// {{{
		FiniteStateMachine _myMachine;

		TreeMap<String, String> _queryMap = Util.treemap();
		TreeMap<String, String> _opMap = Util.treemap();

		private List<String> _graphVizLine;

		public FiniteStateGraphGen(FiniteStateMachine mymachine)
		{
			_myMachine = mymachine;
		}

		private static GvNodeShape getGviz4Type(StateType stype)
		{

			if(stype == StateType.endstate)
				{ return GvNodeShape.diamond; }

			if(stype == StateType.querystate)
				{ return GvNodeShape.ellipse; }

			return GvNodeShape.box;
		}

		private void popNodeInfo(GraphVizTool gvt)
		{
			for(Enum onestate : _myMachine.getStateSet())
			{
				StateType onetype = _myMachine.getTypeOfState(onestate);
				
				// Would like to add a Question mark here, but need to change name of nodes.
				// String nodelabel = onestate.toString() + (onetype == StateType.querystate ? "?" : "");
				gvt.addNode(onestate.toString());
				gvt.setNodeShape(onestate.toString(), getGviz4Type(onetype));
			}			
		}

		private void popLinkInfo(GraphVizTool gvt)
		{
			for(Enum onestate : _myMachine.getStateSet())
			{
				StateType stype = _myMachine.getTypeOfState(onestate);

				if(stype == StateType.endstate)
					{continue; }

				if(stype == StateType.querystate)
				{
					for(boolean qres : Util.listify(true, false))
					{
						Enum nextstate = _myMachine.getQueryNextState(onestate, qres);
						gvt.addEdgeWithLabel(Pair.build(onestate.toString(), nextstate.toString()), (qres ? "T" : "F"));
					}

				} else {
					Enum nextstate = _myMachine.getOpNextState(onestate);
					gvt.addEdge(onestate.toString(), nextstate.toString());
				}
			}			
		}
		

		public List<String> getLineList()
		{
			GraphVizTool gtool = new GraphVizTool();
			
			gtool.setProperty(GraphVizProp.graphname, "FiniteStateMachine");
			gtool.setProperty(GraphVizProp.graphlabel,
				Util.sprintf("AutoGen for StateMachine %s", _myMachine.getClass().getSimpleName()));
			
			popNodeInfo(gtool);
			popLinkInfo(gtool);
			return gtool.composeLineList();
		}



		// }}}
	}	
} 
