"""
structures: lightweight composite structures adapted to amicus
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

amicus structures are primarily designed to be the backbones of workflows. So,
the provided subclasses assume that all edges in a composite structure are
unweighted and directed. However, the architecture of Structure and Node can
support weighted edges and undirected composite structures as well.

Contents:
    Node (Element, collections.abc.Hashable):
    Structure (Keystone, ABC): base class for all amicus composite structures.
    Graph (Lexicon, Structure): a lightweight directed acyclic graph (DAG).

To Do:
    Add Tree structure using an amicus Hybrid
    Add Pipeline structure using an amicus Hybrid?
    Add Network structure that is an undirected Graph with potentially weighted
        edges.
    
"""
from __future__ import annotations
import abc
import collections.abc
import copy
import dataclasses
import itertools
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)

import more_itertools

import amicus


Adjacency: Type = Dict[Hashable, List[Hashable]]
Matrix: Type = Union[Tuple[List[List[int]], List[Hashable]], List[List[int]]]
Edge: Tuple[Hashable, Hashable]
Edges: Type = List[Edge]

    
def is_adjacency_list(item: Any) -> bool:
    """[summary]

    Args:
        item (Any): [description]

    Returns:
        bool: [description]
        
    """
    
    return (isinstance(item, Dict) 
            and all(isinstance(v, List) for v in item.values()))

def is_adjacency_matrix(item: Any) -> bool:
    """[summary]

    Args:
        item (Any): [description]

    Returns:
        bool: [description]
        
    """
    if isinstance(item, tuple):
        item = item[0]
    return isinstance(item, List) and all(isinstance(i, List) for i in item)

def is_edge_list(item: Any) -> bool:
    """[summary]

    Args:
        item (Any): [description]

    Returns:
        bool: [description]
        
    """
    return (isinstance(item, List) 
            and all(isinstance(i, Tuple) for i in item)
            and all(len(i) == 2 for i in item))

def adjacency_to_edges(source: Adjacency) -> Edges:
    """Converts an adjacency list to an edge list."""
    edges = []
    for node, connections in source.items():
        for connection in connections:
            edges.append(tuple(node, connection))
    return 

def adjacency_to_matrix(source: Adjacency) -> Matrix:
    """Converts an adjacency list to an adjacency matrix."""
    names = list(source.keys())
    matrix = []
    for i in range(len(source)): 
        matrix.append([0] * len(source))
        for j in source[i]:
            matrix[i][j] = 1
    return tuple(matrix, names)

def edges_to_adjacency(source: Edges) -> Adjacency:
    """Converts and edge list to an adjacency list."""
    adjacency = {}
    for edge_pair in source:
        if edge_pair[0] not in adjacency:
            adjacency[edge_pair[0]] = [edge_pair[1]]
        else:
            adjacency[edge_pair[0]].append(edge_pair[1])
        if edge_pair[1] not in adjacency:
            adjacency[edge_pair[1]] = []
    return adjacency

def matrix_to_adjacency(source: Matrix) -> Adjacency:
    """Converts adjacency matrix to an adjacency list."""
    matrix = source[0]
    names = source[1]
    name_mapping = dict(zip(range(len(matrix)), names))
    raw_adjacency = {
        i: [j for j, adjacent in enumerate(row) if adjacent] 
        for i, row in enumerate(matrix)}
    adjacency = {}
    for key, value in raw_adjacency.items():
        new_key = name_mapping[key]
        new_values = []
        for edge in value:
            new_values.append(name_mapping[edge])
        adjacency[new_key] = new_values
    return adjacency


@dataclasses.dataclass
class Node(amicus.quirks.Element, amicus.base.Proxy, collections.abc.Hashable):
    """Vertex wrapper to provide hashability to any object.
    
    Node acts a basic wrapper for any item stored in an amicus Structure. An
    amicus Structure does not require Node instances to be stored. Rather, they
    are offered as a convenient type which is also used internally in amicus.
    
    By inheriting from Proxy, a Node will act as a pass-through class for access
    methods seeking attributes not in a Node instance but rather stored in 
    'contents'.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Configuration instance, 'name' should 
            match the appropriate section name in a Configuration instance. 
            Defaults to None. 
        contents (Any): any stored item(s). Defaults to None.

    """
    name: str = None
    contents: Any = None

    """ Initialization Methods """
    
    def __init_subclass__(cls, *args, **kwargs):
        """Forces subclasses to use the same hash methods as Node.
        
        This is necessary because dataclasses, by design, do not automatically 
        inherit the hash and equivalance dunder methods from their super 
        classes.
        
        """
        super().__init_subclass__(*args, **kwargs)
        cls.__hash__ = Node.__hash__
        cls.__eq__ = Node.__eq__
        cls.__ne__ = Node.__ne__
        
    """ Dunder Methods """

    def __hash__(self) -> Hashable:
        """Makes Node hashable so that it can be used as a key in a dict.

        Rather than using the object ID, this method prevents too Nodes with
        the same name from being used in a composite object that uses a dict as
        its base storage type.
        
        Returns:
            Hashable: of Node 'name'.
            
        """
        return hash(self.name)

    def __eq__(self, other: Node) -> bool:
        """Makes Node hashable so that it can be used as a key in a dict.

        Args:
            other (Node): other Node instance to test for equivalance.
            
        Returns:
            bool: whether 'name' is the same as 'other.name'.
            
        """
        try:
            return str(self.name) == str(other.name)
        except AttributeError:
            return str(self.name) == other

    def __ne__(self, other: Node) -> bool:
        """Completes equality test dunder methods.

        Args:
            other (Node): other Node instance to test for equivalance.
           
        Returns:
            bool: whether 'name' is not the same as 'other.name'.
            
        """
        return not(self == other)


@dataclasses.dataclass
class Graph(amicus.base.Lexicon):
    """Base class for connected amicus data structures.
    
    Graph stores a directed acyclic graph (DAG) as an adjacency list. Despite 
    being called an adjacency "list," the typical and most efficient way to 
    store one is using a python dict. An amicus Graph inherits from a Lexicon 
    in order to allow use of its extra functionality over a plain dict.
    
    Graph supports '+' and '+=' to be used to join two amicus Graph instances. 
    
    Graph also supports autovivification where a list is created as a value for
    a missing key. This means that a Graph need not inherit from defaultdict.
    
    Args:
        contents (Adjacency): an adjacency list where the 
            keys are nodes and the values are nodes which the key is connected 
            to. Defaults to an empty dict.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.
                  
    """  
    contents: Adjacency = dataclasses.field(
        default_factory = dict)
    default: Any = dataclasses.field(default_factory = list)
    
    """ Properties """

    @property
    def adjacency(self) -> Adjacency:
        """Returns the stored graph as an adjacency list."""
        return self.contents

    @property
    def edges(self) -> Edges:
        """Returns the stored graph as an adjacency matrix."""
        return adjacency_to_edges(source = self.contents)

    @property
    def endpoints(self) -> List[Hashable]:
        """Returns endpoint nodes in the Graph."""
        return [k for k in self.contents.keys() if not self.contents[k]]

    @property
    def matrix(self) -> Matrix:
        """Returns the stored graph as an edge list."""
        return adjacency_to_matrix(source = self.contents)
                      
    @property
    def nodes(self) -> Dict[str, Hashable]:
        """Returns a dict of node names as keys and nodes as values.
        
        Because Graph allows various Hashable objects to be used as keys,
        including the Nodes class, there isn't an obvious way to access already
        stored nodes. This property creates a new dict with str keys derived
        from the nodes (looking first for a 'name' attribute) so that a user
        can access a node. 
        
        This property is not needed if the stored nodes are all strings.
        
        Returns:
            Dict[str, Hashable]: keys are the name or has of nodes and the 
                values are the nodes themselves.
            
        """
        return {self._hashify(n): n for n in self.contents.keys()}

    @property
    def paths(self) -> List[List[Hashable]]:
        """Returns all paths through the Graph in a list of lists form.
        
        Returns:
            List[List[Hashable]]: returns all paths from 'roots' to 'endpoints' 
                in a list of lists of nodes.
                
        """
        return self._find_all_paths(starts = self.roots, ends = self.endpoints)
       
    @property
    def roots(self) -> List[Hashable]:
        """Returns root nodes in the Graph.

        Returns:
            List[Hashable]: root nodes.
            
        """
        stops = list(itertools.chain.from_iterable(self.contents.values()))
        return [k for k in self.contents.keys() if k not in stops]
    
    """ Class Methods """
    
    @classmethod
    def create(cls, source: Union[Adjacency, Edges, Matrix]) -> Graph:
        """Creates an instance of a Graph from 'source'.
        
        Args:
            source (Union[Adjacency, Edges, Matrix]): an adjacency list, 
                adjacency matrix, or edge list which can used to create the
                stored graph.
                
        Returns:
            Graph: a Graph instance created based on 'source'.
                
        """
        if is_adjacency_list(item = source):
            return cls.from_adjacency(adjacency = source)
        elif is_adjacency_matrix(item = source):
            return cls.from_matrix(matrix = source)
        elif is_edge_list(item = source):
            return cls.from_adjacency(edges = source)
        else:
            raise TypeError(
                f'create requires source to be an adjacency list, adjacency '
                f'matrix, or edge list')
           
    @classmethod
    def from_adjacency(cls, adjacency: Adjacency) -> Graph:
        """Creates a Graph instance from an adjacency list.
        
        'adjacency' should be formatted with nodes as keys and values as lists
        of names of nodes to which the node in the key is connected.

        Args:
            adjacency (Adjacency): adjacency list used to 
                create a Graph instance.

        Returns:
            Graph: a Graph instance created based on 'adjacent'.
              
        """
        return cls(contents = adjacency)
    
    @classmethod
    def from_edges(cls, edges: Edges) -> Graph:
        """Creates a Graph instance from an edge list.

        'edges' should be a list of tuples, where the first item in the tuple
        is the node and the second item is the node (or name of node) to which
        the first item is connected.
        
        Args:
            edges (Edges): Edge list used to create a Graph 
                instance.
                
        Returns:
            Graph: a Graph instance created based on 'edges'.

        """
        return cls(contents = edges_to_adjacency(source = edges))
    
    @classmethod
    def from_matrix(cls, matrix: Matrix) -> Graph:
        """Creates a Graph instance from an adjacency matrix

        Args:
            matrix (Matrix): adjacency matrix used to create a Graph instance. 
                The values in the matrix should be 1 (indicating an edge) and 0 
                (indicating no edge).
 
        Returns:
            Graph: a Graph instance created based on 'matrix'.
                        
        """
        return cls(contents = matrix_to_adjacency(source = matrix))
    
    """ Public Methods """
    
    def add(self, node: Hashable) -> None:
        """Adds nodes or edges to 'contents' depending on type.
        
        Args:
            item (Union[Hashable, tuple[Hashable]]): either a node or a tuple 
                containing the names of nodes for an edge to be created.

        """
        self.contents[self._hashify(node)] = []
        return self

    def connect(self, start: Hashable, stop: Hashable) -> None:
        """Adds an edge to 'contents'.

        Args:
            start (Hashable): name of node for edge to start.
            stop (Hashable): name of node for edge to stop.
            
        Raises:
            ValueError: if 'start' is the same as 'stop'.
            
        """
        if start == stop:
            raise ValueError(
                'The start of an edge cannot be the same as the stop')
        else:
            if stop not in self.contents:
                self.add(node = stop)
            if start not in self.contents:
                self.add(node = start)
            if stop not in self.contents[start]:
                self.contents[start].append(self._hashify(stop))
        return self

    def append(self, 
        node: Hashable,
        start: Union[Hashable, Sequence[Hashable]] = None) -> None:
        """Appends 'node' to the stored data structure.

        Subclasses should ordinarily provide their own methods.
        
        Args:
            node (Hashable): item to add to 'contents'.
            start (Union[Hashable, Sequence[Hashable]]): where to add new node 
                to. If there are multiple nodes in 'start', 'node' will be added 
                to each of the starting points. If 'start' is None, 'endpoints'
                will be used. Defaults to None.
            
        """ 
        if start is None:
            start = self.endpoints
        if start:
            for starting in more_itertools.always_iterable(start):
                if node not in [starting]:
                    self.connect(start = starting, stop = node)
        else:
            self.add(node = node)
        return self  

    def disconnect(self, start: Hashable, stop: Hashable) -> None:
        """Deletes edge from graph.

        Args:
            start (Hashable): starting node for the edge to delete.
            stop (Hashable): ending node for the edge to delete.
        
        Raises:
            KeyError: if 'start' is not a node in the Graph.
            ValueError: if 'stop' does not have an edge with 'start'.

        """
        try:
            self.contents[start].remove(stop)
        except KeyError:
            raise KeyError(f'{start} does not exist in the graph')
        except ValueError:
            raise ValueError(f'{stop} is not connected to {start}')
        return self
       
    def delete(self, node: Hashable) -> None:
        """Deletes node from graph.
        
        Args:
            node (Hashable): node to delete from 'contents'.
        
        Raises:
            KeyError: if 'node' is not in 'contents'.
            
        """
        try:
            del self.contents[node]
        except KeyError:
            raise KeyError(f'{node} does not exist in the graph')
        self.contents = {
            k: v.remove(node) for k, v in self.contents.items() if node in v}
        return self
       
    def excludify(self, subset: Union[Any, Sequence[Any]], **kwargs) -> Graph:
        """Returns a new instance without a subset of 'contents'.

        Args:
            subset (Union[Any, Sequence[Any]]): key(s) for which key/value pairs 
                from 'contents' should not be returned.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.

        Returns:
            Graph: with only key/value pairs with keys not in 'subset'.

        """
        new_graph = copy.deepcopy(self)
        for node in more_itertools.always_iterable(subset):
            new_graph.delete_node(node = node)
        return new_graph

    def extend(self, 
        nodes: Sequence[Union[Hashable, List]],
        start: Union[Hashable, Sequence[Hashable]] = None) -> None:
        """Adds 'nodes' to the stored data structure.

        Args:
            nodes (Sequence[Hashable]): names of items to add.
            start (Union[Hashable, Sequence[Hashable]]): where to add new node 
                to. If there are multiple nodes in 'start', 'node' will be added 
                to each of the starting points. If 'start' is None, 'endpoints'
                will be used. Defaults to None.
                
        """
        if any(isinstance(n, (list, tuple)) for n in nodes):
            nodes = tuple(more_itertools.collapse(nodes))
        if start is None:
            start = self.endpoints
        if start:
            for starting in more_itertools.always_iterable(start):
                self.connect(start = starting, stop = nodes[0])
        else:
            self.add(nodes[0])
        edges = more_itertools.windowed(nodes, 2)
        for edge_pair in edges:
            self.connect(start = edge_pair[0], stop = edge_pair[1])
        return self  
  
    def find_paths(self, 
        start: Hashable, 
        end: Hashable, 
        path: List[Hashable] = []) -> List[List[Hashable]]:
        """Returns all paths in graph from 'start' to 'end'.

        The code here is adapted from: https://www.python.org/doc/essays/graphs/
        
        Args:
            start (Hashable): node to start paths from.
            end (Hashable): node to end paths.
            path (List[Hashable]): a path from 'start' to 'end'. Defaults to an 
                empty list. 

        Returns:
            List[List[Hashable]]: a list of possible paths (each path is a list 
                nodes) from 'start' to 'end'.
            
        """
        path = path + [start]
        if start == end:
            return [path]
        if start not in self.contents:
            return []
        paths = []
        for node in self.contents[start]:
            if node not in path:
                new_paths = self.find_paths(
                    start = node, 
                    end = end, 
                    path = path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths

    def join(self, structure: Graph) -> None:
        """Adds 'structure' to this Graph.

        Combining creates an edge between every endpoint of this instance's
        Graph and the every root of 'graph'.

        Args:
            structure (Graph): a second Graph to join with this one.
            
        Raises:
            ValueError: if 'graph' has nodes that are also in 'contents'.
            TypeError: if 'graph' is not a Graph type.
            
        """
        if isinstance(structure, Graph):
            if self.contents:
                current_endpoints = self.endpoints
                self.contents.update(structure.contents)
                for endpoint in current_endpoints:
                    for root in structure.roots:
                        self.connect(start = endpoint, stop = root)
            else:
                self.contents = structure.contents
        else:
            raise TypeError('structure must be a Graph type to join')
        return self

    def replace_node(self, node: Hashable) -> None:
        """Replaces a node that already exists but leaves its edges intact.

        Args:
            node (Hashable): node to replace a current node with the same hash
                value.

        Raises:
            ValueError: if a node with the same hash value is not in 'contents'.
            
        """
        if node not in self.contents:
            raise ValueError(
                f'{self._hashify(node)} cannot replace a node that does not '
                f'currently exist')   
        else:
            edges = self.contents[node]
            self.contents[node] = edges
        return self
           
    def search(self, 
        start: Hashable = None, 
        depth_first: bool = True) -> List[Hashable]:
        """Returns a path through the stored data structure.

        Args:
            start (Hashable): node to start the path from. If None, it is 
                assigned to 'roots'. Defaults to None.
            depth_first (bool): whether the search should be depth first (True)
                or breadth first (False). Defaults to True.

        Returns:
            List[Hashable]: nodes in a path through the stored data structure.
            
        """        
        if start is None:
            start = self.roots[0]
        if depth_first:
            visited = self._depth_first_search(node = start, visited = [])
        else:
            visited = self._breadth_first_search(node = start)
        return visited
                   
    def subsetify(self, subset: Union[Any, Sequence[Any]], **kwargs) -> Graph:
        """Returns a new instance with a subset of 'contents'.

        Args:
            subset (Union[Any, Sequence[Any]]): key(s) for which key/value pairs 
                from 'contents' should be returned.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.

        Returns:
            Graph: with only key/value pairs with keys in 'subset'.

        """
        excludables = [i for i in self.contents if i not in subset]
        return self.excludify(subset = excludables, **kwargs)

    """ Private Methods """
    
    def _hashify(self, node: Any) -> str:
        """[summary]

        Args:
            node (Any): [description]

        Returns:
            str: [description]
            
        """        
        if isinstance(node, Hashable):
            return node
        else:
            try:
                return node.name
            except AttributeError:
                try:
                    return amicus.tools.snakify(node.__name__)
                except AttributeError:
                    return amicus.tools.snakify(node.__class__.__name__)


    def _breadth_first_search(self, node: Hashable) -> List[Hashable]:
        """Returns a breadth first search path through the Graph.

        Args:
            node (Hashable): node to start the search from.

        Returns:
            List[Hashable]: nodes in a path through the Graph.
            
        """        
        visited = set()
        queue = [node]
        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                visited.add(vertex)
                queue.extend(set(self[vertex]) - visited)
        return list(visited)
       
    def _depth_first_search(self, 
        node: Hashable, 
        visited: List[Hashable]) -> List[Hashable]:
        """Returns a depth first search path through the Graph.

        Args:
            node (Hashable): node to start the search from.
            visited (List[Hashable]): list of visited nodes.

        Returns:
            List[Hashable]: nodes in a path through the Graph.
            
        """  
        if node not in visited:
            visited.append(node)
            for edge in self[node]:
                self._depth_first_search(node = edge, visited = visited)
        return visited
  
    def _find_all_paths(self, 
        starts: Union[Hashable, Sequence[Hashable]],
        ends: Union[Hashable, Sequence[Hashable]]) -> List[List[Hashable]]:
        """[summary]

        Args:
            start (Union[Hashable, Sequence[Hashable]]): starting points for 
                paths through the Graph.
            ends (Union[Hashable, Sequence[Hashable]]): endpoints for paths 
                through the Graph.

        Returns:
            List[List[Hashable]]: list of all paths through the Graph from all
                'starts' to all 'ends'.
            
        """
        all_paths = []
        for start in more_itertools.always_iterable(starts):
            for end in more_itertools.always_iterable(ends):
                paths = self.find_paths(start = start, end = end)
                if paths:
                    if all(isinstance(path, Hashable) for path in paths):
                        all_paths.append(paths)
                    else:
                        all_paths.extend(paths)
        return all_paths
            
    """ Dunder Methods """

    def __add__(self, other: Structure) -> None:
        """Adds 'other' Structure to this Structure.

        Adding another structure uses the 'join' method. Read that method's 
        docstring for further details about how the structures are added 
        together.
        
        Args:
            other (Structure): a second Structure to join with this one.
            
        """
        self.join(structure = other)        
        return self

    def __iadd__(self, other: Structure) -> None:
        """Adds 'other' Structure to this Structure.

        Adding another structure uses the 'join' method. Read that method's 
        docstring for further details about how the structures are added 
        together.
        
        Args:
            other (Structure): a second Structure to join with this one.
            
        """
        self.join(structure = other)        
        return self

    def __str__(self) -> str:
        """Returns prettier representation of the Graph.

        Returns:
            str: a formatted str of class information and the contained 
                adjacency list.
            
        """
        new_line = '\n'
        representation = [f'{new_line}amicus {self.__class__.__name__}']
        representation.append('adjacency list:')
        for node, edges in self.contents.items():
            representation.append(f'    {node}: {str(edges)}')
        return new_line.join(representation) 


# @dataclasses.dataclass
# class Pipeline(amicus.base.Hybrid, Structure):
#     """Stores a pipeline structure using an amicus Hybrid.
    
#     Unlike a Graph, items stored do not need to be hashable, even though the
#     Pipeline, by virtue of inheriting from Hybrid, provides a dict interface.
#     However, to offer this functionality, all items stored in Pipeline should
#     have a 'name' attribute to provide pseudo-keys for the dict interface.
    
#     Args:
#         contents (Sequence[Any]): items with 'name' attributes to store. If a 
#             dict is passed, the keys will be ignored and only the values will be 
#             added to 'contents'. If a single item is passed, it will be placed 
#             in a list. Defaults to an empty list.
#         default (Any): default value to return when the 'get' method is used.
#             Defaults to None.
            
#     """
#     contents: Sequence[Any] = dataclasses.field(default_factory = list)
#     default: Any = None

#     """ Properties """
           
#     @property
#     def endpoints(self) -> List[Any]:
#         """Returns endpoint nodes in the Pipeline.

#         Returns:
#             List[Any] nodes at the end of the stored data structure.
            
#         """
#         if self.consistent_interface:
#             return [self.contents[-1]]
#         else:
#             return self.contents[-1]
           
#     @property             
#     def nodes(self) -> List[Any]:
#         """Returns all nodes in the Graph.

#         Returns:
#             List[Any]: nodes in the stored data structure.
            
#         """
#         return self.contents
        
#     @property
#     def paths(self) -> List[List[Any]]:
#         """Returns all paths through the stored data structure.
            
#         Returns:
#             List[List[Any]]: returns all paths from 'roots' to 'endpoints' in a 
#                 list of lists of nodes.
                
#         """
#         if self.consistent_interface:
#             return [self.contents]
#         else:
#             return self.contents
           
#     @property
#     def roots(self) -> List[Any]:
#         """Returns root nodes in Pipeline
        
#         Returns:
#             List[Any]: names of root nodes in the stored data structure.
            
#         """
#         if self.consistent_interface:
#             return [self.contents[0]]
#         else:
#             return self.contents[0]

#     """ Class Methods """
    
#     @classmethod
#     def create(cls, **kwargs) -> Pipeline:
#         """Creates an instance of a Graph subclass from kwargs.
        
#         Returns:
#             Pipeline: a Pipline instance created using kwargs.
            
#         """
#         if ('nodes' in kwargs 
#                 and isinstance(kwargs['nodes'], Sequence) 
#                 and (all(isinstance(n, str) for n in kwargs['nodes'])
#                      or (all(hasattr(n, 'name') for n in kwargs['nodes'])))):
#             return cls.from_nodes(**kwargs)
#         else:
#             return cls(**kwargs)
 
#     @classmethod
#     def from_nodes(cls, nodes: Union[Any, Sequence[Any]]) -> Pipeline:
#         """[summary]

#         Args:
#             nodes (Union[Any, Sequence[Any]]): [description]

#         Returns:
#             Pipeline: [description]
            
#         """        
#         return cls(contents = amicus.tools.listify(nodes))    
        
#     """ Public Methods """
    
#     def add(self, nodes: Any, **kwargs) -> None:
#         """Adds 'nodes' to the stored data structure.
        
#         Subclasses should ordinarily provide their own methods.
        
#         Args:
#             nodes (Any): item(s) to add to 'contents'.
            
#         """
#         raise NotImplementedError(
#             f'{__name__} is not implemented for a {self.__class__.__name__} '
#             f'structure')

#     def append(self, 
#         node: str,
#         start: Union[str, Sequence[str]] = None, 
#         **kwargs) -> None:
#         """Appends 'node' to the stored data structure.

#         Subclasses should ordinarily provide their own methods.
        
#         Args:
#             node (str): item to add to 'contents'.
#             start (Union[str, Sequence[str]]): where to add new node to. If
#                 there are multiple nodes in 'start', 'node' will be added to
#                 each of the starting points. If 'start' is None, 'endpoints'
#                 will be used. Defaults to None.
            
#         """ 
#         raise NotImplementedError(
#             f'{__name__} is not implemented for a {self.__class__.__name__} '
#             f'structure')

#     def extend(self, 
#         nodes: Sequence[str],
#         start: Union[str, Sequence[str]] = None) -> None:
#         """Adds 'nodes' to the stored data structure.

#         Subclasses should ordinarily provide their own methods.

#         Args:
#             nodes (Sequence[str]): names of items to add.
#             start (Union[str, Sequence[str]]): where to add new nodes to. If
#                 there are multiple nodes in 'start', 'nodes' will be added to
#                 each of the starting points. If 'start' is None, 'endpoints'
#                 will be used. Defaults to None.
                
#         """
#         raise NotImplementedError(
#             f'{__name__} is not implemented for a {self.__class__.__name__} '
#             f'structure')

#     def join(self, structure: Structure) -> None:
#         """Adds 'other' Structure to this Structure.

#         Subclasses should ordinarily provide their own methods.
        
#         Args:
#             structure (Structure): a second Structure to join with this one.
            
#         """
#         raise NotImplementedError(
#             f'{__name__} is not implemented for a {self.__class__.__name__} '
#             f'structure')
         
#     def search(self, 
#         start: Hashable = None, 
#         depth_first: bool = True) -> List[Any]:
#         """Returns a path through the stored data structure.

#         Args:
#             start (str): node to start the path from. If None, it is assigned to
#                 'roots'. Defaults to None.
#             depth_first (bool): whether the search should be depth first (True)
#                 or breadth first (False). Defaults to True.

#         Returns:
#             List[Any]: nodes in a path through the stored data structure.
            
#         """        
#         return self.contents


# @dataclasses.dataclass
# class Tree(amicus.base.Hybrid, Structure):
#     """Stores a general tree structure using an amicus Hybrid.
    
#     Args:
#         contents (Sequence[Any]): items with 'name' attributes to store. If a 
#             dict is passed, the keys will be ignored and only the values will be 
#             added to 'contents'. If a single item is passed, it will be placed 
#             in a list. Defaults to an empty list.
#         default (Any): default value to return when the 'get' method is used.
            
#     """
#     contents: Sequence[Any] = dataclasses.field(default_factory = list)
#     default: Any = None
    