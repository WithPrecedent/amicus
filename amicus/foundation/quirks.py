"""
quirks: amicus mixin architecture
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

amicus quirks are not technically mixins because some have required attributes. 
Traditionally, mixins do not have any attributes and only add functionality. 
quirks are designed for multiple inheritance and easy addition to other classes. 
Despite not meeting the traditional definition of "mixin," they are internally 
referred to as "mixins" because their design and goals are otherwise similar to 
mixins.

Although python doesn't require the separation of interfaces in the same way
that more structured languages do, some of the includes quirks in this module
are designed to make it clearer for users trying to expand amicus' 
functionality. These quirks show the required and included methods for core
classes in amicus. So, whether you intend to directly subclass or write 
alternate classes for use in amicus, these quirks show how to survive static 
type-checkers and other internal checks made by amicus.

Contents:
    Quirk (ABC): base class for all amicus quirks (described above). Its 
        'library' class attribute stores all subclasses.
    Core (Quirk, ABC): base class to be used for all subclasses that wish 
        to use amicus's automatic subclass registration system.
    Element (Quirk, ABC): quirk that automatically assigns a 'name' attribute if 
        none is passed. The default 'name' will be the snakecase name of the 
        class.
    Importer (Quirk): quirk that supports lazy importation of modules and items 
        stored within them.
    Needy (Quirk):

ToDo:
    Add in Validator mixins.
    Fix ProxyMixin as explained in its docs.

"""
from __future__ import annotations
import abc
import copy
import dataclasses
import inspect
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import more_itertools

import amicus
       
    
@dataclasses.dataclass
class Quirk(abc.ABC):
    """Core class for amicus quirks (mixin-approximations).
    
    Args:
        library (ClassVar[amicus.Catalog]): related Catalog instance that 
            will store concrete subclasses and allow runtime construction and 
            instancing of those stored subclasses.
    
    Namespaces: library
    
    """
    library: ClassVar[amicus.Catalog] = amicus.Catalog()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'library' if it is a concrete class."""
        super().__init_subclass__(**kwargs)
        # Adds concrete subclasses to 'library' using 'key'.
        if not abc.ABC in cls.__bases__:
            # Creates a snakecase key of the class name.
            key = amicus.tools.snakify(cls.__name__)
            cls.library[key] = cls


@dataclasses.dataclass
class Core(abc.ABC):
    """Base mixin for automatic registration of subclasses and instances. 
    
    Any concrete (non-abstract) subclass will automatically store itself in the 
    class attribute 'subclasses' using the snakecase name of the class as the 
    key.
    
    Any direct subclass will automatically store itself in the class attribute 
    'bases' using the snakecase name of the class as the key.
    
    Any instance of a subclass will be stored in the class attribute 'instances'
    as long as '__post_init__' is called (either by a 'super()' call or if the
    instance is a dataclass and '__post_init__' is not overridden).
    
    Args:
        bases (ClassVar[amicus.types.Library]): library that stores direct 
            subclasses (those with Base in their '__bases__' attribute) and 
            allows runtime access and instancing of those stored subclasses.
    
    Attributes:
        subclasses (ClassVar[amicus.types.Catalog]): library that stores 
            concrete subclasses and allows runtime access and instancing of 
            those stored subclasses. 'subclasses' is automatically created when 
            a direct Core subclass (Core is in its '__bases__') is instanced.
        instances (ClassVar[amicus.types.Catalog]): library that stores
            subclass instances and allows runtime access of those stored 
            subclass instances. 'instances' is automatically created when a 
            direct Core subclass (Core is in its '__bases__') is instanced. 
                      
    Namespaces: 
        bases, subclasses, instances, borrow, instance, and __init_subclass__.
    
    """
    bases: ClassVar[amicus.types.Library] = amicus.types.Library()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to appropriate class libraries."""
        super().__init_subclass__(**kwargs)
        # Creates a snakecase key of the class name.
        key = amicus.tools.snakify(cls.__name__)
        # Adds class to 'bases' if it is a base class.
        if Core in cls.__bases__:
            # Creates libraries on this class base for storing subclasses.
            cls.subclasses = amicus.types.Catalog()
            cls.instances = amicus.types.Catalog()
            # Adds this class to 'bases' using 'key'.
            cls.bases.register(name = key, item = cls)
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
    def select(cls, name: Union[str, Sequence[str]]) -> Type[Core]:
        """Returns matching subclass from 'subclasses.
        
        Args:
            name (Union[str, Sequence[str]]): name of item in 'subclasses' to
                return
            
        Raises:
            KeyError: if no match is found for 'name' in 'subclasses'.
            
        Returns:
            Type[Core]: stored Core subclass.
            
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
    def instance(cls, name: Union[str, Sequence[str]], **kwargs) -> Core:
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
            Core: stored Core subclass instance.
            
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
class Element(Quirk):
    """Mixin for classes that need a 'name' attribute.
    
    Automatically provides a 'name' attribute to a subclass, if it isn't 
    otherwise passed. This is important for parts of amicus composite objects 
    like trees and graphs.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if a 
            amicus instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None. 

    Namespaces: library, bases, name, __post_init__, and _get_name

    """
    name: str = None
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' attribute.
        if not hasattr(self, 'name') or self.name is None:  
            self.name = self._get_name()
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass

    """ Private Methods """
    
    def _get_name(self) -> str:
        """Returns snakecase of the class name.

        If a user wishes to use an alternate naming system, a subclass should
        simply override this method. 
        
        Returns:
            str: name of class for internal referencing and some access methods.
        
        """
        return amicus.tools.snakify(self.__class__.__name__)


@dataclasses.dataclass
class Importer(Quirk):
    """Faciliates lazy importing from modules.

    Subclasses with attributes storing strings containing import paths 
    (indicated by having a '.' in their text) will automatically have those
    attribute values turned into the corresponding stored classes.

    The 'importify' method also allows this process to be performed manually.

    Subclasses should not have custom '__getattribute__' methods or properties
    to avoid errors.

    Namespaces: 'importify', '__getattribute__'
    
    """
 
    """ Public Methods """

    def importify(self, path: str, instance: bool = False, 
             **kwargs) -> Union[object, Type]:
        """Returns object named by 'key'.

        Args:
            key (str): name of class, function, or variable to try to import 
                from modules listed in 'modules'.

        Returns:
            object: imported from a python module.

        """
        item = path.split('.')[-1]
        module = path[:-len(item) - 1]
        imported = amicus.tools.importify(module = module, key = item)
        if kwargs or instance:
            return imported(**kwargs)
        else:
            return imported

    """ Dunder Methods """

    def __getattribute__(self, name: str) -> Any:
        """Converts stored import paths into the corresponding objects.

        If an import path is stored, that attribute is permanently converted
        from a str to the imported object or class.
        
        Args:
            name (str): name of attribute sought.

        Returns:
            Any: the stored value or, if the value is an import path, the
                class or object stored at the designated import path.
            
        """
        value = super().__getattribute__(name)
        if (isinstance(value, str) and '.' in value):
            value = self.importify(path = value)
            super().__setattr__(name, value)
        return value


@dataclasses.dataclass
class Needy(Quirk):
    """Provides internal creation and automatic parameterization.
    
    Args:
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. The first item
            in 'needs' to correspond to an internal factory classmethod named
            f'from_{first item in needs}'. Defaults to an empty list.
            
    """
    needs: ClassVar[Union[Sequence[str], str]] = []
    
    """ Class Methods """

    @classmethod
    def create(cls, **kwargs) -> Needy:
        """Calls corresponding creation class method to instance a subclass.
        
        For create to work properly, there should be a corresponding classmethod
        named f'from_{first item in needs}'.

        Raises:
            ValueError: If there is no corresponding method.

        Returns:
            Needy: instance of a Needy subclass.
            
        """
        needs = list(more_itertools.always_iterable(cls.needs))
        method = getattr(cls, f'from_{needs[0]}')
        for need in needs:
            if need not in kwargs:
                raise ValueError(
                    f'The create method must include a {need} argument')
        return method(**kwargs)      
    
    @classmethod
    def needify(cls, instance: object) -> Mapping[str, Any]:
        """Populates keywords from 'instance' based on 'needs'.

        Args:
            instance (object): instance with attributes or items in its 
                'contents' attribute with data to compose arguments to be
                passed to the 'create' classmethod.

        Raises:
            KeyError: if data could not be found for an argument.

        Returns:
            Mapping[str, Any]: keyword parameters and arguments to pass to the
                'create' classmethod.
            
        """
        kwargs = {}
        for need in more_itertools.always_iterable(cls.needs):
            try:
                kwargs[need] = getattr(instance, need)
            except AttributeError:
                try:
                    kwargs[need] = instance.contents[need]
                except (AttributeError, KeyError):
                    raise KeyError(
                        f'{need} could not be found in order to call a '
                        f'method of {cls.__name__}')
        return kwargs

 
# @dataclasses.dataclass
# class Registrar(Quirk):
#     """Registry interface for core amicus classes.
    
#     A Registrar automatically registers all concrete (non-abstract) subclasses
#     using the 'registry' class attribute which must be provided by the class 
#     using this quirk.

#     Namespaces: 'registry', 'register', 'acquire'

#     Args:
#         registry (ClassVar[Mapping[str, Type]]):
    
#     """
#     registry: ClassVar[Mapping[str, Type]] = amicus.Catalog()

#     """ Initialization Methods """
    
#     def __init_subclass__(cls, **kwargs):
#         """Adds 'cls' to 'registry' if it is a concrete class."""
#         super().__init_subclass__(**kwargs)
#         if not abc.ABC in cls.__bases__:
#             cls.register()
        
#     """ Class Methods """

#     @classmethod
#     def register(cls) -> None:
#         """Registers a subclass in a Catalog.
        
#         The default 'register' method uses the snake-case name of the class as
#         the key for the stored subclass.
        
#         """
#         key = amicus.tools.snakify(cls.__name__)
#         cls.registry[key] = cls
#         return cls

#     @classmethod
#     def acquire(cls, key: str) -> Any:
#         """Returns the stored class matching 'key'.

#         Args:
#             key (str): name of stored class to returned, as defined by the
#                 'register' method.

#         Returns:
#             Any: stored subclass.
            
#         """
#         return cls.registry.select(key = key)
    
    
# @dataclasses.dataclass
# class Librarian(Quirk):
#     """Store interface for core amicus classes.
    
#     Librarian automatically registers all subclass instances using the 'deposit' 
#     method which stores the subclass instances in 'store'.
    
#     To use this quirk, the '__post_init__' method must be called.
    
#     """
#     store: ClassVar[Mapping[str, object]] = amicus.Catalog()

#     """ Initialization Methods """

#     def __post_init__(self) -> None:
#         """Initializes class instance attributes."""
#         # Calls parent and/or mixin initialization method(s).
#         try:
#             super().__post_init__()
#         except AttributeError:
#             pass
#         # Stores subclass in Store.
#         self.deposit()

#     """ Public Methods """

#     def deposit(self) -> None:
#         """Stores a subclass instance in a Catalog.
        
#         The 'deposit' method with use the 'name' attribute of an instance, if
#         it exists. Otherwise, it will use the snake-case '__name__' or 
#         '__class_name__' of the instance.
        
#         """
#         try:
#             self.store[self.name] = self
#         except (AttributeError, TypeError):
#             try:
#                 self.store[amicus.tools.snakify(self.__name__)] = self
#             except (AttributeError, TypeError):
#                 self.store[amicus.tools.snakify(
#                     self.__class__.__name__)] = self 
#         return self
    
#     """ Class Methods """

#     @classmethod
#     def borrow(cls, key: str) -> object:
#         """Returns the stored class matching 'key'.

#         Args:
#             key (str): name of stored subclass instance to be returned, as 
#                 defined by the 'deposit' method.

#         Returns:
#             object: stored subclass isntance.
            
#         """
#         return copy.deepcopy(cls.store.select(key))


# @dataclasses.dataclass
# class ProxyMixin(object):
#     """ which creates a proxy name for a Element subclass attribute.

#     The 'proxify' method dynamically creates a property to access the stored
#     attribute. This allows class instances to customize names of stored
#     attributes while still maintaining the interface of the base amicus
#     classes.

#     Only one proxy should be created per class. Otherwise, the created proxy
#     properties will all point to the same attribute.

#     Namespaces: 'proxify', '_proxy_getter', '_proxy_setter', 
#         '_proxy_deleter', '_proxify_attribute', '_proxify_method', the name of
#         the proxy property set by the user with the 'proxify' method.
       
#     To Do:
#         Add property to class instead of instance to prevent return of property
#             object.
#         Implement '__set_name__' in a secondary class to simplify the code and
#             namespace usage.
        
#     """

#     """ Public Methods """

#     def proxify(self,
#             proxy: str,
#             attribute: str,
#             default_value: Any = None,
#             proxify_methods: bool = True) -> None:
#         """Adds a proxy property to refer to class attribute.

#         Args:
#             proxy (str): name of proxy property to create.
#             attribute (str): name of attribute to link the proxy property to.
#             default_value (Any): default value to use when deleting 'attribute' 
#                 with '__delitem__'. Defaults to None.
#             proxify_methods (bool): whether to create proxy methods replacing 
#                 'attribute' in the original method name with the string passed 
#                 in 'proxy'. So, for example, 'add_chapter' would become 
#                 'add_recipe' if 'proxy' was 'recipe' and 'attribute' was
#                 'chapter'. The original method remains as well as the proxy.
#                 This does not change the rest of the signature of the method so
#                 parameter names remain the same. Defaults to True.

#         """
#         self._proxied_attribute = attribute
#         self._default_proxy_value = default_value
#         self._proxify_attribute(proxy = proxy)
#         if proxify_methods:
#             self._proxify_methods(proxy = proxy)
#         return self

#     """ Proxy Property Methods """

#     def _proxy_getter(self) -> Any:
#         """Proxy getter for '_proxied_attribute'.

#         Returns:
#             Any: value stored at '_proxied_attribute'.

#         """
#         return getattr(self, self._proxied_attribute)

#     def _proxy_setter(self, value: Any) -> None:
#         """Proxy setter for '_proxied_attribute'.

#         Args:
#             value (Any): value to set attribute to.

#         """
#         setattr(self, self._proxied_attribute, value)
#         return self

#     def _proxy_deleter(self) -> None:
#         """Proxy deleter for '_proxied_attribute'."""
#         setattr(self, self._proxied_attribute, self._default_proxy_value)
#         return self

#     """ Other Private Methods """

#     def _proxify_attribute(self, proxy: str) -> None:
#         """Creates proxy property for '_proxied_attribute'.

#         Args:
#             proxy (str): name of proxy property to create.

#         """
#         setattr(self, proxy, property(
#             fget = self._proxy_getter,
#             fset = self._proxy_setter,
#             fdel = self._proxy_deleter))
#         return self

#     def _proxify_methods(self, proxy: str) -> None:
#         """Creates proxy method with an alternate name.

#         Args:
#             proxy (str): name of proxy to repalce in method names.

#         """
#         for item in dir(self):
#             if (self._proxied_attribute in item
#                     and not item.startswith('__')
#                     and callable(item)):
#                 self.__dict__[item.replace(self._proxied_attribute, proxy)] = (
#                     getattr(self, item))
#         return self
 
      