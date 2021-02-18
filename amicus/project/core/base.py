"""
base: core classes for a amicus data science project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    SimpleSettings (amicus.project.Settings):
    SimpleFiler (amicus.project.Filer):
    SimpleManager (amicus.project.Manager):
    SimpleComponent (amicus.project.Component):
    SimpleAlgorithm
    SimpleCriteria
    
"""
from __future__ import annotations
import abc
import copy
import dataclasses
import inspect
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import more_itertools
import amicus


@dataclasses.dataclass
class Component(amicus.quirks.Keystone, amicus.quirks.Element, abc.ABC):
    """Base class for parts of a amicus Workflow.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if a amicus 
            instance needs options from a Settings instance, 'name' should match 
            the appropriate section name in a Settings instance. Defaults to 
            None. 
                
    Attributes:
        keystones (ClassVar[amicus.types.Library]): library that stores amicus base 
            classes and allows runtime access and instancing of those stored 
            subclasses.
        subclasses (ClassVar[amicus.types.Catalog]): library that stores 
            concrete subclasses and allows runtime access and instancing of 
            those stored subclasses. 
        instances (ClassVar[amicus.types.Catalog]): library that stores
            subclass instances and allows runtime access of those stored 
            subclass instances.
                
    """
    name: str = None

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def execute(self, project: amicus.Project, 
                **kwargs) -> amicus.Project:
        """[summary]
        Args:
            project (amicus.Project): [description]
        Returns:
            amicus.Project: [description]
            
        """ 
        return project

    @abc.abstractmethod
    def implement(self, project: amicus.Project, 
                  **kwargs) -> amicus.Project:
        """[summary]
        Args:
            project (amicus.Project): [description]
        Returns:
            amicus.Project: [description]
            
        """  
        return project
        
    """ Public Class Methods """
    
    @classmethod
    def create(cls, name: Union[str, Sequence[str]], **kwargs) -> Component:
        """[summary]
        Args:
            name (Union[str, Sequence[str]]): [description]
        Raises:
            KeyError: [description]
        Returns:
            Component: [description]
            
        """        
        keys = more_itertools.always_iterable(name)
        for key in keys:
            for library in ['instances', 'subclasses']:
                item = None
                try:
                    item = getattr(cls, library)[key]
                    break
                except KeyError:
                    pass
            if item is not None:
                break
        if item is None:
            raise KeyError(f'No matching item for {str(name)} was found') 
        elif inspect.isclass(item):
            return cls(name = name, **kwargs)
        else:
            instance = copy.deepcopy(item)
            for key, value in kwargs.items():
                setattr(instance, key, value)
            return instance


@dataclasses.dataclass
class Stage(amicus.quirks.Keystone, amicus.quirks.Needy, abc.ABC):
    """Creates a amicus object.
    
    Args:
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. Defaults to an
            empty list.     
                
    Attributes:
        keystones (ClassVar[amicus.types.Library]): library that stores amicus base 
            classes and allows runtime access and instancing of those stored 
            subclasses.
        subclasses (ClassVar[amicus.types.Catalog]): library that stores 
            concrete subclasses and allows runtime access and instancing of 
            those stored subclasses. 
        instances (ClassVar[amicus.types.Catalog]): library that stores
            subclass instances and allows runtime access of those stored 
            subclass instances.
                       
    """
    needs: ClassVar[Union[Sequence[str], str]] = []
