"""
amicus.project.core:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import abc
import copy
import dataclasses
import itertools
import multiprocessing
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)

import more_itertools

import amicus
from . import configuration
from . import workshop

     
@dataclasses.dataclass
class Workflow(amicus.structures.Graph):
    """Stores a workflow as an adjacency list.

    Args:
        contents (Dict[Hashable, List[Hashable]]): an adjacency list where the 
            keys are nodes and the values are nodes which the key is connected 
            to. Defaults to an empty dict.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.
                  
    """  
    contents: Dict[Hashable, List[Hashable]] = dataclasses.field(
        default_factory = dict)
    default: Any = dataclasses.field(default_factory = list)
    components: MutableMapping[str, object] = (
        amicus.project.configuration.bases.component.library)

    """ Public Class Methods """
        
    @classmethod
    def create(cls, project: amicus.Project, **kwargs) -> Workflow:
        """Creates a Workflow instance from 'project'.
                
        Returns:
            Workflow: created from attributes of 'project' and/or any default
                options if the data for creation is not in 'project'.
                
        """
        return workshop.create_workflow(project = project, **kwargs)

    """ Public Methods """

    def branchify(self, 
        nodes: Sequence[Sequence[Hashable]],
        start: Union[Hashable, Sequence[Hashable]] = None) -> None:
        """Adds parallel paths to the stored data structure.

        Subclasses should ordinarily provide their own methods.

        Args:
            nodes (Sequence[Sequence[Hashable]]): a list of list of nodes which
                should have a Cartesian product determined and extended to
                the stored data structure.
            start (Union[Hashable, Sequence[Hashable]]): where to add new node 
                to. If there are multiple nodes in 'start', 'node' will be added 
                to each of the starting points. If 'start' is None, 'endpoints'
                will be used. Defaults to None.
                
        """
        if start is None:
            start = copy.deepcopy(self.endpoints) 
        paths = list(map(list, itertools.product(*nodes))) 
        for path in paths:
            if start:
                for starting in more_itertools.always_iterable(start):
                    self.add_edge(start = starting, stop = path[0])
            elif path[0] not in self.contents:
                self.add_node(path[0])
            edges = more_itertools.windowed(path, 2)
            for edge_pair in edges:
                self.add_edge(start = edge_pair[0], stop = edge_pair[1]) 
        return self    
  
  
@dataclasses.dataclass
class Recipe(amicus.base.Lexicon):            
    """Stores results from a single path through a Workflow.

    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.  
        default (Any): default value to return when the 'get' method is used.
        name (str): name of particular path through a workflow for which 
            'contents' are associated.
        path (Sequence[str]): the names of the nodes through a workflow 
            corresponding to the results stored in 'contents'.
        
    """
    contents: Mapping[str, object] = dataclasses.field(default_factory = dict)
    default: Any = None
    name: str = None
    results: amicus.base.Lexicon[str, Any] = dataclasses.field(
        default_factory = amicus.base.Lexicon)
                    
    """ Properties """
    
    @property
    def components(self) -> Mapping[str, Any]:
        return self.contents
    
    @components.setter
    def components(self, value: Mapping[str, Any]) -> None:
        self.contents = value
        return self
    
    @components.deleter
    def components(self) -> None:
        self.contents = None
        return self
   
    """ Public Methods """
    
    @classmethod
    def create(cls, 
        path: Sequence[str], 
        components: amicus.base.Catalog,
        name: str = None) -> Recipe:
        """
                
        """
        if name is None:
            name = '_'.join(path)
        needed = [v for k, v in components.items() if k in path]
        contents = dict(zip(path, needed))
        return cls(contents = contents, name = name)
       
       
@dataclasses.dataclass
class Cookbook(amicus.base.Lexicon):
    """Stores a collection of Recipes.
    
    Args:
        contents (Mapping[Hashable, Recipe]]): stored dictionary. Defaults to an 
            empty dict.
        default (Any): default value to return when the 'get' method is used.
            Defaults to None.
              
    """
    contents: Mapping[Hashable, Recipe] = dataclasses.field(
        default_factory = dict)
    default: Any = Recipe

    """ Public Class Methods """
    
    @classmethod
    def create(cls, project: amicus.Project, **kwargs) -> Cookbook:
        """Creates a Cookbook instance from 'project'.
                
        Returns:
            Cookbook: created from attributes of 'project' and/or any default
                options if the data for creation is not in 'project'.
                
        """
        cookbook = cls(**kwargs)
        for i, path in enumerate(project.workflow.paths):
            name = f'{cls.prefix}_{str(i)}'
            recipe = Recipe.create(
                path = path, 
                components = project.workflow.components,
                name = name)
            cookbook[name] = recipe
        return cookbook
          
    """ Public Methods """
    
    def add(self, recipe: Recipe, prefix: str = None) -> None:
        """Adds a recipe to 'contents'.

        Args:
            recipe (Recipe): Recipe instance to store in the cookbook.
            prefix (str): prefix to use for the key in storing 'recipe'. If it
                is None, the snake case name of the class of 'recipe' will be
                used as the prefix. Defaults to None.

        """
        prefix = prefix or amicus.tools.snakify(recipe.__class__.__name__)
        key = f'{prefix}_{len(self.contents) + 1}'
        self.contents[key] = recipe
        return self
  
            
@dataclasses.dataclass
class Summary(amicus.base.Lexicon):
    """Collects and stores results of all paths through a Workflow.
    
    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
        default (Any): default value to return when the 'get' method is used.       
              
    """
    contents: Mapping[str, Recipe] = dataclasses.field(default_factory = dict)
    default: Any = Recipe()

    """ Public Class Methods """
     
    @classmethod
    def create(cls, project: amicus.Project, **kwargs) -> Summary:
        """Creates a Summary instance from 'project'.
                
        Returns:
            Summary: created from attributes of 'project' and/or any default
                options if the data for creation is not in 'project'.
                
        """
        return workshop.create_summary(project = project, **kwargs)
