
package net.danburfoot.shared; 

import java.util.*;
import java.io.*;

import net.danburfoot.shared.Util.*;
import net.danburfoot.shared.FiniteState.*;

public class DiagramUtil
{

	public static class FsDiagramCreator
	{
		private FiniteStateMachine _theMachine;
		
		private File _outputDir;
		
		private boolean _keepGvOutput;
		
		private FsDiagramCreator() {}
		
		public static FsDiagramCreator build()
		{
			return new FsDiagramCreator();	
		}
		
		public FsDiagramCreator setMachine(FiniteStateMachine fsm)
		{
			_theMachine = fsm;
			return this;
		}
		
		public FsDiagramCreator setOutputDir(File outputdir)
		{
			Util.massert(outputdir.exists() && outputdir.isDirectory(), 
				"Problem with output dir %s", outputdir);
		
			_outputDir = outputdir;
			return this;
		}
		
		public FsDiagramCreator setKeepGvFile(boolean keepgv)
		{
			_keepGvOutput = keepgv;
			return this;
		}		
		
		
		public void runProcess()
		{
			{
				FiniteStateGraphGen fsgg = new FiniteStateGraphGen(_theMachine);
				
				FileUtils.getWriterUtil()
						.setFile(getGvFilePath())
						.writeLineListE(fsgg.getLineList());
			}

			{
				File gvfile = new File(getGvFilePath());
				
				File gvpngfile = createDiagram(gvfile, "dot");
				
				File pngfile = new File(getDiagramPath());
				
				gvpngfile.renameTo(pngfile);
				
				Util.massert(pngfile.exists(), "Failed to move file to webapp dir");				
				
				if(!_keepGvOutput)
					{ gvfile.delete(); }
			}
		}
		
		
		private String getGvFilePath()
		{
			return Util.sprintf("%s/%s.gv", _outputDir.getAbsolutePath(), _theMachine.getClass().getSimpleName());
		}

		private String getDiagramPath()
		{
			return Util.sprintf("%s/%s.png", _outputDir.getAbsolutePath(), _theMachine.getClass().getSimpleName());
		}
	}
	
	
	public static String getCanonicalGvPath(String simplename)
	{
		return Util.sprintf("/userdata/crm/miscdata/gvoutput/%s.gv", simplename);
	}
	
	
	public static String getCanonicalDiagramPath(String simplename)
	{
		return Util.sprintf("/userdata/crm/src/jsp/images/diagram/%s.png", simplename);
	}
	
	public static void generateGvtDiagram(GraphVizTool gvt, String diagname)
	{
		FileUtils.getWriterUtil()
				.setFile(DiagramUtil.getCanonicalGvPath(diagname))
				.writeLineListE(gvt.composeLineList());
		
		DiagramUtil.createDiagramNCopy(diagname);
		
		Util.pf("Built graph %s with %d nodes and %d edges\n",
			diagname, gvt.getNodeCount(), gvt.getEdgeCount());
		
		
	}
	
	public static void createDiagramNCopy(String simplename)
	{
		createDiagramNCopy(simplename, "dot");	
	}
	
	public static void createDiagramNCopy(String simplename, String dotcommand)
	{
		String commline = Util.sprintf("%s -Tpng -O %s", dotcommand, getCanonicalGvPath(simplename));
		
		Util.pf("%s\n", commline);
		
		(new SyscallWrapper(commline)).execE();
		
		File pngoutput = new File(getCanonicalGvPath(simplename) + ".png");
		
		Util.massert(pngoutput.exists(),
			"Output file %s doesn't exist, perhaps GraphViz command failed", pngoutput);
		
		File webapploc = new File(getCanonicalDiagramPath(simplename));
		
		pngoutput.renameTo(webapploc);
		
		Util.massert(webapploc.exists(), "Failed to move file to webapp dir");
		
		Util.pf("Generated PNG file and moved to %s\n", webapploc.getAbsolutePath());		
	}
	
	public static File createDiagram(File inputfile, String dotcommand)
	{
		Util.massert(inputfile.exists(), "Missing input file %s", inputfile);
		
		Util.massert(inputfile.getAbsolutePath().endsWith(".gv"), 
			"Expected input file ending with .gv, found %s", inputfile);
		
		String commline = Util.sprintf("%s -Tpng -O %s", dotcommand, inputfile.getAbsolutePath());
		
		Util.pf("%s\n", commline);
		
		(new SyscallWrapper(commline)).execE();
		
		File pngoutput = new File(inputfile.getAbsolutePath() + ".png");
		
		Util.massert(pngoutput.exists(),
			"Output file %s doesn't exist, perhaps GraphViz command failed", pngoutput);
		
		return pngoutput;
	}	
	
	public enum GraphVizProp
	{
		graphname,
		graphlabel,
		defnodeshape,
		fontsize;
	}
	
	public enum GvNodeShape
	{
		box,
		diamond,
		ellipse;
	}	
	
	
	public static class GraphVizTool 
	{
		private Set<String> _nodeSet = Util.treeset();
		
		private	Set<Pair<String, String>> _edgeSet = Util.treeset();
		
		// Info about node types, no entry for default shape.
		private Map<String, String> _nodeTypeMap = Util.treemap();
		
		private Map<Pair<String, String>, String> _edgeLabelMap = Util.treemap();
		
		private Map<GraphVizProp, String> _propMap = Util.treemap();
		// private Map<
		
		public GraphVizTool()
		{
			_propMap.put(GraphVizProp.graphname, "MyGraphName");			
			_propMap.put(GraphVizProp.graphlabel, "MyGraphLabel");
			_propMap.put(GraphVizProp.defnodeshape, GvNodeShape.box.toString());
			_propMap.put(GraphVizProp.fontsize, "12");
		}
			
		public GraphVizTool setProperty(GraphVizProp gvp, String val)
		{
			_propMap.put(gvp, val);	
			return this;
		}
		
		public void addNode(String nodecode)
		{
			Util.putNoDup(_nodeSet, nodecode);	
		}
		
		public void setNodeShape(String nodecode, GvNodeShape gvshape)
		{
			Util.massert(_nodeSet.contains(nodecode));
			_nodeTypeMap.put(nodecode, gvshape.toString());
		}
		
		public void addEdge(String src, String dst)
		{
			Util.massert(_nodeSet.contains(src) && _nodeSet.contains(dst),
				"Missing either src node %s or dst node %s in nodeset %s", src, dst, _nodeSet);
			
			Util.putNoDup(_edgeSet, Pair.build(src, dst));
			
		}
		
		public void removeNoEdgeNode()
		{
			Set<String> remset = _nodeSet
						.stream()
						.filter(node -> getOutEdgeCount(node)+getInEdgeCount(node) == 0)
						.collect(CollUtil.toSet());
			
			_nodeSet.removeAll(remset);
			_nodeTypeMap.keySet().removeAll(remset);
		}
		
		public long getOutEdgeCount(String node)
		{
			return _edgeSet
					.stream()
					.filter(edge -> edge._1.equals(node))
					.collect(CollUtil.counting());
			
		}
		
		public long getInEdgeCount(String node)
		{
			return _edgeSet
					.stream()
					.filter(edge -> edge._2.equals(node))
					.collect(CollUtil.counting());
		}

		
		
		
		public int getEdgeCount()
		{
			return _edgeSet.size();	
		}
		
		public int getNodeCount()
		{
			return _nodeSet.size();	
		}
		
		public void addEdgeWithLabel(Pair<String, String> edgekey, String label)
		{
			addEdge(edgekey._1, edgekey._2);
			addEdgeLabel(edgekey, label);
		}		
		

		public void addEdgeLabel(Pair<String, String> edgekey, String label)
		{
			Util.massert(_edgeSet.contains(edgekey));
			
			Util.putNoDup(_edgeLabelMap, edgekey, label); 
		}	
		
		
		public List<String> composeLineList()
		{
			List<String> gvlist = Util.vector();
			
			gvlist.add(Util.sprintf("digraph %s { ", _propMap.get(GraphVizProp.graphname)));
			
			popNodeInfo(gvlist);
			popLinkInfo(gvlist);
			
			gvlist.add("overlap=false");
			
			gvlist.add(Util.sprintf("label=\"%s\"", _propMap.get(GraphVizProp.graphlabel)));
			
			// This will do an error if fontsize is not an integer, but better here than in GViz.
			gvlist.add(Util.sprintf("fontsize=%d", Integer.valueOf(_propMap.get(GraphVizProp.fontsize))));
			gvlist.add("}");			
			
			return gvlist;
		}
		
		
		private void popNodeInfo(List<String> gvlist)
		{
			Util.listify(GvNodeShape.values())
				.stream()
				.map(gvn -> getRecord4Shape(gvn))
				.forEach(rec -> gvlist.add(rec));	
		}
		
		private String getRecord4Shape(GvNodeShape gvshape)
		{
			String nodeliststr = Util.join(getNodeWithShape(gvshape), "; ");
			return Util.sprintf("node [shape=%s] %s", gvshape, nodeliststr);
		}
		
		private List<String> getNodeWithShape(GvNodeShape targshape)
		{
			return _nodeSet
					.stream()
					.filter(node -> getNodeShape(node).equals(targshape.toString()))
					.collect(CollUtil.toList());
		}
		
		private String getNodeShape(String node)
		{
			return Util.ifANullThenB(_nodeTypeMap.get(node), _propMap.get(GraphVizProp.defnodeshape));
		}
		
		private void popLinkInfo(List<String> gvlist)
		{
			_edgeSet
				.stream()
				.map(edge -> getSingleEdgeRec(edge._1, edge._2))
				.forEach(rec -> gvlist.add(rec));
		}			
		
		private String getSingleEdgeRec(String src, String dst)
		{
			String label = _edgeLabelMap.get(Pair.build(src, dst));
			label = (label == null ? "" : label);
			return Util.sprintf("%s->%s [label=\"%s\"];", src, dst, label);
		}
	}

	
	
	



}
