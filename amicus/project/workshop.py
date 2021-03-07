"""
amicus.project.foundry:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""
from __future__ import annotations
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)

import more_itertools

import amicus
from . import nodes


def settings_to_workflow(
    name: str,
    settings: amicus.options.Settings, 
    library: nodes.Library,
    design: str = None) -> nodes.Worker:
    """[summary]

    Args:
        name (str): [description]
        settings (amicus.options.Settings): [description]
        library (nodes.Library): [description]

    Returns:
        nodes.Worker: [description]
        
    """
    if design is None:
        design: str = get_design(
            name = name, 
            section = name, 
            settings = settings,
            library = library)
    component: nodes.Component = component_from_section(
        name = name,
        section = name,
        settings = settings,
        library = library,
        design = design)
    subcomponents: Dict[str, str] = get_subcomponents(
        name = name, 
        section = name, 
        settings = settings,
        library = library)
    instances: Dict[str, nodes.Component] = {}
    for subcomponent, subcomponent_base in subcomponents.items():
        subcomponent_design: str = get_design(
            name = subcomponent, 
            section = name, 
            settings = settings,
            library = library)
        subcomponent_design = subcomponent_design or subcomponent_base
        if subcomponent in settings:
            instance: nodes.Component = settings_to_workflow(
                name = subcomponent, 
                settings = settings,
                library = library,
                design = subcomponent_design)
        else:
            instance: nodes.Component = component_from_section(
                name = subcomponent,
                section = name,
                settings = settings,
                library = library,
                design = subcomponent_design)
        instances[subcomponent] = instance
    edges = settings_to_workflow(
        name = name, 
        settings = settings, 
        library = library, 
        design = design)
    component.organize(edges = edges)
    return component
     
def get_design(
    name: str, 
    section: str, 
    settings: amicus.options.Settings,
    library = nodes.Library) -> str:
    """Gets name of a Component design.

    Args:
        name (str): name of the Component.
        section (str):
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
                design = settings[section][f'{name}_design']
            except KeyError:
                if name == section:
                    design = settings['amicus']['default_design']
                else:
                    design = 'technique'
    return design  
        
def component_from_section(
    name: str, 
    section: str,
    settings: amicus.options.Settings,
    library: nodes.Library,
    design: str = None, 
    **kwargs) -> nodes.Component:
    """[summary]

    Args:
        name (str): [description]
        section (str): [description]
        settings (amicus.options.Settings): [description]
        library (nodes.Library): [description]
        
    Returns:
        nodes.Component: [description]
        
    """
    if design is None:
        design = get_design(name = name, section = section, settings = settings)
    parameters = get_initialization(
        name = name, 
        design = design,
        section = section, 
        settings = settings,
        library = library)
    parameters.update(kwargs)
    implementation = get_implementation(
        name = name, 
        design = design,
        settings = settings)
    parameters['parameters'] = implementation
    print('test parameters', parameters)
    return library.instance(name = [name, design], **parameters)

def get_subcomponents(
    name: str, 
    section: str,
    settings: amicus.options.Settings,
    library: nodes.Library) -> Dict[str, str]:
    """[summary]

    Args:
        name (str): [description]
        section (Dict[str, Any]): [description]
        ignore_prefixes (bool, optional): [description]. Defaults to False.

    Returns:
        Dict[str, str]: [description]
        
    """
    subsettings = settings[section]
    suffixes = library.subclasses.suffixes
    component_keys = [k for k in subsettings.keys() if k.endswith(suffixes)]
    subcomponents = {}
    for key in component_keys:
        prefix, suffix = amicus.tools.divide_string(key)
        if key.startswith(name) or (name == section and prefix == suffix):
            edges = subsettings[key]
            subcomponents.update(dict.fromkeys(edges, suffix[:-1]))
    return subcomponents

def get_initialization(
    name: str, 
    section: str,
    design: str,
    settings: amicus.options.Settings,
    library: nodes.Library) -> Dict[Hashable, Any]:
    """Gets parameters for a specific Component from 'settings'.

    Args:
        name (str): name of the Component.
        settings (amicus.options.Settings): Settings instance that possibly
            contains initialization parameters.

    Returns:
        Dict[Hashable, Any]: any matching parameters.
        
    """
    subsettings = settings[section]
    print('test name for init', name, design)
    print('test library', library.subclasses, library.instances)
    dummy_component = library.select(name = [name, design])
    possible = tuple(
        i for i in list(dummy_component.__annotations__.keys()) 
        if i not in ['name', 'contents', 'design'])
    print('test possible parameters', possible)
    parameter_keys = [k for k in subsettings.keys() if k.endswith(possible)]
    parameters = {}
    for key in parameter_keys:
        prefix, suffix = amicus.tools.divide_string(key)
        if key.startswith(name) or (name == section and prefix == suffix):
            parameters[suffix] = subsettings[key]
    return parameters   
        
def get_implementation(
    name: str, 
    design: str,
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
            parameters = {}
    return parameters

def settings_to_edges(
    settings: amicus.options.Settings,
    library: nodes.Library) -> Dict[str, List[str]]:
    """[summary]

    Args:
        section (str): [description]
        settings (amicus.options.Settings): [description]
        library (nodes.Library): [description]

    Returns:
        Dict[str, List[str]]: [description]
    """
    suffixes = library.subclasses.suffixes
    edges = {}
    for section in settings.items():
        keys = [k for k in section.keys() if k.endswith(suffixes)]
        for key in keys:
            prefix, suffix = amicus.tools.divide_string(key)
            if prefix == suffix:
                edges[section] = section[key]
            else:
                edges[prefix] = section[key]
    return edges
