"""
structures: lightweight composite structures adapted to amicus
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Structure (Keystone, ABC): base class for all amicus composite structures.
    Graph (Lexicon, Structure): a lightweight directed acyclic graph (DAG).

To Do:
    Add Tree structure.
    Add Pipeline structure?
    
"""
from __future__ import annotations
import abc
import copy
import dataclasses
import itertools
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import more_itertools

import amicus


@dataclasses.dataclass
class Structure(amicus.Bunch, abc.ABC):
    """Abstract base class for iterable amicus data structures.
    
    Args:
        contents (Iterable): stored iterable. Defaults to None.
              
    """
    contents: Iterable = None

    """ Required Subclass Properties """
           
    @property
    def endpoints(self) -> List[str]:
        """Returns endpoint nodes in the Graph.

        Subclasses must provide their own properties.
        
        Returns:
            List[str] namea of endpoints in the stored data structure.
            
        """
        raise NotImplementedError(
            f'{__name__} is not implemented for a {self.name} structure')
           
    @property             
    def nodes(self) -> List[str]:
        """Returns all nodes in the Graph.

        Subclasses must provide their own properties.
        
        Returns:
            List[str]: names of all nodes in the stored data structure.
            
        """
        raise NotImplementedError(
            f'{__name__} is not implemented for a {self.name} structure')
        
    @property
    def paths(self) -> List[List[str]]:
        """Returns all paths through the stored data structure.

        Subclasses must provide their own properties.
                
        Returns:
            List[List[str]]: returns all paths from 'roots' to 'endpoints' in a 
                list of lists of names of nodes.
                
        """
        raise NotImplementedError(
            f'{__name__} is not implemented for a {self.name} structure')
           
    @property
    def roots(self) -> List[str]:
        """Returns root nodes in the stored data structure.

        Subclasses must provide their own properties.

        Returns:
            List[str]: names of root nodes in the stored data structure.
            
        """
        raise NotImplementedError(
            f'{__name__} is not implemented for a {self.name} structure')

    """ Required Subclass Class Methods """
    
    @classmethod
    def create(cls, *kwargs) -> Structure:
        """Creates an instance of a Structure subclass from 'source'.
        
        Subclasses must proivde their own classmethods.
                
        """
        raise NotImplementedError(
            f'{__name__} is not implemented for a {self.name} structure')
 
    """ Required Subclass Methods """
    
    def add(self, nodes: Any, **kwargs) -> None:
        """Adds 'nodes' to the stored data structure.
        
        Subclasses must provide their own methods.
        
        Args:
            nodes (Any): item(s) to add to 'contents'.
            
        """
        raise NotImplementedError(
            f'{__name__} is not implemented for a {self.name} structure')

    def append(self, 
        node: str,
        start: Union[str, Sequence[str]] = None, 
        **kwargs) -> None:
        """Appends 'node' to the stored data structure.

        Subclasses must provide their own methods.
        
        Args:
            node (str): item to add to 'contents'.
            start (Union[str, Sequence[str]]): where to add new node to. If
                there are multiple nodes in 'start', 'node' will be added to
                each of the starting points. If 'start' is None, 'endpoints'
                will be used. Defaults to None.
            
        """ 
        raise NotImplementedError(
            f'{__name__} is not implemented for a {self.name} structure')
    
    def branchify(self, 
        nodes: Sequence[Sequence[str]],
        start: Union[str, Sequence[str]] = None, 
        **kwargs) -> None:
        """Adds parallel paths to the stored data structure.

        Subclasses must provide their own methods.

        Args:
            nodes (Sequence[Sequence[str]]): a list of list of nodes which
                should have a Cartesian product determined and extended to
                the stored data structure.
            start (Union[str, Sequence[str]]): where to add new nodes to. If
                there are multiple nodes in 'start', 'nodes' will be added to
                each of the starting points. If 'start' is None, 'endpoints'
                will be used. Defaults to None.
                
        """ 
        raise NotImplementedError(
            f'{__name__} is not implemented for a {self.name} structure')   

    def combine(self, structure: Structure) -> None:
        """Adds 'other' Structure to this Structure.

        Subclasses must provide their own methods.
        
        Args:
            structure (Structure): a second Structure to combine with this one.
            
        """
        raise NotImplementedError(
            f'{__name__} is not implemented for a {self.name} structure')

    def extend(self, 
        nodes: Sequence[str],
        start: Union[str, Sequence[str]] = None) -> None:
        """Adds 'nodes' to the stored data structure.

        Subclasses must provide their own methods.

        Args:
            nodes (Sequence[str]): names of items to add.
            start (Union[str, Sequence[str]]): where to add new nodes to. If
                there are multiple nodes in 'start', 'nodes' will be added to
                each of the starting points. If 'start' is None, 'endpoints'
                will be used. Defaults to None.
                
        """
        raise NotImplementedError(
            f'{__name__} is not implemented for a {self.name} structure')
         
    def search(self, start: str = None, depth_first: bool = True) -> List[str]:
        """Returns a path through the stored data structure.

        Subclasses must provide their own methods.

        Args:
            start (str): node to start the path from. If None, it is assigned to
                'roots'. Defaults to None.
            depth_first (bool): whether the search should be depth first (True)
                or breadth first (False). Defaults to True.

        Returns:
            List[str]: nodes in a path through the stored data structure.
            
        """        
        raise NotImplementedError(
            f'{__name__} is not implemented for a {self.name} structure')

    """ Dunder Methods """

    def __add__(self, other: Structure) -> None:
        """Adds 'other' Structure to this Structure.

        Structure adding uses the 'combine' method. Read its docstring for further
        details about how the graphs are added together.
        
        Args:
            other (Structure): a second Structure to combine with this one.
            
        """
        self.combine(graph = other)        
        return self

    def __iadd__(self, other: Any) -> None:
        """Adds 'other' Structure to this Structure.

        Structure adding uses the 'combine' method. Read its docstring for further
        details about how the graphs are added together.
        
        Args:
            other (Structure): a second Structure to combine with this one.
            
        """
        self.combine(graph = other)        
        return self


@dataclasses.dataclass
class Graph(amicus.Lexicon, Structure):
    """Stores a directed acyclic graph (DAG) as an adjacency list.

    Despite being called an adjacency "list," the typical and most efficient
    way to store one is using a python dict. A amicus Graph inherits from a 
    Lexicon in order to allow use of its extra functionality over a plain dict.
    
    Graph also supports autovivification where a list is created as a value for
    a missing key. This means that a Graph need not inherit from defaultdict.
    
    The Graph does not actually store node objects. Rather, it maintains the
    string names of nodes which can then be used to create and iterate over
    nodes (as is done by Workflow in the project subpackage).
    
    Args:
        contents (Dict[str, List[str]]): an adjacency list where the keys are 
            the names of nodes and the values are names of nodes which the key 
            is connected to. Defaults to an empty dict.
        default (Any): default value to return when the 'get' method is used.
                  
    """  
    contents: Dict[str, List[str]] = dataclasses.field(default_factory = dict)
    default: Any = dataclasses.field(default_factory = list)
    
    """ Properties """
           
    @property
    def endpoints(self) -> List[str]:
        """Returns endpoint nodes in the Graph.

        Returns:
            List[str]: names of endpoint node in 'contents'. 
            
        """
        return [k for k in self.contents.keys() if not self.contents[k]]
              
    @property
    def nodes(self) -> List[str]:
        """Returns all nodes in the Graph.

        Returns:
            List[str]: all nodes.
            
        """
        return list(self.keys())

    @property
    def paths(self) -> List[List[str]]:
        """Returns all paths through the Graph in a list of lists form.
        
        Returns:
            List[List[str]]: returns all paths from 'roots' to 'endpoints' in a 
                list of lists of names of nodes.
                
        """
        return self._find_all_permutations(
            starts = self.roots, 
            ends = self.endpoints)
       
    @property
    def roots(self) -> List[str]:
        """Returns root nodes in the Graph.

        Returns:
            List[str]: root nodes.
            
        """
        stops = list(itertools.chain.from_iterable(self.contents.values()))
        return [k for k in self.contents.keys() if k not in stops]
    
    """ Class Methods """
    
    @classmethod
    def create(cls, source: Any, **kwargs) -> Graph:
        """Creates an instance of a Graph subclass from 'source'.
        
        'source' must be an adjacency list, adjacency matrix, or edge list. For
        specific formatting of each supported source type, look at the docs for
        each of the called methods beginning with 'from_'.
                
        If 'source' is an adjacency matrix, 'names' should also be passed as a
        list of node names corresponding with the adjacency matrix.
        
        Args:
            source (Any): data in another form to convert to the internal 
                structure in a Graph.
                
        Raises:
            TypeError: if source is not an adjacency list, adjacency matrix, or
                edge list.
                
        """
        if (isinstance(source, Dict) 
                and all(isinstance(v, List) for v in source.values())):
            return cls.from_adjacency(adjaceny = source)
        elif isinstance(source, List):
            if all(isinstance(i, Tuple) for i in source):
                return cls.from_edges(egdes = source)
            elif all(isinstance(i, List) for i in source):
                return cls.from_matrix(matrix = source, **kwargs)
        raise TypeError(
            'source must be an adjacency list, adjacency matrix, or edge list')
           
    @classmethod
    def from_adjacency(cls, adjacency: Dict[str, List[str]]) -> Graph:
        """Creates a Graph instance from an adjacency list.

        Args:
            adjacency (Dict[str, List[str]]): adjacency list used to create a
                Graph instance.
            
        """
        return cls(contents = adjacency)
    
    @classmethod
    def from_edges(cls, edges: List[Tuple[str]]) -> Graph:
        """Creates a Graph instance from an edge list.

        Args:
            edges (List[Tuple[str]]): Edge list used to create a Graph instance.
            
        """
        contents = {}
        for edge_pair in edges:
            if edge_pair[0] not in contents:
                contents[edge_pair[0]] = [edge_pair[1]]
            else:
                contents[edge_pair[0]].append(edge_pair[1])
            if edge_pair[1] not in contents:
                contents[edge_pair[1]] = []
        return cls(contents = contents)
    
    @classmethod
    def from_matrix(cls, matrix: List[List[int]], names: List[str]) -> Graph:
        """Creates a Graph instance from an adjacency matrix

        Args:
            matrix (matrix: List[List[int]]): adjacency matrix used to create a 
                Graph instance. The values in the matrix should be 1 
                (indicating an edge) and 0 (indicating no edge).
            names (List[str]): names of nodes in the order of the rows and
                columns in 'matrix'.
            
        """
        name_mapping = dict(zip(range(len(matrix)), names))
        raw_adjacency = {
            i: [j for j, adjacent in enumerate(row) if adjacent] 
            for i, row in enumerate(matrix)}
        contents = {}
        for key, value in raw_adjacency.items():
            new_key = name_mapping[key]
            new_values = []
            for edge in value:
                new_values.append(name_mapping[edge])
            contents[new_key] = new_values
        return cls(contents = contents)
    
    """ Public Methods """
    
    def add(self, nodes: Union[str, Tuple[str]]) -> None:
        """Adds nodes or edges to 'contents' depending on type.
        
        Args:
            nodes (Union[str, Tuple[str]]): either a str name or a tuple 
                containing the names of nodes for an edge to be created.
        
        Raises:
            TypeError: if 'nodes' is neither a str or a tuple of two strings.
            
        """
        if isinstance(nodes, str):
            self.add_node(node = nodes)
        elif isinstance(nodes, tuple) and len(nodes) == 2:
            self.add_edge(start = nodes[0], stop = nodes[1])
        else:
            raise TypeError('nodes must be a str for adding a node or a tuple '
                            'of two strings for adding an edge')
        return self

    def add_edge(self, start: str, stop: str) -> None:
        """Adds an edge to 'contents'.

        Args:
            start (str): node for edge to start.
            stop (str): node for edge to stop.
            
        Raises:
            ValueError: if 'start' is the same as 'stop'.
            
        """
        if start == stop:
            raise ValueError(
                'The start of an edge cannot be the same as the stop')
        else:
            if stop not in self.contents:
                self.add_node(node = stop)
            if start not in self.contents:
                self.add_node(node = start)
            if stop not in self.contents[start]:
                self.contents[start].append(stop)
        return self

    def add_node(self, node: str) -> None:
        """Adds a node to 'contents'.
        
        Args:
            node (str): node to add to the graph.
            
        Raises:
            ValueError: if 'node' is already in 'contents'.
        
        """
        if node in self.contents:
            pass
        else:
            self.contents[node] = []
        return self

    def append(self, 
        node: str,
        start: Union[str, Sequence[str]] = None) -> None:
        """Appends 'node' to the stored data structure.

        Subclasses must provide their own methods.
        
        Args:
            node (str): item to add to 'contents'.
            start (Union[str, Sequence[str]]): where to add new node to. If
                there are multiple nodes in 'start', 'node' will be added to
                each of the starting points. If 'start' is None, 'endpoints'
                will be used. Defaults to None.
            
        """ 
        if start is None:
            start = self.endpoints
        if start:
            for starting in more_itertools.always_iterable(start):
                if node not in [starting]:
                    self.add_edge(start = starting, stop = node)
        else:
            self.add_node(node = node)
        return self  
    
    def branchify(self, 
        nodes: Sequence[Sequence[str]],
        start: Union[str, Sequence[str]] = None) -> None:
        """Adds parallel paths to the stored data structure.

        Subclasses must provide their own methods.

        Args:
            nodes (Sequence[Sequence[str]]): a list of list of nodes which
                should have a Cartesian product determined and extended to
                the stored data structure.
            start (Union[str, Sequence[str]]): where to add new nodes to. If
                there are multiple nodes in 'start', 'nodes' will be added to
                each of the starting points. If 'start' is None, 'endpoints'
                will be used. Defaults to None.tr]], optional): [description]. 
                Defaults to None.
                
        """
        if start is None:
            start = copy.deepcopy(self.endpoints) 
        paths = list(map(list, itertools.product(*nodes))) 
        for path in paths:
            self.extend(nodes = path, start = start) 
        return self    

    def combine(self, structure: Graph) -> None:
        """Adds 'structure' to this Graph.

        Combining creates an edge between every endpoint of this instance's
        Graph and the every root of 'graph'.

        Args:
            structure (Graph): a second Graph to combine with this one.
            
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
                        self.add_edge(start = endpoint, stop = root)
            else:
                self.contents = structure.contents
        else:
            raise TypeError('structure must be a Graph type to combine')
        return self

    def delete_edge(self, start: str, stop: str) -> None:
        """Deletes edge from graph.

        Args:
            start (str): starting node for the edge to delete.
            stop (str): ending node for the edge to delete.
        
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
       
    def delete_node(self, node: str) -> None:
        """Deletes node from graph.
        
        Args:
            node (str): node to delete from 'contents'.
        
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
            new_graph.delete_node(node)
        return new_graph

    def extend(self, 
        nodes: Sequence[str],
        start: Union[str, Sequence[str]] = None) -> None:
        """Adds 'nodes' to the stored data structure.

        Args:
            nodes (Sequence[str]): names of items to add.
            start (Union[str, Sequence[str]]): where to add new nodes to. If
                there are multiple nodes in 'start', 'nodes' will be added to
                each of the starting points. If 'start' is None, 'endpoints'
                will be used. Defaults to None.
                
        """
        if start is None:
            start = self.endpoints
        if start:
            for starting in more_itertools.always_iterable(start):
                self.add_edge(start = starting, stop = nodes[0])
        else:
            self.add_node(nodes[0])
        edges = more_itertools.windowed(nodes, 2)
        for edge_pair in edges:
            self.add_edge(start = edge_pair[0], stop = edge_pair[1])
        return self  
           
    def search(self, start: str = None, depth_first: bool = True) -> List[str]:
        """Returns a path through the stored data structure.

        Args:
            start (str): node to start the path from. If None, it is assigned to
                'roots'. Defaults to None.
            depth_first (bool): whether the search should be depth first (True)
                or breadth first (False). Defaults to True.

        Returns:
            List[str]: nodes in a path through the stored data structure.
            
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

    def _breadth_first_search(self, node: str) -> List[str]:
        """Returns a breadth first search path through the Graph.

        Args:
            node (str): node to start the search from.

        Returns:
            List[str]: nodes in a path through the Graph.
            
        """        
        visited = set()
        queue = [node]
        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                visited.add(vertex)
                queue.extend(set(self[vertex]) - visited)
        return list(visited)
       
    def _depth_first_search(self, node: str, visited: List[str]) -> List[str]:
        """Returns a depth first search path through the Graph.

        Args:
            node (str): node to start the search from.
            visited (List[str]): list of visited nodes.

        Returns:
            List[str]: nodes in a path through the Graph.
            
        """  
        if node not in visited:
            visited.append(node)
            for edge in self[node]:
                self._depth_first_search(node = edge, visited = visited)
        return visited
    
    def _find_all_paths(self, 
        start: str, 
        end: str, 
        path: List[str] = []) -> List[List[str]]:
        """Returns all paths in graph from 'start' to 'end'.

        The code here is adapted from: https://www.python.org/doc/essays/graphs/
        
        Args:
            start (str): node to start paths from.
            end (str): node to end paths.
            path (List[str]): a path from 'start' to 'end'. Defaults to an empty 
                list. 

        Returns:
            List[List[str]]: a list of possible paths (each path is a list of
                Element names) from 'start' to 'end'
            
        """
        path = path + [start]
        if start == end:
            return [path]
        if start not in self.contents:
            return []
        paths = []
        for node in self.contents[start]:
            if node not in path:
                new_paths = self._find_all_paths(
                    start = node, 
                    end = end, 
                    path = path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths
       
    def _find_all_permutations(self, 
        starts: Union[str, Sequence[str]],
        ends: Union[str, Sequence[str]]) -> List[List[str]]:
        """[summary]

        Args:
            start (Union[str, Sequence[str]]): starting points for paths through
                the Graph.
            ends (Union[str, Sequence[str]]): endpoints for paths through the
                Graph.

        Returns:
            List[List[str]]: list of all paths through the Graph from all
                'starts' to all 'ends'.
            
        """
        all_permutations = []
        for start in more_itertools.always_iterable(starts):
            for end in more_itertools.always_iterable(ends):
                paths = self._find_all_paths(
                    start = start, 
                    end = end)
                if paths:
                    if all(isinstance(path, str) for path in paths):
                        all_permutations.append(paths)
                    else:
                        all_permutations.extend(paths)
        return all_permutations
