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
import inspect
import multiprocessing
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)

import more_itertools

import amicus
from . import configuration
from . import workshop



 
@dataclasses.dataclass
class Cookbook(amicus.types.Lexicon):
    """Stores a xollection of Recipes.
    
    Args:
        contents (Mapping[Hashable, Recipe]]): stored dictionary. Defaults to an 
            empty dict.
        default (Any): default value to return when the 'get' method is used.
            Defaults to None.
              
    """
    contents: Mapping[Hashable, Recipe] = dataclasses.field(
        default_factory = dict)
    default: Any = None

    """ Public Methods """
    
    @classmethod
    def create(cls, project: amicus.Project, **kwargs) -> Workflow:
        """Creates a Workflow instance from 'project'.
                
        Returns:
            Cookbook: created from attributes of 'project' and/or any default
                options if the data for creation is not in 'project'.
                
        """
        return workshop.create_cookbook(project = project, **kwargs)  


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

    """ Public Methods """
    
    @classmethod
    def create(cls, project: amicus.Project, **kwargs) -> Summary:
        """Creates a Result instance from 'workflow' and 'path'.
                
        Returns:
            Summary: created from attributes of 'project' and/or any default
                options if the data for creation is not in 'project'.
                
        """
        return workshop.create_result(project = project, **kwargs)
         
        
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
     