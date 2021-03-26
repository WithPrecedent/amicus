"""
amicus.project.core:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import collections.abc
import dataclasses
import inspect
import logging
import multiprocessing
import pathlib
from types import ModuleType
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)

import more_itertools

import amicus
from . import configuration
from . import nodes
from . import workshop


@dataclasses.dataclass
class Workflow(amicus.structures.Graph):
    """Creates, stores, and execustes a directed acyclic graph (DAG).
    
    Args:
        contents (Dict[Hashable, List[Hashable]]): an adjacency list where the 
            keys are names of nodes and the values are names of nodes which the 
            key is connected to. All nodes that are named in the keys and values
            should be stored in 'library.subclasses' or 'library.instances'. 
            Defaults to an empty dict.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.
        library (Library): catalogs of Component subclasses and instances
            that are used to execute a Workflow. Defaults to an empty library.
                  
    """  
    contents: Dict[Hashable, List[Hashable]] = dataclasses.field(
        default_factory = dict)
    default: Any = dataclasses.field(default_factory = list) 
    library: nodes.Library = dataclasses.field(default_factory = nodes.Library)
    
    """ Public Methods """
    
    @classmethod
    def create(cls, project: amicus.Project, **kwargs) -> Workflow:
        """Creates a Workflow instance from 'project'.
                
        Returns:
            Workflow: created from attributes of 'project' and/or any default
                options if the data for creation is not in 'project'.
                
        """
        return workshop.create_workflow(project = project, **kwargs)
    

@dataclasses.dataclass
class Result(amicus.types.Lexicon):            
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
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    default: Any = None
    name: str = None
    path: Sequence[str] = dataclasses.field(default_factory = list)
      
        
@dataclasses.dataclass
class Summary(amicus.types.Lexicon):
    """Collects and stores results of all paths through a Workflow.
    
    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
        default (Any): default value to return when the 'get' method is used.
        prefix (str): prefix to use when storing different paths through a 
            workflow. So, for example, a prefix of 'path' will create keys of
            'path_1', 'path_2', etc. Defaults to 'path'.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. Defaults to 
            a list with 'workflow' and 'data'.          
              
    """
    contents: Mapping[str, Result] = dataclasses.field(default_factory = dict)
    default: Any = Result()
    prefix: str = 'path'

    """ Public Methods """
    
    @classmethod
    def create(cls, project: amicus.Project, **kwargs) -> Summary:
        """Creates a Summary instance from 'project'.
                
        Returns:
            Summary: created from attributes of 'project' and/or any default
                options if the data for creation is not in 'project'.
                
        """
        return workshop.create_summary(project = project, **kwargs)
     