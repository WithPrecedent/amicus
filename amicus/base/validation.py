"""
validation: type converter and validator classes
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)


Contents:
    Validator
    Converter
    SettingsConverter
    ClerkConverter

ToDo:
    Support complex types like List[List[str]]
    
"""
from __future__ import annotations
import abc
import dataclasses
import inspect
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union, get_args, 
                    get_origin)

import amicus


@dataclasses.dataclass
class Validator(amicus.quirks.Quirk):
    """Mixin for calling validation methods

    Args:
        validations (List[str]): a list of attributes that need validating.
            Each item in 'validations' should have a corresponding method named 
            f'_validate_{name}' or match a key in 'converters'. Defaults to an 
            empty list. 
        converters (amicus.Catalog):
               
    """
    validations: ClassVar[Sequence[str]] = []
    converters: ClassVar[amicus.Catalog] = amicus.Catalog()

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

