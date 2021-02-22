"""
converters: type converters specific to the project subpackage
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""
from __future__ import annotations
import dataclasses
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union, get_args, 
                    get_origin)

import amicus


@dataclasses.dataclass
class SettingsConverter(amicus.Converter):
    """Type converter for Settings.

    Args:
        base (str): 
        parameters (Dict[str, Any]):
        alternatives (Tuple[Type])
        
    """     
    base: str = 'settings'
    parameters: Dict[str, Any] = dataclasses.field(default_factory = dict)
    alternatives: Tuple[Type] = tuple([pathlib.Path, Mapping])


@dataclasses.dataclass
class FilerConverter(amicus.Converter):
    """Type Converter for Filer

    Args:
        base (str): 
        parameters (Dict[str, Any]):
        alternatives (Tuple[Type])
        
    """
    base: str = 'filer'
    parameters: Dict[str, Any] = dataclasses.field(
        default_factory = lambda: {'settings': 'settings'})
    alternatives: Tuple[Type] = tuple([pathlib.Path, Mapping])
    
    
@dataclasses.dataclass
class WorkerConverter(amicus.Converter):
    """Type converter for Worker

    Args:
        base (str): 
        parameters (Dict[str, Any]):
        alternatives (Tuple[Type])
        
    """        
    base: str = 'component'
    parameters: Dict[str, Any] = dataclasses.field(
        default_factory = lambda: {'project': 'self'})
    alternatives: Tuple[Type] = None

    
@dataclasses.dataclass
class WorkersConverter(amicus.Converter):
    """Type converter for Workers.

    Args:
        base (str): 
        parameters (Dict[str, Any]):
        alternatives (Tuple[Type])
        
    """        
    base: str = 'component'
    parameters: Dict[str, Any] = dataclasses.field(
        default_factory = lambda: {'project': 'self'})
    alternatives: Tuple[Type] = None


    def validate(self, item: Any, instance: object) -> object:
        """[summary]

        Args:
            workers (Sequence[Union[ base.Worker, 
                Type[base.Worker], str]]): [description]

        Returns:
            Sequence[base.Worker]: [description]
            
        """
        if not item:
            try:
                item = instance.settings[instance.name][
                    f'{instance.name}_workers']
            except KeyError:
                pass
        new_workers = []
        for worker in item:
            converter = instance.initialize_converter(
                name = 'worker',
                converter = 'worker')
            new_workers.append(converter.validate(
                item = [worker, 'worker'],
                instance = instance))
        return new_workers
    

@dataclasses.dataclass
class CreatorConverter(amicus.Converter):
    """Type converter for Creator.

    Args:
        base (str): 
        parameters (Dict[str, Any]):
        alternatives (Tuple[Type])
        
    """         
    base: str = 'creator'
    parameters: Dict[str, Any] = dataclasses.field(default_factory = dict)
    alternatives: Tuple[Type] = None
    
    
@dataclasses.dataclass
class CreatorsConverter(amicus.Converter):
    """Type converter for Creators.

    Args:
        base (str): 
        parameters (Dict[str, Any]):
        alternatives (Tuple[Type])
        
    """        
    base: str = 'creator'
    parameters: Dict[str, Any] = dataclasses.field(default_factory = dict)
    alternatives: Tuple[Type] = None


    def validate(self, item: Any, instance: object) -> object:
        """
        """
        new_creators = []
        for creator in item:
            converter = instance.initialize_converter(
                name = 'creator',
                converter = 'creator')
            new_creators.append(converter.validate(
                item = [creator, 'worker'],
                instance = instance))
        return new_creators
    
       
@dataclasses.dataclass
class ComponentConverter(amicus.Converter):
    """Type converter for Component.

    Args:
        base (str): 
        parameters (Dict[str, Any]):
        alternatives (Tuple[Type])
        
    """         
    base: str = 'component'
    parameters: Dict[str, Any] = dataclasses.field(
        default_factory = lambda: {'name': 'str'})
    alternatives: Tuple[Type] = None


@dataclasses.dataclass
class WorkflowConverter(amicus.Converter):
    """Type converter for Workflow

    Args:
        base (str): 
        parameters (Dict[str, Any]):
        alternatives (Tuple[Type])
        
    """         
    base: str = 'workflow'
    parameters: Dict[str, Any] = dataclasses.field(default_factory = dict)
    alternatives: Tuple[Type] = None
    

@dataclasses.dataclass
class ResultsConverter(amicus.Converter):
    """Type converter for Results.

    Args:
        base (str): 
        parameters (Dict[str, Any]):
        alternatives (Tuple[Type])
        
    """         
    base: str = 'results'
    parameters: Dict[str, Any] = dataclasses.field(
        default_factory = lambda: {'name': 'name', 
                                   'identification': 'identification'})
    alternatives: Tuple[Type] = None
    