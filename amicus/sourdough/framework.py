"""
framework:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)


Contents:
    Library (object):
    Keystone (Quirk, ABC):
    create_keystone (FunctionType):
    Validator (Quirk):
    Converter (ABC):

ToDo:
    Validator support for complex types like List[List[str]]
    Add deannotation ability to Validator to automatically determine needed
        converters
    
"""
from __future__ import annotations
import abc
import copy
import dataclasses
import inspect
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, Optional, Sequence, Set, Tuple, Type, Union)
# from typing import get_args, get_origin

import more_itertools

import amicus


@dataclasses.dataclass
class Registry(amicus.types.Catalog):
    """A Catalog of Keystone subclasses."""

    """ Properties """
    
    @property
    def suffixes(self) -> tuple[str]:
        """Returns all subclass names with an 's' added to the end.
        
        Returns:
            tuple[str]: all subclass names with an 's' added in order to create
                simple plurals.
                
        """
        return tuple(key + 's' for key in self.contents.keys())


@dataclasses.dataclass
class Library(object):
    """A set of Keystone subclasses."""
    
    """ Public Methods """

    def register(self, name: str, keystone: Keystone) -> None:
        """[summary]

        Args:
            name (str): [description]
            keystone (Keystone): [description]

        """
        keystone.instances = amicus.types.Catalog()
        keystone.subclasses = Registry()
        setattr(self, name, keystone)
        return self

    def remove(self, name: str) -> None:
        """[summary]

        Args:
            name (str): [description]

        """
        delattr(self, name)
        return self


@dataclasses.dataclass
class Keystone(amicus.types.Quirk, abc.ABC):
    """Base mixin for automatic registration of subclasses and instances. 
    
    Any concrete (non-abstract) subclass will automatically store itself in the 
    class attribute 'subclasses' using the snakecase name of the class as the 
    key.
    
    Any direct subclass will automatically store itself in the class attribute 
    'library' using the snakecase name of the class as the key.
    
    Any instance of a subclass will be stored in the class attribute 'instances'
    as long as '__post_init__' is called (either by a 'super()' call or if the
    instance is a dataclass and '__post_init__' is not overridden).
    
    Args:
        library (ClassVar[Library]): library that stores direct subclasses 
            (those with Keystone in their '__bases__' attribute) and allows 
            runtime access and instancing of those stored subclasses.
    
    Attributes:
        subclasses (ClassVar[amicus.types.Catalog]): catalog that stores 
            concrete subclasses and allows runtime access and instancing of 
            those stored subclasses. 'subclasses' is automatically created when 
            a direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced.
        instances (ClassVar[amicus.types.Catalog]): catalog that stores
            subclass instances and allows runtime access of those stored 
            subclass instances. 'instances' is automatically created when a 
            direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced. 
                      
    Namespaces: 
        library, subclasses, instances, select, instance, __init_subclass__
    
    """
    library: ClassVar[Library] = Library()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to appropriate class libraries."""
        super().__init_subclass__(**kwargs)
        # Creates a snakecase key of the class name.
        key = amicus.tools.snakify(cls.__name__)
        # Adds class to 'library' if it is a base class.
        if Keystone in cls.__bases__:
            # Registers a new Keystone.
            cls.library.register(name = key, keystone = cls)
        # Adds concrete subclasses to 'library' using 'key'.
        if not abc.ABC in cls.__bases__:
            cls.subclasses[key] = cls

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        try:
            key = self.name
        except AttributeError:
            key = amicus.tools.snakify(self.__class__.__name__)
        self.instances[key] = self

    """ Class Methods """
    
    @classmethod
    def select(cls, name: Union[str, Sequence[str]]) -> Type[Keystone]:
        """Returns matching subclass from 'subclasses.
        
        Args:
            name (Union[str, Sequence[str]]): name of item in 'subclasses' to
                return
            
        Raises:
            KeyError: if no match is found for 'name' in 'subclasses'.
            
        Returns:
            Type[Keystone]: stored Keystone subclass.
            
        """
        item = None
        for key in more_itertools.always_iterable(name):
            try:
                item = cls.subclasses[key]
                break
            except KeyError:
                pass
        if item is None:
            raise KeyError(f'No matching item for {str(name)} was found') 
        else:
            return item
    
    @classmethod
    def instance(cls, name: Union[str, Sequence[str]], **kwargs) -> Keystone:
        """Returns match from 'instances' or 'subclasses'.
        
        The method prioritizes 'instances' before 'subclasses'. If a match is
        found in 'subclasses', 'kwargs' are passed to instance the matching
        subclass. If a match is found in 'instances', the 'kwargs' are manually
        added as attributes to the matching instance.
        
        Args:
            name (Union[str, Sequence[str]]): name of item in 'instances' or 
                'subclasses' to return.
            
        Raises:
            KeyError: if no match is found for 'name' in 'instances' or 
                'subclasses'.
            
        Returns:
            Keystone: stored Keystone subclass instance.
            
        """
        item = None
        for key in more_itertools.always_iterable(name):
            for library in ['instances', 'subclasses']:
                try:
                    item = getattr(cls, library)[key]
                    break
                except KeyError:
                    pass
            if item is not None:
                break
        if item is None:
            raise KeyError(f'No matching item for {str(name)} was found') 
        elif inspect.isclass(item):
            return cls(name = name, **kwargs)
        else:
            instance = copy.deepcopy(item)
            for key, value in kwargs.items():
                setattr(instance, key, value)
            return instance


def create_keystone(
        keystone: Union[str, Keystone] = object, 
        name: str = None, 
        quirks: Union[
            str, 
            amicus.types.Quirk, 
            Sequence[str],
            Sequence[amicus.types.Quirk]] = None) -> Keystone:
    """[summary]

    Args:
        keystone (Union[str, Keystone], optional): [description]. Defaults to 
            object.
        name (str, optional): [description]. Defaults to None.
        quirks (Union[ str, amicus.types.Quirk, Sequence[str], 
            Sequence[amicus.types.Quirk]], optional): Defaults to None.

    Raises:
        ValueError: [description]
        TypeError:
        
    Returns:
        Keystone: [description]
        
    """
    bases = []
    for quirk in more_itertools.always_iterable(quirks):
        if isinstance(quirk, str):
            bases.append(amicus.types.Quirk.quirks[quirk])
        elif isinstance(quirk, amicus.types.Quirk):
            bases.append(quirk)
        else:
            raise TypeError('All quirks must be str or Quirk type')
    if keystone is not object and name is None:
        raise ValueError('name must not be None is keystone is object')
    elif isinstance(keystone, str):
        bases.append(Keystone.library[keystone])
    elif isinstance(keystone, Keystone):
        bases.append(keystone)
    else:
        raise TypeError('keystone must be a str, Keystone type, or object')
    creation = dataclasses.dataclass(type(name, tuple(bases), {}))
    if keystone is object:
        Keystone.library[name] = creation
    return creation
        

@dataclasses.dataclass
class Validator(amicus.types.Quirk):
    """Mixin for calling validation methods

    Args:
        validations (List[str]): a list of attributes that need validating.
            Each item in 'validations' should have a corresponding method named 
            f'_validate_{name}' or match a key in 'converters'. Defaults to an 
            empty list. 
        converters (amicus.types.Catalog):
               
    """
    validations: ClassVar[Sequence[str]] = []
    converters: ClassVar[amicus.types.Catalog] = amicus.types.Catalog()

    """ Public Methods """

    def validate(self, validations: Sequence[str] = None) -> None:
        """Validates or converts stored attributes.
        
        Args:
            validations (List[str]): a list of attributes that need validating.
                Each item in 'validations' should have a corresponding method 
                named f'_validate_{name}' or match a key in 'converters'. If not 
                passed, the 'validations' attribute will be used instead. 
                Defaults to None. 
        
        """
        if validations is None:
            validations = self.validations
        # Calls validation methods based on names listed in 'validations'.
        for name in validations:
            if hasattr(self, f'_validate_{name}'):
                kwargs = {name: getattr(self, name)}
                validated = getattr(self, f'_validate_{name}')(**kwargs)
            else:
                converter = self._initialize_converter(name = name)
                try:
                    validated = converter.validate(
                        item = getattr(self, name),
                        instance = self)
                except AttributeError:
                    validated = getattr(self, name)
            setattr(self, name, validated)
        return self     

#     def deannotate(self, annotation: Any) -> tuple[Any]:
#         """Returns type annotations as a tuple.
        
#         This allows even complicated annotations with Union to be converted to a
#         form that fits with an isinstance call.

#         Args:
#             annotation (Any): type annotation.

#         Returns:
#             tuple[Any]: base level of stored type in an annotation
        
#         """
#         origin = get_origin(annotation)
#         args = get_args(annotation)
#         if origin is Union:
#             accepts = tuple(self.deannotate(a)[0] for a in args)
#         else:
#             self.stores = origin
#             accepts = get_args(annotation)
#         return accepts

    """ Private Methods """
    
    def _initialize_converter(self, name: str) -> Converter:
        """[summary]

        Args:
            converter (Union[Converter, Type[Converter]]): [description]

        Returns:
            Converter: [description]
        """
        try:
            converter = self.converters[name]
        except KeyError:
            raise KeyError(
                f'No local or stored type validator exists for {name}')
        return converter()             


@dataclasses.dataclass
class Converter(abc.ABC):
    """Keystone class for type converters and validators.

    Args:
        base (str): 
        parameters (Dict[str, Any]):
        alternatives (tuple[Type])
        
    """
    base: str = None
    parameters: Dict[str, Any] = dataclasses.field(default_factory = dict)
    alterantives: tuple[Type] = dataclasses.field(default_factory = tuple)
    default: Type = None

    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'Validator.converters' if it is a concrete class."""
        super().__init_subclass__(**kwargs)
        if not abc.ABC in cls.__bases__:
            key = amicus.tools.snakify(cls.__name__)
            # Removes '_converter' from class name so that the key is consistent
            # with the key name for the class being constructed.
            try:
                key = key.replace('_converter', '')
            except ValueError:
                pass
            Validator.converters[key] = cls
                       
    """ Public Methods """

    def validate(self, item: Any, instance: object) -> object:
        """[summary]

        Args:
            item (Any): [description]
            instance (object): [description]

        Raises:
            TypeError: [description]
            AttributeError: [description]

        Returns:
            object: [description]
            
        """ 
        if hasattr(instance, 'library') and instance.library is not None:
            kwargs = {
                k: self._kwargify(v, instance, item) 
                for k, v in self.parameters.items()}
            try:
                base = getattr(instance.library, self.base)
                if item is None:
                    validated = base(**kwargs)
                elif isinstance(item, base):
                    validated = item
                    for key, value in kwargs.items():
                        setattr(validated, key, value)
                elif inspect.isclass(item) and issubclass(item, base):
                    validated = item(**kwargs)
                elif (isinstance(item, str) 
                        or isinstance(item, List)
                        or isinstance(item, Tuple)):
                    validated = base.library.select(names = item)(**kwargs)
                elif isinstance(item, self.alternatives) and self.alternatives:
                    validated = base(item, **kwargs)
                else:
                    raise TypeError(
                        f'{item} could not be validated or converted')
            except AttributeError:
                validated = self.default(**kwargs)
        else:
            try:
                validated = self.default(**kwargs)
            except (TypeError, ValueError):
                raise AttributeError(
                    f'Cannot validate or convert {item} without library')
        return validated

    """ Private Methods """
    
    def _kwargify(self, attribute: str, instance: object, item: Any) -> Any:
        """[summary]

        Args:
            attribute (str): [description]
            instance (object): [description]
            item (Any): [description]

        Returns:
            Any: [description]
            
        """
        if attribute in ['self']:
            return instance
        elif attribute in ['str']:
            return item
        else:
            return getattr(instance, attribute)
