"""
core: essential classes for an amicus project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Configuration
    Component
    Outline
    Workflow
    Summary

"""
from __future__ import annotations
import abc
import copy
import dataclasses
import inspect
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Set, Tuple, Type, Union)
import warnings

import more_itertools

import amicus


@dataclasses.dataclass
class Library(amicus.types.Lexicon):
    """Stores Keystone classes with first-level dot notation access.
    
    A Library inherits the differences between a Lexicon and an ordinary python
    dict.

    A Library differs from a Lexicon in 5 significant ways:
        1) It adds on dot access for first level keys. Ordinary dict access
            methods are still available, inherited from Lexicon.
        2) It has a 'borrow' method that accepts multiple keys and returns the 
            first match.
        3) It has a 'deposit' method which returns an error if the passed key
            already exists in the stored dict.
        4) It has a 'suffixes' property which returns simple plurals (adding an
            's') to each key in 'contents'.
        5) It is designed to hold Keystone classes.
    
    Args:
        contents (Mapping[str, amicus.quirks.Keystone]]): stored dictionary of
            Keystone classes. Defaults to an empty dict.
        default (Any): default value to return when the 'get' method is used.
              
    """
    contents: Mapping[str, amicus.quirks.Keystone] = dataclasses.field(
        default_factory = dict)
    default: Any = None
    
    """ Public Methods """

    def borrow(self, name: Union[str, Sequence[str]]) -> amicus.quirks.Keystone:
        """Returns a stored subclass unchanged.
        
        Args:
            name (str): key to accessing subclass in 'contents'.
            
        Returns:
            Type: stored class.
            
        """
        match = self.default
        for item in more_itertools.always_iterable(name):
            try:
                match = self.contents[item]
                break
            except KeyError:
                pass
        return match
        
    def deposit(self, name: str, item: amicus.quirks.Keystone) -> None:
        """Adds 'item' at 'name' to 'contents' if 'name' isn't in 'contents'.
        
        Args:
            name (str): key to use to store 'item'.
            item (amicus.quirks.Keystone): item to store in 'contents'.
            
        Raises:
            ValueError: if 'name' matches an existing key in 'contents'.
            
        """
        if name in dir(self):
            raise ValueError(f'{name} is already in {self.__class__.__name__}')
        else:
            self[name] = item
        return self

    """ Dunder Methods """
    
    def __getattr__(self, key: str) -> Any:
        """Returns an item in 'contents' matching 'key'.

        Args:
            key (str): name of item in 'contents' to return.

        Raises:
            AttributeError: if 'key' doesn't match an item in 'contents'.

        Returns:
            Any: item stored in 'contents'.
            
        """
        try:
            return self[key]
        except KeyError as key_error:
            raise AttributeError(key_error)

    def __setattr__(self, key: str, value: Any) -> None:
        """Stores 'value' in 'contents' at 'key'.

        Args:
            key (str): name of item to store in 'contents'.
            value (Any): item to store in 'contents'.
            
        """
        self[key] = value
        return self

    def __delattr__(self, key: str) -> None:
        """Deletes item in 'contents' corresponding to 'key'

        Args:
            key (str): name of item in 'contents' to delete.

        Raises:
            AttributeError: if 'key' doesn't match an item in 'contents'.
           
        """
        try:
            del self[key]
        except KeyError as key_error:
            raise AttributeError(key_error)


library = Library()


@dataclasses.dataclass
class Keystone(amicus.quirks.Quirk, abc.ABC):
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
        keystones (ClassVar[amicus.types.Library]): library that stores direct 
            subclasses (those with Keystone in their '__bases__' attribute) and 
            allows runtime access and instancing of those stored subclasses.
    
    Attributes:
        subclasses (ClassVar[amicus.types.Catalog]): library that stores 
            concrete subclasses and allows runtime access and instancing of 
            those stored subclasses. 'subclasses' is automatically created when 
            a direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced.
        instances (ClassVar[amicus.types.Catalog]): library that stores
            subclass instances and allows runtime access of those stored 
            subclass instances. 'instances' is automatically created when a 
            direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced. 
                      
    Namespaces: 
        keystones, subclasses, instances, select, instance, __init_subclass__
    
    """
    keystones: ClassVar[amicus.types.Library] = amicus.types.Library()
    
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
class Settings(amicus.quirks.Keystone, amicus.framework.Configuration):
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
            for an amicus project. Defaults to a list with 'general', 'files',
            'amicus', and 'parameters'.
    
    Attributes:
        keystones (ClassVar[amicus.types.Library]): library that stores direct 
            subclasses (those with Keystone in their '__bases__' attribute) and 
            allows runtime access and instancing of those stored subclasses.
        subclasses (ClassVar[amicus.types.Catalog]): library that stores 
            concrete subclasses and allows runtime access and instancing of 
            those stored subclasses. 'subclasses' is automatically created when 
            a direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced.
        instances (ClassVar[amicus.types.Catalog]): library that stores
            subclass instances and allows runtime access of those stored 
            subclass instances. 'instances' is automatically created when a 
            direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced. 
            
    """
    contents: Union[str, pathlib.Path, Mapping[str, Mapping[str, Any]]] = (
        dataclasses.field(default_factory = dict))
    infer_types: bool = True
    defaults: Mapping[str, Mapping[str, Any]] = dataclasses.field(
        default_factory = lambda: {
            'general': {
                'verbose': False, 
                'parallelize': False, 
                'conserve_memery': False}, 
            'files': {
                'source_format': 'csv',
                'interim_format': 'csv',
                'final_format': 'csv',
                'file_encoding': 'windows-1252'},
            'amicus': {
                'default_design': 'pipeline',
                'default_workflow': 'graph'}})
    skip: Sequence[str] = dataclasses.field(
        default_factory = lambda: ['general', 'files', 'amicus', 'parameters'])
    
  
@dataclasses.dataclass
class Component(amicus.quirks.Keystone, amicus.quirks.Element, abc.ABC):
    """Keystone class for parts of an amicus Workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an 
            amicus instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
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
    
    Attributes:
        keystones (ClassVar[amicus.types.Library]): library that stores direct 
            subclasses (those with Keystone in their '__bases__' attribute) and 
            allows runtime access and instancing of those stored subclasses.
        subclasses (ClassVar[amicus.types.Catalog]): library that stores 
            concrete subclasses and allows runtime access and instancing of 
            those stored subclasses. 'subclasses' is automatically created when 
            a direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced.
        instances (ClassVar[amicus.types.Catalog]): library that stores
            subclass instances and allows runtime access of those stored 
            subclass instances. 'instances' is automatically created when a 
            direct Keystone subclass (Keystone is in its '__bases__') is 
            instanced. 
                
    """
    name: str = None
    contents: Any = None
    iterations: Union[int, str] = 1
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = False

    """ Properties """
    
    @property
    def suffixes(self) -> Tuple[str]:
        """
        """
        return tuple(key + 's' for key in self.subclasses.keys())
    
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
        elif isinstance(source, cls.keystones.Stage):
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

    def implement(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            amicus.Project: [description]
            
        """
        if self.parameters:
            parameters = self.parameters
            parameters.update(kwargs)
        else:
            parameters = kwargs
        if self.contents not in [None, 'None', 'none']:
            project = self.contents.implement(project = project, **parameters)
        return project

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


@dataclasses.dataclass
class Outline(amicus.quirks.Keystone, amicus.quirks.Needy):
    """Information needed to construct and execute a Workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if a 
            amicus instance needs settings from a Configuration 
            instance, 'name' should match the appropriate section name in a 
            Configuration instance. Defaults to None. 
        structure (str): the name matching the type of workflow to be used in a
            project. Defaults to None.
        components (Dict[str, List]): a dictionary with keys that are names of
            components and values that are lists of subcomponents for the keys. 
            Defaults to an empty dict.
        designs (Dict[str, str]): a dictionary with keys that are names of 
            components and values that are the names of the design structure for
            the keys. Defaults to an empty dict.
        initialization (Dict[str, Dict[str, Any]]): a dictionary with keys that 
            are the names of components and values which are dictionaries of 
            pararmeters to use when created the component listed in the key. 
            Defaults to an empty dict.
        runtime (Dict[str, Dict[str, Any]]): a dictionary with keys that 
            are the names of components and values which are dictionaries of 
            pararmeters to use when calling the 'execute' method of the 
            component listed in the key. Defaults to an empty dict.
        attributes (Dict[str, Dict[str, Any]]): a dictionary with keys that 
            are the names of components and values which are dictionaries of 
            attributes to automatically add to the component constructed from
            that key. Defaults to an empty dict.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. Defaults to a
            list with 'settings' and 'name'.
            
    """
    name: str = None
    structure: str = None
    components: Dict[str, List] = dataclasses.field(default_factory = dict)
    designs: Dict[str, str] = dataclasses.field(default_factory = dict)
    initialization: Dict[str, Dict[str, Any]] = dataclasses.field(
        default_factory = dict)
    runtime: Dict[str, Dict[str, Any]] = dataclasses.field(
        default_factory = dict)
    attributes: Dict[str, Dict[str, Any]] = dataclasses.field(
        default_factory = dict)
    needs: ClassVar[Union[Sequence[str], str]] = ['settings', 'name']

    """ Public Class Methods """
    
    @classmethod   
    def from_settings(cls, settings: Settings, name: str = None) -> Outline:
        """[summary]

        Args:
            source (base.Configuration): [description]

        Returns:
            Outline: [description]
            
        """   
        skips = [k for k in settings.keys() if k.endswith(tuple(settings.skip))]
        component_keys = [k for k in settings.keys() if k not in skips]
        if name is None:
            try:
                name = component_keys[0]
            except IndexError:
                raise ValueError('No sections in settings indicate how to '
                                 'construct a project outline')
        structure = cls._get_structure(name = name, settings = settings) 
        outline = cls(name = name, structure = structure)      
        for section in component_keys:
            outline = cls._parse_section(name = section, 
                                         settings = settings,
                                         outline = outline)
        outline = cls._add_runtime_parameters(outline = outline, 
                                              settings = settings)
        return outline 
    
    """ Private Class Methods """
    
    @classmethod
    def _parse_section(cls, name: str, settings: base.Configuration, 
                       outline: Outline) -> Outline:
        """[summary]

        Args:
            name (str): [description]
            settings (base.Configuration): [description]
            outline (Outline): [description]

        Returns:
            Outline: [description]
        """        
        section = settings[name]
        design = cls._get_design(name = name, settings = settings)
        outline.designs[name] = design
        outline.initialization[name] = {}
        outline.attributes[name] = {}
        component = cls.keystones.component.subclasses.borrow(names = [name, design])
        parameters = tuple(i for i in list(component.__annotations__.keys()) 
                           if i not in ['name', 'contents'])
        for key, value in section.items():
            suffix = key.split('_')[-1]
            prefix = key[:-len(suffix) - 1]
            if suffix in ['design', 'workflow']:
                pass
            elif suffix in cls.keystones.component.library.suffixes:
                outline.designs.update(dict.fromkeys(value, suffix[:-1]))
                outline.components[prefix] = value 
            elif suffix in parameters:
                outline.initialization[name][suffix] = value 
            elif prefix in [name]:
                outline.attributes[name][suffix] = value
            else:
                outline.attributes[name][key] = value
        return outline   

    @classmethod
    def _get_design(cls, name: str, settings: base.Configuration) -> str:
        """[summary]

        Args:
            name (str): [description]
            settings (base.Configuration):

        Raises:
            KeyError: [description]

        Returns:
            str: [description]
            
        """
        try:
            design = settings[name][f'{name}_design']
        except KeyError:
            try:
                design = settings[name][f'design']
            except KeyError:
                try:
                    design = settings['amicus']['default_design']
                except KeyError:
                    raise KeyError(f'To designate a design, a key in settings '
                                   f'must either be named "design" or '
                                   f'"{name}_design"')
        return design    

    @classmethod
    def _get_structure(cls, name: str, settings: base.Configuration) -> str:
        """[summary]

        Args:
            name (str): [description]
            section (Mapping[str, Any]): [description]

        Raises:
            KeyError: [description]

        Returns:
            str: [description]
            
        """
        try:
            structure = settings[name][f'{name}_workflow']
        except KeyError:
            try:
                structure = settings[name][f'workflow']
            except KeyError:
                try:
                    structure = settings['amicus']['default_workflow']
                except KeyError:
                    raise KeyError(f'To designate a workflow structure, a key '
                                   f' in settings must either be named '
                                   f'"workflow" or "{name}_workflow"')
        return structure  

    @classmethod
    def _add_runtime_parameters(cls, outline: Outline, 
                                settings: base.Configuration) -> Outline:
        """[summary]

        Args:
            outline (Outline): [description]
            settings (base.Configuration): [description]

        Returns:
            Outline: [description]
            
        """
        for component in outline.components.keys():
            names = [component]
            if component in outline.designs:
                names.append(outline.designs[component])
            for name in names:
                try:
                    outline.runtime[name] = settings[f'{name}_parameters']
                except KeyError:
                    pass
        return outline
       

@dataclasses.dataclass
class Workflow(amicus.quirks.Keystone, amicus.quirks.Needy, amicus.Graph):
    """Stores lightweight workflow and corresponding components.
    
    Args:
        contents (Dict[str, List[str]]): an adjacency list where the keys are 
            the names of nodes and the values are names of nodes which the key 
            is connected to. Defaults to an empty dict.
        default (Any): default value to use when a key is missing and a new
            one is automatically corrected. Defaults to an empty list.
        components (amicus.types.Catalog): stores Component instances that 
            correspond to nodes in 'contents'. Defaults to an empty Catalog.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. Defaults to 
            a list with 'outline' and 'name'.
                   
    """
    contents: Dict[str, List[str]] = dataclasses.field(default_factory = dict)
    default: Any = dataclasses.field(default_factory = list)
    components: amicus.types.Catalog = amicus.types.Catalog()
    needs: ClassVar[Union[Sequence[str], str]] = ['outline', 'name']

    """ Public Class Methods """
            
    @classmethod
    def from_outline(cls, outline: Outline, name: str) -> Workflow:
        """Creates a Workflow from an Outline.

        Args:
            outline (Outline): [description]
            name (str): [description]

        Returns:
            Workflow: [description]
            
        """        
        workflow = cls()
        workflow = cls._add_component(name = name,
                                      outline = outline,
                                      workflow = workflow)
        for component in outline.components[name]:
            workflow = cls._add_component(name = component,
                                          outline = outline,
                                          workflow = workflow)
        return workflow
                             
    """ Public Methods """
    
    def combine(self, workflow: Workflow) -> None:
        """Adds 'other' Workflow to this Workflow.
        
        Combining creates an edge between every endpoint of this instance's
        Workflow and the every root of 'workflow'.
        
        Args:
            workflow (Workflow): a second Workflow to combine with this one.
            
        Raises:
            ValueError: if 'workflow' has nodes that are also in 'flow'.
            
        """
        if any(k in workflow.components.keys() for k in self.components.keys()):
            raise ValueError('Cannot combine Workflows with the same nodes')
        else:
            self.components.update(workflow.components)
        super().combine(structure = workflow)
        return self
   
    def execute(self, data: Any, copy_components: bool = True, **kwargs) -> Any:
        """Iterates over 'contents', using 'components'.
        
        Args:
            
        Returns:
            
        """
        for path in iter(self):
            data = self.execute_path(data = data, 
                                     path = path, 
                                     copy_components = copy_components, 
                                     **kwargs)  
        return data

    def execute_path(self, data: Any, path: Sequence[str], 
                     copy_components: bool = True, **kwargs) -> Any:
        """Iterates over 'contents', using 'components'.
        
        Args:
            
        Returns:
            
        """
        for node in more_itertools.always_iterable(path):
            if copy_components:
                component = copy.deepcopy(self.components[node])
            else:
                component = self.components[node]
            data = component.execute(data = data, **kwargs)    
        return data
            
    """ Private Class Methods """
    
    @classmethod
    def _add_component(cls, name: str, outline: Outline,
                       workflow: Workflow) -> Workflow:
        """[summary]

        Args:
            name (str): [description]
            details (Details): [description]
            workflow (Workflow): [description]

        Returns:
            Workflow: [description]
            
        """
        workflow.append(node = name)
        design = outline.designs[name]
        component = cls.keystones.component.library.borrow(names = [name, design])
        instance = component.from_outline(name = name, outline = outline)
        workflow.components[name] = instance
        return workflow
  

@dataclasses.dataclass
class Summary(amicus.quirks.Keystone, amicus.quirks.Needy, amicus.types.Lexicon):
    """Collects and stores results of executing a Workflow.
    
    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
        default (Any): default value to return when the 'get' method is used.
        prefix (str): prefix to use when storing different paths through a 
            workflow. So, for example, a prefix of 'path' will create keys of
            'path_1', 'path_2', etc. Defaults to 'path'.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. Defaults to 
            a list with 'workflow' and 'data'.          
              
    """
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    default: Any = None
    prefix: str = 'path'
    needs: ClassVar[Union[Sequence[str], str]] = ['workflow', 'data']

    """ Public Methods """
    
    @classmethod
    def from_workflow(cls, workflow: Workflow, data: Any = None,
                      copy_data: bool = True, **kwargs) -> amicus.Project:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            amicus.Project: [description]
            
        """
        summary = cls()
        for i, path in enumerate(workflow):
            key = f'{cls.prefix}_{str(i)}'
            if copy_data:
                to_use = copy.deepcopy(data)
            else:
                to_use = data
            summary.contents[key] = workflow.execute_path(data = to_use,
                                                          path = path,
                                                          **kwargs)
        return summary


@dataclasses.dataclass
class Project(amicus.quirks.Keystone, amicus.Validator, 
              amicus.types.Lexicon):
    """Directs construction and execution of an amicus project.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if a 
            amicus instance needs settings from a Configuration 
            instance, 'name' should match the appropriate section name in a 
            Configuration instance. Defaults to None. 
        settings (Union[base.Configuration, Type[base.Configuration], pathlib.Path, str, 
            Mapping[str, Mapping[str, Any]]]): a Configuration-compatible subclass or 
            instance, a str or pathlib.Path containing the file path where a 
            file of a supported file type with settings for a Configuration 
            instance is located, or a 2-level mapping containing settings. 
            Defaults to the default Configuration instance.
        filer (Union[base.Filer, Type[base.Filer], pathlib.Path, str]): a 
            Clerk-compatible class or a str or pathlib.Path containing the full 
            path of where the root folder should be located for file input and 
            output. A 'filer' must contain all file path and import/export 
            methods for use throughout amicus. Defaults to the default Clerk 
            instance. 
        identification (str): a unique identification name for an amicus
            Project. The name is used for creating file folders related to the 
            project. If it is None, a str will be created from 'name' and the 
            date and time. Defaults to None.   
        outline (amicus.project.Stage): an outline of a project workflow 
            derived from 'settings'. Defaults to None.
        workflow (amicus.project.Stage): a workflow of a project derived from 
            'outline'. Defaults to None.
        summary (amicus.project.Stage): a summary of a project execution
            derived from 'workflow'. Defaults to None.
        automatic (bool): whether to automatically advance 'worker' (True) or 
            whether the worker must be advanced manually (False). Defaults to 
            True.
        data (Any): any data object for the project to be applied. If it is
            None, an instance will still execute its workflow, but it won't
            apply it to any external data. Defaults to None.  
        states (ClassVar[Sequence[Union[str, amicus.project.Stage]]]): a
            list of Stages or strings corresponding to keys in 
            'keystones.stage.library'. Defaults to a list containing 'outline',
            'workflow', and 'summary'.
        validations (ClassVar[Sequence[str]]): a list of attributes that need 
            validating. Defaults to a list of attributes in the dataclass field.
    
    Attributes:
        keystones (ClassVar[amicus.types.Lexicon]): a class attribute containing
            a dictionary of base classes with libraries of subclasses of those 
            keystones classes. This attribute is inherited from 
            'amicus.base.Quirks'. Changing this attribute will entirely
            replace the existing links between this instance and all other base
            classes.
        
    """
    name: str = None
    settings: Union[base.Configuration, Type[base.Configuration], pathlib.Path, str, 
                    Mapping[str, Mapping[str, Any]]] = None
    filer: Union[base.Filer, Type[base.Filer], pathlib.Path, str] = None
    identification: str = None
    outline: base.Stage = None
    workflow: base.Stage = None
    summary: base.Stage = None
    automatic: bool = True
    data: Any = None
    stages: ClassVar[Sequence[Union[str, base.Stage]]] = [
        'outline', 'workflow', 'summary']
    validations: ClassVar[Sequence[str]] = [
        'settings', 'name', 'identification', 'filer']
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Calls validation methods.
        self.validate(validations = self.validations)
        # Adds 'general' section attributes from 'settings'.
        self.settings.inject(instance = self)
        # Calls 'create' and 'execute' if 'automatic' is True.
        if self.automatic:
            self.create()

    """ Public Methods """

    def create(self) -> None:
        """[summary]

        Raises:
            TypeError: [description]

        Returns:
            [type]: [description]
            
        """
        for item in self.stages:
            if isinstance(item, str):
                stage = self.keystones.stage.library.borrow(names = item)
            elif inspect.isclass(item) and issubclass(item, self.keystones.stage):
                stage = item
            else:
                raise TypeError(
                    f'Items in stages must be str or {self.keystones.stage} '
                    f'subclasses (not instances)')
            kwargs = stage.needify(instance = self)
            setattr(self, item, stage.create(**kwargs))
            print('test product', getattr(self, item))
        return self 

    def execute(self, **kwargs) -> None:
        """ """
        pass
                        
    """ Private Methods """

    def _validate_name(self, name: str) -> str:
        """Creates 'name' if one doesn't exist.
        
        If 'name' was not passed, this method first tries to infer 'name' as the 
        first appropriate section name in 'settings'. If that doesn't work, it 
        uses the snakecase name of the class.
        
        Args:
            name (str): name of the project, if passed.
            
        Returns:
            str: a default name, if none was passed. But if the passed 'name'
                exists, it is returned unchanged. 
            
        """
        if not name:
            sections = self.settings.excludify(subset = self.settings.skip)
            try:
                name = sections.keys()[0]
            except IndexError:
                name = amicus.tools.snakify(self.__class__)
        return name

    def _validate_identification(self, identification: str) -> str:
        """Creates unique 'identification' if one doesn't exist.
        
        By default, 'identification' is set to the 'name' attribute followed by
        an underscore and the date and time.
        
        Args:
            identification (str): unique identification string for a project.
            
        Returns:
            str: a default identification, derived from the project's 'name'
                attribute and the date and time.
        
        """
        if not identification:
            identification = amicus.tools.datetime_string(prefix = self.name)
        return identification
     