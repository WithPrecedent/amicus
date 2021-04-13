"""
amicus.project.settings:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

This module stores universally accessible configuration options in the form of
module-level constants.
 
"""
from __future__ import annotations
import dataclasses
import itertools
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)

import amicus


""" 
General Default Configuration Options 

These will be replaced with values if a Settings instance passed to the
controlling Project instance includes lower-case versions of these settings in
the 'general' section. So, if 'settings["general"]["seed"] = 50, then 'SEED'
will automatically be changed to 50 by the Project instance.

"""
CONSERVE_MEMORY: bool = False
PARALLELIZE: bool = False
SEED: int = 42
VERBOSE: bool = True

""" Default Classes and Related Options """

@dataclasses.dataclass
class Bases(amicus.quirks.Importer):
    """Base classes for amicus projects.
    
    Args:
            
    """
    component: Union[str, Type] = 'nodes.Component'
    laborer: Union[str, Type] = 'nodes.Laborer' 
    manager: Union[str, Type] = 'nodes.Manager'
    task: Union[str, Type] = 'nodes.Task'
    worker: Union[str, Type] = 'nodes.Worker'
    
    cookbook: Union[str, Type] = 'core.Cookbook'
    recipe: Union[str, Type] = 'core.Recipe'
    summary: Union[str, Type] = 'core.Summary'
    workflow: Union[str, Type] = 'core.Workflow'
   
    """ Public Methods """

    def add(self, name: str, base: Union[str, Type]) -> None:
        setattr(self, name, base)
        return self
    
    def change(self, name: str, base: Union[str, Type]) -> None:
        if name in dir(self):
            setattr(self, name, base)
        else:
            raise ValueError(f'{name} is not an existing base class name')
        return self
        
bases = Bases()
   
   
""" Configuration Subclass for amicus Projects """

@dataclasses.dataclass
class Settings(amicus.options.Configuration):
    """Loads and stores configuration settings for an amicus project.

    Args:
        contents (Mapping[str, Mapping[str, Any]]): a two-level nested dict for
            storing configuration options. Defaults to en empty dict.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty dict.
        standard (Mapping[str, Mapping[str]]): any standard options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to an empty dict.
        infer_types (bool): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, all values will be strings. Defaults to True.
        project (amicus.Project): associated Project instance. This is needed 
            for this class' properties and additional methods to function
            properly. Defaults to None.

    """
    contents: Mapping[str, Mapping[str, Any]] = dataclasses.field(
        default_factory = dict)
    default: Any = dataclasses.field(default_factory = dict)
    standard: Mapping[str, Mapping[str, Any]] = dataclasses.field(
        default_factory = dict)
    infer_types: bool = True
    project: amicus.Project = None
    
    """ Properties """
    
    @property
    def bases(self) -> Dict[str, str]:
        return self._get_bases()
    
    @property
    def connections(self) -> Dict[str, List[str]]:
        return self._get_connections()

    @property
    def designs(self) -> Dict[str, str]:
        return self._get_designs()
    
    @property
    def managers(self) -> Dict[str, str]:
        return self._get_managers()
     
    @property
    def nodes(self) -> List[str]:
        key_nodes = list(self.connections.keys())
        value_nodes = list(
            itertools.chain.from_iterable(self.connections.values()))
        return amicus.tools.deduplicate(iterable = key_nodes + value_nodes) 
        
    """ Private Methods """

    def _get_bases(self) -> Dict[str, str]:  
        suffixes = self.project.library.subclasses.suffixes 
        managers = self.managers
        bases = {}
        for name in self.nodes:
            section = managers[name]
            component_keys = [
                k for k in self[section].keys() if k.endswith(suffixes)]
            if component_keys:
                bases[name] = settings_to_base(
                    name = name,
                    section = managers[name])
                for key in component_keys:
                    prefix, suffix = amicus.tools.divide_string(key)
                    values = amicus.tools.listify(self[section][key])
                    if suffix.endswith('s'):
                        design = suffix[:-1]
                    else:
                        design = suffix            
                    bases.update(dict.fromkeys(values, design))
        return bases
      
    def _get_connections(self) -> Dict[str, List[str]]:
        suffixes = self.project.library.subclasses.suffixes 
        connections = {}
        for name, section in self.items():
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
    
    def _get_designs(self) -> Dict[str, str]:  
        suffixes = self.project.library.subclasses.suffixes 
        managers = self.managers
        designs = {}
        for name in self.nodes:
            section = managers[name]
            component_keys = [
                k for k in self[section].keys() if k.endswith(suffixes)]
            if component_keys:
                designs[name] = settings_to_base(
                    name = name,
                    section = managers[name])
                for key in component_keys:
                    prefix, suffix = amicus.tools.divide_string(key)
                    values = amicus.tools.listify(self[section][key])
                    if suffix.endswith('s'):
                        design = suffix[:-1]
                    else:
                        design = suffix            
                    designs.update(dict.fromkeys(values, design))
        return designs
    
    def _get_managers(self) -> Dict[str, str]:
        suffixes = self.project.library.subclasses.suffixes 
        managers = {}
        for name, section in self.items():
            component_keys = [k for k in section.keys() if k.endswith(suffixes)]
            if component_keys:
                managers[name] = name
                for key in component_keys:
                    values = amicus.tools.listify(section[key])
                    managers.update(dict.fromkeys(values, name))
        return managers

settings = Settings()

filer = amicus.options.Clerk(settings = settings)
