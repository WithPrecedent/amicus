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


DEFAULT_DESIGN = 'technique'


def settings_to_workflow(project: amicus.Project, **kwargs) -> nodes.Component:
    """[summary]

    Args:
        project (amicus.Project): [description]

    Returns:
        nodes.Component: [description]
        
    """        
    return component_from_settings(
        name = project.name,
        section = project.name,
        settings = project.settings,
        library = project.library,
        **kwargs)
     
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
                    design = DEFAULT_DESIGN
    return design  

def component_from_settings(
    name: str, 
    section: str,
    settings: amicus.options.Settings,
    library: nodes.Library = None,
    edges: Dict[str, List[str]] = None,
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
    if library is None:
        library = nodes.Component.library
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
        try:
            component.organize(edges = edges)
        except AttributeError:
            pass
        for node in component.keys():
            if node not in library.instances:
                if node in settings:
                    subsection = node
                else: 
                    subsection = section
                subcomponent = component_from_settings(
                    name = node,
                    section = subsection,
                    settings = settings,
                    library = library,
                    edges = edges)
    return component

# def get_subcomponents(
#     name: str, 
#     section: str,
#     settings: amicus.options.Settings,
#     library: nodes.Library) -> Dict[str, str]:
#     """[summary]

#     Args:
#         name (str): [description]
#         section (str): [description]
#         settings (amicus.options.Settings): [description]
#         library (nodes.Library): [description]

#     Returns:
#         Dict[str, str]: [description]
        
#     """    
#     subsettings = settings[section]
#     suffixes = library.subclasses.suffixes
#     component_keys = [k for k in subsettings.keys() if k.endswith(suffixes)]
#     subcomponents = {}
#     for key in component_keys:
#         prefix, suffix = amicus.tools.divide_string(key)
#         if key.startswith(name) or (name == section and prefix == suffix):
#             edges = subsettings[key]
#             subcomponents.update(dict.fromkeys(edges, suffix[:-1]))
#     return subcomponents

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
        settings (amicus.options.Settings): [description]
        library (nodes.Library): [description]

    Returns:
        Dict[str, List[str]]: [description]
        
    """
    suffixes = library.subclasses.suffixes
    edges = {}
    for name, section in settings.items():
        component_keys = [k for k in section.keys() if k.endswith(suffixes)]
        for key in component_keys:
            prefix, suffix = amicus.tools.divide_string(key)
            values = amicus.tools.listify(section[key])
            if prefix == suffix:
                if name in edges:
                    edges[name].extend(values)
                else:
                    edges[name] = values
            else:
                if prefix in edges:
                    edges[prefix].extend(values)
                else:
                    edges[prefix] = values
    return edges
