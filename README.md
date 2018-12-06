# FlowState

This package demonstrates a style of structured state-machine based programming.
In this style, there are two basic types of methods: queries and operations.
A query returns a boolean response variable, while an operation potentially alters the state of the machine.

By using this style in conjunction with this library, programmers can achieve several nice benefits:

1. Automatic extraction of control flow diagrams. 
1. Command line steppable debugging, without the use of an IDE.
1. A general improvement in code clarity, as a result of the required structure. 


This library is mostly written in Java, though there is a Python implementation under development as well.
There are some example programs in the java/flowstate directory.
These have corresponding control flow diagrams in the diagrams directory. 
A diagram will take its name from the class that implements the finite state machine;
this is often an inner class of a Java file. 
For example, the file `HeapSortFlow.java` contains an inner class `HeapSortMachine` that produces `HeapSortMachine.png` in the diagram folder.

To write code using this programming style, follow this procedure:

1. Define a Java `Enum` that implements `StringCodeStateEnum`. 
This enum specifies the states in your machine, and the transitions between the states, see below.
1. Write a class that extends `FiniteStateMachineImpl`. This is the finite state machine. 
It can have any internal data structures you need.
1. Write methods on the FS machine class that corresponds to items in the enum class. 
The naming convention is: the method name is same as the enum name, except the first letter is decapitalized.
1. There are two types of methods: query and operation. 
Query methods must return `boolean`, and not change the state of the machine. 
Operation methods must return `void`, and can change the machine data.
1. The machine superclass constructor for `FiniteStateMachineImpl` takes an Enum argument
	corresponding to the initial state of the machine.
	
	
The state machine transitions are specified with a somewhat terse DSL that applies to the state Enums.
The rules of the DSL are as follows. 
First, every operation state must have a *single* transition, while every query state must have two transitions.
However, the subsequent enum in the listing is considered to be a *default* transition.
So, if you order the state Enums cleverly, you will save a lot of typing by relying on the defaults.
For example, consider this state Enum:


```java
public enum MinTreeCalcState implements StringCodeStateEnum
{
	SetupEdgeList,
	InitComponentMap,
	HaveAnotherMstEdge("F->CC"),
	CalcEdgeContribution,
	UpdateComponentMap, 
	CheckInvariant,
	PollMstEdge("HAME"),
	CalcComplete;
	
	public final String tCode;
	
	MinTreeCalcState() 			{  tCode  = ""; }	
	MinTreeCalcState(String tc) 		{  tCode = tc; }	
	
	public String getTransitionCode()  { return tCode; }		
}
```

Which corresponds to this diagram: 

![MinTreeCalc](/diagram/MinTreeCalcMachine.png)

We need to override the defaults in only two cases. 
First, we need to say that `PollMstEdge` leads back to `HaveAnotherMstEdge`, 
	which is specified using the acronym `HAME`.
Second, we need to specify that the false branch from `HaveAnotherMstEdge`
	leads to `CalcComplete`, with the acronym `CC`.

