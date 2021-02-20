"""
core.options: 
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
Contents:
    
    
"""
from __future__ import annotations
import dataclasses
import pathlib
import random
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import amicus


@dataclasses.dataclass
class Configuration(amicus.Configuration):
    """Loads and stores configuration settings for an amicus project.
    Args:
        contents (Union[str, pathlib.Path, Mapping[str, Mapping[str, Any]]]): a 
            dict, a str file path to a file with settings, or a pathlib Path to
            a file with settings. Defaults to en empty dict.
        infer_types (bool): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, a False value will leave all values as strings. 
            Defaults to True.
        defaults (Mapping[str, Mapping[str]]): any default options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to a dict with 'general', 
            'files', and 'amicus' sections listed.
        skip (Sequence[str]): names of suffixes to skip when constructing nodes
            for an amicus project. Defaults to a list with 'general', 'files',
            'amicus', and 'parameters'. 
                          
    """
    contents: Union[str, pathlib.Path, Mapping[str, Mapping[str, Any]]] = (
        dataclasses.field(default_factory = dict))
    infer_types: bool = True
    defaults: Mapping[str, Mapping[str, Any]] = dataclasses.field(
        default_factory = lambda: {'general': {'verbose': False,
                                               'parallelize': False,
                                               'conserve_memory': False,
                                               'gpu': False,
                                               'seed': random.randrange(1000)},
                                   'files': {'source_format': 'csv',
                                             'interim_format': 'csv',
                                             'final_format': 'csv',
                                             'file_encoding': 'windows-1252'},
                                   'amicus': {'default_design': 'pipeline',
                                                'default_workflow': 'graph'}})
    skip: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['general', 
                                   'files', 
                                   'amicus', 
                                   'parameters'])

 
@dataclasses.dataclass
class Filer(amicus.Clerk):
    pass  

