"""
interface: amicus project interface
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Project (amicus.Project): main access point and interface for
        creating and implementing data science projects.
    
"""
from __future__ import annotations
import dataclasses
import logging
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import numpy as np
import pandas as pd

from . import base
from . import quirks
from . import stages
import amicus


@dataclasses.dataclass
class Project(quirks.Keystone, amicus.Project):
    """Directs construction and execution of a data science project.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if a 
            amicus instance needs settings from a SimpleConfiguration instance, 
            'name' should match the appropriate section name in a SimpleConfiguration 
            instance. Defaults to None. 
        settings (Union[SimpleSimpleConfiguration, Type[SimpleSimpleConfiguration], 
            pathlib.Path, str, Mapping[str, Mapping[str, Any]]]): a 
            Configuration-compatible subclass or instance, a str or pathlib.Path 
            containing the file path where a file of a supported file type with
            settings for a SimpleConfiguration instance is located, or a 2-level 
            mapping containing settings. Defaults to the default SimpleConfiguration 
            instance.
        filer (Union[SimpleSimpleFiler, Type[SimpleSimpleFiler], pathlib.Path, 
            str]): a SimpleFiler-compatible class or a str or pathlib.Path 
            containing the full path of where the root folder should be located 
            for file input and output. A 'filer' must contain all file path and 
            import/export methods for use throughout amicus. Defaults to the 
            default SimpleFiler instance. 
        identification (str): a unique identification name for an amicus
            Project. The name is used for creating file folders related to the 
            project. If it is None, a str will be created from 'name' and the 
            date and time. Defaults to None.   
        outline (project.Stage): an outline of a project workflow derived from 
            'settings'. Defaults to None.
        workflow (project.Stage): a workflow of a project derived from 
            'outline'. Defaults to None.
        summary (project.Stage): a summary of a project execution derived from 
            'workflow'. Defaults to None.
        automatic (bool): whether to automatically advance 'worker' (True) or 
            whether the worker must be advanced manually (False). Defaults to 
            True.
        data (Any): any data object for the project to be applied. If it is
            None, an instance will still execute its workflow, but it won't
            apply it to any external data. Defaults to None.  
        states (ClassVar[Sequence[Union[str, project.Stage]]]): a list of Stages 
            or strings corresponding to keys in 'keystones.stage.library'. Defaults 
            to a list containing 'outline', 'workflow', and 'summary'.
        validations (ClassVar[Sequence[str]]): a list of attributes that need 
            validating. Defaults to a list of attributes in the dataclass field.
    
    Attributes:
        keystones (ClassVar[amicus.types.Lexicon]): a class attribute containing
            a dictionary of base classes with libraries of subclasses of those 
            keystones classes. Changing this attribute will entirely replace the 
            existing links between this instance and all other base classes.
        
    """
    name: str = None
    settings: Union[base.SimpleConfiguration, 
                    Type[base.SimpleConfiguration], 
                    Mapping[str, Mapping[str, Any]],
                    pathlib.Path, 
                    str] = None
    filer: Union[base.SimpleFiler, 
                 Type[base.SimpleFiler],
                 pathlib.Path, 
                 str] = None
    identification: str = None
    outline: stages.SimpleOutline = None
    workflow: stages.SimpleWorkflow = None
    summary: stages.SimpleStage = None
    automatic: bool = True
    data: Union[str, np.ndarray, pd.DataFrame, pd.Series] = None
    stages: ClassVar[Sequence[Union[str, base.SimpleStage]]] = ['outline', 
                                                                'workflow', 
                                                                'summary']
    validations: ClassVar[Sequence[str]] = ['settings', 
                                            'name', 
                                            'identification', 
                                            'filer']
    
