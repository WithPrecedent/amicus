"""
amicus.project.workshop:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import itertools
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)

import more_itertools

import amicus
from . import configuration
from . import nodes
from . import core


""" Settings Parsing Functions """

def create_workflow(project: amicus.Project, **kwargs) -> nodes.Component:
    """[summary]

    Args:
        project (amicus.Project): [description]

    Returns:
        nodes.Component: [description]
        
    """
    settings = project.settings
    try:
        library = project.library
    except AttributeError:
        library = configuration.library
    workflow = settings_to_workflow(
        settings = settings,
        library = library,
        **kwargs)
    return workflow

def settings_to_workflow(
    settings: amicus.options.Settings,
    library: nodes.Library,
    **kwargs) -> nodes.Component:
    """[summary]

    Args:
        settings (amicus.options.Settings): [description]
        library (nodes.Library): [description]
        suffixes (Sequence[str]): [description]

    Returns:
        nodes.Component: [description]
        
    """
    suffixes = library.subclasses.suffixes  
    connections = settings_to_connections(
        settings = settings,
        suffixes = suffixes)
    sections = settings_to_sections(
        settings = settings,
        suffixes = suffixes)  
    all_nodes = (list(connections.keys()) 
                 + list(itertools.chain.from_iterable(connections.values())))
    nodes = amicus.tools.deduplicate(iterable = list(all_nodes))
    bases = settings_to_bases(
        settings = settings,
        suffixes = suffixes,
        nodes = nodes,
        sections = sections)
    for name in nodes:
        settings_to_component(
            name = name,
            bases = bases,
            sections = sections,
            settings = settings,
            library = library)
    workflow = settings_to_graph(
        settings = settings,
        library = library,
        connections = connections,
        **kwargs)
    workflow.library = library
    return workflow

def settings_to_connections(
    settings: amicus.options.Settings,
    suffixes: Sequence[str]) -> Dict[str, List[str]]:
    """[summary]

    Args:
        settings (amicus.options.Settings): [description]
        suffixes (Sequence[str]): [description]

    Returns:
        Dict[str, List[str]]: [description]
        
    """    
    connections = {}
    for name, section in settings.items():
        component_keys = [k for k in section.keys() if k.endswith(suffixes)]
        for key in component_keys:
            prefix, suffix = amicus.tools.divide_string(key)
            values = amicus.tools.listify(section[key])
            if prefix == suffix:
                if name in connections:
                    connections[name].extend(values)
                else:
                    connections[name] = values
            else:
                if prefix in connections:
                    connections[prefix].extend(values)
                else:
                    connections[prefix] = values
    return connections

def settings_to_sections(
    settings: amicus.options.Settings,
    suffixes: Sequence[str]) -> Dict[str, str]:
    """[summary]

    Args:
        settings (amicus.options.Settings): [description]
        suffixes (Sequence[str]): [description]

    Returns:
        Dict[str, str]: [description]
        
    """   
    sections = {}
    for name, section in settings.items():
        component_keys = [k for k in section.keys() if k.endswith(suffixes)]
        if component_keys:
            sections[name] = name
            for key in component_keys:
                values = amicus.tools.listify(section[key])
                sections.update(dict.fromkeys(values, name))
    return sections

def settings_to_bases(
    settings: amicus.options.Settings,
    suffixes: Sequence[str],
    nodes: Dict[str, str],
    sections: Dict[str, str]) -> Dict[str, str]:
    """[summary]

    Args:
        settings (amicus.options.Settings): [description]
        suffixes (Sequence[str]): [description]
        nodes (Dict[str, str]):
        sections (Dict[str, str]):

    Returns:
        Dict[str, str]: [description]
        
    """    
    bases = {}
    for name in nodes:
        section = sections[name]
        component_keys = [
            k for k in settings[section].keys() if k.endswith(suffixes)]
        if component_keys:
            bases[name] = settings_to_base(
                name = name,
                section = sections[name],
                settings = settings)
            for key in component_keys:
                prefix, suffix = amicus.tools.divide_string(key)
                values = amicus.tools.listify(settings[section][key])
                if suffix.endswith('s'):
                    design = suffix[:-1]
                else:
                    design = suffix            
                bases.update(dict.fromkeys(values, design))
    return bases

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
        bases (Dict[str, str]): a set of default bases if one is not found
             in 'settings'. This might be separately created by the
             'settings_to_connections' method from 'settings'.

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
                design = None
    return design  
 
def settings_to_graph(
    settings: amicus.options.Settings,
    library: nodes.Library = None,
    connections: Dict[str, List[str]] = None) -> amicus.structures.Graph:
    """[summary]

    Args:
        settings (amicus.options.Settings): [description]
        library (nodes.Library, optional): [description]. Defaults to None.
        connections (Dict[str, List[str]], optional): [description]. Defaults 
            to None.

    Returns:
        amicus.structures.Graph: [description]
        
    """    
    library = library or configuration.LIBRARY
    connections = connections or settings_to_connections(
        settings = settings, 
        library = library)
    graph = amicus.structures.Graph()
    for node in connections.keys():
        kind = library.classify(component = node)
        method = locals()[f'finalize_{kind}']
        graph = method(
            node = node, 
            connections = connections,
            library = library, 
            graph = graph)     
    return graph

def settings_to_component(
    name: str, 
    bases: Dict[str, str],
    sections: Dict[str, str],
    settings: amicus.options.Settings,
    library: nodes.Library,
    **kwargs) -> nodes.Component:
    """[summary]

    Args:
        name (str): [description]
        section (str): [description]
        settings (amicus.options.Settings): [description]
        library (nodes.Library, optional): [description]. Defaults to None.
        connections (Dict[str, List[str]], optional): [description]. Defaults 
            to None.
        design (str, optional): [description]. Defaults to None.
        recursive (bool, optional): [description]. Defaults to True.
        overwrite (bool, optional): [description]. Defaults to False.

    Returns:
        nodes.Component: [description]
    
    """
    design = bases[name]
    section = sections[name]
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
    return component

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

def finalize_serial(
    node: str,
    connections: Dict[str, List[str]],
    library: nodes.Library,
    graph: amicus.structures.Graph) -> amicus.structures.Graph:
    """[summary]

    Args:
        node (str): [description]
        connections (Dict[str, List[str]]): [description]
        library (nodes.Library): [description]
        graph (amicus.structures.Graph): [description]

    Returns:
        amicus.structures.Graph: [description]
        
    """    
    connections = _serial_order(
        name = node, 
        connections = connections)
    nodes = list(more_itertools.collapse(connections))
    if nodes:
        graph.extend(nodes = nodes)
    return graph      

def _serial_order(
    name: str,
    connections: Dict[str, List[str]]) -> List[Hashable]:
    """[summary]

    Args:
        name (str): [description]
        directive (core.Directive): [description]

    Returns:
        List[Hashable]: [description]
        
    """   
    organized = []
    components = connections[name]
    for item in components:
        organized.append(item)
        if item in connections:
            organized_connections = []
            connections = _serial_order(
                name = item, 
                connections = connections)
            organized_connections.append(connections)
            if len(organized_connections) == 1:
                organized.append(organized_connections[0])
            else:
                organized.append(organized_connections)
    return organized   


""" Workflow Executing Functions """

def workflow_to_summary(project: amicus.Project, **kwargs) -> amicus.Project:
    """[summary]

    Args:
        project (amicus.Project): [description]

    Returns:
        nodes.Component: [description]
        
    """
    # summary = None
    # print('test workflow', project.workflow)
    # print('test paths', project.workflow.paths)
    # print('test parser contents', library.instances['parser'].contents)
    # print('test parser paths', library.instances['parser'].paths)
    summary = configuration.SUMMARY()
    print('test project paths', project.workflow.paths)
    # for path in enumerate(project.workflow.paths):
    #     name = f'{summary.prefix}_{i + 1}'
    #     summary.add({name: workflow_to_result(
    #         path = path,
    #         project = project,
    #         data = project.data)})
    return summary
        
def workflow_to_result(
    path: Sequence[str],
    project: amicus.Project,
    data: Any = None,
    library: nodes.Library = None,
    result: core.Result = None,
    **kwargs) -> object:
    """[summary]

    Args:
        name (str): [description]
        path (Sequence[str]): [description]
        project (amicus.Project): [description]
        data (Any, optional): [description]. Defaults to None.
        library (nodes.Library, optional): [description]. Defaults to None.
        result (core.Result, optional): [description]. Defaults to None.

    Returns:
        object: [description]
        
    """    
    library = library or configuration.LIBRARY
    result = result or configuration.RESULT
    data = data or project.data
    result = result()
    for node in path:
        print('test node in path', node)
        try:
            component = library.instance(name = node)
            result.add(component.execute(project = project, **kwargs))
        except (KeyError, AttributeError):
            pass
    return result
