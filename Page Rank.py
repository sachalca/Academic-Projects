"""
COMP 614
Homework 6: DFS + PageRank
"""

import comp614_module6

def bfs_dfs(graph, start_node, rac_class):
    """
    Performs a breadth-first search on graph starting at the given node.
    Returns a two-element tuple containing a dictionary mapping each visited
    node to its distance from the start node and a dictionary mapping each
    visited node to its parent node.
    """

    is_queue = True
    if rac_class is comp614_module6.Stack:
        is_queue = False
    if is_queue and rac_class is not comp614_module6.Queue:
        print('Wrong rac_class input')
        return None

    # Initialize all data structures
    if is_queue:
        structure = comp614_module6.Queue()
    else:
        structure = comp614_module6.Stack()

    dist = {}
    parent = {}

    # Initialize distances and parents; no nodes have been visited yet
    for node in graph.nodes():
        dist[node] = float("inf")
        parent[node] = None

    # Initialize start node's distance to 0
    dist[start_node] = 0
    structure.push(start_node)

    # Continue as long as there are new reachable nodes
    while structure:
        node = structure.pop()
        nbrs = graph.get_neighbors(node)

        for nbr in nbrs:
            # Only update neighbors that have not been seen before
            if dist[nbr] == float('inf'):
                dist[nbr] = dist[node] + 1
                parent[nbr] = node
                structure.push(nbr)

    return parent

def recursive_dfs(graph, start_node, parent):
    """
    Given a graph, a start node from which to search, and a mapping of nodes to
    their parents, performs a recursive depth-first search on graph from the 
    given start node, populating the parents mapping as it goes.
    """
    nbrs = graph.get_neighbors(start_node)
    flag = True

    for nbr in nbrs:
        if nbr not in parent:
            flag = False
    if flag:
        return None

    for nbr in nbrs:
        if nbr not in parent:
            parent[nbr] = start_node
            recursive_dfs(graph, nbr, parent)

    return None

def get_inbound_nbrs(graph):
    """
    Given a directed graph, returns a mapping of each node n in the graph to
    the set of nodes that have edges into n.
    """
    mapping = {}
    for node in graph.nodes():
        if node not in mapping:
            mapping[node] = set()
        for nbr in graph.get_neighbors(node):
            if nbr not in mapping:
                mapping[nbr] = set()
            mapping[nbr].add(node)
    return mapping

def remove_sink_nodes(graph):
    """
    Given a directed graph, returns a new copy of the graph where every node that
    was a sink node in the original graph now has an outbound edge linking it to 
    every other node in the graph (excluding itself).
    """
    copy = graph.copy()

    for node in copy.nodes():
        if len(copy.get_neighbors(node)) == 0:
            for outbound in copy.nodes():
                if outbound == node:
                    continue
                copy.add_edge(node, outbound)

    return copy

def page_rank(graph, damping):
    """
    Given a directed graph and a damping factor, implements the PageRank algorithm
    -- continuing until delta is less than 10^-8 -- and returns a dictionary that
    maps each node in the graph to its page rank.
    """

    old_page_rank = {}
    new_page_rank = {}
    inbound = get_inbound_nbrs(remove_sink_nodes(graph))
    node_count = len(graph.nodes())
    prefix = ((1 - damping) / node_count)

    for node in graph.nodes():
        old_page_rank[node] = 1 / node_count

    while True:

        for node in graph.nodes():

            suffix = 0
            for value in inbound[node]:
                old = old_page_rank[value]
                if len(graph.get_neighbors(value)) == 0:
                    leng = len(graph.nodes()) - 1
                else:
                    leng = len(graph.get_neighbors(value))

                suffix += old / leng
            new_page_rank[node] = prefix + (damping * suffix)

        delta = 0
        for key, _ in inbound.items():
            delta += abs(old_page_rank[key] - new_page_rank[key])

        old_page_rank = new_page_rank.copy()

        if delta < 0.00000001:
            break
    return new_page_rank

graph = comp614_module6.file_to_graph('wikipedia_articles_streamlined.txt')
dict = page_rank(graph, 0.85)

top_10 = sorted(dict.items(), key=lambda x: x[1], reverse=True)[:10]

print(top_10)
#print(get_inbound_nbrs(remove_sink_nodes(graph)))
#print(get_inbound_nbrs(graph))
