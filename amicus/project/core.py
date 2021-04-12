"""
amicus.project.core:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import abc
import dataclasses
import inspect
import itertools
import multiprocessing
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)

import more_itertools

import amicus
from . import configuration
from . import workshop


@dataclasses.dataclass
class Settings(amicus.options.Configuration):
    """Loads and stores configuration settings for an amicus project

    Args:
        contents (Mapping[str, Mapping[str, Any]]): a two-level nested dict for
            storing configuration options. Defaults to en empty dict.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty dict.
        standard (Mapping[str, Mapping[str]]): any standard options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to an empty dict.
        infer_types (bool): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, all values will be strings. Defaults to True.
        project (amicus.Project): associated Project instance. This is needed 
            for this class' properties and additional methods to function
            properly. Defaults to None.

    """
    contents: Mapping[str, Mapping[str, Any]] = dataclasses.field(
        default_factory = dict)
    default: Any = dataclasses.field(default_factory = dict)
    standard: Mapping[str, Mapping[str, Any]] = dataclasses.field(
        default_factory = dict)
    infer_types: bool = True
    project: amicus.Project = None
    
    """ Properties """
    
    @property
    def bases(self) -> Dict[str, str]:
        return self._get_bases()
    
    @property
    def connections(self) -> Dict[str, List[str]]:
        return self._get_connections()

    @property
    def designs(self) -> Dict[str, str]:
        return self._get_designs()
    
    @property
    def managers(self) -> Dict[str, str]:
        return self._get_managers()
     
    @property
    def nodes(self) -> List[str]:
        key_nodes = list(self.connections.keys())
        value_nodes = list(
            itertools.chain.from_iterable(self.connections.values()))
        return amicus.tools.deduplicate(iterable = key_nodes + value_nodes)
        
        
    """ Private Methods """

    def _get_bases(self) -> Dict[str, str]:  
        suffixes = self.project.library.subclasses.suffixes 
        managers = self.managers
        bases = {}
        for name in self.nodes:
            section = managers[name]
            component_keys = [
                k for k in self[section].keys() if k.endswith(suffixes)]
            if component_keys:
                bases[name] = settings_to_base(
                    name = name,
                    section = managers[name])
                for key in component_keys:
                    prefix, suffix = amicus.tools.divide_string(key)
                    values = amicus.tools.listify(self[section][key])
                    if suffix.endswith('s'):
                        design = suffix[:-1]
                    else:
                        design = suffix            
                    bases.update(dict.fromkeys(values, design))
        return bases
      
    def _get_connections(self) -> Dict[str, List[str]]:
        suffixes = self.project.library.subclasses.suffixes 
        connections = {}
        for name, section in self.items():
            component_keys = [k for k in section.keys() if k.endswith(suffixes)]
            for key in component_keys:
                prefix, suffix = amicus.tools.divide_string(key)
                values = amicus.tools.listify(section[key])
                if prefix == suffix:
                    if name in connections:
                        connections[name].extend(values)
                    else:
                        connections[name] = values
                else:
                    if prefix in connections:
                        connections[prefix].extend(values)
                    else:
                        connections[prefix] = values
        return connections
    
    def _get_designs(self) -> Dict[str, str]:  
        suffixes = self.project.library.subclasses.suffixes 
        managers = self.managers
        designs = {}
        for name in self.nodes:
            section = managers[name]
            component_keys = [
                k for k in self[section].keys() if k.endswith(suffixes)]
            if component_keys:
                designs[name] = settings_to_base(
                    name = name,
                    section = managers[name])
                for key in component_keys:
                    prefix, suffix = amicus.tools.divide_string(key)
                    values = amicus.tools.listify(self[section][key])
                    if suffix.endswith('s'):
                        design = suffix[:-1]
                    else:
                        design = suffix            
                    designs.update(dict.fromkeys(values, design))
        return designs
    
    def _get_managers(self) -> Dict[str, str]:
        suffixes = self.project.library.subclasses.suffixes 
        managers = {}
        for name, section in self.items():
            component_keys = [k for k in section.keys() if k.endswith(suffixes)]
            if component_keys:
                managers[name] = name
                for key in component_keys:
                    values = amicus.tools.listify(section[key])
                    managers.update(dict.fromkeys(values, name))
        return managers
    

@dataclasses.dataclass
class Registry(amicus.types.Catalog):
    """A Catalog of Component subclasses or subclass instances."""

    """ Properties """
    
    @property
    def suffixes(self) -> tuple[str]:
        """Returns all stored names and naive plurals of those names.
        
        Returns:
            tuple[str]: all names with an 's' added in order to create simple 
                plurals combined with the stored keys.
                
        """
        plurals = [key + 's' for key in self.contents.keys()]
        return tuple(list(self.contents.keys()) + plurals)

 
@dataclasses.dataclass
class Library(object):
    
    subclasses: Registry = Registry()
    instances: Registry = Registry()

    """ Properties """
    
    @property
    def leaves(self) -> Tuple[str]:
        instances = [
            k for k, v in self.instances.items() if isinstance(v, Leaf)]
        subclasses = [
            k for k, v in self.subclasses.items() if issubclass(v, Leaf)]
        return tuple(instances + subclasses)

    @property
    def hubs(self) -> Tuple[str]:
        instances = [
            k for k, v in self.instances.items() if isinstance(v, Hub)]
        subclasses = [
            k for k, v in self.subclasses.items() if issubclass(v, Hub)]
        return tuple(instances + subclasses)
    
    @property
    def recipes(self) -> Tuple[str]:
        instances = [
            k for k, v in self.instances.items() if isinstance(v, Recipe)]
        subclasses = [
            k for k, v in self.subclasses.items() if issubclass(v, Recipe)]
        return tuple(instances + subclasses)   
    
    """ Public Methods """
    
    def classify(self, component: str) -> str:
        """[summary]

        Args:
            component (str): [description]

        Returns:
            str: [description]
            
        """        
        if component in self.leaves:
            return 'leaf'
        elif component in self.hubs:
            return 'parallel'
        elif component in self.recipes:
            return 'serial'

    def instance(self, name: Union[str, Sequence[str]], **kwargs) -> Component:
        """Returns instance of first match of 'name' in stored catalogs.
        
        The method prioritizes the 'instances' catalog over 'subclasses' and any
        passed names in the order they are listed.
        
        Args:
            name (Union[str, Sequence[str]]): [description]
            
        Raises:
            KeyError: [description]
            
        Returns:
            Component: [description]
            
        """
        names = amicus.tools.listify(name)
        primary = names[0]
        item = None
        for key in names:
            for catalog in ['instances', 'subclasses']:
                try:
                    item = getattr(self, catalog)[key]
                    break
                except KeyError:
                    pass
            if item is not None:
                break
        if item is None:
            raise KeyError(f'No matching item for {name} was found') 
        elif inspect.isclass(item):
            instance = item(name = primary, **kwargs)
        else:
            instance = copy.deepcopy(item)
            for key, value in kwargs.items():
                setattr(instance, key, value)  
        return instance 

    def register(self, component: Union[Component, Type[Component]]) -> None:
        """[summary]

        Args:
            component (Union[Component, Type[Component]]): [description]

        Raises:
            TypeError: [description]

        Returns:
            [type]: [description]
            
        """
        if isinstance(component, Component):
            instances_key = self._get_instances_key(component = component)
            self.instances[instances_key] = component
            subclasses_key = self._get_subclasses_key(component = component)
            if subclasses_key not in self.subclasses:
                self.subclasses[subclasses_key] = component.__class__
        elif inspect.isclass(component) and issubclass(component, Component):
            subclasses_key = self._get_subclasses_key(component = component)
            self.subclasses[subclasses_key] = component
        else:
            raise TypeError(
                f'component must be a Component subclass or instance')
        return self
    
    def select(self, name: Union[str, Sequence[str]]) -> Component:
        """Returns subclass of first match of 'name' in stored catalogs.
        
        The method prioritizes the 'subclasses' catalog over 'instances' and any
        passed names in the order they are listed.
        
        Args:
            name (Union[str, Sequence[str]]): [description]
            
        Raises:
            KeyError: [description]
            
        Returns:
            Component: [description]
            
        """
        names = amicus.tools.listify(name)
        item = None
        for key in names:
            for catalog in ['subclasses', 'instances']:
                try:
                    item = getattr(self, catalog)[key]
                    break
                except KeyError:
                    pass
            if item is not None:
                break
        if item is None:
            raise KeyError(f'No matching item for {name} was found') 
        elif inspect.isclass(item):
            component = item
        else:
            component = item.__class__  
        return component 

    def parameterify(self, name: Union[str, Sequence[str]]) -> List[str]:
        """[summary]

        Args:
            name (Union[str, Sequence[str]]): [description]

        Returns:
            List[str]: [description]
            
        """        
        component = self.select(name = name)
        return list(component.__annotations__.keys())
           
    """ Private Methods """
    
    def _get_instances_key(self, 
        component: Union[Component, Type[Component]]) -> str:
        """Returns a snakecase key of the class name.
        
        Returns:
            str: the snakecase name of the class.
            
        """
        try:
            key = component.name 
        except AttributeError:
            try:
                key = amicus.tools.snakify(component.__name__) 
            except AttributeError:
                key = amicus.tools.snakify(component.__class__.__name__)
        return key
    
    def _get_subclasses_key(self, 
        component: Union[Component, Type[Component]]) -> str:
        """Returns a snakecase key of the class name.
        
        Returns:
            str: the snakecase name of the class.
            
        """
        try:
            key = amicus.tools.snakify(component.__name__) 
        except AttributeError:
            key = amicus.tools.snakify(component.__class__.__name__)
        return key      


@dataclasses.dataclass    
class Parameters(amicus.types.Lexicon):
    """Creates and stores parameters for a Component.
    
    The use of Parameters is entirely optional, but it provides a handy tool
    for aggregating data from an array of sources, including those which only 
    become apparent during execution of an amicus project, to create a unified 
    set of implementation parameters.
    
    Parameters can be unpacked with '**', which will turn the 'contents' 
    attribute an ordinary set of kwargs. In this way, it can serve as a drop-in
    replacement for a dict that would ordinarily be used for accumulating 
    keyword arguments.
    
    If an amicus class uses a Parameters instance, the 'finalize' method should
    be called before that instance's 'implement' method in order for each of the
    parameter types to be incorporated.
    
    Args:
        contents (Mapping[str, Any]): keyword parameters for use by an amicus
            classes' 'implement' method. The 'finalize' method should be called
            for 'contents' to be fully populated from all sources. Defaults to
            an empty dict.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. To properly match parameters
            in a Configuration instance, 'name' should be the prefix to "_parameters"
            as a section name in a Configuration instance. Defaults to None. 
        default (Mapping[str, Any]): default parameters that will be used if 
            they are not overridden. Defaults to an empty dict.
        implementation (Mapping[str, str]): parameters with values that can only 
            be determined at runtime due to dynamic nature of amicus and its 
            workflows. The keys should be the names of the parameters and the 
            values should be attributes or items in 'contents' of 'project' 
            passed to the 'finalize' method. Defaults to an emtpy dict.
        selected (Sequence[str]): an exclusive list of parameters that are 
            allowed. If 'selected' is empty, all possible parameters are 
            allowed. However, if any are listed, all other parameters that are
            included are removed. This is can be useful when including 
            parameters in a Configuration instance for an entire step, only some of
            which might apply to certain techniques. Defaults to an empty list.

    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    default: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    implementation: Mapping[str, str] = dataclasses.field(
        default_factory = dict)
    selected: Sequence[str] = dataclasses.field(default_factory = list)
      
    """ Public Methods """

    def finalize(self, project: amicus.Project, **kwargs) -> None:
        """Combines and selects final parameters into 'contents'.

        Args:
            project (amicus.Project): instance from which implementation and 
                settings parameters can be derived.
            
        """
        # Uses kwargs and 'default' parameters as a starting base.
        parameters = self.default
        parameters.update(kwargs)
        # Adds any parameters from 'settings'.
        try:
            parameters.update(self._from_settings(settings = project.settings))
        except AttributeError:
            pass
        # Adds any implementation parameters.
        if self.implementation:
            parameters.update(self._at_runtime(project = project))
        # Adds any parameters already stored in 'contents'.
        parameters.update(self.contents)
        # Limits parameters to those in 'selected'.
        if self.selected:
            self.contents = {k: self.contents[k] for k in self.selected}
        self.contents = parameters
        return self

    """ Private Methods """
     
    def _from_settings(self, 
        settings: amicus.options.Configuration) -> Dict[str, Any]: 
        """Returns any applicable parameters from 'settings'.

        Args:
            settings (amicus.options.Configuration): instance with possible 
                parameters.

        Returns:
            Dict[str, Any]: any applicable settings parameters or an empty dict.
            
        """
        try:
            parameters = settings[f'{self.name}_parameters']
        except KeyError:
            suffix = self.name.split('_')[-1]
            prefix = self.name[:-len(suffix) - 1]
            try:
                parameters = settings[f'{prefix}_parameters']
            except KeyError:
                try:
                    parameters = settings[f'{suffix}_parameters']
                except KeyError:
                    parameters = {}
        return parameters
   
    def _at_runtime(self, project: amicus.Project) -> Dict[str, Any]:
        """Adds implementation parameters to 'contents'.

        Args:
            project (amicus.Project): instance from which implementation 
                parameters can be derived.

        Returns:
            Dict[str, Any]: any applicable settings parameters or an empty dict.
                   
        """    
        for parameter, attribute in self.implementation.items():
            try:
                self.contents[parameter] = getattr(project, attribute)
            except AttributeError:
                try:
                    self.contents[parameter] = project.contents[attribute]
                except (KeyError, AttributeError):
                    pass
        return self
 

@dataclasses.dataclass
class Component(abc.ABC):
    """Base Keystone class for nodes in a project workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Configuration instance, 'name' should 
            match the appropriate section name in a Configuration instance. Defaults 
            to None. 
        contents (Any): stored item(s) to be used by the 'implement' method.
            Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.

    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of Component. 
  
    """
    name: str = None
    contents: Any = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)
    iterations: Union[int, str] = 1
    library: ClassVar[Library] = Library()

    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'library'."""
        super().__init_subclass__(**kwargs)
        # Adds concrete subclasses to 'library'.
        if not abc.ABC in cls.__bases__:
            cls.library.register(component = cls)
            
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Adds instance to 'library'.
        self.library.register(component = self)
  
    """ Required Subclass Methods """

    @abc.abstractmethod
    def implement(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """Applies 'contents' to 'project'.

        Subclasses must provide their own methods.

        Args:
            project (amicus.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            amicus.Project: with possible changes made.
            
        """
        pass

    """ Public Methods """
    
    def execute(self, 
        project: amicus.Project, 
        iterations: Union[int, str] = None, 
        **kwargs) -> amicus.Project:
        """Calls the 'implement' method the number of times in 'iterations'.

        Args:
            project (amicus.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            amicus.Project: with possible changes made.
            
        """
        if iterations is None:
            iterations = self.iterations
        if self.contents not in [None, 'None', 'none']:
            if self.parameters:
                if isinstance(self.parameters, Parameters):
                    self.parameters.finalize(project = project)
                parameters = self.parameters
                parameters.update(kwargs)
            else:
                parameters = kwargs
            if iterations in ['infinite']:
                while True:
                    project = self.implement(project = project, **parameters)
            else:
                for iteration in range(iterations):
                    project = self.implement(project = project, **parameters)
        return project

    """ Dunder Methods """
    
    def __call__(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """Applies 'implement' method if an instance is called.
        
        Args:
            project (amicus.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            amicus.Project: with possible changes made.
            
        """
        return self.implement(project = project, **kwargs)

      
@dataclasses.dataclass
class Recipe(amicus.structures.Pipeline, Component):
    """Creates, stores, and executes a serial pipeline of Components.

    Args:
        contents (Sequence[Any]): items with 'name' attributes to store. If a 
            dict is passed, the keys will be ignored and only the values will be 
            added to 'contents'. If a single item is passed, it will be placed 
            in a list. Defaults to an empty list.
        default (Any): default value to return when the 'get' method is used.
            
    """
    contents: Sequence[nodes.Component] = dataclasses.field(
        default_factory = list)
    default: Any = None
    
    """ Public Methods """
    
    @classmethod
    def create(cls, project: amicus.Project, **kwargs) -> Workflow:
        """Creates a Workflow instance from 'project'.
                
        Returns:
            Workflow: created from attributes of 'project' and/or any default
                options if the data for creation is not in 'project'.
                
        """
        return workshop.create_workflow(project = project, **kwargs)   

    def organize(self, subcomponents: Dict[str, List[str]]) -> None:
        """[summary]

        Args:
            subcomponents (Dict[str, List[str]]): [description]

        """
        subcomponents = self._serial_order(
            name = self.name, 
            subcomponents = subcomponents)
        nodes = list(more_itertools.collapse(subcomponents))
        if nodes:
            self.extend(nodes = nodes)
        return self       

    def implement(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """Applies 'contents' to 'project'.
        
        Args:
            project (amicus.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            amicus.Project: with possible changes made.
            
        """
        return self._implement_in_serial(project = project, **kwargs)    

    """ Private Methods """
    
    def _serial_order(self, 
        name: str,
        subcomponents: Dict[str, List[str]]) -> List[Hashable]:
        """[summary]

        Args:
            name (str): [description]
            directive (core.Directive): [description]

        Returns:
            List[Hashable]: [description]
            
        """   
        organized = []
        components = subcomponents[name]
        for item in components:
            organized.append(item)
            if item in subcomponents:
                organized_subcomponents = []
                subcomponents = self._serial_order(
                    name = item, 
                    subcomponents = subcomponents)
                organized_subcomponents.append(subcomponents)
                if len(organized_subcomponents) == 1:
                    organized.append(organized_subcomponents[0])
                else:
                    organized.append(organized_subcomponents)
        return organized   


@dataclasses.dataclass
class Workflow(amicus.structures.Graph, Component):
    """Creates, stores, and execustes a directed acyclic graph (DAG).
    
    Args:
        contents (Dict[Hashable, List[Hashable]]): an adjacency list where the 
            keys are names of nodes and the values are names of nodes which the 
            key is connected to. All nodes that are named in the keys and values
            should be stored in 'library.subclasses' or 'library.instances'. 
            Defaults to an empty dict.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.
        library (Library): catalogs of Component subclasses and instances
            that are used to execute a Workflow. Defaults to an empty library.
                  
    """  
    contents: Dict[Hashable, List[Hashable]] = dataclasses.field(
        default_factory = dict)
    default: Any = dataclasses.field(default_factory = list) 
    components: Registry = dataclasses.field(default_factory = Registry)

    """ Properties """   
    
    @property
    def recipes(self) -> List[Recipe]:
        """Returns all paths through the Graph as a list of Recipe instances.
        
        Returns:
            List[Recipe]: returns all paths from 'roots' to 'endpoints' as a
                list of Component instances.
                
        """
        paths = self.paths
        recipes = []
        for i, path in enumerate(paths):
            components = [self.library.instance(name = c) for c in path]
            recipes.append(Recipe(contents = components))
        return recipes
    
    """ Public Methods """
    
    @classmethod
    def create(cls, project: amicus.Project, **kwargs) -> Workflow:
        """Creates a Workflow instance from 'project'.
                
        Returns:
            Workflow: created from attributes of 'project' and/or any default
                options if the data for creation is not in 'project'.
                
        """
        return workshop.create_workflow(project = project, **kwargs)


@dataclasses.dataclass
class Hub(Workflow, abc.ABC):
    """Base class for branching and parallel Workers.
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Configuration instance, 'name' should 
            match the appropriate section name in a Configuration instance. Defaults 
            to None. 
        contents (Dict[str, List[str]]): an adjacency list where the keys are 
            names of components and the values are names of components which the 
            key component is connected to. Defaults to an empty dict.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.
        criteria (Union[Callable, str]): algorithm to use to resolve the 
            parallel branches of the workflow or the name of a Component in 
            'library' to use. Defaults to None.

    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of Component. 
                          
    """
    name: str = None
    contents: Dict[str, List[str]] = dataclasses.field(default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    critera: Union[Callable, str] = None
              
    """ Public Methods """

    def organize(self, subcomponents: Dict[str, List[str]]) -> None:
        """[summary]

        Args:
            subcomponents (Dict[str, List[str]]): [description]

        """
        step_names = subcomponents[self.name]
        nodes = [subcomponents[step] for step in step_names]
        self.branchify(nodes = nodes)
        return self  
       
    def implement(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """Applies 'contents' to 'project'.
        
        Args:
            project (amicus.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            amicus.Project: with possible changes made.
            
        """
        if len(self.contents) > 1 and project.parallelize:
            project = self._implement_in_parallel(project = project, **kwargs)
        else:
            project = self._implement_in_serial(project = project, **kwargs)
        return project      

    """ Private Methods """
   
    def _implement_in_parallel(self, 
        project: amicus.Project, 
        **kwargs) -> amicus.Project:
        """Applies 'implementation' to 'project' using multiple cores.

        Args:
            project (Project): amicus project to apply changes to and/or
                gather needed data from.
                
        Returns:
            Project: with possible alterations made.       
        
        """
        if project.parallelize:
            with multiprocessing.Pool() as pool:
                project = pool.starmap(
                    self._implement_in_serial, 
                    project, 
                    **kwargs)
        return project 


@dataclasses.dataclass
class Contest(Hub):
    """Resolves a parallel workflow by selecting the best option.

    It resolves a parallel workflow based upon criteria in 'contents'
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Configuration instance, 'name' should 
            match the appropriate section name in a Configuration instance. Defaults 
            to None. 
        contents (Dict[str, List[str]]): an adjacency list where the keys are 
            names of components and the values are names of components which the 
            key component is connected to. Defaults to an empty dict.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.
        criteria (Union[Callable, str]): algorithm to use to resolve the 
            parallel branches of the workflow or the name of a Component in 
            'library' to use. Defaults to None.
            
    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of Component. 
                          
    """
    name: str = None
    contents: Dict[str, List[str]] = dataclasses.field(default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    critera: Callable = None
 
    
@dataclasses.dataclass
class Study(Hub):
    """Allows parallel workflow to continue

    A Study might be wholly passive or implement some reporting or alterations
    to all parallel workflows.
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Configuration instance, 'name' should 
            match the appropriate section name in a Configuration instance. Defaults 
            to None. 
        contents (Dict[str, List[str]]): an adjacency list where the keys are 
            names of components and the values are names of components which the 
            key component is connected to. Defaults to an empty dict.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.
        criteria (Union[Callable, str]): algorithm to use to resolve the 
            parallel branches of the workflow or the name of a Component in 
            'library' to use. Defaults to None.
            
    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of Component. 
                        
    """
    name: str = None
    contents: Dict[str, List[str]] = dataclasses.field(default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    critera: Callable = None
  
    
@dataclasses.dataclass
class Survey(Hub):
    """Resolves a parallel workflow by averaging.

    It resolves a parallel workflow based upon the averaging criteria in 
    'contents'
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Configuration instance, 'name' should 
            match the appropriate section name in a Configuration instance. Defaults 
            to None. 
        contents (Dict[str, List[str]]): an adjacency list where the keys are 
            names of components and the values are names of components which the 
            key component is connected to. Defaults to an empty dict.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.
        criteria (Union[Callable, str]): algorithm to use to resolve the 
            parallel branches of the workflow or the name of a Component in 
            'library' to use. Defaults to None.
            
    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of Component. 
                            
    """
    name: str = None
    contents: Dict[str, List[str]] = dataclasses.field(default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    critera: Callable = None

 
@dataclasses.dataclass
class Cookbook(amicus.types.Lexicon):
    """Stores a xollection of Recipes.
    
    Args:
        contents (Mapping[Hashable, Recipe]]): stored dictionary. Defaults to an 
            empty dict.
        default (Any): default value to return when the 'get' method is used.
            Defaults to None.
              
    """
    contents: Mapping[Hashable, Recipe] = dataclasses.field(
        default_factory = dict)
    default: Any = None

    """ Public Methods """
    
    @classmethod
    def create(cls, project: amicus.Project, **kwargs) -> Workflow:
        """Creates a Workflow instance from 'project'.
                
        Returns:
            Cookbook: created from attributes of 'project' and/or any default
                options if the data for creation is not in 'project'.
                
        """
        return workshop.create_cookbook(project = project, **kwargs)  


@dataclasses.dataclass
class Result(amicus.types.Lexicon):            
    """Stores results from a single path through a Workflow.

    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.  
        default (Any): default value to return when the 'get' method is used.
        name (str): name of particular path through a workflow for which 
            'contents' are associated.
        path (Sequence[str]): the names of the nodes through a workflow 
            corresponding to the results stored in 'contents'.
        
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    default: Any = None
    name: str = None
    path: Sequence[str] = dataclasses.field(default_factory = list)

    """ Public Methods """
    
    @classmethod
    def create(cls, project: amicus.Project, **kwargs) -> Summary:
        """Creates a Result instance from 'workflow' and 'path'.
                
        Returns:
            Summary: created from attributes of 'project' and/or any default
                options if the data for creation is not in 'project'.
                
        """
        return workshop.create_result(project = project, **kwargs)
         
        
@dataclasses.dataclass
class Summary(amicus.types.Lexicon):
    """Collects and stores results of all paths through a Workflow.
    
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
    contents: Mapping[str, Result] = dataclasses.field(default_factory = dict)
    default: Any = Result()
    prefix: str = 'path'

    """ Public Methods """
    
    @classmethod
    def create(cls, project: amicus.Project, **kwargs) -> Summary:
        """Creates a Summary instance from 'project'.
                
        Returns:
            Summary: created from attributes of 'project' and/or any default
                options if the data for creation is not in 'project'.
                
        """
        return workshop.create_summary(project = project, **kwargs)
     