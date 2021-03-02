"""
components:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Step
    Technique
    Worker
    Pipeline
    Contest
    Study
    Survey

"""
from __future__ import annotations
import abc
import copy
import dataclasses
import inspect
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, Optional, Sequence, Set, Tuple, Type, Union)

import more_itertools

import amicus
from . import core


@dataclasses.dataclass
class Leaf(core.Component, abc.ABC):
    """Base class for primitive leaf nodes in an amicus Workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Any): stored item(s) to be used by the 'implement' method.
        parameters (Union[Mapping[Hashable, Any], Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the Component 'instances' catalog.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. The first item
            in 'needs' to correspond to an internal factory classmethod named
            f'from_{first item in needs}'. Defaults to an empty list.   
    
    Attributes:
        library (ClassVar[amicus.framework.Library]): library that stores 
            direct subclasses (those with Keystone in their '__bases__' 
            attribute) and allows runtime access and instancing of those 
            stored subclasses.
        subclasses (ClassVar[amicus.types.Catalog]): catalog that stores 
            concrete subclasses and allows runtime access and instancing of 
            those stored subclasses. 'subclasses' is automatically created when 
            a direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced.
        instances (ClassVar[amicus.types.Catalog]): catalog that stores
            subclass instances and allows runtime access of those stored 
            subclass instances. 'instances' is automatically created when a 
            direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced. 
                                                               
    """
    name: str = None
    contents: Any = None
    parameters: Union[Mapping[Hashable, Any], core.Parameters] = (
        dataclasses.field(default_factory = dict))
    iterations: Union[int, str] = 1
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']
        
 
@dataclasses.dataclass
class Step(Leaf):
    """Wrapper for a Technique.

    Subclasses of Step can store additional methods and attributes to implement
    all possible technique instances that could be used. This is often useful 
    when creating branching, parallel workflows which test a variety of 
    strategies with similar or identical parameters and/or methods.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Technique): stored Technique instance to be used by the 
            'implement' method. Defaults to None.
        parameters (Union[Mapping[Hashable, Any], Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the Component 'instances' catalog.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. The first item
            in 'needs' to correspond to an internal factory classmethod named
            f'from_{first item in needs}'. Defaults to an empty list.   
    
    Attributes:
        library (ClassVar[amicus.framework.Library]): library that stores 
            direct subclasses (those with Keystone in their '__bases__' 
            attribute) and allows runtime access and instancing of those 
            stored subclasses.
        subclasses (ClassVar[amicus.types.Catalog]): catalog that stores 
            concrete subclasses and allows runtime access and instancing of 
            those stored subclasses. 'subclasses' is automatically created when 
            a direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced.
        instances (ClassVar[amicus.types.Catalog]): catalog that stores
            subclass instances and allows runtime access of those stored 
            subclass instances. 'instances' is automatically created when a 
            direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced. 
                                                               
    """
    name: str = None
    contents: Technique = None
    parameters: Union[Mapping[Hashable, Any], core.Parameters] = (
        dataclasses.field(default_factory = dict))
    iterations: Union[int, str] = 1
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']
                    
    """ Properties """
    
    @property
    def technique(self) -> Technique:
        return self.contents
    
    @technique.setter
    def technique(self, value: Technique) -> None:
        self.contents = value
        return self
    
    @technique.deleter
    def technique(self) -> None:
        self.contents = None
        return self
    
    """ Public Methods """
    
    def implement(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """Applies 'contents' to 'project'.

        Args:
            project (amicus.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            amicus.Project: with possible changes made.
            
        """
        project = self.contents.execute(project = project, **kwargs)
        return project 
                          
                          
@dataclasses.dataclass
class Technique(core.Component):
    """Keystone class for primitive objects in an amicus composite object.
    
    The 'contents' and 'parameters' attributes are combined at the last moment
    to allow for runtime alterations.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Callable): stored callable algorithm to be used by the 
            'implement' method. Defaults to None.
        parameters (Union[Mapping[Hashable, Any], Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the Component 'instances' catalog.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. The first item
            in 'needs' to correspond to an internal factory classmethod named
            f'from_{first item in needs}'. Defaults to an empty list.   
    
    Attributes:
        library (ClassVar[amicus.framework.Library]): library that stores 
            direct subclasses (those with Keystone in their '__bases__' 
            attribute) and allows runtime access and instancing of those 
            stored subclasses.
        subclasses (ClassVar[amicus.types.Catalog]): catalog that stores 
            concrete subclasses and allows runtime access and instancing of 
            those stored subclasses. 'subclasses' is automatically created when 
            a direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced.
        instances (ClassVar[amicus.types.Catalog]): catalog that stores
            subclass instances and allows runtime access of those stored 
            subclass instances. 'instances' is automatically created when a 
            direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced. 
                                                               
    """
    name: str = None
    contents: Callable = None
    parameters: Union[Mapping[Hashable, Any], core.Parameters] = (
        dataclasses.field(default_factory = dict))
    iterations: Union[int, str] = 1
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']
        
    """ Properties """
    
    @property
    def algorithm(self) -> Union[object, str]:
        return self.contents
    
    @algorithm.setter
    def algorithm(self, value: Union[object, str]) -> None:
        self.contents = value
        return self
    
    @algorithm.deleter
    def algorithm(self) -> None:
        self.contents = None
        return self
    
    """ Public Methods """
    
    def implement(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """Applies 'contents' to 'project'.

        Generally, subclasses should provide their own methods. This is simply
        a basic template that is compatible with some specific amicus 
        algorithms.
        
        Args:
            project (amicus.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            amicus.Project: with possible changes made.
            
        """
        project = self.contents(project = project, **kwargs)
        return project 

                 
@dataclasses.dataclass
class Worker(amicus.structures.Graph, core.Component):
    """Keystone class for parts of an amicus workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Dict[core.Component, List[str]]): an adjacency list where the 
            keys are Component instances and the values are the names of nodes 
            which the key is connected to. Defaults to an empty dict.
        parameters (Union[Mapping[Hashable, Any], Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the Component 'instances' catalog.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. The first item
            in 'needs' to correspond to an internal factory classmethod named
            f'from_{first item in needs}'. Defaults to an empty list.   
    
    Attributes:
        library (ClassVar[amicus.framework.Library]): library that stores 
            direct subclasses (those with Keystone in their '__bases__' 
            attribute) and allows runtime access and instancing of those 
            stored subclasses.
        subclasses (ClassVar[amicus.types.Catalog]): catalog that stores 
            concrete subclasses and allows runtime access and instancing of 
            those stored subclasses. 'subclasses' is automatically created when 
            a direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced.
        instances (ClassVar[amicus.types.Catalog]): catalog that stores
            subclass instances and allows runtime access of those stored 
            subclass instances. 'instances' is automatically created when a 
            direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced. 
                                            
    """
    name: str = None
    contents: Dict[core.Component, List[str]] = dataclasses.field(
        default_factory = dict)
    parameters: Union[Mapping[Hashable, Any], core.Parameters] = (
        dataclasses.field(default_factory = dict))
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']

    """ Public Methods """
    
    @abc.abstractmethod
    def organize(self, outline: core.Outline) -> None:
        """[summary]

        Subclasses must provide their own methods.
        Args:
            outline (core.Outline): [description]

        Returns:
            [type]: [description]
            
        """   
        return self   
    
    """ Dunder Methods """
    
    def __str__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        new_line = '\n'
        representation = [f'{new_line}amicus {self.__class__.__name__}']
        representation.append('adjacency list:')
        for node, edges in self.contents.items():
            representation.append(f'    {node.name}: {str(edges)}')
        return new_line.join(representation) 
  

@dataclasses.dataclass
class Process(amicus.structures.Pipeline, Worker):
    """A Worker with a serial Workflow.
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Any): stored item(s) to be used by the 'implement' method.
        parameters (Union[Mapping[Hashable, Any], Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the Component 'instances' catalog.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. The first item
            in 'needs' to correspond to an internal factory classmethod named
            f'from_{first item in needs}'. Defaults to an empty list.   
    
    Attributes:
        library (ClassVar[amicus.framework.Library]): library that stores 
            direct subclasses (those with Keystone in their '__bases__' 
            attribute) and allows runtime access and instancing of those 
            stored subclasses.
        subclasses (ClassVar[amicus.types.Catalog]): catalog that stores 
            concrete subclasses and allows runtime access and instancing of 
            those stored subclasses. 'subclasses' is automatically created when 
            a direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced.
        instances (ClassVar[amicus.types.Catalog]): catalog that stores
            subclass instances and allows runtime access of those stored 
            subclass instances. 'instances' is automatically created when a 
            direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced. 
                                       
    """
    name: str = None
    contents: Any = None
    parameters: Union[Mapping[Hashable, Any], core.Parameters] = (
        dataclasses.field(default_factory = dict))
    iterations: Union[int, str] = 1
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['outline', 'name']
  
    """ Public Methods """
    
    def organize(self, outline: core.Outline) -> None:
        """[summary]

        Args:
            outline (core.Outline): [description]

        Returns:
            [type]: [description]
            
        """   
        directive = outline[self.name]             
        components = self._serial_order(name = self.name, directive = directive)
        collapsed = list(more_itertools.collapse(components))
        nodes = []
        for node in collapsed:
            nodes.append(self.from_name(name = [node, directive.designs[node]]))
        self.extend(nodes = nodes)
        return self      
                 
    """ Private Methods """
    
    def _serial_order(self, name: str, directive: Directive) -> List:
        """

        Args:
            name (str):
            details (Blueprint): [description]

        Returns:
            List[List[str]]: [description]
            
        """
        organized = []
        components = directive.edges[name]
        for item in components:
            organized.append(item)
            if item in directive.edges:
                organized_subcomponents = []
                subcomponents = self._serial_order(
                    name = item, 
                    directive = directive)
                organized_subcomponents.append(subcomponents)
                if len(organized_subcomponents) == 1:
                    organized.append(organized_subcomponents[0])
                else:
                    organized.append(organized_subcomponents)
        return organized    
        

@dataclasses.dataclass
class Nexus(Worker, abc.ABC):
    """Base class for branching and parallel Workers.
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Dict[core.Component, List[str]]): an adjacency list where the 
            keys are Component instances and the values are string names of 
            Components which the key is connected to. Defaults to an empty dict.
        parameters (Union[Mapping[Hashable, Any], Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the Component 'instances' catalog.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. The first item
            in 'needs' to correspond to an internal factory classmethod named
            f'from_{first item in needs}'. Defaults to an empty list.    
    
    Attributes:
        library (ClassVar[amicus.framework.Library]): library that stores 
            direct subclasses (those with Keystone in their '__bases__' 
            attribute) and allows runtime access and instancing of those 
            stored subclasses.
        subclasses (ClassVar[amicus.types.Catalog]): catalog that stores 
            concrete subclasses and allows runtime access and instancing of 
            those stored subclasses. 'subclasses' is automatically created when 
            a direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced.
        instances (ClassVar[amicus.types.Catalog]): catalog that stores
            subclass instances and allows runtime access of those stored 
            subclass instances. 'instances' is automatically created when a 
            direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced. 
                                        
    """
    name: str = None
    contents: Dict[core.Component, List[str]] = dataclasses.field(
        default_factory = dict)
    parameters: Union[Mapping[Hashable, Any], core.Parameters] = (
        dataclasses.field(default_factory = dict))
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']
    
    """ Public Methods """
    
    def organize(self, outline: core.Outline) -> None:
        """[summary]

        Args:
            outline (core.Outline): [description]

        Returns:
            [type]: [description]
            
        """   
        directive = outline[self.name]
        step_names = directive.edges[directive.name]
        possible = [directive.edges[step] for step in step_names]
        nodes = []
        for i, step_options in enumerate(possible):
            permutation = []
            for option in step_options:
                t_keys = [option, directive.designs[option]]
                technique = self.library.component.from_name(
                    name = t_keys,
                    container = step_names[i])
                s_keys = [step_names[i], directive.designs[step_names[i]]]    
                step = self.library.component.select(name = s_keys)
                step = step(name = option, contents = technique)
                permutation.append(step)
            nodes.append(permutation)
        self.branchify(nodes = nodes)
        return self


@dataclasses.dataclass
class Contest(Nexus):
    """Resolves a parallel workflow by selecting the best option.

    It resolves a parallel workflow based upon criteria in 'contents'
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Dict[core.Component, List[str]]): an adjacency list where the 
            keys are Component instances and the values are string names of 
            Components which the key is connected to. Defaults to an empty dict.
        parameters (Union[Mapping[Hashable, Any], Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the Component 'instances' catalog.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. The first item
            in 'needs' to correspond to an internal factory classmethod named
            f'from_{first item in needs}'. Defaults to an empty list.    
    
    Attributes:
        library (ClassVar[amicus.framework.Library]): library that stores 
            direct subclasses (those with Keystone in their '__bases__' 
            attribute) and allows runtime access and instancing of those 
            stored subclasses.
        subclasses (ClassVar[amicus.types.Catalog]): catalog that stores 
            concrete subclasses and allows runtime access and instancing of 
            those stored subclasses. 'subclasses' is automatically created when 
            a direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced.
        instances (ClassVar[amicus.types.Catalog]): catalog that stores
            subclass instances and allows runtime access of those stored 
            subclass instances. 'instances' is automatically created when a 
            direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced. 
                                        
    """
    name: str = None
    contents: Dict[core.Component, List[str]] = dataclasses.field(
        default_factory = dict)
    parameters: Union[Mapping[Hashable, Any], core.Parameters] = (
        dataclasses.field(default_factory = dict))
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']

    
@dataclasses.dataclass
class Study(Nexus):
    """Allows parallel workflow to continue

    A Study might be wholly passive or implement some reporting or alterations
    to all parallel workflows.
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Dict[core.Component, List[str]]): an adjacency list where the 
            keys are Component instances and the values are string names of 
            Components which the key is connected to. Defaults to an empty dict.
        parameters (Union[Mapping[Hashable, Any], Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the Component 'instances' catalog.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. The first item
            in 'needs' to correspond to an internal factory classmethod named
            f'from_{first item in needs}'. Defaults to an empty list.    
    
    Attributes:
        library (ClassVar[amicus.framework.Library]): library that stores 
            direct subclasses (those with Keystone in their '__bases__' 
            attribute) and allows runtime access and instancing of those 
            stored subclasses.
        subclasses (ClassVar[amicus.types.Catalog]): catalog that stores 
            concrete subclasses and allows runtime access and instancing of 
            those stored subclasses. 'subclasses' is automatically created when 
            a direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced.
        instances (ClassVar[amicus.types.Catalog]): catalog that stores
            subclass instances and allows runtime access of those stored 
            subclass instances. 'instances' is automatically created when a 
            direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced. 
                                         
    """
    name: str = None
    contents: Dict[core.Component, List[str]] = dataclasses.field(
        default_factory = dict)
    parameters: Union[Mapping[Hashable, Any], core.Parameters] = (
        dataclasses.field(default_factory = dict))
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']
 
    
@dataclasses.dataclass
class Survey(Nexus):
    """Resolves a parallel workflow by averaging.

    It resolves a parallel workflow based upon the averaging criteria in 
    'contents'
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Dict[core.Component, List[str]]): an adjacency list where the 
            keys are Component instances and the values are string names of 
            Components which the key is connected to. Defaults to an empty dict.
        parameters (Union[Mapping[Hashable, Any], Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the Component 'instances' catalog.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. The first item
            in 'needs' to correspond to an internal factory classmethod named
            f'from_{first item in needs}'. Defaults to an empty list.    
    
    Attributes:
        library (ClassVar[amicus.framework.Library]): library that stores 
            direct subclasses (those with Keystone in their '__bases__' 
            attribute) and allows runtime access and instancing of those 
            stored subclasses.
        subclasses (ClassVar[amicus.types.Catalog]): catalog that stores 
            concrete subclasses and allows runtime access and instancing of 
            those stored subclasses. 'subclasses' is automatically created when 
            a direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced.
        instances (ClassVar[amicus.types.Catalog]): catalog that stores
            subclass instances and allows runtime access of those stored 
            subclass instances. 'instances' is automatically created when a 
            direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced. 
                                          
    """
    name: str = None
    contents: Dict[core.Component, List[str]] = dataclasses.field(
        default_factory = dict)
    parameters: Union[Mapping[Hashable, Any], core.Parameters] = (
        dataclasses.field(default_factory = dict))
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']
    