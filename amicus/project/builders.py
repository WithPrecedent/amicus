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
import functools
import inspect
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, Optional, Sequence, Set, Tuple, Type, Union)

import more_itertools

import amicus


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
    initialization = {name: {}}
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
            if prefix in edges:
                edges[prefix].extend(amicus.tools.listify(value))
            else:
                edges[prefix] = amicus.tools.listify(value)  
            for subcomponent in more_itertools.always_iterable(value):
                try:
                    subcomponent_design = get_design(
                        name = subcomponent, 
                        settings = settings)
                except KeyError:
                    subcomponent_design = suffix[:-1]
                designs.update({subcomponent: subcomponent_design})
        elif suffix in possible_initialization:
            initialization[suffix] = value 
        elif prefix in [name]:
            attributes[suffix] = value
        else:
            attributes[key] = value
    implementation = {}
    components = list(edges.keys())
    components.append(name)
    more_components = list(more_itertools.collapse(edges.values()))      
    components.extend(more_components)
    if components:
        for component in components:
            try:
                implementation[component] = settings[f'{component}_parameters']
            except KeyError:
                implementation[component] = {}
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
    package: str = 'amicus',
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
        package = settings[package]
    except (KeyError, TypeError):
        package = {}
    directives = {name: amicus.project.Directive.create(
        name = name,
        settings = settings)}
    section = settings[name]
    suffixes = library.component.subclasses.suffixes
    keys = [v for k, v in section.items() if k.endswith(suffixes)][0]
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
