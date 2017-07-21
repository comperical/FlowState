
package net.danburfoot.shared;

import java.io.*;
import java.util.*;

public class Pair<A, B> implements Serializable, Comparable<Pair<A, B>>
{

	public A _1;
	public B _2;

	public Pair(A a, B b)
	{
		_1 = a;
		_2 = b;
	}
	
	public int compareTo(Pair<A, B> that)
	{
		Comparable<A> ca = Util.cast(_1);
		
		int f = ca.compareTo(that._1);
		
		if(f != 0 || !(_2 instanceof Comparable))
			return f;

		Comparable<B> cb = Util.cast(_2);
		return cb.compareTo(that._2);
	}	
	
	
	public Pair<B, A> reversePair()
	{
		return Pair.build(_2, _1);
	}
	
	
	/*
	public int compareTo(Object t)
	{
		Pair<A, B> that = Util.cast(t);
		
		Comparable<A> ca = Util.cast(_1);
		
		int f = ca.compareTo(that._1);
		
		if(f != 0 || !(_2 instanceof Comparable))
			return f;

		Comparable<B> cb = Util.cast(_2);
		return cb.compareTo(that._2);
	}
	*/
	
	public boolean equals(Object t)
	{
		Pair<A, B> that = Util.cast(t);
		return _1.equals(that._1) && _2.equals(that._2);
	}
	
	public String toString()
	{
		return Util.sprintf("[%s, %s]", _1, _2);
	}
	
	public static <A, B> Pair<A, B> build(A a, B b)
	{
		return new Pair<A, B>(a, b);
	}
	
	public static <A, B> Pair<A, B> build(Map.Entry<A, B> mapent)
	{
		return new Pair<A, B>(mapent.getKey(), mapent.getValue());
	}
	
	public static <A, B> List<A> getOneList(Collection<Pair<A, B>> paircol)
	{
		List<A> flist = Util.vector();
		
		for(Pair<A, B> onepair : paircol)
			{ flist.add(onepair._1); }
		
		return flist;
	}
	
	public static <A, B> List<B> getTwoList(Collection<Pair<A, B>> paircol)
	{
		List<B> flist = Util.vector();
		
		for(Pair<A, B> onepair : paircol)
			{ flist.add(onepair._2); }
		
		return flist;
	}	
	
}
