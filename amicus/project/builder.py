"""
amicus.project.builder:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""
from __future__ import annotations
import copy
import dataclasses
import functools
import inspect
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, Optional, Sequence, Set, Tuple, Type, Union)

import more_itertools

import amicus
from . import draft
from . import nodes
from . import execute


DIRECTIVE: Type = draft.Directive
OUTLINE: Type = draft.Outline
COMPONENT: Type = nodes.Component
RESULT: Type = execute.Result
SUMMARY: Type = execute.Summary


@dataclasses.dataclass
class Workshop(amicus.quirks.Needy, amicus.framework.Keystone):
    """Builds amicus project objects
    
    """
    """ Public Methods """


@dataclasses.dataclass
class Draft(Workshop):
    """Builds an Outlines and Directives.
    
    """
    needs: ClassVar[Sequence[str]] = ['settings', 'name']
    
    
    
    
    
    
@dataclasses.dataclass
class Publish(Workshop):
    """Builds Components.
    
    """
    needs: ClassVar[Sequence[str]] = ['outline', 'name']
    
    """ Public Methods """

    def create(self, 
        name: Union[str, Sequence[str]] = None,
        directive: draft.Directive = None,
        outline: draft.Outline = None,
        **kwargs) -> nodes.Component:
        """[summary]

        Args:
            outline (draft.Outline): [description]
            directive (draft.Directive): [description]
            name (str): [description]

        Returns:
            nodes.Component: [description]
            
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

    def from_name(self, 
        name: Union[str, Sequence[str]], 
        **kwargs) -> nodes.Component:
        """Returns instance of first match of 'name' in stored catalogs.
        
        The method prioritizes the 'instances' catalog over 'subclasses' and any
        passed names in the order they are listed.
        
        Args:
            name (Union[str, Sequence[str]]): [description]
            
        Raises:
            KeyError: [description]
            
        Returns:
            nodes.Component: [description]
            
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
            return amicus.tools.listify(name)
        elif directive is not None:
            return amicus.tools.listify(directive.name)
        else:
            return amicus.tools.listify(outline.name)
        
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
        component: nodes.Component,
        directive: draft.Directive,
        outline: draft.Outline) -> nodes.Component:
        """[summary]

        Args:
            component (Component): [description]
            directive (draft.Directive): [description]
            outline (draft.Outline): [description]

        Returns:
            nodes.Component: [description]
            
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
        component: nodes.Component,
        directive: draft.Directive,
        outline: draft.Outline) -> nodes.Component:
        """[summary]

        Args:
            component (Component): [description]
            directive (draft.Directive): [description]
            outline (draft.Outline): [description]

        Returns:
            nodes.Component: [description]
            
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
    
    def _serial_order(self, 
        name: str, 
        directive: draft.Directive) -> List[Hashable]:
        """[summary]

        Args:
            name (str): [description]
            directive (draft.Directive): [description]

        Returns:
            List[Hashable]: [description]
            
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
class Execute(Workshop):
    """Builds an Outlines and Directives.
    
    """
    needs: ClassVar[Sequence[str]] = ['workflow', 'outline', 'data']
    
    

