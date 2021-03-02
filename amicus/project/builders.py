"""
amicus.project.builders:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    creators (Catalog): catalog storing all functions with a 'builder' 
        decorator.
    builder (FunctionType): decorator that stores a function in the CREATORS
        catalog.
    create_directive (FunctionType):
    create_outline (FunctionType):
    create_component (FunctionType):
    create_workflow (FunctionType):
    create_result (FunctionType):
    create_summary (FunctionType):

"""
from __future__ import annotations
import copy
import dataclasses
import functools
import inspect
import multiprocessing
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, Optional, Sequence, Set, Tuple, Type, Union)

import more_itertools

import amicus


CREATORS: amicus.types.Catalog = amicus.types.Catalog()

def builder(func: Callable) -> Callable:
    """Decorator for creation functions that stores them in 'creators'.
    
    Args:
        func (Callable)
        
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        name = func.__name__
        try:
            name = name.replace('create_', '')
        except ValueError:
            pass
        CREATORS[name] = func
        return func(*args, **kwargs)
    return wrapper

def get_design(self, name: str, settings: amicus.options.Settings) -> str:
    """[summary]

    Args:
        name (str): [description]

    Raises:
        KeyError: [description]

    Returns:
        str: [description]
        
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
 
@builder
def create_directive(
    name: str, 
    settings: amicus.project.Settings,
    library: amicus.types.Library = None,
    **kwargs) -> amicus.project.Directive:
    """[summary]

    Args:
        name (str): [description]
        settings (amicus.project.Settings): [description]
        library (amicus.types.Library, optional): [description]. 
            Defaults to None.

    Returns:
        amicus.project.Directive: [description]
        
    """
    if library is None:
        library = amicus.project.Component.library    
    edges = {}
    designs = {}
    initialization = {}
    attributes = {}        
    designs[name] = get_design(name = name, settings = settings)
    lookups = [name, designs[name]]
    dummy_component = library.component.create(name = lookups)
    possible_initialization = tuple(
        i for i in list(dummy_component.__annotations__.keys()) 
        if i not in ['name', 'contents'])
    for key, value in settings[name].items():
        suffix = key.split('_')[-1]
        prefix = key[:-len(suffix) - 1]
        if suffix in ['design']:
            pass
        elif suffix in library.component.subclasses.suffixes:
            designs.update(dict.fromkeys(value, suffix[:-1]))
            connections = amicus.tools.listify(value)
            if prefix in edges:
                edges[prefix].extend(connections)
            else:
                edges[prefix] = connections  
        elif suffix in possible_initialization:
            initialization[suffix] = value 
        elif prefix in [name]:
            attributes[suffix] = value
        else:
            attributes[key] = value
    implementation = {}
    components = list(edges.keys())
    more_components = list(more_itertools.collapse(edges.values()))      
    components = components.extend(more_components)
    if components:
        for name in components:
            try:
                implementation[name] = settings[f'{name}_parameters']
            except KeyError:
                implementation[name] = {}
    return amicus.project.Directive(
        name = name, 
        edges = edges,
        designs = designs,
        initialization = initialization,
        implementation = implementation,
        attributes = attributes,
        **kwargs)

@builder
def create_outline(
    name: str, 
    settings: amicus.project.Settings, 
    library: amicus.types.Library = None,
    **kwargs) -> amicus.project.Outline:
    """[summary]

    Args:
        name (str): [description]
        settings (amicus.options.Settings): [description]
        library (amicus.types.Library): [description]

    Returns:
        Outline: [description]
        
    """
    if library is None:
        library = amicus.project.Component.library
    try:
        general = settings['general']
    except KeyError:
        general = {}
    try:
        files = settings['files']
    except KeyError:
        try:
            files = settings['filer']
        except KeyError:
            files = {}
    try:
        package = settings['amicus']
    except KeyError:
        package = {}
    section = settings[name]
    suffixes = library.component.subclasses.suffixes
    print('test section', section)
    print('test suffixes', suffixes)
    keys = [v for k, v in section.items() if k.endswith(suffixes)][0]
    directives = {}
    for key in keys:
        if key in settings:
            directives[key] = amicus.project.Directive.create(
                name = key,
                settings = settings)
    return amicus.project.Outline(
        contents = directives,
        general = general,
        files = files,
        package = package,
        **kwargs)       

def create_workflow(
    name: str, 
    outline: amicus.project.Outline,
    library: amicus.framework.Library, 
    **kwargs) -> amicus.project.Component:
    """[summary]

    Args:
        name (str): [description]. Defaults to None.
        outline (amicus.project.Outline): [description]. 
            Defaults to None.
        library (amicus.framework.Library): [description]. 
            Defaults to None.

    Returns:
        amicus.project.Component: [description]
        
    """
    directive = outline[name]
    design = directive.designs[name]
    component = create_component(
        name = design, 
        directive = directive, 
        library = library,
        **kwargs)
    component.name = name
    return component
    

def create_component(
    name: str = None, 
    directive: amicus.project.Directive = None,
    library: amicus.framework.Library = None, 
    **kwargs) -> amicus.project.Component:
    """[summary]

    Args:
        name (str, optional): [description]. Defaults to None.
        directive (amicus.project.Directive, optional): [description]. 
            Defaults to None.
        library (amicus.framework.Library, optional): [description]. 
            Defaults to None.

    Raises:
        KeyError: [description]
        ValueError: [description]

    Returns:
        Component: [description]
        
    """
    if library is None:
        library = amicus.project.Component.library
    if directive is not None:
        if name is None:
            name = directive.name     
        lookups = [name, directive.designs[name]]
        parameters = directive.initialization
        parameters.update({'parameters': directive.implementation[name]}) 
        parameters.update(kwargs)
        if name in [directive.name]:
            parameters.update(directive.attributes)
        instance = create_component(
            name = lookups, 
            library = library, 
            **parameters)
    elif name is not None:
        names = amicus.tools.listify(name)
        primary = names[0]
        item = None
        for key in names:
            for catalog in ['instances', 'subclasses']:
                try:
                    item = getattr(library.component, catalog)[key]
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
    else:
        raise ValueError(
            f'create_componnt requires a name or directive argument')
    return instance  
