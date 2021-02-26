"""
framework:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)


Contents:
    Keystone (Quirk, ABC): base class to be used for all subclasses that wish 
        to use amicus's automatic subclass registration system.
    Validator (Quirk):
    Converter (ABC):

ToDo:
    Update Workshop to the current amicus version.
    Support complex types like List[List[str]]
    Automatically validate types from annotations using 'get_args' and 
        'get_origin'
    
"""
from __future__ import annotations
import abc
import copy
import dataclasses
import inspect
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union, get_args, 
                    get_origin)

import more_itertools

import amicus


@dataclasses.dataclass
class Keystone(amicus.types.Quirk, abc.ABC):
    """Base mixin for automatic registration of subclasses and instances. 
    
    Any concrete (non-abstract) subclass will automatically store itself in the 
    class attribute 'subclasses' using the snakecase name of the class as the 
    key.
    
    Any direct subclass will automatically store itself in the class attribute 
    'keystones' using the snakecase name of the class as the key.
    
    Any instance of a subclass will be stored in the class attribute 'instances'
    as long as '__post_init__' is called (either by a 'super()' call or if the
    instance is a dataclass and '__post_init__' is not overridden).
    
    Args:
        keystones (ClassVar[amicus.framework.Library]): library that stores 
            direct subclasses (those with Keystone in their '__bases__' 
            attribute) and allows runtime access and instancing of those stored 
            subclasses.
    
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
        keystones, subclasses, instances, select, instance, __init_subclass__
    
    """
    keystones: ClassVar[amicus.framework.Library] = amicus.framework.Library()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to appropriate class libraries."""
        super().__init_subclass__(**kwargs)
        # Creates a snakecase key of the class name.
        key = amicus.tools.snakify(cls.__name__)
        # Adds class to 'keystones' if it is a base class.
        if Keystone in cls.__bases__:
            # Creates libraries on this class base for storing subclasses.
            cls.subclasses = amicus.types.Catalog()
            cls.instances = amicus.types.Catalog()
            # Adds this class to 'keystones' using 'key'.
            cls.keystones.register(name = key, item = cls)
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
 
    """ Public Class Methods """
    
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

    def initialize_converter(self, name: str,
            converter: Union[str, Converter, Type[Converter]]) -> Converter:
        """[summary]

        Args:
            converter (Union[Converter, Type[Converter]]): [description]

        Returns:
            Converter: [description]
        """
        if isinstance(converter, str):
            try:
                converter = self.converters[name]
            except KeyError:
                raise KeyError(
                    f'No local or stored type validator exists for {name}')
        if not isinstance(converter, Converter):
            converter = converter()
            self.converters[name] = converter  
        return converter     

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
                converter = self.initialize_converter(
                    name = name, 
                    converter = name)
                try:
                    validated = converter.validate(
                        item = getattr(self, name),
                        instance = self)
                except AttributeError:
                    validated = getattr(self, name)
            setattr(self, name, validated)
        return self     

#     def deannotate(self, annotation: Any) -> Tuple[Any]:
#         """Returns type annotations as a tuple.
        
#         This allows even complicated annotations with Union to be converted to a
#         form that fits with an isinstance call.

#         Args:
#             annotation (Any): type annotation.

#         Returns:
#             Tuple[Any]: base level of stored type in an annotation
        
#         """
#         origin = get_origin(annotation)
#         args = get_args(annotation)
#         if origin is Union:
#             accepts = tuple(self.deannotate(a)[0] for a in args)
#         else:
#             self.stores = origin
#             accepts = get_args(annotation)
#         return accepts
           

@dataclasses.dataclass
class Converter(abc.ABC):
    """Keystone class for type converters and validators.

    Args:
        base (str): 
        parameters (Dict[str, Any]):
        alternatives (Tuple[Type])
        
    """
    base: str = None
    parameters: Dict[str, Any] = dataclasses.field(default_factory = dict)
    alterantives: Tuple[Type] = dataclasses.field(default_factory = tuple)

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
        if hasattr(instance, 'keystones') and instance.keystones is not None:
            base = getattr(instance.keystones, self.base)
            kwargs = {k: self._kwargify(v, instance, item) 
                      for k, v in self.parameters.items()}
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
                validated = base.library.borrow(names = item)(**kwargs)
            elif isinstance(item, self.alternatives) and self.alternatives:
                validated = base(item, **kwargs)
            else:
                raise TypeError(f'{item} could not be validated or converted')
        else:
            raise AttributeError(
                f'Cannot validate or convert {item} without keystones and base')
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
        

# @dataclasses.dataclass
# class Workshop(object):
#     """
#     """
#     bases: Library = Library()
#     quirks: Library = Quirk.quirks

#     """ Public Methods """
    
#     def create_bases(self) -> None:
#         """[summary]

#         Returns:
#             [type]: [description]
#         """
#         quirks = self._get_settings_quirks()
#         for key, value in self.manager.project.bases.items():
#             self.contents[key] = self.create_class(
#                 name = key, 
#                 base = value, 
#                 quirks = quirks)
#         return self
            
#     def create_class(self, name: str, base: Callable, 
#                      quirks: Sequence[sourdough.Quirk]) -> Callable:
#         """[summary]

#         Args:
#             name (str): [description]
#             base (Callable): [description]
#             quirks (Sequence[sourdough.Quirk])

#         Returns:
#             Callable: [description]
            
#         """
#         if quirks:
#             bases = quirks.append(base)
#             new_base = dataclasses.dataclass(type(name, tuple(bases), {}))
#             # Recursively adds quirks to items in the 'registry' of 'base'.
#             if hasattr(base, 'registry'):
#                 newregistry = {}
#                 for key, value in base.registry.items():
#                     newregistry[key] = self.create_class(
#                         name = key,
#                         base = value,
#                         quirks = quirks)
#                 new_base.registry = newregistry
#         else:
#             new_base = base
#         return new_base
             
#     """ Private Methods """
    
#     def _get_settings_quirks(self) -> Sequence[sourdough.Quirk]:
#         """[summary]

#         Returns:
#             Sequence[sourdough.Quirk]: [description]
            
#         """
#         settings_keys = {
#             'verbose': 'talker', 
#             'early_validation': 'validator', 
#             'conserve_memory': 'conserver'}
#         quirks = []
#         for key, value in settings_keys.items():
#             try:
#                 if self.manager.project.settings['general'][key]:
#                     quirks.append(sourdough.Quirk.options[value])
#             except KeyError:
#                 pass
#         return quirks

 



# @dataclasses.dataclass
# class Mapify(Validator):
#     """Type validator and converter for Mappings.

#     Attributes:
#         accepts (Tuple[Any]): type(s) accepted by the parent class either as an 
#             individual item, in a Mapping, or in a Sequence.
#         stores (Any): a single type stored by the parent class. Set to dict.
            
#     """    

#     """ Initialization Methods """
    
#     def __post_init__(self):
#         """Registers an instance with 'contents'."""
#         # Calls initialization method of other inherited classes.
#         try:
#             super().__post_init__()
#         except AttributeError:
#             pass
#         self.stores = dict
    
#     """ Public Methods """
    
#     def convert(self, contents: Any) -> (Mapping[str, Any]):
#         """Converts 'contents' to a Mapping type.
        
#         Args:
#             contents (Any): an object containing item(s) with 'name' attributes.
                
#         Returns:
#             Mapping[str, Any]: converted 'contents'.
            
#         """
#         contents = self.verify(contents = contents)
#         converted = {}
#         if isinstance(contents, Mapping):
#             converted = contents
#         elif (isinstance(contents, Sequence) 
#                 and not isinstance(contents, str)
#                 and all(hasattr(i, 'name') for i in contents)):
#             for item in contents:
#                 try:
#                     converted[item.name] = item
#                 except AttributeError:
#                     converted[item.get_name()] = item
#         return converted
    

# @dataclasses.dataclass    
# class Sequencify(Validator):
#     """Type validator and converter for Sequences.
    
#     Args:
#         accepts (Union[Sequence[Any], Any]): type(s) accepted by the parent 
#             class either as an individual item, in a Mapping, or in a Sequence.
#             Defaults to amicus.quirks.Element.
#         stores (Any): a single type accepted by the parent class. Defaults to 
#             list.
            
#     """        

#     """ Initialization Methods """
    
#     def __post_init__(self):
#         """Registers an instance with 'contents'."""
#         # Calls initialization method of other inherited classes.
#         try:
#             super().__post_init__()
#         except AttributeError:
#             pass
#         self.stores = list
    
#     """ Public Methods """
       
#     def convert(self, 
#             contents: Any) -> (
#                 Sequence[amicus.quirks.Element]):
#         """Converts 'contents' to a Sequence type.
        
#         Args:
#             contents (Any): an object containing one or 
#                 more Element subclasses or Element subclass instances.
        
#         Raises:
#             TypeError: if 'contents' is not an Any.
                
#         Returns:
#             Sequence[Element]: converted 'contents'.
            
#         """
#         converted = self.stores()
#         if isinstance(contents, Mapping):
#             converted = converted.extend(contents.values())
#         elif isinstance(contents, Sequence):
#             converted = contents
#         elif isinstance(contents, amicus.quirks.Element):
#             converted = converted.append(contents)
#         return converted  

#     def verify(self, contents: Any) -> Any:
#         """Verifies that 'contents' is one of the types in 'accepts'.
        
#         Args:
#             contents (Any): item(s) to be type validated.
            
#         Raises:
#             TypeError: if 'contents' is not one of the types in 'accepts'.
            
#         Returns:
#             Any: original contents if there is no TypeError.
        
#         """
#         if all(isinstance(c, self.accepts) for c in contents):
#             return contents
#         else:
#             raise TypeError(
#                 f'contents must be or contain one of the following types: ' 
#                 f'{self.accepts}')        

