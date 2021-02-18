"""
base: essential base classes for a amicus project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Catalog (Catalog): specialized Catalog for runtime construction and 
        instancing of classes. Catalog methods allow for the integration of 
        amicus Quirks to preexisting classes.
    Settings
    Filer
    Stage
    Manager
    Component

"""
from __future__ import annotations
import abc
import dataclasses
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import more_itertools

import amicus


@dataclasses.dataclass
class Catalog(Catalog):
    """Specialized Catalog for runtime class construction and instancing.

    A Catalog inherits the differences between a Catalog and a Lexicon.
    
    A Catalog differs from a Catalog in 2 significant ways:
        1) It should only store classes as values.
        2) It includes methods for accessing, building, customizing, and 
            instancing the stored subclasses.
        
    Args:
        contents (Mapping[str, Any]): stored dictionary with only classes as 
            values. Defaults to an empty dict.
        defaults (Sequence[Any]]): a list of keys in 'contents' which will be 
            used to return items when 'default' is sought. If not passed, 
            'default' will be set to all keys.
        always_return_list (bool): whether to return a list even when the key 
            passed is not a list or special access key (True) or to return a 
            list only when a list or special access key is used (False). 
            Defaults to False. 
                  
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    default: Any = None
    defaults: Sequence[Any] = dataclasses.field(default_factory = list)
    always_return_list: bool = False

    """ Properties """
    
    @property
    def suffixes(self) -> Tuple[str]:
        """
        """
        return tuple(key + 's' for key in self.contents.keys())
    
    """ Public Methods """

    def borrow(self, names: Union[str, Sequence[str]]) -> Type:
        """Returns a stored subclass unchanged.

        Args:
            name (str): key to accessing subclass in 'contents'.

        Returns:
            Type: stored class.
            
        """
        match = self.default
        for item in more_itertools.always_iterable(names):
            try:
                match = self.contents[item]
                break
            except KeyError:
                pass
        return match

    def build(self, name: str, 
              quirks: Union[str, Sequence[str]] = None) -> Type:
        """Returns subclass matching 'name' with selected quirks.

        Args:
            name (str): key name of stored class in 'contents' to returned.
            quirks (Union[str, Sequence[str]]): names of Quirk subclasses to
                add to the custom built class. Defaults to None.

        Returns:
            Type: stored class with selected quirks added.
            
        """
        bases = []
        if quirks is not None:
            bases.extend(more_itertools.always_iterable(
                amicus.quirks.Quirk.library.borrow(names = quirks)))
        bases.append(self.borrow(names = name))
        return dataclasses.dataclass(type(name, tuple(bases), {}))
    
    def instance(self, name: str, quirks: Union[str, Sequence[str]] = None, 
                 **kwargs) -> object:
        """Returns the stored class instance matching 'name'.
        
        If 'quirks' are also passed, they will be added to the returned class
        inheritance.

        Args:
            name (str): key name of stored class in 'contents' to returned.
            quirks (Union[str, Sequence[str]]): names of Quirk subclasses to
                add to the custom built class. Defaults to None.
            kwargs: parameters and arguments to pass to the instanced class.

        Returns:
            object: stored class instance or custom built class with 'quirks'.
            
        """
        if quirks is None:
            return self.borrow(names = name)(**kwargs)
        else:
            return self.build(name = name, quirks = quirks)(**kwargs)


@dataclasses.dataclass
class Settings(amicus.quirks.Keystone, amicus.Settings):
    """Loads and stores configuration settings for a Project.

    Args:
        contents (Union[str, pathlib.Path, Mapping[str, Mapping[str, Any]]]): a 
            dict, a str file path to a file with settings, or a pathlib Path to
            a file with settings. Defaults to en empty dict.
        infer_types (bool): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, a False value will leave all values as strings. 
            Defaults to True.
        defaults (Mapping[str, Mapping[str]]): any default options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to a dict with 'general', 
            'files', and 'amicus' sections listed.
        skip (Sequence[str]): names of suffixes to skip when constructing nodes
            for a amicus project. Defaults to a list with 'general', 'files',
            'amicus', and 'parameters'.
        library (ClassVar[Catalog]): related Catalog instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.    
            
    """
    contents: Union[str, pathlib.Path, Mapping[str, Mapping[str, Any]]] = (
        dataclasses.field(default_factory = dict))
    infer_types: bool = True
    defaults: Mapping[str, Mapping[str, Any]] = dataclasses.field(
        default_factory = lambda: {'general': {'verbose': False,
                                               'parallelize': False,
                                               'conserve_memery': False},
                                   'files': {'source_format': 'csv',
                                             'interim_format': 'csv',
                                             'final_format': 'csv',
                                             'file_encoding': 'windows-1252'},
                                   'amicus': {'default_design': 'pipeline',
                                                 'default_workflow': 'graph'}})
    skip: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['general', 
                                   'files', 
                                   'amicus', 
                                   'parameters'])
    library: ClassVar[amicus.Catalog] = amicus.Catalog()


@dataclasses.dataclass
class Filer(amicus.quirks.Keystone, amicus.Clerk):
    pass  


@dataclasses.dataclass
class Stage(amicus.quirks.Keystone, amicus.quirks.Needy, abc.ABC):
    """Creates a amicus object.

    Args:
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. Defaults to an
            empty list.
        library (ClassVar[Catalog]): related Catalog instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.              
            
    """
    needs: ClassVar[Union[Sequence[str], str]] = []
    library: ClassVar[amicus.Catalog] = amicus.Catalog()  

    """ Class Methods """
    
    @classmethod
    def create(cls, **kwargs) -> object:
        """[summary]

        Raises:
            ValueError: [description]

        Returns:
            object: [description]
            
        """
        needs = list(more_itertools.always_iterable(cls.needs))
        method = getattr(cls, f'from_{needs[0]}')
        for need in needs:
            if need not in kwargs:
                raise ValueError(
                    f'The create method must include a {need} argument')
        return method(**kwargs)    
     
            
@dataclasses.dataclass
class Manager(amicus.quirks.Keystone, amicus.quirks.Element):
    """Manages a distinct portion of a amicus project workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if a 
            amicus instance needs settings from a Settings instance, 
            'name' should match the appropriate section name in a Settings 
            instance. Defaults to None. 
        workflow (amicus.Structure): a workflow of a project subpart derived 
            from 'outline'. Defaults to None.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. Defaults to an
            empty list.
        library (ClassVar[Catalog]): related Catalog instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.
                
    """
    name: str = None
    workflow: amicus.Structure = None
    needs: ClassVar[Union[Sequence[str], str]] = ['outline', 'name']
    library: ClassVar[amicus.Catalog] = amicus.Catalog()
    
    """ Public Class Methods """

    @classmethod
    def create(cls, **kwargs) -> object:
        """[summary]

        Raises:
            ValueError: [description]

        Returns:
            object: [description]
            
        """
        needs = list(more_itertools.always_iterable(cls.needs))
        method = getattr(cls, f'from_{needs[0]}')
        for need in needs:
            if need not in kwargs:
                raise ValueError(
                    f'The create method must include a {need} argument')
        return method(**kwargs)   
    
    @classmethod
    def from_outline(cls, outline: Stage, name: str, **kwargs) -> Manager:
        """[summary]

        Args:
            outline (Stage): [description]
            name (str): [description]

        Returns:
            Manager: [description]
            
        """        
        names = [name]
        if name in outline.designs:
            names.append(outline.design[name])
        manager = cls.library.borrow(names = names)
        structure = cls.bases.stage.library.borrow(names = 'workflow')
        workflow = structure.create(outline = outline, name = name)
        return manager(name = name, workflow = workflow, **kwargs)          

    """ Public Methods """
    
    def execute(self, data: Any) -> Any:
        """[summary]

        Args:
            data (Any): [description]

        Returns:
            Any: [description]
        """        
        for node in self.workflow:
            data = node.execute(data = data)
        return data
                
  
@dataclasses.dataclass
class Component(amicus.quirks.Keystone, amicus.quirks.Element, abc.ABC):
    """Keystone class for parts of a amicus Workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if a 
            amicus instance needs settings from a Settings instance, 
            'name' should match the appropriate section name in a Settings 
            instance. Defaults to None.
        contents (Any): stored item(s) for use by a Component subclass instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            False.
        library (ClassVar[Catalog]): related Catalog instance that will store
            subclasses and allow runtime construction and instancing of those
            stored subclasses.    
                
    """
    name: str = None
    contents: Any = None
    iterations: Union[int, str] = 1
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = False
    library: ClassVar[amicus.Catalog] = amicus.Catalog()
    
    """ Public Class Methods """
    
    @classmethod
    def create(cls, source: str, **kwargs) -> Component:
        """[summary]

        Args:
            source (str): [description]

        Raises:
            NotImplementedError: [description]

        Returns:
            Component: [description]
            
        """
        if (isinstance(source, str)
                or (isinstance(source, Sequence) and all(source, str))):
            return cls.from_name(name = source, **kwargs)
        elif isinstance(source, cls.bases.Stage):
            return 
  
    @classmethod
    def from_outline(cls, name: str, outline: amicus.project.Outline, 
                     **kwargs) -> Component:
        """[summary]

        Args:
            name (str): [description]
            section (str): [description]
            outline (amicus.project.Outline): [description]

        Returns:
            Component: [description]
        """              
        if name in outline.initialization:
            parameters = outline.initialization[name]
            parameters.update(kwargs)
        else:
            parameters = kwargs
        component = cls.library.borrow(names = [name, outline.designs[name]])
        instance = component(name = name, **parameters)
        return instance

    """ Public Methods """
    
    def execute(self, data: Any, **kwargs) -> Any:
        """[summary]

        Args:
            data (Any): [description]

        Returns:
            Any: [description]
            
        """ 
        if self.iterations in ['infinite']:
            while True:
                data = self.implement(data = data, **kwargs)
        else:
            for iteration in range(self.iterations):
                data = self.implement(data = data, **kwargs)
        return data

    def implement(self, data: Any, **kwargs) -> Any:
        """[summary]

        Args:
            data (Any): [description]

        Returns:
            Any: [description]
            
        """  
        if self.parameters:
            parameters = self.parameters
            parameters.update(kwargs)
        else:
            parameters = kwargs
        if self.contents not in [None, 'None', 'none']:
            data = self.contents.implement(data = data, **parameters)
        return data

    """ Private Methods """
    
    def _add_attributes(self, attributes: Dict[Any, Any]) -> None:
        """[summary]

        Args:
            attributes (Dict[Any, Any]): [description]

        Returns:
            [type]: [description]
            
        """
        for key, value in attributes.items():
            setattr(self, key, value)
        return self
    