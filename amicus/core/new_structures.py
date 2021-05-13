"""
structures: lightweight composite structures adapted to amicus
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

amicus structures are primarily designed to be the backbones of workflows. So,
the provided subclasses assume that all edges in a composite structure are
unweighted and directed.

Types:
    Adjacency (Type): annotation type for an adjacency list.
    Matrix (Type): annotation type for an adjacency matrix.
    Edge (Type): annotation type for a tuple of edge endpoints.
    Edges (Type): annotation type for an edge list.
    Pipeline (Type): annotation type for a pipeline.
    Pipelines (Type): annotation type for pipelines.
    Nodes (Type): annotation type for one or more nodes.
    
Functions:
    is_adjacency_list (Callable): tests if an object is an adjacency list.
    is_adjacency_matrix (Callable): tests if an object is an adjacency matrix.
    is_edge_list (Callable): tests if an object is an edge list.
    is_pipeline (Callable): tests if an object is a pipeline.
    adjacency_to_edges (Callable): converts adjacency list to edge list.
    adjacency_to_matrix (Callable): converts adjacency list to adjacency matrix.
    edges_to_adjacency (Callable): converts edge list to an adjacency list.
    matrix_to_adjacency (Callable): converts adjacency matrix to an adjacency 
        list.
    pipeline_to_adjacency (Callable): converts pipeline to an adjacency list.

Classes:
    Node (Element, Proxy, collections.abc.Hashable): Wrapper for non-hashable 
        objections that a user wishes to store as nodes. It can be subclassed,
        but a subclass must be a dataclass and call super().__post_init__ to 
        ensure that the hash equivalence methods are added to subclasses.
    Graph (Bunch): a lightweight directed acyclic graph (DAG) that serves as
        the base class for amicus composite structures. Internally, the graph is
        stored as an adjacency list. As a result, it should primarily be used
        for workflows or other uses that do form large graphs. In those
        instances, an adjacency matrix would be far more efficient.

To Do:
    Add an Edge class and seamless support for it in Graph to allow for weights,
        direction, and other edge attributes.
    
"""
from __future__ import annotations
import collections.abc
import copy
import dataclasses
import itertools
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)

import more_itertools

import amicus


Adjacency: Type = Dict[Hashable, MutableSequence[Hashable]]
Matrix: Type = Union[Tuple[MutableSequence[MutableSequence[int]], 
                           MutableSequence[Hashable]], 
                     MutableSequence[MutableSequence[int]]]
Edge: Tuple[Hashable, Hashable]
Edges: Type = MutableSequence[Edge]
Pipeline: Type = Union[MutableSequence[Hashable], Tuple[Hashable]]
Pipelines: Type = MutableSequence[MutableSequence[Hashable]]
Nodes: Type = Union[Hashable, Pipeline]

    
def is_adjacency_list(item: Any) -> bool:
    """Returns whether 'item' is an adjacency list."""
    return (isinstance(item, MutableMapping) 
            and all(isinstance(v, MutableSequence) for v in item.values()))

def is_adjacency_matrix(item: Any) -> bool:
    """Returns whether 'item' is an adjacency matrix."""
    if isinstance(item, tuple):
        item = item[0]
    return (isinstance(item, MutableSequence) 
            and all(isinstance(i, MutableSequence) for i in item))

def is_edge_list(item: Any) -> bool:
    """Returns whether 'item' is an edge list."""
    return (isinstance(item, MutableSequence) 
            and all(isinstance(i, Tuple) for i in item)
            and all(len(i) == 2 for i in item))
    
def is_pipeline(item: Any) -> bool:
    """Returns whether 'item' is a pipeline."""
    return isinstance(item, (MutableSequence, Tuple, Set)
                      and all(isinstance(i, Hashable) for i in item))

def adjacency_to_edges(source: Adjacency) -> Edges:
    """Converts an adjacency list to an edge list."""
    edges = []
    for node, connections in source.items():
        for connection in connections:
            edges.append(tuple(node, connection))
    return edges

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

def pipeline_to_adjacency(source: Pipeline) -> Adjacency:
    """Converts a pipeline to an adjacency list."""
    adjacency = {}
    edges = more_itertools.windowed(source, 2)
    for edge_pair in edges:
        adjacency[edge_pair[0]] = edge_pair[1]
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
class Graph(amicus.base.Bunch):
    """Base class for connected amicus data structures.
    
    Graph stores a directed acyclic graph (DAG) as an adjacency list. Despite 
    being called an adjacency "list," the typical and most efficient way to 
    store one is using a python dict. An amicus Graph inherits from a Lexicon 
    in order to allow use of its extra functionality over a plain dict.
    
    Graph supports '+' and '+=' to be used to join two amicus Graph instances. A
    properly formatted adjacency list could also be the added object.
    
    Graph internally supports autovivification where a list is created as a 
    value for a missing key. This means that a Graph need not inherit from 
    defaultdict.
    
    Args:
        contents (Adjacency): an adjacency list where the keys are nodes and the 
            values are nodes which the key is connected to. Defaults to an empty 
            dict.
                  
    """  
    contents: Adjacency = dataclasses.field(default_factory = dict)
    
    """ Properties """

    @property
    def adjacency(self) -> Adjacency:
        """Returns the stored graph as an adjacency list."""
        return self.contents

    @property
    def breadths(self) -> Pipelines:
        """Returns all paths through the Graph using breadth-first search.
        
        Returns:
            Pipelines: returns all paths from 'roots' to 'endpoints' in a list 
                of lists of nodes.
                
        """
        return self._find_all_paths(starts = self.roots, 
                                    ends = self.endpoints,
                                    depth_first = False)

    @property
    def depths(self) -> Pipelines:
        """Returns all paths through the Graph using depth-first search.
        
        Returns:
            Pipelines: returns all paths from 'roots' to 'endpoints' in a list 
                of lists of nodes.
                
        """
        return self._find_all_paths(starts = self.roots, 
                                    ends = self.endpoints,
                                    depth_first = True)
     
    @property
    def edges(self) -> Edges:
        """Returns the stored graph as an edge list."""
        return adjacency_to_edges(source = self.contents)

    @property
    def endpoints(self) -> MutableSequence[Hashable]:
        """Returns a list of endpoint nodes in the Graph."""
        return [k for k in self.contents.keys() if not self.contents[k]]

    @property
    def matrix(self) -> Matrix:
        """Returns the stored graph as an adjacency matrix."""
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
    def roots(self) -> MutableSequence[Hashable]:
        """Returns root nodes in the Graph.

        Returns:
            MutableSequence[Hashable]: root nodes.
            
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
        """Creates a Graph instance from an adjacency matrix.

        Args:
            matrix (Matrix): adjacency matrix used to create a Graph instance. 
                The values in the matrix should be 1 (indicating an edge) and 0 
                (indicating no edge).
 
        Returns:
            Graph: a Graph instance created based on 'matrix'.
                        
        """
        return cls(contents = matrix_to_adjacency(source = matrix))
    
    @classmethod
    def from_pipeline(cls, pipeline: Pipeline) -> Graph:
        """Creates a Graph instance from a Pipeline.

        Args:
            pipeline (Pipeline): serial pipeline used to create a Graph
                instance.
 
        Returns:
            Graph: a Graph instance created based on 'pipeline'.
                        
        """
        return cls(contents = pipeline_to_adjacency(source = pipeline))
       
    """ Public Methods """
    
    def add(self, 
            node: Hashable,
            from_nodes: Nodes = None,
            to_nodes: Nodes = None) -> None:
        """Adds 'node' to 'contents' with no corresponding edges.
        
        Args:
            node (Hashable): a node to add to the stored graph.
            from_nodes (Nodes): node(s) from which node should be connected.
            to_nodes (Nodes): node(s) to which node should be connected.

        """
        if to_nodes is None:
            self.contents[node] = []
        elif to_nodes in self:
            self.contents[node] = amicus.tools.listify(to_nodes)
        else:
            missing = [n for n in to_nodes if n not in self.contents]
            raise KeyError(f'to_nodes {missing} are not in the Graph')
        if from_nodes is not None:  
            if (isinstance(from_nodes, Hashable) and from_nodes in self
                    or (isinstance(from_nodes, (MutableSequence, Tuple, Set)) 
                        and all(isinstance(n, Hashable) for n in from_nodes)
                        and all(n in self.contents for n in from_nodes))):
                start = from_nodes
            elif (hasattr(self.__class__, from_nodes) 
                    and isinstance(getattr(type(self), from_nodes), property)):
                start = getattr(self, from_nodes)
            else:
                missing = [n for n in from_nodes if n not in self.contents]
                raise KeyError(f'from_nodes {missing} are not in the Graph')
            for starting in more_itertools.always_iterable(start):
                if node not in [starting]:
                    self.connect(start = starting, stop = node)                 
        return self 

    def append(self, 
               source: Union[Graph, Adjacency, Edges, Matrix, Nodes]) -> None:
        """Adds 'source' to this Graph.

        Combining creates an edge between every endpoint of this instance's
        Graph and the every root of 'source'.

        Args:
            source (Union[Graph, Adjacency, Edges, Matrix, Nodes]): another 
                Graph to join with this one, an adjacency list, an edge list, an
                adjacency matrix, or Nodes.
            
        Raises:
            TypeError: if 'source' is neither a Graph, Adjacency, Edges, Matrix,
                or Nodes type.
            
        """
        if isinstance(source, Graph):
            if self.contents:
                current_endpoints = self.endpoints
                self.contents.update(source.contents)
                for endpoint in current_endpoints:
                    for root in source.roots:
                        self.connect(start = endpoint, stop = root)
            else:
                self.contents = source.contents
        elif isinstance(source, Adjacency):
            self.append(source = self.from_adjacency(adjacecny = source))
        elif isinstance(source, Edges):
            self.append(source = self.from_edges(edges = source))
        elif isinstance(source, Matrix):
            self.append(source = self.from_matrix(matrix = source))
        elif isinstance(source, Nodes):
            if isinstance(source, (MutableSequence, Tuple, Set)):
                new_graph = Graph()
                edges = more_itertools.windowed(source, 2)
                for edge_pair in edges:
                    new_graph.add(node = edge_pair[0], to_nodes = edge_pair[1])
                self.append(source = new_graph)
            else:
                self.add(node = source)
        else:
            raise TypeError(
                'source must be a Graph, Adjacency, Edges, Matrix, or Nodes '
                'type')
        return self
  
    def connect(self, start: Hashable, stop: Hashable) -> None:
        """Adds an edge from 'start' to 'stop'.

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

    def merge(self, source: Union[Graph, Adjacency, Edges, Matrix]) -> None:
        """Adds 'source' to this Graph.

        This method is roughly equivalent to a dict.update, just adding the
        new keys and values to the existing graph. It converts the supported
        formats to an adjacency list that is then added to the existing 
        'contents'.
        
        Args:
            source (Union[Graph, Adjacency, Edges, Matrix]): another Graph to 
                add to this one, an adjacency list, an edge list, or an
                adjacency matrix.
            
        Raises:
            TypeError: if 'source' is neither a Graph, Adjacency, Edges, or 
                Matrix type.
            
        """
        if isinstance(source, Graph):
            source = source.contents
        elif isinstance(source, Adjacency):
            pass
        elif isinstance(source, Edges):
            source = self.from_edges(edges = source).contents
        elif isinstance(source, Matrix):
            source = self.from_matrix(matrix = source).contents
        else:
            raise TypeError(
                'source must be a Graph, Adjacency, Edges, or Matrix type to '
                'update')
        self.contents.update(source)
        return self
  
    def subgraph(self, 
                 include: Union[Any, Sequence[Any]] = None,
                 exclude: Union[Any, Sequence[Any]] = None) -> Graph:
        """Returns a new Graph without a subset of 'contents'.
        
        All edges will be removed that include any nodes that are not part of
        the new subgraph.
        
        Any extra attributes that are part of a Graph (or a subclass) will be
        maintained in the returned subgraph.

        Args:
            include (Union[Any, Sequence[Any]]): nodes which should be included
                with any applicable edges in the new subgraph.
            exclude (Union[Any, Sequence[Any]]): nodes which should not be 
                included with any applicable edges in the new subgraph.

        Returns:
            Graph: with only key/value pairs with keys not in 'subset'.

        """
        if include is None and exclude is None:
            raise ValueError(
                'subgraph requiest either include or exclude to not be None')
        else:
            if include:
                excludables = [k for k in self.contents if k not in include]
            else:
                excludables = []
            excludables.extend([i for i in self.contents if i not in exclude])
            new_graph = copy.deepcopy(self)
            for node in more_itertools.always_iterable(excludables):
                new_graph.delete(node = node)
        return new_graph

    def walk(self, 
             start: Hashable, 
             stop: Hashable, 
             path: Pipeline = None,
             depth_first: bool = True) -> Pipelines:
        """Returns all paths in graph from 'start' to 'stop'.

        The code here is adapted from: https://www.python.org/doc/essays/graphs/
        
        Args:
            start (Hashable): node to start paths from.
            stop (Hashable): node to stop paths.
            path (Pipeline): a path from 'start' to 'stop'. Defaults to an 
                empty list. 

        Returns:
            Pipelines: a list of possible paths (each path is a list 
                nodes) from 'start' to 'stop'.
            
        """
        if path is None:
            path = []
        path = path + [start]
        if start == stop:
            return [path]
        if start not in self.contents:
            return []
        if depth_first:
            method = self._depth_first_search
        else:
            method = self._breadth_first_search
        paths = []
        for node in self.contents[start]:
            if node not in path:
                new_paths = self.walk(
                    start = node, 
                    stop = stop, 
                    path = path,
                    depth_first = depth_first)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths

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


    def _breadth_first_search(self, node: Hashable) -> Pipeline:
        """Returns a breadth first search path through the Graph.

        Args:
            node (Hashable): node to start the search from.

        Returns:
            Pipeline: nodes in a path through the Graph.
            
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
        visited: MutableSequence[Hashable]) -> Pipeline:
        """Returns a depth first search path through the Graph.

        Args:
            node (Hashable): node to start the search from.
            visited (MutableSequence[Hashable]): list of visited nodes.

        Returns:
            Pipeline: nodes in a path through the Graph.
            
        """  
        if node not in visited:
            visited.append(node)
            for edge in self[node]:
                self._depth_first_search(node = edge, visited = visited)
        return visited
  
    def _find_all_paths(self, 
        starts: Union[Hashable, Sequence[Hashable]],
        stops: Union[Hashable, Sequence[Hashable]],
        depth_first: bool = True) -> Pipelines:
        """[summary]

        Args:
            start (Union[Hashable, Sequence[Hashable]]): starting points for 
                paths through the Graph.
            ends (Union[Hashable, Sequence[Hashable]]): endpoints for paths 
                through the Graph.

        Returns:
            Pipelines: list of all paths through the Graph from all
                'starts' to all 'ends'.
            
        """
        all_paths = []
        for start in more_itertools.always_iterable(starts):
            for end in more_itertools.always_iterable(stops):
                paths = self.walk(start = start, 
                                  stop = end, 
                                  depth_first = depth_first)
                if paths:
                    if all(isinstance(path, Hashable) for path in paths):
                        all_paths.append(paths)
                    else:
                        all_paths.extend(paths)
        return all_paths
            
    """ Dunder Methods """

    def __add__(self, other: Graph) -> None:
        """Adds 'other' Graph to this Graph.

        Adding another graph uses the 'join' method. Read that method's 
        docstring for further details about how the graphs are added 
        together.
        
        Args:
            other (Graph): a second Graph to join with this one.
            
        """
        self.join(graph = other)        
        return self

    def __iadd__(self, other: Graph) -> None:
        """Adds 'other' Graph to this Graph.

        Adding another graph uses the 'join' method. Read that method's 
        docstring for further details about how the graphs are added 
        together.
        
        Args:
            other (Graph): a second Graph to join with this one.
            
        """
        self.join(graph = other)        
        return self

    def __contains__(self, nodes: Nodes) -> bool:
        """[summary]

        Args:
            nodes (Nodes): [description]

        Returns:
            bool: [description]
            
        """
        if isinstance(nodes, (MutableSequence, Tuple, Set)):
            return all(n in self.contents for n in nodes)
        elif isinstance(nodes, Hashable):
            return nodes in self.contents
        else:
            return False   
        
    def __getitem__(self, key: Hashable) -> Any:
        """Returns value for 'key' in 'contents'.

        Args:
            key (Hashable): key in 'contents' for which a value is sought.

        Returns:
            Any: value stored in 'contents'.

        """
        return self.contents[key]

    def __setitem__(self, key: Hashable, value: Any) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (Hashable): key to set in 'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        self.contents[key] = value
        return self

    def __delitem__(self, key: Hashable) -> None:
        """Deletes 'key' in 'contents'.

        Args:
            key (Hashable): key in 'contents' to delete the key/value pair.

        """
        del self.contents[key]
        return self

    def __missing__(self) -> List:
        """Returns an empty list when a key doesn't exist.

        Returns:
            List: an empty list.

        """
        return []
    
    def __str__(self) -> str:
        """Returns prettier representation of the Graph.

        Returns:
            str: a formatted str of class information and the contained 
                adjacency list.
            
        """
        new_line = '\n'
        tab = '    '
        representation = [f'{new_line}amicus {self.__class__.__name__}']
        representation.append('adjacency list:')
        for node, edges in self.contents.items():
            representation.append(f'{tab}{node}: {str(edges)}')
        return new_line.join(representation) 
