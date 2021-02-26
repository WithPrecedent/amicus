"""
core: essential classes for an amicus project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Settings
    Filer
    Parameters
    Directive
    Workflow
    Summary

"""
from __future__ import annotations
import abc
import collections.abc
import copy
import dataclasses
import inspect
import multiprocessing
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, Optional, Sequence, Set, Tuple, Type, Union)

import more_itertools

import amicus


@dataclasses.dataclass
class Settings(amicus.framework.Keystone, amicus.options.Configuration):
    """Loads and stores configuration settings for a Project.

    Args:
        contents (Mapping[str, Mapping[str, Any]]): a two-level nested dict for
            storing configuration options. Defaults to en empty dict.
        infer_types (bool): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, a False value will leave all values as strings. 
            Defaults to True.
        standard (Mapping[str, Mapping[str]]): any default options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to a dict with 'general', 
            'files', and 'amicus' sections listed.
        skip (Sequence[str]): names of suffixes to skip when constructing nodes
            for an amicus project. Defaults to a list with 'general', 'files',
            'amicus', and 'parameters'.
    
    Attributes:
        keystones (ClassVar[amicus.framework.Library]): library that stores 
            direct subclasses (those with Keystone in their '__bases__' 
            attribute) and allows runtime access and instancing of those stored 
            subclasses.
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
            
    """
    contents: Mapping[str, Mapping[str, Any]] = dataclasses.field(
        default_factory = dict)
    infer_types: bool = True
    standard: Mapping[str, Mapping[str, Any]] = dataclasses.field(
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
class Filer(amicus.Clerk):
    pass  


@dataclasses.dataclass    
class Parameters(amicus.types.Lexicon):
    """Creates and stores parameters for an amicus component.
    
    Parameters allows parameters to be drawn from several different sources, 
    including those which only become apparent during execution of an amicus
    project.
    
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
            in a Settings instance, 'name' should be the prefix to "_parameters"
            as a section name in a Settings instance. Defaults to None. 
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
            parameters in a Settings instance for an entire step, only some of
            which might apply to certain techniques. Defaults to an empty list.

    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: str = None
    default: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    implementation: Mapping[str, str] = dataclasses.field(default_factory = dict)
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
     
    def _from_settings(self, settings: Settings) -> Dict[str, Any]: 
        """Returns any applicable parameters from 'settings'.

        Args:
            settings (Settings): instance with possible parameters.

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
class Directive(object):
    """Information needed to construct and execute a Workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None.
        edges (Dict[str, List]): a dictionary with keys that are names of
            components and values that are lists of subcomponents for the keys.
            However, these named connections are not necessarily the same as an 
            adjacency list because of different design possiblities. Defaults to 
            an empty dict.
        designs (Dict[str, str]): keys are the names of nodes and values are the
            base Node subclass of the named node. Defaults to None.
        initialization (Dict[str, Dict[str, Any]]): a dictionary with keys that 
            are the names of components and values which are dictionaries of 
            pararmeters to use when created the component listed in the key. 
            Defaults to an empty dict.
        implementation (Dict[str, Dict[str, Any]]): a dictionary with keys that 
            are the names of components and values which are dictionaries of 
            pararmeters to use when calling the 'implement' method of the 
            component listed in the key. Defaults to an empty dict.
        attributes (Dict[str, Dict[str, Any]]): a dictionary with keys that 
            are the names of components and values which are dictionaries of 
            attributes to automatically add to the component constructed from
            that key. Defaults to an empty dict.
            
    """
    name: str = None
    edges: Dict[str, List[str]] = dataclasses.field(default_factory = dict)
    designs: Dict[str, str] = dataclasses.field(default_factory = dict)
    initialization: Dict[str, Any] = dataclasses.field(default_factory = dict)
    implementation: Dict[str, Any] = dataclasses.field(default_factory = dict)
    attributes: Dict[str, Any] = dataclasses.field(default_factory = dict)

    """ Public Methods """
    
    @classmethod   
    def create(cls, 
        name: str, 
        settings: Settings, 
        keystones: amicus.framework.Library) -> Directive:
        """[summary]

        Args:
            name (str): [description]
            settings (Settings): [description]
            keystones (amicus.framework.Library): [description]

        Returns:
            Directive: [description]
            
        """        
        edges = {}
        designs = {}
        initialization = {}
        attributes = {}        
        section = settings[name]
        designs[name] = cls._get_design(name = name, settings = settings)
        lookups = [name, designs[name]]
        dummy_component = keystones.component.create(name = lookups)
        possible_initialization = tuple(
            i for i in list(dummy_component.__annotations__.keys()) 
            if i not in ['name', 'contents'])
        for key, value in section.items():
            suffix = key.split('_')[-1]
            prefix = key[:-len(suffix) - 1]
            if suffix in ['design', 'workflow']:
                pass
            elif suffix in keystones.component.subclasses.suffixes:
                designs.update(dict.fromkeys(value, suffix[:-1]))
                connections = amicus.tools.listify(value)
                if prefix in edges:
                    edges[prefix].extend(connections)
                else:
                    edges[prefix] = connections  
            elif suffix in possible_initialization:
                initialization[suffix] = value 
            elif prefix in [name]:
                attributes[suffix] = value
            else:
                attributes[key] = value
        implementation = cls._add_implementation(
            name = name, 
            settings = settings,
            edges = edges)
        return cls(
            name = name, 
            edges = edges,
            designs = designs,
            initialization = initialization,
            implementation = implementation,
            attributes = attributes)

    """ Private Methods """

    @staticmethod
    def _get_design(name: str, settings: Settings) -> str:
        """[summary]

        Args:
            name (str): [description]
            settings (base.Settings):

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

    @staticmethod        
    def _add_implementation(
        name: str, 
        settings: Settings,
        edges: Dict[str, List[str]]) -> Dict[str, Dict[str, Any]]:
        """[summary]

        Args:
            name (str): [description]
            settings (Settings): [description]
            edges

        Returns:
            Dict[str, Any]: [description]
            
        """
        implementation = {}
        components = list(edges.keys())
        more_components = list(more_itertools.collapse(edges.values()))      
        components = components.extend(more_components)
        if components:
            for name in components:
                try:
                    implementation[name] = settings[f'{name}_parameters']
                except KeyError:
                    implementation[name] = {}
        return implementation

    
@dataclasses.dataclass
class Outline(amicus.quirks.Needy, amicus.types.Lexicon):
    """Creates and stores Directive instances derived from Settings.
    
    Args:
        contents (Mapping[str, Directive]]): stored dictionary of Directive 
            instances. Defaults to an empty dict.
        default (Any): default value to return when the 'get' method is used.
              
    """
    contents: Dict[str, Directive] = dataclasses.field(default_factory = dict)
    default: Any = Directive()
    general: Dict[str, Any] = dataclasses.field(default_factory = dict)
    files: Dict[str, Any] = dataclasses.field(default_factory = dict)
    package: Dict[str, Any] = dataclasses.field(default_factory = dict)
    needs: ClassVar[Sequence[str]] = ['settings', 'keystones']
    
    """ Public Methods """
    
    def from_settings(cls, 
        settings: Settings, 
        keystones: amicus.framework.Library) -> Outline:
        """[summary]

        Args:
            settings (Settings): [description]
            name (str, optional): [description]. Defaults to None.
            identification (str, optional): [description]. Defaults to None.

        Raises:
            ValueError: [description]

        Returns:
            Outline: [description]
            
        """
        try:
            general = settings['general']
        except KeyError:
            general = {}
        try:
            files = settings['files']
        except KeyError:
            try:
                files = settings['filer']
            except KeyError:
                files = {}
        try:
            package = settings['amicus']
        except KeyError:
            package = {}
        skips = [k for k in settings.keys() if k.endswith(tuple(settings.skip))]
        keys = [k for k in settings.keys() if k not in skips] 
        directives = {}
        for key in keys:
            directives[key] = Directive.create(
                name = key,
                settings = settings,
                keystones = keystones)
        return cls(
            contents = directives,
            general = general,
            files = files,
            package = package)


@dataclasses.dataclass
class Component(
    amicus.framework.Keystone, 
    amicus.quirks.Needy,
    amicus.structures.Node, 
    abc.ABC):
    """Keystone class for nodes in a project Workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Any): stored item(s) to be used by the 'implement' method.
        parameters (Union[Mapping[Hashable, Any], Parameters): parameters to be 
            attached to 'contents' when the 'implement' method is called. 
            Defaults to an empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
    
    Attributes:
        keystones (ClassVar[amicus.framework.Library]): library that stores 
            direct subclasses (those with Keystone in their '__bases__' 
            attribute) and allows runtime access and instancing of those 
            stored subclasses.
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
                
    """
    name: str = None
    contents: Any = None
    parameters: Union[Mapping[Hashable, Any], Parameters] = dataclasses.field(
        default_factory = dict)
    iterations: Union[int, str] = 1
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']
    
    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        if self.suffix is None:
            key = self.name
        else:
            key = f'{self.name}_{self.suffix}'
        self.instances[key] = self
        
    """ Construction Methods """

    @classmethod
    def from_name(cls, name: Union[str, Sequence[str]], **kwargs) -> Component:
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
            return item(name = primary, **kwargs)
        else:
            instance = copy.deepcopy(item)
            instance._add_attributes(attributes = kwargs)
            return instance
  
    @classmethod
    def from_directive(cls, 
        directive: Directive, 
        name: str = None, 
        **kwargs) -> Component:
        """[summary]

        Args:
            directive (Directive): [description]
            name (str, optional): [description]. Defaults to None.

        Returns:
            Component: [description]
        """        
        if name is None:
            name = directive.name     
        lookups = [name, directive.designs[name]]
        parameters = directive.initialization
        parameters.update({'parameters': directive.implementation[name]}) 
        parameters.update(kwargs)
        instance = cls.from_name(name = lookups, **parameters)
        if name in [directive.name]:
            instance._add_attributes(attributes = directive.attributes) 
        return instance                   
        
    """ Public Methods """
    
    def execute(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """Calls the 'implement' method the number of times in 'iterations'.

        Args:
            project (amicus.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            amicus.Project: with possible changes made.
            
        """
        if self.contents not in [None, 'None', 'none']:
            if self.parameters:
                if isinstance(self.parameters, Parameters):
                    self.parameters.finalize(project = project)
                parameters = self.parameters
                parameters.update(kwargs)
            else:
                parameters = kwargs
            if self.iterations in ['infinite']:
                while True:
                    project = self.implement(project = project, **kwargs)
            else:
                for iteration in range(self.iterations):
                    project = self.implement(project = project, **kwargs)
        return project

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
    
    # """ Dunder Methods """
    
    # def __str__(self) -> str:
    #     return self.name
    
    
@dataclasses.dataclass
class Workflow(amicus.framework.Keystone, amicus.quirks.Needy, abc.ABC):
    """A workflow factory that can be constructed from a Settings instance.
    
    Args:
        contents (Dict[Component], List[str]]): an edges list where the 
            keys are nodes and the values are nodes which the key is connected 
            to. Defaults to an empty dict.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. Defaults to a
            list with 'settings' and 'name'.   
                
    Attributes:
        keystones (ClassVar[amicus.framework.Library]): library that stores 
            amicus base classes and allows runtime access and instancing of 
            those stored subclasses.
        subclasses (ClassVar[amicus.types.Catalog]): catalog that stores 
            concrete subclasses and allows runtime access and instancing of 
            those stored subclasses. 
        instances (ClassVar[amicus.types.Catalog]): catalog that stores
            subclass instances and allows runtime access of those stored 
            subclass instances.
                       
    """
    contents: Dict[amicus.structures.Node, List[str]] = dataclasses.field(
        default_factory = dict)
    default: Any = dataclasses.field(default_factory = list)
    needs: ClassVar[Union[Sequence[str], str]] = ['settings', 'name']

    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'Validator.converters' if it is a concrete class."""
        super().__init_subclass__(**kwargs)
        if not abc.ABC in cls.__bases__:
            # Creates a snakecase key of the class name.
            key = amicus.tools.snakify(cls.__name__)
            # Removes '_workflow' from class name so that the key is consistent
            # with the key name for the class being constructed.
            try:
                key = key.replace('_workflow', '')
            except ValueError:
                pass
            # Adds concrete subclasses to 'library' using 'key'.
            cls.subclasses[key] = cls
            
    """ Class Methods """
    
    @classmethod   
    def from_settings(cls, settings: Settings, name: str = None) -> Workflow:
        """[summary]

        Args:
            source (base.Settings): [description]

        Returns:
            Workflow: [description]
            
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
        workflow = cls.keystones.workflow.select(name = structure)
        return workflow.from_settings(settings = settings, name = name)

    """ Private Methods """
    
    def _add_attributes(self, 
        node: amicus.structures.Node, 
        attributes: Dict[Any, Any]) -> amicus.structures.Node:
        """[summary]

        Args:
            node (amicus.structures.Node): [description]
            attributes (Dict[Any, Any]): [description]

        Returns:
            amicus.structures.Node: [description]
            
        """
        for key, value in attributes.items():
            setattr(node, key, value)
        return node
    

@dataclasses.dataclass
class GraphWorkflow(Workflow, amicus.structures.Graph):
    """A Workflow Graph that can be created from a Settings instance.

    Args:
        contents (Dict[Component], List[str]]): an edges list where the 
            keys are nodes and the values are nodes which the key is connected 
            to. Defaults to an empty dict.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. Defaults to a
            list with 'settings' and 'name'.   
     
    """
    contents: Dict[str, List[str]] = dataclasses.field(default_factory = dict)
    default: Any = dataclasses.field(default_factory = list)
    needs: ClassVar[Union[Sequence[str], str]] = ['settings', 'name']
    
    """ Public Class Methods """
    
    @classmethod   
    def from_settings(cls, settings: Settings, name: str = None) -> Workflow:
        """[summary]

        Args:
            settings (Settings): [description]
            name (str, optional): [description]. Defaults to None.

        Raises:
            ValueError: [description]

        Returns:
            Workflow: [description]
            
        """        
        # skips = [k for k in settings.keys() if k.endswith(tuple(settings.skip))]
        # keys = [k for k in settings.keys() if k not in skips] 
        # if name is None:
        #     try:
        #         name = keys[0]
        #     except IndexError:
        #         raise ValueError(
        #             'No settings indicate how to construct a project workflow') 
        try:
            primary = settings[name]
        except (KeyError, TypeError):
            first_key = list(settings.keys())[0]
            primary = settings[first_key]
        suffixes = cls.keystones.component.subclasses.suffixes
        matches = [v for k, v in primary.items() if k.endswith(suffixes)]
        keys = more_itertools.chain(matches)
        
            
        directives = {} 
        for key in keys:
            directives[key] = Directive.create(
                name = key,
                settings = settings, 
                keystones = cls.keystones)
        workflow = cls.from_directives(directives = directives, name = name) 
        return workflow 
    
    @classmethod
    def from_directives(cls, directives: Dict[str, Directive], name: str) -> Workflow:
        """
        """
        workflow = cls()
        directives.pop(name)
        for directive in directives.values():
            component = cls.keystones.component.from_directive(directive = directive)
            kwargs = {'directive': directive, 'component': component}
            if component.parallel:
                workflow._add_parallel_components(**kwargs)
            else:
                workflow._add_serial_components(**kwargs)
        return workflow
               
    """ Private Methods """
    
    def _add_parallel_components(self, 
            directive: Directive, 
            component: Component) -> None:
        """[summary]

        Args:
            directive (Directive): [description]

        Returns:
        
        """
        self.append(component)
        step_names = directive.edges[directive.name]
        possible = [directive.edges[step] for step in step_names]
        nodes = []
        for i, step_options in enumerate(possible):
            permutation = []
            for option in step_options:
                t_keys = [option, directive.designs[option]]
                technique = self.keystones.component.from_name(
                    name = t_keys,
                    container = step_names[i])
                s_keys = [step_names[i], directive.designs[step_names[i]]]    
                step = self.keystones.component.select(name = s_keys)
                step = step(name = option, contents = technique)
                permutation.append(step)
            nodes.append(permutation)
        self.branchify(nodes = nodes)
        # self.append(component.resolver)
        return self

    def _add_serial_components(self, 
            directive: Directive, 
            component: Component) -> None:
        """[summary]

        Args:
            directive (Directive): [description]

        Returns:
        
        """
        self.append(component)
        components = self._depth_first(name = directive.name, directive = directive)
        collapsed = list(more_itertools.collapse(components))
        nodes = []
        for node in collapsed:
            keys = [node, directive.designs[node]]
            component = self.keystones.component.from_name(name = keys)
            nodes.append(component)
        self.extend(nodes = nodes)
        return self
    
    def _depth_first(self, name: str, directive: Directive) -> List:
        """

        Args:
            name (str):
            details (Blueprint): [description]

        Returns:
            List[List[str]]: [description]
            
        """
        organized = []
        components = directive.edges[name]
        for item in components:
            organized.append(item)
            if item in directive.edges:
                organized_subcomponents = []
                subcomponents = self._depth_first(
                    name = item, 
                    directive = directive)
                organized_subcomponents.append(subcomponents)
                if len(organized_subcomponents) == 1:
                    organized.append(organized_subcomponents[0])
                else:
                    organized.append(organized_subcomponents)
        return organized

    def _get_component(self, name: str, directive: Directive) -> Component:
        """
        """
        lookups = [name, directive.designs[name]]
        kwargs = {}
        try:
            kwargs.update(directive.initialization[name])
        except KeyError:
            pass
        try:
            kwargs.update({'parameters': directive.implementation[name]})
        except KeyError:
            pass     
        component = self.keystones.component.from_name(name = name, **kwargs)
        if name in [directive.name]:
            component = self._add_attributes(
                node = component,
                attributes = directive.attributes)
        return component     
        
    """ Dunder Methods """
    
    def __str__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        new_line = '\n'
        representation = [f'{new_line}amicus {self.__class__.__name__}']
        representation.append('adjacency list:')
        for node, edges in self.contents.items():
            representation.append(f'    {node.name}: {str(edges)}')
        return new_line.join(representation) 
    
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
    

@dataclasses.dataclass
class Summary(
    amicus.framework.Keystone, 
    amicus.quirks.Needy, 
    amicus.types.Lexicon):
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
    needs: ClassVar[Union[Sequence[str], str]] = ['self']

    """ Public Methods """
    
    @classmethod
    def from_project(cls, project: amicus.Project, **kwargs) -> amicus.Project:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            amicus.Project: [description]
            
        """
        summary = cls()
        summary.execute(project = project, **kwargs)
        return summary

    """ Public Methods """
   
    def execute(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            amicus.Project: [description]
            
        """
        if project.parallelize:
            multiprocessing.set_start_method('spawn')
        project._result = None
        for i, path in enumerate(project.workflow.paths):
            name = f'{self.prefix}_{i + 1}'
            project._result = Result(name = name, path = path)
            for node in path:
                try:
                    component = self.keystones.component.instance(name = node)
                    project = component.execute(project = project, **kwargs)
                except KeyError:
                    pass
            self.contents[name] = project._result    
        del project._result    
        return project
    
    # def implement(self, 
    #     node: str, 
    #     project: amicus.Project, 
    #     **kwargs) -> amicus.Project:
    #     """[summary]

    #     Args:
    #         node (str):
    #         project (amicus.Project): [description]

    #     Returns:
    #         amicus.Project: [description]
            
    #     """      
    #     component = self.components[node]
    #     project = component.execute(project = project, **kwargs)
    #     subcomponents = self.contents[node]
    #     if len(subcomponents) > 1:
    #         if project.parallelize:
    #             project = self._implement_parallel(
    #                 component = component,
    #                 project = project, 
    #                 **kwargs)
    #     elif len(subcomponents) == 1:
    #         project = self._implement_in_serial(
    #             component = component,
    #             project = project,
    #             **kwargs)
    #     return project      

    # """ Private Methods """
   
    # def _implement_in_parallel(self, 
    #     component: Component,
    #     project: amicus.Project, 
    #     **kwargs) -> amicus.Project:
    #     """Applies 'implementation' to 'project' using multiple cores.

    #     Args:
    #         project (Project): amicus project to apply changes to and/or
    #             gather needed data from.
                
    #     Returns:
    #         Project: with possible alterations made.       
        
    #     """
    #     if project.parallelize:
    #         with multiprocessing.Pool() as pool:
    #             project = pool.starmap(
    #                 self._implement_in_serial, 
    #                 component, 
    #                 project, 
    #                 **kwargs)
    #     return project 

    # def _implement_in_serial(self, 
    #     component: Component,
    #     project: amicus.Project, 
    #     **kwargs) -> amicus.Project:
    #     """Applies 'implementation' to 'project' using multiple cores.

    #     Args:
    #         project (Project): amicus project to apply changes to and/or
    #             gather needed data from.
                
    #     Returns:
    #         Project: with possible alterations made.       
        
    #     """
    #     return component.execute(project = project, **kwargs)
