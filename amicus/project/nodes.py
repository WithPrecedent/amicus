"""
amicus.project.nodes:
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
import multiprocessing
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, Optional, Sequence, Set, Tuple, Type, Union)

import more_itertools

import amicus
from . import core


@dataclasses.dataclass
class Workshop(object):
    """Builds Component instances.
    
    """
    base: Type[core.Component] = core.Component
    
    """ Public Methods """

    def create(self, 
        name: str = None, 
        directive: draft.Directive = None,
        outline: draft.Outline = None,
        **kwargs) -> core.Component:
        """[summary]

        Args:
            outline (draft.Outline): [description]
            directive (draft.Directive): [description]
            name (str): [description]

        Returns:
            core.Component: [description]
            
        """
        if name is None and directive is None and outline is None:
            raise ValueError(
                'create needs either a name, directive, or outline argument')
        else:
            name = self._get_name(
                name = name, 
                directive = directive, 
                outline = outline)
            directive = self._get_directive(
                name = name, 
                directive = directive, 
                outline = outline)
            outline = self._get_outline(
                name = name, 
                directive = directive, 
                outline = outline)
        if directive is None:
            component = self.from_name(name = name, **kwargs)
        else:  
            if name == directive.name:
                parameters = directive.initialization
            else:
                parameters = {}   
            parameters.update({'parameters': directive.implementation[name]}) 
            parameters.update(kwargs)
            lookups = [name]
            try:
                lookups.append(directive.designs[name])   
            except KeyError:
                pass
            component = self.from_name(name = lookups, **parameters)  
            if isinstance(component, Iterable):
                if hasattr(component, 'criteria'):
                    method = self._organize_parallel
                else:
                    method = self._organize_serial
                component = method(
                    component = component,
                    directive = directive,
                    outline = outline)
        return component

    def from_name(self, name: Union[str, Sequence[str]], **kwargs) -> core.Component:
        """Returns instance of first match of 'name' in stored catalogs.
        
        The method prioritizes the 'instances' catalog over 'subclasses' and any
        passed names in the order they are listed.
        
        Args:
            name (Union[str, Sequence[str]]): [description]
            
        Raises:
            KeyError: [description]
            
        Returns:
            core.Component: [description]
            
        """
        names = amicus.tools.listify(name)
        primary = names[0]
        item = None
        for key in names:
            for catalog in ['instances', 'subclasses']:
                try:
                    item = getattr(self.base, catalog)[key]
                    break
                except KeyError:
                    pass
            if item is not None:
                break
        if item is None:
            raise KeyError(f'No matching item for {str(name)} was found') 
        elif inspect.isclass(item):
            instance = item(name = primary, **kwargs)
        else:
            instance = copy.deepcopy(item)
            for key, value in kwargs.items():
                setattr(instance, key, value)  
        return instance  
    
    def from_outline(self, 
        name: str = None, 
        directive: draft.Directive = None,
        outline: draft.Outline = None,
        **kwargs) -> core.Component:
        """[summary]

        Args:
            outline (draft.Outline): [description]
            directive (draft.Directive): [description]
            name (str): [description]

        Returns:
            core.Component: [description]
            
        """
        if name is None and directive is None and outline is None:
            raise ValueError(
                'create needs either a name, directive, or outline argument')
        else:
            name = self._get_name(
                name = name, 
                directive = directive, 
                outline = outline)
            directive = self._get_directive(
                name = name, 
                directive = directive, 
                outline = outline)
            outline = self._get_outline(
                name = name, 
                directive = directive, 
                outline = outline)
        if directive is None:
            component = self.from_name(name = name, **kwargs)
        else:  
            if name == directive.name:
                parameters = directive.initialization
            else:
                parameters = {}   
            parameters.update({'parameters': directive.implementation[name]}) 
            parameters.update(kwargs)
            lookups = [name]
            try:
                lookups.append(directive.designs[name])   
            except KeyError:
                pass
            component = self.from_name(name = lookups, **parameters)  
            if isinstance(component, Iterable):
                if hasattr(component, 'criteria'):
                    method = self._organize_parallel
                else:
                    method = self._organize_serial
                component = method(
                    component = component,
                    directive = directive,
                    outline = outline)
        return component
    
    """ Private Methods """
    
    def _get_name(self, 
        name: str, 
        directive: draft.Directive,
        outline: draft.Outline) -> str:
        """[summary]

        Args:
            outline (draft.Outline): [description]
            name (str): [description]
            directive (draft.Directive): [description]

        Returns:
            str: [description]
            
        """
        if name is not None:
            return name
        elif directive is not None:
            return directive.name
        else:
            return outline.name
        
    def _get_directive(self, 
        name: str, 
        directive: draft.Directive,
        outline: draft.Outline) -> draft.Directive:
        """[summary]

        Args:
            outline (draft.Outline): [description]
            name (str): [description]
            directive (draft.Directive): [description]

        Returns:
            draft.Directive: [description]
            
        """
        if directive is not None:
            return directive
        elif name is not None and outline is not None:
            try:
                return outline[name]
            except KeyError:
                return None
        else:
            try:
                return outline[outline.name]   
            except KeyError:
                return None

    def _get_outline(self, 
        name: str, 
        directive: draft.Directive,
        outline: draft.Outline) -> draft.Outline:
        """[summary]

        Args:
            outline (draft.Outline): [description]
            name (str): [description]
            directive (draft.Directive): [description]

        Returns:
            draft.Outline: [description]
            
        """
        if outline is not None:
            return directive
        elif name is not None and directive is not None:
            return draft.Outline(name = name, contents = {name: directive}) 
        else:
            return None
                                   
    def _organize_serial(self, 
        component: core.Component,
        directive: core.Directive,
        outline: core.Outline) -> core.Component:
        """[summary]

        Args:
            component (core.Component): [description]
            directive (core.Directive): [description]
            outline (core.Outline): [description]

        Returns:
            core.Component: [description]
            
        """     
        subcomponents = self._serial_order(
            name = component.name, 
            directive = directive)
        collapsed = list(more_itertools.collapse(subcomponents))
        nodes = []
        for node in collapsed:
            subnode = self.create(
                name = [node, directive.designs[node]],
                directive = directive,
                outline = outline)
            nodes.append(subnode)
        component.extend(nodes = nodes)
        return component      

    def _organize_parallel(self, 
        component: core.Component,
        directive: core.Directive,
        outline: core.Outline) -> core.Component:
        """[summary]

        Args:
            component (core.Component): [description]
            directive (core.Directive): [description]
            outline (core.Outline): [description]

        Returns:
            core.Component: [description]
            
        """ 
        step_names = directive.edges[directive.name]
        possible = [directive.edges[step] for step in step_names]
        nodes = []
        for i, step_options in enumerate(possible):
            permutation = []
            for option in step_options:
                t_keys = [option, directive.designs[option]]
                technique = self.create(
                    name = t_keys,
                    directive = directive,
                    outline = outline,
                    suffix = step_names[i])
                s_keys = [step_names[i], directive.designs[step_names[i]]]    
                step = self.create(
                    name = s_keys,
                    directive = directive,
                    outline = outline,
                    contents = technique)
                step.name = option
                permutation.append(step)
            nodes.append(permutation)
        component.branchify(nodes = nodes)
        return component
    
    def _serial_order(self, name: str, directive: core.Directive) -> List:
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
class Leaf(core.Component, abc.ABC):
    """Base class for primitive leaf nodes in an amicus Workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Any): stored item(s) to be used by the 'implement' method.
        parameters (Union[Mapping[Hashable, Any], core.Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large core.Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the core.Component 'instances' catalog.
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
    parameters: Union[Mapping[Hashable, Any], core.Parameters] = core.Parameters()
    iterations: Union[int, str] = 1
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']
    
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
class Step(amicus.types.Proxy, Leaf):
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
        parameters (Union[Mapping[Hashable, Any], core.Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large core.Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the core.Component 'instances' catalog.
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
    parameters: Union[Mapping[Hashable, Any], core.Parameters] = core.Parameters()
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

                                                  
@dataclasses.dataclass
class Technique(Leaf):
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
        parameters (Union[Mapping[Hashable, Any], core.Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large core.Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the core.Component 'instances' catalog.
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
    parameters: Union[Mapping[Hashable, Any], core.Parameters] = core.Parameters()
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
            keys are core.Component instances and the values are the names of nodes 
            which the key is connected to. Defaults to an empty dict.
        parameters (Union[Mapping[Hashable, Any], core.Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large core.Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the core.Component 'instances' catalog.
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
    parameters: Union[Mapping[Hashable, Any], core.Parameters] = core.Parameters()
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']

    """ Private Methods """
    
    def _implement_in_serial(self, 
        project: amicus.Project, 
        **kwargs) -> amicus.Project:
        """Applies stored nodes to 'project' in order.

        Args:
            project (Project): amicus project to apply changes to and/or
                gather needed data from.
                
        Returns:
            Project: with possible alterations made.       
        
        """
        for node in self.paths[0]:
            project = node.execute(project = project, **kwargs)
        return project
    
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
class Process(Worker):
    """A Worker with a serial Workflow.
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Any): stored item(s) to be used by the 'implement' method.
        parameters (Union[Mapping[Hashable, Any], core.Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large core.Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the core.Component 'instances' catalog.
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
    parameters: Union[Mapping[Hashable, Any], core.Parameters] = core.Parameters()
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['outline', 'name']
  
    """ Public Methods """  

    def implement(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """Applies 'contents' to 'project'.
        
        Args:
            project (amicus.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            amicus.Project: with possible changes made.
            
        """
        return self._implement_in_serial(project = project, **kwargs)    
    

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
            keys are core.Component instances and the values are string names of 
            Components which the key is connected to. Defaults to an empty dict.
        parameters (Union[Mapping[Hashable, Any], core.Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large core.Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the core.Component 'instances' catalog.
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
    parameters: Union[Mapping[Hashable, Any], core.Parameters] = core.Parameters()
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']
    
    def implement(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """Applies 'contents' to 'project'.
        
        Args:
            project (amicus.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            amicus.Project: with possible changes made.
            
        """
        if len(self.contents) > 1 and project.parallelize:
            project = self._implement_in_parallel(project = project, **kwargs)
        else:
            project = self._implement_in_serial(project = project, **kwargs)
        return project      

    """ Private Methods """
   
    def _implement_in_parallel(self, 
        project: amicus.Project, 
        **kwargs) -> amicus.Project:
        """Applies 'implementation' to 'project' using multiple cores.

        Args:
            project (Project): amicus project to apply changes to and/or
                gather needed data from.
                
        Returns:
            Project: with possible alterations made.       
        
        """
        if project.parallelize:
            with multiprocessing.Pool() as pool:
                project = pool.starmap(
                    self._implement_in_serial, 
                    project, 
                    **kwargs)
        return project 


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
            keys are core.Component instances and the values are string names of 
            Components which the key is connected to. Defaults to an empty dict.
        parameters (Union[Mapping[Hashable, Any], core.Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large core.Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the core.Component 'instances' catalog.
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
    parameters: Union[Mapping[Hashable, Any], core.Parameters] = core.Parameters()
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
            keys are core.Component instances and the values are string names of 
            core.Components which the key is connected to. Defaults to an empty dict.
        parameters (Union[Mapping[Hashable, Any], core.Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large core.Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the core.Component 'instances' catalog.
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
    parameters: Union[Mapping[Hashable, Any], core.Parameters] = core.Parameters()
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
            keys are core.Component instances and the values are string names of 
            core.Components which the key is connected to. Defaults to an empty dict.
        parameters (Union[Mapping[Hashable, Any], core.Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large core.Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the core.Component 'instances' catalog.
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
    parameters: Union[Mapping[Hashable, Any], core.Parameters] = core.Parameters()
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']
    