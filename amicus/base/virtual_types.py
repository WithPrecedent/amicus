"""
types: amicus base types
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

All amicus types have a 'contents' attribute where an item or 'items' are
internally stored. This is used instead of the normal 'data' attribute use in
base python classes to make it easier for users to know which object they are
accessing when using either 'contents' or 'data'.

Contents:
    Proxy (Container): basic wrapper for a stored static or iterable item. 
        Dunder methods attempt to intelligently apply access methods to either 
        the wrapper or the wrapped item.
    Bunch (Iterable, ABC): abstract base class for amicus iterables. All 
        subclasses must have an 'add' method as well as store their contents in 
        the 'contents' attribute.
    Progression (MutableSequence, Bunch): amicus drop-in replacement for list 
        with additional functionality.
    Hybrid (Progression): iterable with both dict and list interfaces and 
        methods that stores items with a 'name' attribute.
    Lexicon (MutableMapping, Bunch): amicus's drop-in replacement for 
        python dicts with some added functionality.
    Catalog (Lexicon): wildcard-accepting dict which is primarily intended for 
        storing different options and strategies. It also returns lists of 
        matches if a list of keys is provided.
    Quirk (ABC): base class for all amicus quirks (described above). Its 
        'quirks' class attribute stores all subclasses.
        
"""
from __future__ import annotations
import abc
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)


@dataclasses.dataclass
class VirtualBase(type, abc.ABC):
    """A meta-metaclass for easy virtual base class implementation.
    
    Args:
        methods (ClassVar[Sequence[str]]): required method names in the class or 
            instance to be checked.
        attributes (ClassVar[Sequence[str]]): required attribute and property
            names in the class or instance to be checked.
            
    """

    methods: ClassVar[Sequence[str]] = []
    attributes: ClassVar[Sequence[str]] = []
    
    def __instancecheck__(cls, instance) -> bool:
        """[summary]

        Args:
            instance ([type]): [description]

        Returns:
            [type]: [description]
            
        """
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, subclass) -> bool:
        """[summary]

        Args:
            subclass ([type]): [description]

        Returns:
            bool: [description]
            
        """
        all_checks = tuple(cls.methods + cls.attributes)
        return (all(hasattr(subclass, a) for a in all_checks)
                and all(callable(subclass, m) for m in cls.methods))


@dataclasses.dataclass   
class Structure(VirtualBase, abc.ABC):
    """A composite structure metaclass for type checking.

    Args:
        methods (ClassVar[Sequence[str]]): required method names in the class or 
            instance to be checked.
        attributes (ClassVar[Sequence[str]]): required attribute and property
            names in the class or instance to be checked.
            
    """
    methods: ClassVar[Sequence[str]] = [
        'add',
        'append',
        'create',
        'extend',
        'join']
    attributes: ClassVar[Sequence[str]] = [
        'edges',
        'endpoints',
        'nodes',
        'paths',
        'roots']


@dataclasses.dataclass   
class Node(VirtualBase, abc.ABC):
    """A composite structure metaclass for type checking.

    Args:
        methods (ClassVar[Sequence[str]]): required method names in the class or 
            instance to be checked.
        attributes (ClassVar[Sequence[str]]): required attribute and property
            names in the class or instance to be checked.
            
    """
    methods: ClassVar[Sequence[str]] = []
    attributes: ClassVar[Sequence[str]] = [
        'contents',
        'name']


@dataclasses.dataclass   
class Executable(VirtualBase, abc.ABC):
    """A composite structure metaclass for type checking.

    Args:
        methods (ClassVar[Sequence[str]]): required method names in the class or 
            instance to be checked.
        attributes (ClassVar[Sequence[str]]): required attribute and property
            names in the class or instance to be checked.
            
    """
    methods: ClassVar[Sequence[str]] = [
        'execute']
    attributes: ClassVar[Sequence[str]] = [
        'contents',
        'iterations',
        'name',
        'parameters']


@dataclasses.dataclass   
class Library(VirtualBase, abc.ABC):
    """A composite structure metaclass for type checking.

    Args:
        methods (ClassVar[Sequence[str]]): required method names in the class or 
            instance to be checked.
        attributes (ClassVar[Sequence[str]]): required attribute and property
            names in the class or instance to be checked.
            
    """
    methods: ClassVar[Sequence[str]] = [
        'add',
        'borrow']
    attributes: ClassVar[Sequence[str]] = [
        'subclasses',
        'instances']


@dataclasses.dataclass   
class Keystone(VirtualBase, abc.ABC):
    """A composite structure metaclass for type checking.

    Args:
        methods (ClassVar[Sequence[str]]): required method names in the class or 
            instance to be checked.
        attributes (ClassVar[Sequence[str]]): required attribute and property
            names in the class or instance to be checked.
            
    """
    methods: ClassVar[Sequence[str]] = [
        'create']
    attributes: ClassVar[Sequence[str]] = [
        'library']

