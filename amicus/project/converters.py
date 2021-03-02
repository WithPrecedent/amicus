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
        alternatives (tuple[Type])
        
    """     
    base: str = 'settings'
    parameters: Dict[str, Any] = dataclasses.field(default_factory = dict)
    alternatives: tuple[Type] = tuple([pathlib.Path, Mapping])
    default: Type = amicus.options.Settings


@dataclasses.dataclass
class FilerConverter(amicus.Converter):
    """Type Converter for Filer

    Args:
        base (str): 
        parameters (Dict[str, Any]):
        alternatives (tuple[Type])
        
    """
    base: str = 'filer'
    parameters: Dict[str, Any] = dataclasses.field(
        default_factory = lambda: {'settings': 'settings'})
    alternatives: tuple[Type] = tuple([pathlib.Path, Mapping])
    default: Type = amicus.options.Clerk
    
    