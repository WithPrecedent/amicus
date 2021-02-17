"""
.. module:: tools
:synopsis: amicus function tools
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""
from __future__ import annotations
import collections.abc
import datetime
import importlib
import inspect
import pathlib
import re
import sys
import textwrap
import typing
from typing import (
    Any, Callable, ClassVar, Iterable, Mapping, Sequence, Tuple, Type, Union)

import more_itertools

# Tries to import numpy and pandas for functions that support those packages.
# Neither is a required dependency and are only listed for optional support.
try:
    import numpy as np
except ImportError:
    pass
try:
    import pandas as pd
except ImportError:
    pass


NEW_LINE = '\n'
INDENT = '    '

""" Conversion/Validation tools """

def classify(
        variable: Any, 
        options: Mapping[Any, Any] = None) -> object:
    """Converts 'variable' to a class, if possible.

    Args:
        variable (Any): variable to create a class out of.
        options (Mapping[Any, Any]): mapping containing str keys and
            classes as values. If 'variable' is a string, the method will seek
            to use it as a key in options. Defaults to None.

    Returns:
        object: a class object, if possible.
        
    """
    if inspect.isclass(variable):
        return variable
    else:
        if options:
            try:
                return options[variable]
            except (KeyError, TypeError):
                pass
        try:
            return variable.__class__
        except AttributeError:
            return variable

def deannotate(annotation: Any) -> Tuple[Any]:
    """Returns type annotations as a tuple.
    
    This allows even complicated annotations with Union to be converted to a
    form that fits with an isinstance call.

    Args:
        annotation (Any): type annotation.

    Returns:
        Tuple[Any]: base level of stored type in an annotation
    
    """
    origin = typing.get_origin(annotation)
    args = typing.get_args(annotation)
    if origin is Union:
        return tuple(deannotate(a)[0] for a in args)
    elif origin is None:
        return annotation
    else:
        return typing.get_args(annotation)
            
def delistify(
        variable: Any,
        default_value: Any = None) -> Sequence[Any]:
    """

    """
    if variable is None:
        if default_value is None:
            return []
        elif default_value in ['None', 'none']:
            return None
        else:
            return default_value
    elif isinstance(variable, list):
        return variable[0]
    else:
        return variable
          
def importify(module: str, key: str) -> object:
    """Lazily loads object from 'module'.

    Args:
        module (str): name of module holding object that is sought.
        key (str): name of object sought.

    Raises:
        ImportError: if 'key' is not found in 'module'.

    Returns:
        object: class, function, or variable in 'module'.
        
    """
    try:
        return getattr(importlib.import_module(module), key)
    except (ImportError, AttributeError):
        raise ImportError(f'failed to load {key} in {module}')

def importify_file(
        module: str, 
        file_path: Union[pathlib.Path, str] = None, 
        key: str = None) -> object:
    """Lazily loads 'module' or object from 'module'.

    If 'file_path' is passed, this function will import the python module from
    that path.

    Args:
        module (str): name of module holding object that is sought.
        file_path (pathlib.Path, str): file path where the python module is
            located. Defaults to None.
        key (str): name of object within 'module' that is sought. Defaults to 
            None.

    Raises:
        ImportError: if 'key' is not found in 'module'.

    Returns:
        object: class, function, or variable in 'module'.
        
    """
    if file_path:
        try:
            spec = importlib.util.spec_from_file_location(module, file_path)
            loaded = importlib.util.module_from_spec(spec)
            sys.modules[module] = loaded
            spec.loader.exec_module(loaded)
        except (ImportError, AttributeError):
            raise ImportError(f'failed to load {module} in {file_path}')   
    else:
        try:
            loaded = importlib.import_module(module)
        except (ImportError, AttributeError):
            raise ImportError(f'failed to load {key} in {module}')
    if key:
        try:
            loaded = getattr(loaded, key)
        except AttributeError:
            raise ImportError(f'{key} not found in {module}')
    return loaded
             
def instancify(
        variable: Any, 
        options: Mapping[Any, Any] = None,
        **kwargs) -> object:
    """Converts 'variable' to a class instance with 'kwargs' as parameters.

    Args:
        variable (Any): variable to create an instance out of.
        options (Mapping[Any, Any]]): mapping containing str keys and
            classes as values. If 'variable' is a string, the method will seek
            to use it as a key in options. Defaults to None.

    Returns:
        object: a class instance, if possible.
        
    """
    if options:
        try:
            variable = options[variable]
        except (KeyError, TypeError):
            pass           
    if inspect.isclass(variable):
        return variable(**kwargs)
    else:
        return variable
            
def listify(
        variable: Any,
        default_value: Any = None) -> Sequence[Any]:
    """Returns passed variable as a list (if not already a list).

    Args:
        variable (any): variable to be transformed into a list to allow proper
            iteration.
        default_value (Any): the default value to return if 'variable' is None.
            Unfortunately, to indicate you want None to be the default value,
            you need to put 'None' in quotes. If not passed, 'default_value'
            is set to [].

    Returns:
        Sequence[Any]: a passed list, 'variable' converted to a list, or 
            'default_value'.

    """
    if variable is None:
        if default_value is None:
            return []
        elif default_value in ['None', 'none']:
            return None
        else:
            return default_value
    elif isinstance(variable, list) and not isinstance(variable, str):
        return variable
    else:
        return [variable]

def numify(variable: str) -> Union[int, float, str]:
    """Attempts to convert 'variable' to a numeric type.
    
    If 'variable' cannot be converted to a numeric type, it is returned as is.

    Args:
        variable (str): variable to be converted.

    Returns
        variable (int, float, str) converted to numeric type, if possible.

    """
    try:
        return int(variable)
    except ValueError:
        try:
            return float(variable)
        except ValueError:
            return variable

def pathlibify(path: Union[str, pathlib.Path]) -> pathlib.Path:
    """Converts string 'path' to pathlib.pathlib.Path object.

    Args:
        path (Union[str, pathlib.Path]): either a string representation of a
            path or a pathlib.Path object.

    Returns:
        pathlib.Path object.

    Raises:
        TypeError if 'path' is neither a str or pathlib.Path type.

    """
    if isinstance(path, str):
        return pathlib.Path(path)
    elif isinstance(path, pathlib.Path):
        return path
    else:
        raise TypeError('path must be str or pathlib.Path type')

def representify(item: Any, package: str = 'amicus') -> str:
    """[summary]

    Args:
        item (Any): [description]

    Returns:
        str: [description]
    """
    representation = [f'{NEW_LINE}{package} {item.__class__.__name__}']
    representation.append(f'name: {item.name}')
    attributes = [a for a in item.__dict__ if not a.startswith('_')]
    attributes.remove('name')
    if hasattr(item, 'identification'):
        representation.append(f'identification: {item.identification}')
        attributes.remove('identification')
    for attribute in attributes:
        stored = getattr(item, attribute)
        if isinstance(stored, dict):
            for key, value in stored.items():
                representation.append(
                    textwrap.indent(f'{key}: {value}', INDENT))
        elif isinstance(stored, (list, tuple, set)):
            line = [f'{attribute}:']
            for key in stored:
                line.append(f'{str(key)}')
            representation.append(' '.join(line))
        # elif isinstance(stored, str):
        #     representation.append(item)
        else:
            representation.append(str(stored))
    return NEW_LINE.join(representation)     

def snakify(item: str) -> str:
    """Converts a capitalized word name to snake case.

    Args:
        item (str): string to convert.

    Returns:
        str: 'item' converted to snake case.

    """
    item = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', item)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', item).lower()

def stringify(
        variable: Union[str, Sequence],
        default_null: bool = False,
        default_empty: bool = False) -> str:
    """Converts one item list to a string (if not already a string).

    Args:
        variable (str, list): variable to be transformed into a string.
        default_null (boolean): whether to return None (True) or ['none']
            (False).

    Returns:
        variable (str): either the original str, a string pulled from a
            one-item list, or the original list.

    """
    if variable is None:
        if default_null:
            return None
        elif default_empty:
            return []
        else:
            return ['none']
    elif isinstance(variable, str):
        return variable
    else:
        try:
            return variable[0]
        except TypeError:
            return variable

def subsetify(
    dictionary: Mapping[Any, Any],
    subset: Union[Any, Sequence[Any]]) -> Mapping[Any, Any]:
    """Returns a subset of a dictionary.

    The returned subset is a dictionary with keys in 'subset'.

    Args:
        dictionary (MutableMapping[Any, Any]): dict to be subsetted.
        subset (Union[Any, Sequence[Any]]): key(s) to get key/value pairs from
            'dictionary'.

    Returns:
        Mapping[Any, Any]: with only keys in 'subset'

    """
    return {key: dictionary[key] for key in listify(subset)}

def tuplify(
        variable: Any,
        default_value: Any = None) -> Tuple[Any]:
    """Returns passed variable as a tuple (if not already a tuple).

    Args:
        variable (Any): variable to be transformed into a tuple.
        default_value (Any): the default value to return if 'variable' is None.
            Unfortunately, to indicate you want None to be the default value,
            you need to put 'None' in quotes. If not passed, 'default_value'
            is set to ().

    Returns:
        Tuple[Any]: a passed tuple, 'variable' converted to a tuple, or 
            'default_value'.

    """
    if variable is None:
        if default_value is None:
            return ()
        elif default_value in ['None', 'none']:
            return None
        else:
            return default_value
    elif isinstance(variable, tuple) and not isinstance(variable, str):
        return variable
    else:
        return tuple(variable)
        
def typify(variable: str) -> Union[Sequence, int, float, bool, str]:
    """Converts stingsr to appropriate, supported datatypes.

    The method converts strings to list (if ', ' is present), int, float,
    or bool datatypes based upon the content of the string. If no
    alternative datatype is found, the variable is returned in its original
    form.

    Args:
        variable (str): string to be converted to appropriate datatype.

    Returns:
        variable (str, list, int, float, or bool): converted variable.

    """
    if not isinstance(variable, str):
        return variable
    try:
        return int(variable)
    except ValueError:
        try:
            return float(variable)
        except ValueError:
            if variable.lower() in ['true', 'yes']:
                return True
            elif variable.lower() in ['false', 'no']:
                return False
            elif ', ' in variable:
                variable = variable.split(', ')
                return [numify(item) for item in variable]
            else:
                return variable

def validate(
    item: Any,
    types: Sequence[Callable],
    allow_lists: bool = False,
    allow_dicts: bool = False) -> Any:
    """Type checks 'item' based upon other arguments passed.
    
    Args:
    
    Raises:
        TypeError: if 'item' is not of the right datatype(s).
    
    Returns:

    """
    if isinstance(item, types):
        return item
    elif (allow_lists
            and isinstance(item, Sequence)
            and all(isinstance(i, types) for i in item)):
        return item
    elif (allow_dicts
            and isinstance(item, Mapping)
            and all(isinstance(i, types) for i in item.values())):
        return item
    else:
        raise TypeError(f'{item} must be {str(types)}')

""" Other tools """

def add_prefix(
        iterable: Union[Mapping[str, Any], Sequence[str]],
        prefix: str) -> Union[Mapping[str, Any], Sequence[str]]:
    """Adds prefix to each item in a list or keys in a dict.

    An underscore is automatically added after the string prefix.

    Args:
        iterable (list(str) or dict(str: any)): iterable to be modified.
        prefix (str): prefix to be added.

    Returns:
        list or dict with prefixes added.

    """
    try:
        return {prefix + '_' + k: v for k, v in iterable.items()}
    except AttributeError:
        return [prefix + '_' + item for item in iterable]

def add_suffix(
        iterable: Union[Mapping[str, Any], Sequence[str]],
        suffix: str) -> Union[Mapping[str, Any], Sequence[str]]:
    """Adds suffix to each item in a list or keys in a dict.

    An underscore is automatically added after the string suffix.

    Args:
        iterable (list(str) or dict(str: any)): iterable to be modified.
        suffix (str): suffix to be added.

    Returns:
        list or dict with suffixes added.

    """
    try:
        return {k + '_' + suffix: v for k, v in iterable.items()}
    except AttributeError:
        return [item + '_' + suffix for item in iterable]

def datetime_string(prefix: str = None) -> str:
    """Creates a string from current date and time.

    Returns:
        str with current date and time in Y/M/D/H/M format.

    """
    if prefix is None:
        prefix = ''
    time_string = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    return f'{prefix}_{time_string}'

def deduplicate(
    iterable: Union[Sequence, pd.DataFrame, pd.Series]) -> (
        Union[Sequence, pd.DataFrame, pd.Series]):
    """Deduplicates list, pandas DataFrame, or pandas Series.

    Args:
        iterable (list, DataFrame, or Series): iterable to have duplicate
            entries removed.

    Returns:
        iterable (list, DataFrame, or Series, same as passed type):
            iterable with duplicate entries removed.

    """
    if isinstance(iterable, list):
        return list(set(iterable))
    elif isinstance(iterable, (pd.DataFrame, pd.Series)):
        return iterable.drop_duplicates(inplace = True)
    else:
        return iterable

         
def divide_string(item: str, divider: str = None) -> Tuple[str, str]:
    """[summary]

    Args:
        key (str): [description]

    Returns:
        
        Tuple[str, str]: [description]
        
    """
    if divider is None:
        divider = '_'
    if divider in item:
        suffix = item.split(divider)[-1]
        prefix = item[:-len(suffix) - 1]
    else:
        prefix = suffix = item
    return prefix, suffix


def drop_prefix(
        iterable: Union[Mapping[str, Any], Sequence[str]],
        prefix: str) -> Union[Mapping[str, Any], Sequence[str]]:
    """Drops prefix from each item in a list or keys in a dict.

    Args:
        iterable (list(str) or dict(str: any)): iterable to be modified.
        prefix (str): prefix to be dropped

    Returns:
        list or dict with prefixes dropped.

    """
    try:
        return {k.rstrip(prefix): v for k, v in iterable.items()}
    except AttributeError:
        return [item.rstrip(prefix) for item in iterable]
    
def drop_suffix(
        iterable: Union[Mapping[str, Any], Sequence[str]],
        suffix: str) -> Union[Mapping[str, Any], Sequence[str]]:
    """Drops suffix from each item in a list or keys in a dict.

    Args:
        iterable (list(str) or dict(str: any)): iterable to be modified.
        suffix (str): suffix to be dropped

    Returns:
        list or dict with suffixes dropped.

    """
    try:
        return {k.rstrip(suffix): v for k, v in iterable.items()}
    except AttributeError:
        return [item.rstrip(suffix) for item in iterable]

def isiterable(item: Any) -> bool:
    """Returns if 'item' is iterable but is NOT a str type.

    Args:
        item (Any): object to be tested.

    Returns:
        bool: indicating whether 'item' is iterable but is not a str.

    """
    return (isinstance(item, collections.abc.Iterable) 
            and not isinstance(item, str))

def isnested(dictionary: Mapping[Any, Any]) -> bool:
    """Returns if passed 'contents' is nested at least one-level.

    Args:
        dictionary (dict): dict to be tested.

    Returns:
        bool: indicating whether any value in the 'contents' is also a
            dict (meaning that 'contents' is nested).

    """
    return any(isinstance(v, dict) for v in dictionary.values())

def propertify(
        instance: object,
        name: str,
        getter: Callable,
        setter: Callable,
        deleter: Callable) -> object:
    """Adds 'name' property to 'instance' at runtime.

    Args:
        instance (object): instance to add a property to.
        name (str): name that the new property should be given.
        getter (Callable): getter method for the new property.
        setter (Callable]): setter method for the new property.
        deleter (Callable]): deleter method for the new property.

    Returns:
        object: with new 'name' property added.

    """
    def _bind_process(process: Callable, instance: object) -> Callable:
        """Binds 'process' to 'instance'.

        Args:
            process (Callable): function, method in 'instance' or method in
                another class instance.
            instance (object): class instance to bind 'process to'.

        Returns:
            Callable: appropriate process object.

        """
        if process.im_self is not None:
            if process.__name__ in instance.__dict__:
                return process
            else:
                setattr(instance, process.__name__, process)
                return getattr(instance, process.__name__)
        else:
            types.MethodType(process, instance, instance.__class__)
            return getattr(instance, process.__name__)

    def _property_not_implemented() -> NotImplemented:
        raise NotImplemented(f'property method is not implemented')

    if setter and deleter:
        setattr(instance, name, property(
            fget = _bind_process(process = getter, instance = instance),
            fset = _bind_process(process = setter, instance = instance),
            fdel = _bind_process(process = deleter, instance = instance)))
    elif setter:
        setattr(instance, name, property(
            fget = _bind_process(process = getter, instance = instance),
            fset = _bind_process(process = setter, instance = instance),
            fdel = _property_not_implemented))
    elif deleter:
        setattr(instance, name, property(
            fget = _bind_process(process = getter, instance = instance),
            fset = _property_not_implemented,
            fdel = _bind_process(process = deleter, instance = instance)))
    else:
        setattr(instance, name, property(
            fget = _bind_process(process = getter, instance = instance)),
            fset = _property_not_implemented,
            fdel = _property_not_implemented)
    return instance


""" Decorators """

def timer(process: str = None) -> Callable:
    """Decorator for computing the length of time a process takes.

    Args:
        process (str): name of class or method to be used in the
            output describing time elapsed.

    """
    if not process:
        if isinstance(process, types.FunctionType):
            process = process.__class__.__name__
        else:
            process = process.__class__.__name__
    def shell_timer(_function):
        def decorated(*args, **kwargs):
            def convert_time(seconds: int) -> tuple(int, int, int):
                minutes, seconds = divmod(seconds, 60)
                hours, minutes = divmod(minutes, 60)
                return hours, minutes, seconds
            implement_time = time.time()
            result = _function(*args, **kwargs)
            total_time = time.time() - implement_time
            h, m, s = convert_time(total_time)
            print(f'{process} completed in %d:%02d:%02d' % (h, m, s))
            return result
        return decorated
    return shell_timer
