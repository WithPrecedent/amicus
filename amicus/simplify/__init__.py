"""
amicus: data science made simple
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    importables (Dict): dict of imports available directly from 'simplify'.
        This dict is needed for the 'lazily_import' function which is called by
        this modules '__getattr__' function.  
        
amicus uses amicus's lazy import system so that subpackages, modules, and
specific objects are not imported until they are first accessed.
   
"""

from __future__ import annotations
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import amicus

__version__ = '0.1.1'

__author__ = 'Corey Rayburn Yung'


""" 
The keys of 'importables' are the attribute names of how users should access
the modules and other items listed in values. 'importables' is necessary for
the lazy importation system used throughout amicus.
"""
importables: Dict[str, str] = {
    'core': 'core',
    'project': 'project',
    'utilities': 'utilities',
    'decorators': 'utilities.decorators',
    'memory': 'utilities.memory',
    'tools': 'utilities.tools',
    'quirks': 'core.quirks',
    'framework': 'core.framework',
    'base': 'core.base',
    'components': 'core.components',
    'externals': 'core.externals',
    'criteria': 'core.criteria',
    'stages': 'core.stages',
    'dataset': 'core.dataset',
    'analyst': 'analyst',
    'artist': 'artist',
    'critic': 'critic',
    'explorer': 'explorer',
    'wrangler': 'wrangler',
    'Core': 'core.base.Core',
    'Component': 'core.base.Component',
    'Outline': 'core.stages.Outline',
    'Workflow': 'core.stages.Workflow',
    'Summary': 'core.stages.Summary',
    'Parameters': 'core.components.Parameters',
    'Step': 'core.components.Step',
    'Technique': 'core.components.Technique',
    'Worker': 'core.components.Worker',
    'Pipeline': 'core.components.Pipeline',
    'Contest': 'core.components.Contest',
    'Study': 'core.components.Study',
    'Survey': 'core.components.Survey',
    'Dataset': 'core.dataset.Dataset',
    'Project': 'core.interface.Project'}


def __getattr__(name: str) -> Any:
    """Lazily imports modules and items within them.
    
    Args:
        name (str): name of amicus module or item.

    Raises:
        AttributeError: if there is no module or item matching 'name'.

    Returns:
        Any: a module or item stored within a module.
        
    """
    return amicus.lazily_import(name = name,
                                   package = __name__, 
                                   mapping = importables)

