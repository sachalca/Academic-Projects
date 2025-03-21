"""
COMP 614
Homework 4: Graphs
"""

import comp614_module4


def file_to_graph(filename):
    """
    Given the name of a file, reads the contents of that file and uses it to
    build a graph. Assumes that each line will contain the name of a single node.
    If the line does not start with a tab, it contains the name of a new node to
    be added to the graph. If the line starts with a tab, it contains the name of
    a node that is a neighbor of the most recently added node.

    For example, imagine that the file is structured as follows:
    node1
        node2
        node3
    node2
        node1
    node3

    In this case, the graph has three nodes: node1, node2, and node3. node1 has
    outbound edges to node2 and node3. node2 has an outbound edge to node1. node3
    has no outbound edges.
    """

    graph = comp614_module4.DiGraph()
    with open(filename, 'r', encoding='utf-8') as wiki:
        lines = wiki.readlines()

    last_node = ''

    for line in lines:
        if line.isspace():
            continue
        if not line.startswith('\t'):
            graph.add_node(line.strip())
            last_node = line.strip()
        else:
            graph.add_edge(last_node, line.strip())

    return graph

class Queue:
    """
    A representation of a FIFO queue.
    """

    def __init__(self):
        """
        Constructs a new empty queue.
        """
        self._queue = []

    def __len__(self):
        """
        Returns an integer representing the number of items in the queue.
        """
        return len(self._queue)

    def __str__(self):
        """
        Returns a string representation of the queue.
        """
        return str(self._queue)

    def push(self, item):
        """
        Adds the given item to the queue.
        """
        self._queue.append(item)

    def pop(self):
        """
        Removes and returns the least recently added item from the queue.
        Assumes that there is at least one element in the queue.
        """
        if not self._queue:
            raise IndexError('Cannot pop from empty queue')
        return self._queue.pop(0)

    def clear(self):
        """
        Removes all items from the queue.
        """
        self._queue = []


def bfs(graph, start_node):
    """
    Performs a breadth-first search on the given graph starting at the given
    node. Returns a two-element tuple containing a dictionary mapping each
    node to its distance from the start node and a dictionary mapping each
    node to its parent in the search.
    """

    queue = Queue()
    dist = {}
    parent = {}

    for node in graph.nodes():
        dist[node] = float("inf")
        parent[node] = None

    dist[start_node] = 0
    queue.push(start_node)

    while len(queue) > 0:
        node = queue.pop()
        for neighbor in graph.get_neighbors(node):
            if dist[neighbor] == float("inf"):
                dist[neighbor] = dist[node] + 1
                parent[neighbor] = node
                queue.push(neighbor)


    return dist, parent



def connected_components(graph):
    """
    Finds all weakly connected components in the graph. Returns these components
    in the form  of a set of components, where each component is represented as a
    frozen set of nodes. Should not mutate the input graph.
    """

    new_graph = graph.copy()
    sets = set()
    visited = {}

    for node in new_graph.nodes():
        visited[node] = False

    for node in new_graph.nodes():
        for nbr in new_graph.get_neighbors(node):
            new_graph.add_edge(nbr, node)

    for node in new_graph.nodes():
        if visited[node]:
            continue
        visited[node] = True
        temp_set = set()
        elements, _ = bfs(new_graph, node)
        for key, value in elements.items():
            if value != float('inf'):
                temp_set.add(key)
                visited[key] = True
        frozen = frozenset(temp_set)
        sets.add(frozen)

    return sets


