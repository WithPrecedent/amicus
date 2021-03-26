"""
project: subpackage applying the amicus core to create and implement projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    importables (Dict): dict of imports available directly from 'amicus.'.
        This dict is needed for the 'lazily_import' function which is called by
        this modules '__getattr__' function.
    lazily_import (function): function which imports amicus modules and
        contained only when such modules and items are first accessed.
    
"""
__version__ = '0.1.0'

__author__ = 'Corey Rayburn Yung'


from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Set, Tuple, Type, Union)

import amicus

# from .converters import *
# from .nodes import *
# from .workshop import *

""" 
The keys of 'importables' are the attribute names of how users should access
the modules and other items listed in values. 'importables' is necessary for
the lazy importation system used throughout amicus.
"""
importables: Dict[str, str] = {
    'configuration': 'configuration',
    'core': 'core',
    'interface': 'interface',
    'nodes': 'nodes',
    'workshop': 'workshop',
    'Library': 'nodes.Library',
    'Component': 'nodes.Component',
    'Parameters': 'nodes.Parameters',
    'Leaf': 'nodes.Leaf',
    'Technique': 'nodes.Technique',
    'Step': 'nodes.Step',
    'Worker': 'nodes.Worker',
    'Recipe': 'nodes.Recipe',
    'Hub': 'nodes.Hub',
    'Contest': 'nodes.Contest',
    'Study': 'nodes.Study',
    'Survey': 'nodes.Survey',
    'Summary': 'core.Summary',
    'Result': 'core.Result',
    'Builder': 'interface.Builder',
    }


def __getattr__(name: str) -> Any:
    """Lazily imports modules and items within them.
    
    For further information about how this lazy import system works, read the
    documentation accompanying the 'amicus.lazily_import' function.
    
    Args:
        name (str): name of amicus project module or item.

    Raises:
        AttributeError: if there is no module or item matching 'name'.

    Returns:
        Any: a module or item stored within a module.
        
    """
    return amicus.lazily_import(name = name, 
                                   package = __name__, 
                                   mapping = importables)
    