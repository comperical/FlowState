
package net.danburfoot.shared; 

import java.text.*; 
import java.util.*;

import java.util.stream.*;
import java.util.stream.Collectors;

import java.util.function.*;


public class CollUtil
{
	public static <T> Collector<T,?,List<T>> toList()
	{
		return Collectors.toList();	
	}
	
	public static <T> Collector<T,?,Set<T>> toSet()
	{
		return Collectors.toSet();	
	}	
	
	public static <T> Collector<T,?,T> reducing(T identity, BinaryOperator<T> op)	
	{
		return Collectors.reducing(identity, op);	
	}
	
	public static <T> Collector<T,?,Long>	counting()
	{
		return Collectors.counting();	
	}
	
	public static <T,K> Collector<T,?,Map<K,List<T>>> groupingBy(Function<? super T, ? extends K> classifier)
	{
		return Collectors.groupingBy(classifier);	
	}
	
	public static <T,K,A,D> Collector<T,?,Map<K,D>> groupingBy(Function<? super T,? extends K> classifier, Collector<? super T,A,D> downstream)
	{
		return Collectors.groupingBy(classifier, downstream);
	}
	
	public static Collector<CharSequence,?,String>	joining()
	{
		return Collectors.joining();	
	}

	public static Collector<CharSequence,?,String>	joining(CharSequence delimiter)
	{
		return Collectors.joining(delimiter);	
	}
	
	
	public static <T> Collector<T,?,Integer> summingInt(ToIntFunction<? super T> mapper)
	{
		return Collectors.summingInt(mapper);
	}

	public static <T> Collector<T,?,Long> summingLong(ToLongFunction<? super T> mapper)
	{
		return Collectors.summingLong(mapper);
	}	
	
	
	public static <T> Collector<T,?,Double> summingDouble(ToDoubleFunction<? super T> mapper)
	{
		return Collectors.summingDouble(mapper);
	}	
	
	public static <T,K,U> Collector<T,?,Map<K,U>>	toMap(Function<? super T,? extends K> keyMapper, Function<? super T,? extends U> valueMapper)
	{
		return Collectors.toMap(keyMapper, valueMapper);	
	}
	
	
	// Orders list so that elements that maximize the function are at the top.
	public static <T> void sortListDescending(List<T> sortme, ToIntFunction<? super T> maxfunc)
	{
		Collections.sort(sortme, (x1, x2) -> maxfunc.applyAsInt(x1) - maxfunc.applyAsInt(x2));	
	}
	
	
	
	// Orders list so that elements that maximize the function are at the top.
	public static <T, K extends Comparable<K>> void sortListByFunction(List<T> sortme, Function<T, K> sortfunc)
	{
		Collections.sort(sortme, (x1, x2) -> sortfunc.apply(x1).compareTo(sortfunc.apply(x2)));	
	}	
	
	// Dedup the collection by the specified function.
	// Preserves original order of collection
	public static <T, K extends Comparable<K>> List<T> distinctByFunction(Collection<T> dedupme, Function<T, K> dupfunc)
	{
		Set<K> prevset = Util.treeset();
		List<T> deduplist = Util.vector();		
		
		for(T item : dedupme)
		{
			K fres = dupfunc.apply(item);
			
			if(prevset.contains(fres))
				{ continue; }
			
			deduplist.add(item);
			prevset.add(fres);
		}
		
		return deduplist;
	}	
		
	
	
	// Orders list so that elements that maximize the function are at the top.
	public static <T> void inPlaceListFilter(List<T> filterme, Predicate<T> acceptfunc)
	{
		List<T> gimplist = filterme
					.stream()
					.filter(t -> acceptfunc.test(t))
					.collect(CollUtil.toList());
					
		filterme.clear();
		filterme.addAll(gimplist);
	}	
	
	// Orders list so that elements that maximize the function are at the top.
	public static <T,R> void inPlaceMapFilter(Map<T, R> filterme, Predicate<T> acceptfunc)
	{
		List<T> filterlist = new ArrayList<T>(filterme.keySet());
		
		for(T onekey  : filterlist)
		{
			if(!acceptfunc.test(onekey))
				{ filterme.remove(onekey); }	
		}
	}	

	// Orders list so that elements that maximize the function are at the top.
	public static <T> void truncateList2Size(List<T> dalist, int maxsize)
	{
		List<T> gimplist = Util.vector();
		
		for(T item : dalist)
		{
			gimplist.add(item);
			
			if(gimplist.size() >= maxsize)
				{ break; }
		}
		
		dalist.clear();
		
		dalist.addAll(gimplist);
		
	}	
	
	
	public static List<List<Integer>> allPermList(int base)
	{
		Util.massert(base <= 8,
			"This method produces a number of lists that is exponential in base argument");
		
		List<List<Integer>> permlist =  buildPermListRec(base);
		
		int listsize = factorial(base+1);

		Util.massertEqual(permlist.size(), listsize,
			"Got %d but expected listsize %d");
		
		return permlist;
	}

	private static List<List<Integer>> buildPermListRec(int nextnum)
	{
		if(nextnum == 0)
		{
			return Util.listify(Util.listify(0));
		}

		List<List<Integer>> bigsublist = buildPermListRec(nextnum-1);
		List<List<Integer>> bigreslist = Util.vector();
		
		for(int inpos = nextnum; inpos >= 0; inpos--)
		{
			for(List<Integer> sublist : bigsublist)
			{
				List<Integer> newlist = Util.vector();
				
				newlist.addAll(sublist);
				
				if(inpos < sublist.size())
					{ newlist.add(inpos, nextnum); }
				else
					{ newlist.add(nextnum); }
				
				bigreslist.add(newlist);
			}
		}
				
		return bigreslist;
	}
	
	// This is a dumb utility method for allPermList(...) method above.
	private static int factorial(int n)
	{
		if(n <= 1)
			{ return 1; }
		
		return n * factorial(n-1);
	}
	
	public static class ToStringComparator<T> implements Comparator<T>
	{
		public int compare(T a, T b)
		{
			return a.toString().compareTo(b.toString());
		}
		
		public boolean equals(T a, T b)
		{
			return a.toString().equals(b.toString());	
		}
	}
	
	
	public static  class IndexMap<T extends Comparable<T>>
	{
		private List<T> _directOrder = Util.vector();
		
		private Map<T, Integer> _indexMap = Util.treemap();
		
		public int addIfAbsent(T item)
		{
			Integer prevpos = _indexMap.get(item);
			
			if(prevpos != null)
				{ return prevpos; }
			
			return addItem(item);
		}
		
		public int addItem(T item)
		{
			Util.massert(!_indexMap.containsKey(item),
				"Already added item %s to the index", item);
			
			int pos = _directOrder.size();
			_indexMap.put(item, pos);
			_directOrder.add(item);
			return pos;
		}
		
		public boolean haveItem(T item)
		{
			return _indexMap.containsKey(item);
		}
		
		public T getItemAt(int i)
		{
			return _directOrder.get(i);	
		}
		
		public int getPos4Item(T item)
		{
			return _indexMap.get(item);	
		}
		
		public int size()
		{
			return _directOrder.size();	
		}
		
		public Set<T> getItemSet()
		{
			return Collections.unmodifiableSet(_indexMap.keySet());	
		}
	}
} 
