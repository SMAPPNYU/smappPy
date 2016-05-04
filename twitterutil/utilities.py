"""
Basic network utilities. Functions on Networkx package.
@auth dpb
@date 2014
"""

import networkx as nx

def directed_star_graph(n):
	"""
	Create and return a directed graph (networkx.DiGraph) with n nodes, where a set of
	n-1 nodes are connected to the left-out nth node. 
	(Like a complte bipartite graph, but directed)
	"""
	dg = nx.empty_graph(n, create_using=nx.DiGraph())
	nodes = dg.nodes_iter()
	hub = nodes.next()
	dg.add_edges_from([ (n, hub) for n in nodes ])
	return dg
	