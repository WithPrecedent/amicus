"""
amicus.project.workshop:
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
    library: nodes.Library = None,
    design: str = None,
    recursive: bool = True,) -> nodes.Worker:
    """[summary]

    Args:
        name (str): [description]
        settings (amicus.options.Settings): [description]
        library (nodes.Library): [description]
        design (str, optional): [description]. Defaults to None.

    Returns:
        nodes.Worker: [description]
        
    """    
    # if design is None:
    #     design: str = get_design(
    #         name = name, 
    #         section = name, 
    #         settings = settings,
    #         library = library)
    # component: nodes.Component = worker_from_section(
    #     name = name,
    #     section = name,
    #     settings = settings,
    #     library = library,
    #     design = design)
    # subcomponents: Dict[str, str] = get_subcomponents(
    #     name = name, 
    #     section = name, 
    #     settings = settings,
    #     library = library)
    # instances: Dict[str, nodes.Component] = {}
    # for subcomponent, subcomponent_base in subcomponents.items():
    #     subcomponent_design: str = get_design(
    #         name = subcomponent, 
    #         section = name, 
    #         settings = settings,
    #         library = library)
    #     subcomponent_design = subcomponent_design or subcomponent_base
    #     if subcomponent in settings:
    #         instance: nodes.Component = settings_to_workflow(
    #             name = subcomponent, 
    #             settings = settings,
    #             library = library,
    #             design = subcomponent_design)
    #     else:
    #         instance: nodes.Component = component_from_section(
    #             name = subcomponent,
    #             section = name,
    #             settings = settings,
    #             library = library,
    #             design = subcomponent_design)
    #     instances[subcomponent] = instance
    if library is None:
        library = nodes.Component.library
    component = component_from_section(
        name = name,
        seciton = name,
        settings = settings,
        library = library,
        design = design,
        recursive = recursive)
    return component
     
def get_design(
    name: str, 
    section: str, 
    settings: amicus.options.Settings) -> str:
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
    edges: Dict[Hashable, List[Hashable]] = None,
    design: str = None, 
    recursive: bool = True,
    **kwargs) -> nodes.Worker:
    """[summary]

    Args:
        name (str): [description]
        section (str): [description]
        settings (amicus.options.Settings): [description]
        library (nodes.Library): [description]
        design (str, optional): [description]. Defaults to None.
        recursive (bool, optional): [description]. Defaults to True.

    Returns:
        nodes.Component: [description]
        
    """
    if design is None:
        design = get_design(name = name, section = section, settings = settings)
    if edges is None:
        edges = settings_to_edges(settings = settings, library = library)
    initialization = get_initialization(
        name = name, 
        design = design,
        section = section, 
        settings = settings,
        library = library)
    initialization.update(kwargs)
    initialization['parameters'] = get_implementation(
        name = name, 
        design = design,
        settings = settings)
    component = library.instance(name = [name, design], **initialization)
    if isinstance(component, amicus.structures.Structure) and recursive:
        for node in component.nodes.keys():
            subsection = settings.get(node, section)
            subcomponent = component_from_section(
                name = node,
                section = subsection,
                settings = settings,
                library = library,
                edges = edges)
        try:
            component.organize(edges = edges)
        except AttributeError:
            pass
    return component
       
def component_from_section(
    name: str, 
    section: str,
    settings: amicus.options.Settings,
    library: nodes.Library = None,
    design: str = None, 
    recursive: bool = True,
    **kwargs) -> nodes.Component:
    """[summary]

    Args:
        name (str): [description]
        section (str): [description]
        settings (amicus.options.Settings): [description]
        library (nodes.Library): [description]
        design (str, optional): [description]. Defaults to None.
        recursive (bool, optional): [description]. Defaults to True.

    Returns:
        nodes.Component: [description]
        
    """
    if design is None:
        design = get_design(name = name, section = section, settings = settings)
    if library is None:
        library = nodes.Component.library
    initialization = get_initialization(
        name = name, 
        design = design,
        section = section, 
        settings = settings,
        library = library)
    initialization.update(kwargs)
    initialization['parameters'] = get_implementation(
        name = name, 
        design = design,
        settings = settings)
    return library.instance(name = [name, design], **initialization)

def get_subcomponents(
    name: str, 
    section: str,
    settings: amicus.options.Settings,
    library: nodes.Library) -> Dict[str, str]:
    """[summary]

    Args:
        name (str): [description]
        section (str): [description]
        settings (amicus.options.Settings): [description]
        library (nodes.Library): [description]

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
        name (str): [description]
        section (str): [description]
        design (str): [description]
        settings (amicus.options.Settings): [description]
        library (nodes.Library): [description]

    Returns:
        Dict[Hashable, Any]: [description]
        
    """
    subsettings = settings[section]
    parameters = library.parameterify(name = [name, design])
    possible = tuple(i for i in parameters if i not in ['name', 'contents'])
    parameter_keys = [k for k in subsettings.keys() if k.endswith(possible)]
    kwargs = {}
    for key in parameter_keys:
        prefix, suffix = amicus.tools.divide_string(key)
        if key.startswith(name) or (name == section and prefix == suffix):
            kwargs[suffix] = subsettings[key]
    return kwargs  
        
def get_implementation(
    name: str, 
    design: str,
    settings: amicus.options.Settings) -> Dict[Hashable, Any]:
    """[summary]

    Args:
        name (str): [description]
        design (str): [description]
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
        component_keys = [k for k in section.keys() if k.endswith(suffixes)]
        for key in component_keys:
            prefix, suffix = amicus.tools.divide_string(key)
            values = amicus.tools.listify(section[key])
            if prefix == suffix:
                if section in edges:
                    edges[section].extend(values)
                else:
                    edges[section] = values
            else:
                if prefix in edges:
                    edges[prefix].extend(values)
                else:
                    edges[prefix] = values
    return edges
