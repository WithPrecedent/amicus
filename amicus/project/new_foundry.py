"""
amicus.project.foundry:
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
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)

import more_itertools

import amicus
from . import core
from . import nodes


@dataclasses.dataclass
class Workshop(amicus.framework.Keystone, abc.ABC):
    """Builds amicus project objects
    
    """
    """ Public Methods """

    product: ClassVar[str] = None
    action: ClassVar[str] = None   

    """ Public Methods """
    
    @abc.abstractmethod
    def create(self, project: amicus.Project, **kwargs) -> object:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            object
            
        """
        pass

@dataclasses.dataclass
class Essentials(object):
    """Essential characteristics needed for Component construction.
    
    """
    name: str = None
    design: str = None
    base: str = None
    edges: List[str] = None
    initialization: Dict[str, Any] = dataclasses.field(default_factory = dict)
    implementation: Dict[str, Any] = dataclasses.field(default_factory = dict)
    

@dataclasses.dataclass
class Draft(Workshop):
    """Builds Outlines and Directives from Settings.
    
    """
    product: ClassVar[str] = 'workflow'
    action: ClassVar[str] = 'Drafting'
    hierarchy: ClassVar[Dict[str, core.Component]] = {
        'nexus': core.Nexus,
        'recipe': core.Recipe,
        'step': core.Step,
        'technique': core.Technique}
    
    """ Public Methods """

    def create(self, project: amicus.Project, **kwargs) -> nodes.Worker:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            nodes.Worker
            
        """
        settings = project.settings
        name = project.name
        design = self._get_design(name = name, settings = settings)
        return self.create_worker(
            name = name, 
            design = design, 
            settings = settings)
        
    def create_worker(self, 
        name: str,
        design: str,
        settings: amicus.options.Settings, 
        **kwargs) -> nodes.Worker:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            object
            
        """

        workflow = self.create_workflow(
            name = name, 
            settings = settings)
        worker = self.create_component(
            name = [name, design],
            settings = settings,
            contents = workflow.contents,
            **kwargs)
        return worker

    def create_essentials(self,
        name: str, 
        settings: amicus.options.Settings,
        heading: str = None) -> Essentials:
        """[summary]

        Args:
            name (str): [description]
            settings (amicus.options.Settings): [description]
            heading (str, optional): [description]. Defaults to None.

        Returns:
            Essentials: [description]
            
        """
        if heading is None:
            heading = name
        design = self._get_design(name = name, settings = settings)
        base = self._get_base(component = [name, design])
        edges = self._get_subcomponents(
            name = name,
            section = settings[heading],
            heading = heading)
        initialization = self._get_initialization(
            name = name,
            design = design,
            section = settings[heading],
            heading = heading)
        implementation = self._get_implementation(
            name = name,
            design = design,
            base = base,
            settings = settings)
        return Essentials(
            name = name,
            design = design,
            base = base,
            edges = edges,
            initialization = initialization,
            implementation = implementation)
        
    def create_workflow(self,
        name: str, 
        settings: amicus.options.Settings) -> amicus.structures.Graph:
        """[summary]

        Args:
            name (str): [description]
            settings (amicus.options.Settings): [description]

        Returns:
            amicus.structures.Graph: [description]
            
        """
        workflow = amicus.structues.Graph()
        section = settings[name]
        top_level = self._get_subcomponents(
            name = name,
            section = section,
            heading = name)
        top_design = self._get_design(name = name, settings = settings)
        top_base = self._get_base(component = [name, top_design])
        lower_level = {}
        for node in top_level.keys():
            lower_level = self._get_subcomponents(
                name = node,
                section = section,
                heading = name)
            if node in settings:
                lower_design = self._get_design(
                    name = node, 
                    settings = settings)
            else:
                lower_design = top_level[node]
            lower_base = self._get_base(name = node, settings = settings)
        return workflow
        
    """ Private Methods """

    def _get_design(self, name: str, settings: amicus.options.Settings) -> str:
        """Gets name of a Component design.

        Args:
            name (str): name of the Component.
            settings (amicus.options.Settings): Settings instance that contains
                either the design corresponding to 'name' or a default design.

        Raises:
            KeyError: if there is neither a design matching 'name' nor a default
                design.

        Returns:
            str: the name of the design.
            
        """
        try:
            design = settings[name][f'{name}_design']
        except KeyError:
            try:
                design = settings[name][f'design']
            except KeyError:
                try:
                    design = settings['amicus']['default_design']
                except KeyError:
                    raise KeyError(f'To designate a design, a key in settings '
                                    f'must either be named "design" or '
                                    f'"{name}_design"')
        return design    
  
    def _get_base(self, 
        component: Union[
            str, 
            core.Component, 
            Sequence[Union[str, core.Component]]]) -> str:
        """[summary]

        Args:
            component (core.Component): [description]

        Raises:
            ValueError: [description]

        Returns:
            str: [description]
            
        """ 
        for item in amicus.tools.listify(component):
            if isinstance(item, str):
                node = self.library.component.select(component)
            else:
                node = item
            for key, value in self.hierarchy.items():
                if isinstance(node, value):
                    return key
        raise ValueError('component is not a subclass instance in hierarchy') 
       
    def _get_subcomponents(self, 
        name: str, 
        section: Dict[str, Any],
        heading: str) -> Dict[str, str]:
        """[summary]

        Args:
            name (str): [description]
            section (Dict[str, Any]): [description]
            ignore_prefixes (bool, optional): [description]. Defaults to False.

        Returns:
            Dict[str, str]: [description]
            
        """
        suffixes = self.library.component.subclasses.suffixes
        component_keys = [k for k in section.keys() if k.endswith(suffixes)]
        subcomponents = {}
        for key in component_keys:
            prefix, suffix = amicus.tools.divide_string(key)
            if key.startswith(name) or (name == heading and prefix == suffix):
                edges = section[key]
                subcomponents.update(dict.fromkeys(edges, suffix))
        return subcomponents
  
    def _get_initialization(self, 
        name: str, 
        design: str,
        section: Dict[Hashable, Any],
        heading: str = None) -> Dict[Hashable, Any]:
        """Gets parameters for a specific Component from 'settings'.

        Args:
            name (str): name of the Component.
            settings (amicus.options.Settings): Settings instance that possibly
                contains initialization parameters.

        Returns:
            Dict[Hashable, Any]: any matching parameters.
            
        """ 
        if heading is None:
            heading = name
        dummy_component = self.library.component.select(name = [name, design])
        possible = tuple(
            i for i in list(dummy_component.__annotations__.keys()) 
            if i not in ['name', 'contents'])
        parameter_keys = [k for k in section.keys() if k.endswith(possible)]
        parameters = {}
        for key in parameter_keys:
            prefix, suffix = amicus.tools.divide_string(key)
            if key.startswith(name) or (name == heading and prefix == suffix):
                parameters[suffix] = section[key]
        return parameters       
        
    def _get_implementation(self, 
        name: str, 
        design: str,
        base: str,
        settings: amicus.options.Settings) -> Dict[Hashable, Any]:
        """[summary]

        Args:
            name (str): [description]
            design (str): [description]
            base (str): [description]
            settings (amicus.options.Settings): [description]

        Returns:
            Dict[Hashable, Any]: [description]
            
        """
        try:
            parameters = settings[f'{name}_parameters']
        except KeyError:
            try:
                parameters = settings[f'{design}_parameters']
            except KeyError:
                try:
                    parameters = settings[f'{base}_parameters']
                except KeyError:
                    parameters = {}
        return parameters
        
        