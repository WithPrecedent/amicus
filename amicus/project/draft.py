"""
amicus.project.draft: classes and functions for creating a project outline
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Parameters
    Directive
    Outline
    Component
    Result
    Summary

"""
from __future__ import annotations
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, Optional, Sequence, Set, Tuple, Type, Union)

import more_itertools

import amicus


@dataclasses.dataclass
class Directive(amicus.quirks.Needy):
    """Information needed to construct a Worker.
    
    A Directive is typically created from a section of a Settings instance.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None.
        edges (Dict[str, List]): a dictionary with keys that are names of
            components and values that are lists of subcomponents for the keys.
            However, these named connections are not necessarily the same as an 
            adjacency list because of different design possiblities. Defaults to 
            an empty dict.
        designs (Dict[str, str]): keys are the names of nodes and values are the
            base Node subclass of the named node. Defaults to None.
        initialization (Dict[str, Dict[str, Any]]): a dictionary with keys that 
            are the names of components and values which are dictionaries of 
            pararmeters to use when created the component listed in the key. 
            Defaults to an empty dict.
        implementation (Dict[str, Dict[str, Any]]): a dictionary with keys that 
            are the names of components and values which are dictionaries of 
            pararmeters to use when calling the 'implement' method of the 
            component listed in the key. Defaults to an empty dict.
        attributes (Dict[str, Dict[str, Any]]): a dictionary with keys that 
            are the names of components and values which are dictionaries of 
            attributes to automatically add to the component constructed from
            that key. Defaults to an empty dict.
            
    """
    name: str = None
    edges: Dict[str, List[str]] = dataclasses.field(default_factory = dict)
    designs: Dict[str, str] = dataclasses.field(default_factory = dict)
    initialization: Dict[str, Any] = dataclasses.field(default_factory = dict)
    implementation: Dict[str, Dict[str, Any]] = dataclasses.field(
        default_factory = dict)
    attributes: Dict[str, Any] = dataclasses.field(default_factory = dict)
    needs: ClassVar[Sequence[str]] = ['settings', 'name', 'library']

    """ Public Methods """
    
    @classmethod   
    def from_settings(cls, 
        settings: amicus.options.Settings,
        name: str, 
        library: amicus.types.Library = None,
        **kwargs) -> Directive:
        """[summary]

        Args:
            name (str): [description]
            settings (amicus.options.Settings): [description]
            library (amicus.types.Library, optional): [description]. 
                Defaults to None.
                
        Returns:
            Directive: [description]
            
        """        
        return create_directive( 
            settings = settings,
            name = name,
            library = library,
            **kwargs)


@amicus.project.core.builder
def create_directive(
    settings: amicus.project.Settings,
    name: str, 
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
    dummy_component = library.component.select(name = lookups)
    possible_initialization = tuple(
        i for i in list(dummy_component.__annotations__.keys()) 
        if i not in ['name', 'contents'])
    for key, value in settings[name].items():
        prefix, suffix = amicus.tools.divide_string(key, divider = '_')
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

def get_design(name: str, settings: amicus.options.Settings) -> str:
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

       
@dataclasses.dataclass
class Outline(amicus.quirks.Needy, amicus.types.Lexicon):
    """Creates and stores Directive instances.
    
    An Outline is typically derived from a Settings instance.
    
    Args:
        contents (Mapping[str, Directive]]): stored dictionary of Directive 
            instances. Defaults to an empty dict.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty Directive.
        general (Dict[str, Any]): general settings for an amicus project. This
            is typically the 'general' section of a Settings instance. Defaults
            to an empty dict.
        files (Dict[str, Any]): general settings for an amicus project. This
            is typically the 'files' or 'filer' section of a Settings instance. 
            Defaults to an empty dict.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. The first item
            in 'needs' to correspond to an internal factory classmethod named
            f'from_{first item in needs}'. Defaults to a list with 'settings',
            'name', and 'library'.
                   
    """
    name: str = None
    contents: Dict[str, Directive] = dataclasses.field(default_factory = dict)
    default: Any = Directive()
    general: Dict[str, Any] = dataclasses.field(default_factory = dict)
    files: Dict[str, Any] = dataclasses.field(default_factory = dict)
    package: Dict[str, Any] = dataclasses.field(default_factory = dict)
    needs: ClassVar[Sequence[str]] = ['settings', 'name', 'library']
    
    """ Public Methods """
    
    @classmethod
    def from_settings(cls, 
        settings: amicus.options.Settings, 
        name: str, 
        library: amicus.types.Library = None,
        **kwargs) -> Outline:
        """[summary]

        Args:
            name (str): [description]
            settings (amicus.options.Settings): [description]
            library (amicus.types.Library): [description]

        Returns:
            Outline: [description]
            
        """
        return create_outline(
            settings = settings, 
            name = name, 
            library = library,
            **kwargs)


@amicus.project.core.builder
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
    directives = {name: Directive.create(settings = settings, name = name)}
    section = settings[name]
    suffixes = library.component.subclasses.suffixes
    keys = [v for k, v in section.items() if k.endswith(suffixes)][0]
    for key in keys:
        if key in settings:
            directives[key] = Directive.create(settings = settings, name = key)
        else:
            directives[key] = directives[name]
    return amicus.project.Outline(
        contents = directives,
        general = general,
        files = files,
        package = package,
        **kwargs)       

