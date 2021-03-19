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
from . import configuration
from . import nodes
from . import products


""" Settings Parsing Functions """

def settings_to_workflow(project: amicus.Project, **kwargs) -> nodes.Component:
    """[summary]

    Args:
        project (amicus.Project): [description]

    Returns:
        nodes.Component: [description]
        
    """        
    return settings_to_component(
        name = project.name,
        section = project.name,
        settings = project.settings,
        library = project.library,
        recursive = True,
        **kwargs)
  
def settings_to_component(
    name: str, 
    section: str,
    settings: amicus.options.Settings,
    library: nodes.Library = None,
    subcomponents: Dict[str, List[str]] = None,
    design: str = None, 
    recursive: bool = True,
    overwrite: bool = False,
    **kwargs) -> nodes.Component:
    """[summary]

    Args:
        name (str): [description]
        section (str): [description]
        settings (amicus.options.Settings): [description]
        library (nodes.Library, optional): [description]. Defaults to None.
        subcomponents (Dict[str, List[str]], optional): [description]. Defaults to 
            None.
        design (str, optional): [description]. Defaults to None.
        recursive (bool, optional): [description]. Defaults to True.
        overwrite (bool, optional): [description]. Defaults to False.

    Returns:
        nodes.Component: [description]
    
    """
    library = library or configuration.LIBRARY
    subcomponents = subcomponents or settings_to_subcomponents(
        settings = settings, 
        library = library)
    design = design or settings_to_design(
        name = name, 
        section = section, 
        settings = settings)
    initialization = settings_to_initialization(
        name = name, 
        design = design,
        section = section, 
        settings = settings,
        library = library)
    initialization.update(kwargs)
    if 'parameters' not in initialization:
        initialization['parameters'] = settings_to_implementation(
            name = name, 
            design = design,
            settings = settings)
    component = library.instance(name = [name, design], **initialization)
    if isinstance(component, amicus.structures.Structure) and recursive:
        try:
            component.organize(subcomponents = subcomponents)
        except AttributeError:
            pass
        for node in component.keys():
            if node not in library.instances or overwrite:
                if node in settings:
                    subsection = node
                else: 
                    subsection = section
                # Subcomponents don't need to be stored or returned because they 
                # are automatically registered in 'library.instances' when they 
                # are instanced.
                settings_to_component(
                    name = node,
                    section = subsection,
                    settings = settings,
                    library = library,
                    subcomponents = subcomponents)
    return component

def settings_to_subcomponents(
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
    subcomponents = {}
    for name, section in settings.items():
        component_keys = [k for k in section.keys() if k.endswith(suffixes)]
        for key in component_keys:
            prefix, suffix = amicus.tools.divide_string(key)
            values = amicus.tools.listify(section[key])
            if prefix == suffix:
                if name in subcomponents:
                    subcomponents[name].extend(values)
                else:
                    subcomponents[name] = values
            else:
                if prefix in subcomponents:
                    subcomponents[prefix].extend(values)
                else:
                    subcomponents[prefix] = values
    return subcomponents
  
def settings_to_design(
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
                    design = configuration.DESIGN
    return design  

def settings_to_initialization(
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
        
def settings_to_implementation(
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

""" Workflow Executing Functions """

def workflow_to_summary(project: amicus.Project, **kwargs) -> nodes.Component:
    """[summary]

    Args:
        project (amicus.Project): [description]

    Returns:
        nodes.Component: [description]
        
    """
    summary = configuration.SUMMARY()
    for i, path in enumerate(project.workflow.paths):
        name = f'{summary.prefix}_{i + 1}'
        summary.add({name: workflow_to_result(
            path = path,
            project = project,
            data = project.data)})
        
def workflow_to_result(
    path: Sequence[str],
    project: amicus.Project,
    data: Any = None,
    library: nodes.Library = None,
    result: products.Result = None,
    **kwargs) -> object:
    """[summary]

    Args:
        name (str): [description]
        path (Sequence[str]): [description]
        project (amicus.Project): [description]
        data (Any, optional): [description]. Defaults to None.
        library (nodes.Library, optional): [description]. Defaults to None.
        result (products.Result, optional): [description]. Defaults to None.

    Returns:
        object: [description]
        
    """    
    library = library or configuration.LIBRARY
    result = result or configuration.RESULT
    data = data or project.data
    result = result()
    for node in path:
        try:
            component = library.instance(name = node)
            result.add(component.execute(project = project, **kwargs))
        except KeyError:
            pass
    return result
