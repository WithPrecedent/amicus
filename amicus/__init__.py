"""
amicus: a friend to your python projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    importables (Dict): dict of imports available directly from 'amicus'. This 
        dict is needed for the 'lazily_import' function which is called by this 
        modules '__getattr__' function.
    lazily_import (function): function which imports amicus modules and 
        contained only when such modules and items are first accessed.
        
In general, python files in amicus are over-documented to allow beginning
programmers to understand basic design choices that were made. If there is any
area of the documentation that could be made clearer, please don't hesitate to 
email me - I want to ensure the package is as accessible as possible.

"""
__version__ = '0.1.0'

__author__ = 'Corey Rayburn Yung'


import importlib
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, Optional, Sequence, Tuple, Type, Union)

""" 
amicus imports are designed to allow key classes and functions to have first or 
second-level access.

For example:

    Instead of acccesing Hybrid via amicus.sourdough.types.Hybrid,
    you can just use: amicus.Hybrid
    
They also operate on a lazy importing system. This means that modules are only
imported when first needed. This allows users to only use part of amicus without 
the memory footprint of the entire package. This also avoids some of the 
circular import problems (and the need for solutions to those problems) when the 
package is first initialized. However, this can come at the cost of less than 
clear error messages if your fork of amicus imports classes and objects out of 
order. However, given that python 3.8+ calls almost every import error a 
"circular import," I don't think the error tracebacks are any less confusing in 
amicus. It's possible that this lazy import system will cause trouble for some 
IDEs (such as pycharm) if you choose to fork amicus. However, I have not 
encountered any such issuse using VSCode and its default python linter.

The keys of 'importables' are the attribute names of how users should access
the modules and other items listed in values. 'importables' is necessary for
the lazy importation system used throughout amicus.

"""
importables: Dict[str, str] = {
    'sourdough': 'sourdough',
    'project': 'project',
    'utilities': 'utilities',
    'decorators': 'utilities.decorators',
    'memory': 'utilities.memory',
    'tools': 'utilities.tools',
    'quirks': 'sourdough.quirks',
    'types': 'sourdough.types',
    'options': 'sourdough.options',
    'framework': 'sourdough.framework',
    'structures': 'sourdough.structures',
    'Proxy': 'sourdough.types.Proxy',
    'Bunch': 'sourdough.types.Bunch',
    'Progression': 'sourdough.types.Progression',
    'Hybrid': 'sourdough.types.Hybrid',
    'Lexicon': 'sourdough.types.Lexicon',
    'Catalog': 'sourdough.types.Catalog',
    'Configuration': 'sourdough.options.Configuration',
    'Clerk': 'sourdough.options.Clerk',
    'Keystone': 'sourdough.framework.Keystone',
    'create_keystone': 'sourdough.framework.create_keystone',
    'Validator': 'sourdough.framework.Validator',
    'Converter': 'sourdough.framework.Converter',
    'Structure': 'sourdough.structures.Structure',
    'Graph': 'sourdough.structures.Graph',
    'Project': 'project.interface.Project'}

def __getattr__(name: str) -> Any:
    """Lazily imports modules and items within them.
    
    Args:
        name (str): name of amicus module or item being sought.

    Returns:
        Any: a module or item stored within a module.
        
    """
    return lazily_import(name = name, package = __name__, mapping = importables)

def lazily_import(name: str, package: str, mapping: Dict[str, str]) -> Any:
    """Lazily imports modules and items within them.
    
    Lazy importing means that modules are only imported when they are first
    accessed. This can save memory and keep namespaces decluttered.
    
    This code is adapted from PEP 562: https://www.python.org/dev/peps/pep-0562/
    which outlines how the decision to incorporate '__getattr__' functions to 
    modules allows lazy loading. Rather than place this function solely within
    '__getattr__', it is included here seprately so that it can easily be called 
    by '__init__.py' files throughout amicus and by users (as 
    'amicus.lazily_import').
    
    To effictively use 'lazily_import' in an '__init__.py' file, the user needs
    to also include an 'importables' dict which indicates how users should
    accesss imported modules and included items. This modules includes such an
    example 'importables' dict and how to easily add this function to a 
    '__getattr__' function.
    
    Instead of limiting its lazy imports to full import paths as the example in 
    PEP 562, this function has 2 major advantages:
        1) It allows importing items within modules and not just modules. The
            function first tries to import 'name' assuming it is a module. But 
            if that fails, it parses the last portion of 'name' and attempts to 
            import the preceding module and then returns the item within it.
        2) It allows import paths that are less than the full import path by
            using the 'importables' dict. 'importables' has keys which are the
            name of the attribute being sought and values which are the full
            import path (dropping the leading '.'). 'importables' thus acts
            as the normal import block in an __init__.py file but insures that
            all importing is done lazily.
            
    Args:
        name (str): name of module or item within a module.
        package (str): name of package from which the module is sought.
        mapping (Dict[str, str]): keys are the access names for items sought
            and values are the import path where the item is actually located.
        
    Raises:
        AttributeError: if there is no module or item matching 'name' im 
            'mapping'.
        
    Returns:
        Any: a module or item stored within a module.
        
    """
    if name in mapping:
        key = '.' + mapping[name]
        try:
            return importlib.import_module(key, package = package)
        except ModuleNotFoundError:
            item = key.split('.')[-1]
            module_name = key[:-len(item) - 1]
            module = importlib.import_module(module_name, package = package)
            return getattr(module, item)
    raise AttributeError(f'module {package} has no attribute {name}')   
