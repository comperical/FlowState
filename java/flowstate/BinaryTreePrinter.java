
package net.danburfoot.flowstate; 

import java.util.*;
import java.util.stream.*;
import java.util.stream.Collectors;


import net.danburfoot.shared.Util;
import net.danburfoot.shared.Util.*;
import net.danburfoot.shared.FiniteState.*;

public class BinaryTreePrinter<T extends Comparable<T>>
{
	private SortedMap<T, Integer> _rankMap = Util.treemap();
	
	private SortedMap<T, Integer> _depthMap = Util.treemap();
	
	private SortedMap<T, T> _kid2ParMap = Util.treemap();
	
	private int _maxDepth = 0;

	public void reportDataList(List<T> datalist)
	{
		for(T oneitem : datalist)
			{ _rankMap.put(oneitem, _rankMap.size()); }
		
		// Util.pf("Data list is %s\n", datalist);
	}
	
	public void reportDepth(T oneitem, int depth)
	{
		Util.massert(_rankMap.containsKey(oneitem), "Item %s not present in rankmap", oneitem);
		
		_depthMap.put(oneitem, depth);
		
		_maxDepth = depth > _maxDepth ? depth : _maxDepth;
	}
	
	public void reportLink(T paritem, T kiditem)
	{
		Util.putNoDup(_kid2ParMap, kiditem, paritem);
	}
	
	private int getCharWidth()
	{
		return _rankMap.size() * 4;		
	}
	
	public void print2Screen()
	{
		int charwidth = getCharWidth();
		
		// Util.pf("Rank Map is %s\n", _rankMap);
		// Util.pf("Depth map is %s\n", _depthMap);
		
		for(int d : Util.range(_maxDepth+1))
		{
			char[] charbuf = new char[charwidth];
			Arrays.fill(charbuf, ' ');
			
			List<T> itemlist = itemListAtDepth(d);
			
			for(T oneitem : itemlist)
			{	
				double xrank = _rankMap.get(oneitem);
				xrank /= _rankMap.size();
				xrank *= charwidth;
				int xstart = (int) Math.round(xrank);
				
				String toprint = oneitem.toString();
				// Util.pf("Printing %s at position x=%d, depth=%d\n", toprint, xstart, d);
				
				
				for(int i : Util.range(toprint.length()))
				{
					if(xstart+1 >= charwidth)
						{ continue; }
					
					charbuf[xstart+i] = toprint.charAt(i);
				}
			}
			
			StringBuffer sb = new StringBuffer();
			
			for(char c : charbuf)
				{ sb.append(c); }
			
			Util.pf("%s\n", sb.toString());
			
			printLinkRow(d+1);
		}
	}
	
	private void printLinkRow(int kiddepth)
	{
		int charwidth = getCharWidth();
		
		List<T> itemlist = itemListAtDepth(kiddepth);

		char[] charbuf = new char[charwidth];
		Arrays.fill(charbuf, ' ');			
		
		for(T kiditem : itemlist)
		{
			T paritem = _kid2ParMap.get(kiditem);

			double midrank = _rankMap.get(kiditem) + _rankMap.get(paritem);
			midrank /= 2;
			midrank /= _rankMap.size();
			midrank *= charwidth;
			int midstart = (int) Math.round(midrank);			
		
			String toprint = _rankMap.get(kiditem) < _rankMap.get(paritem) ? "//" : "\\\\";
			
			for(int i : Util.range(toprint.length()))
			{
				if(midstart+1 >= charwidth)
					{ continue; }
				
				charbuf[midstart+i] = toprint.charAt(i);
			}			
		}
		
		StringBuffer sb = new StringBuffer();
		
		for(char c : charbuf)
			{ sb.append(c); }
		
		Util.pf("%s\n", sb.toString());		
		
		
	}
	
	private List<T> itemListAtDepth(int d)
	{
		return _depthMap.entrySet()
				.stream()
				.filter(me -> me.getValue() == d)
				.map(me -> me.getKey())
				.collect(Collectors.toList());
	}
	
}
