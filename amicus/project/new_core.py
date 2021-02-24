"""
core: essential classes for an amicus project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Settings
    Filer
    Parameters
    Component
    Stage
    Workflow
    Workflow
    Summary

"""
from __future__ import annotations
import abc
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
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Mapping[str, Any]): keyword parameters for use by an amicus
            classes' 'implement' method. The 'finalize' method should be called
            for 'contents' to be fully populated from all sources. Defaults to
            an empty dict.
        default (Mapping[str, Any]): default parameters to use if none are 
            provided through an argument or settings. 'default' will also be
            used if any parameters are listed in 'required', in which case the
            parameters will be drawn from 'default' if they are not otherwise
            provided. Defaults to an empty dict.
        runtime (Mapping[str, str]): parameters that can only be determined at
            runtime due to dynamic action of amicus. The keys should be the
            names of the parameters and the values should be attributes or items
            in 'contents' of 'project' passed to the 'finalize' method. Defaults
            to an emtpy dict.
        required (Sequence[str]): parameters that must be passed when the 
            'implement' method of an amicus class is called.
        selected (Sequence[str]): an exclusive list of parameters that are 
            allowed. If 'selected' is empty, all possible parameters are 
            allowed. However, if any are listed, all other parameters that are
            included are removed. This is can be useful when including 
            parameters in a Settings instance for an entire step, only some of
            which might apply to certain techniques. Defaults to an empty dict.

    """
    name: str = None
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    default: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    runtime: Mapping[str, str] = dataclasses.field(default_factory = dict)
    required: Sequence[str] = dataclasses.field(default_factory = list)
    selected: Sequence[str] = dataclasses.field(default_factory = list)
      
    """ Public Methods """

    def finalize(self, project: amicus.Project, **kwargs) -> None:
        """Combines and selects final parameters into 'contents'.

        Args:
            project (amicus.Project): instance from which runtime and settings 
                parameters can be derived.
            
        """
        # Uses kwargs or 'default' parameters as a starting base.
        self.contents = kwargs if kwargs else self.default
        # Adds any parameters from 'settings'.
        try:
            self.contents.update(self._get_from_settings(
                settings = project.settings))
        except AttributeError:
            pass
        # Adds any required parameters.
        for item in self.required:
            if item not in self.contents:
                self.contents[item] = self.default[item]
        # Adds any runtime parameters.
        if self.runtime:
            self.add_runtime(project = project) 
            # Limits parameters to those selected.
            if self.selected:
                self.contents = {k: self.contents[k] for k in self.selected}
        return self

    """ Private Methods """
    
    def _add_runtime(self, project: amicus.Project, **kwargs) -> None:
        """Adds runtime parameters to 'contents'.

        Args:
            project (amicus.Project): instance from which runtime parameters can 
                be derived.
            
        """    
        for parameter, attribute in self.runtime.items():
            try:
                self.contents[parameter] = getattr(project, attribute)
            except AttributeError:
                try:
                    self.contents[parameter] = project.contents[attribute]
                except (KeyError, AttributeError):
                    pass
        if self.selected:
            self.contents = {k: self.contents[k] for k in self.selected}
        return self
     
    def _get_from_settings(self, settings: Settings) -> Dict[str, Any]: 
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


@dataclasses.dataclass
class Component(
    amicus.framework.Keystone, 
    amicus.quirks.Needy,
    amicus.structures.SimpleNode, 
    abc.ABC):
    """Keystone class for parts of a Workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
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
    name: str = None
    contents: Any = None
    iterations: Union[int, str] = 1
    parameters: Union[Mapping[str, Any], Parameters] = Parameters()
    parallel: ClassVar[bool] = False
    needs: ClassVar[Union[Sequence[str], str]] = ['name']
    
    """ Class Methods """

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

    """ Public Methods """
    
    def execute(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            amicus.Project: [description]
            
        """ 
        if self.iterations in ['infinite']:
            while True:
                project = self.implement(project = project, **kwargs)
        else:
            for iteration in range(self.iterations):
                project = self.implement(project = project, **kwargs)
        return project

    def implement(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            amicus.Project: [description]
            
        """
        if self.parameters:
            if isinstance(self.parameters, Parameters):
                self.parameters.finalize(project = project)
            parameters = self.parameters
            parameters.update(kwargs)
        else:
            parameters = kwargs
        if self.contents not in [None, 'None', 'none']:
            project = self.contents.execute(project = project, **parameters)
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

    def _add_extras(self, workflow: amicus.project.Workflow) -> None:
        """Hook to allow subclasses to add functionality to base Component.

        Args:
            workflow (amicus.project.Workflow): [description]

        """
        return self
    

@dataclasses.dataclass
class Workflow(amicus.framework.Keystone, amicus.quirks.Needy, abc.ABC):
    """A workflow factory that can be constructed from a Settings instance.
    
    Args:
        contents (Dict[Component], List[str]]): an adjacency list where the 
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
    contents: Dict[Component, List[str]] = dataclasses.field(
        default_factory = dict)
    default: Any = dataclasses.field(default_factory = list)
    needs: ClassVar[Union[Sequence[str], str]] = ['settings', 'name']

    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to 'Validator.converters' if it is a concrete class."""
        super().__init_subclass__(**kwargs)
        if not abc.ABC in cls.__bases__:
            key = amicus.tools.snakify(cls.__name__)
            # Removes '_workflow' from class name so that the key is consistent
            # with the key name for the class being constructed.
            try:
                key = key.replace('_workflow', '')
            except ValueError:
                pass
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


@dataclasses.dataclass
class GraphWorkflow(Workflow, amicus.structures.Graph):
    """A Workflow Graph that can be created from a Settings instance.

    Args:
        contents (Dict[Component], List[str]]): an adjacency list where the 
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
            source (base.Settings): [description]

        Returns:
            Workflow: [description]
            
        """  
        workflow = cls()
        skips = [k for k in settings.keys() if k.endswith(tuple(settings.skip))]
        keys = [k for k in settings.keys() if k not in skips] 
        if name is None:
            try:
                name = keys[0]
            except IndexError:
                raise ValueError(
                    'No settings indicate how to construct a project workflow')  
        workflow = workflow._parse_sections(keys = keys, settings = settings)
        return workflow 
    
    """ Private Methods """

    def _parse_sections(self, keys: List[str], settings: Settings) -> Workflow:
        """[summary]

        Args:
            keys (List[str]): [description]
            settings (Settings): [description]

        Returns:
            Workflow: [description]
            
        """        
        designs = {}
        subcomponents = {}
        for name in keys: 
            section = settings[name]
            design = self._get_design(name = name, settings = settings)
            lookups = [name, design]
            dummy_component = self.keystones.component.create(name = lookups)
            possible_initialization = tuple(
                i for i in list(dummy_component.__annotations__.keys()) 
                if i not in ['name', 'contents'])
            initialization = {}
            attributes = {}
            for key, value in section.items():
                suffix = key.split('_')[-1]
                prefix = key[:-len(suffix) - 1]
                if suffix in ['design', 'workflow']:
                    pass
                elif suffix in self.keystones.component.subclasses.suffixes:
                    designs.update(dict.fromkeys(value, suffix[:-1]))
                    edges = amicus.tools.listify(value)
                    if prefix in subcomponents:
                        subcomponents[prefix].extend(edges)
                    else:
                        subcomponents[prefix] = edges 
                elif suffix in possible_initialization:
                    initialization[suffix] = value 
                elif prefix in [name]:
                    attributes[suffix] = value
                else:
                    attributes[key] = value
            if dummy_component.parallel:
                self._store_parallel_components(
                    lookups = lookups,
                    subcomponents = subcomponents,
                    initialization = initialization,
                    attributes = attributes,
                    settings = settings)
            else:
                self._store_serial_components(
                    lookups = lookups,
                    subcomponents = subcomponents,
                    initialization = initialization,
                    attributes = attributes,
                    settings = settings)
        for node in subcomponents.keys():
            if node not in self.contents:
                self._store_component(
                    lookups = [node, designs[node]],
                    subcomponents = subcomponents,
                    initialization = {},
                    attributes = {},
                    settings = settings)
        return self  
    
    def _get_design(self, name: str, settings: Settings) -> str:
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

    def _get_parallel_order(self, name: str, subcomponents: Dict[str, List[str]]) -> None:
        """[summary]

        Args:
            outline (amicus.project.Outline): [description]

        Returns:
        
        """
        step_names = subcomponents[name]
        possible = [subcomponents[step] for step in step_names]
        nodes = []
        for i, step_options in enumerate(possible):
            permutation = []
            for option in step_options:
                technique = 
                wrapper = self.from_outline(name = step_names[i],
                                           outline = outline,
                                           contents = technique)
                self.workflow.components[option] = wrapper
            nodes.append(permutation)
        self.workflow.branchify(nodes = nodes)
        return self

    def _store_serial_components(self, 
        lookups: Sequence[str],
        subcomponents: Dict[str, List[str]],
        initialization: Dict[str, Any],
        attributes: Dict[Hashable, Any],
        settings: Settings) -> None:
        """[summary]

        Args:
            lookups (Sequence[str]): [description]
            initialization (Dict[str, Any]): [description]
            attributes (Dict[Hashable, Any]): [description]
            settings (Settings): [description]
            
        """
        components = self._depth_first(name = lookups[0], subcomponents = subcomponents)
        collapsed = list(more_itertools.collapse(components))
        nodes = []
        for node in collapsed:
            nodes.append(self._get_component(
                lookups = ,
                initialization = initialization,
                attributes = attributes,
                settings = settings))
        self.extend(nodes = nodes)
        return self
    
    def _store_component(self, 
        lookups: Sequence[str],
        subcomponents: Dict[str, List[str]],
        initialization: Dict[str, Any],
        attributes: Dict[Hashable, Any],
        settings: Settings) -> None:
        """[summary]

        Args:
            lookups (Sequence[str]): [description]
            initialization (Dict[str, Any]): [description]
            attributes (Dict[Hashable, Any]): [description]
            settings (Settings): [description]
            
        """
        instance = self.keystones.component.create(
            name = lookups, 
            **initialization)
        instance = self._add_settings_parameters(
            name = lookups, 
            settings = settings, 
            instance = instance)
        instance._add_attributes(attributes = attributes)
        self.contents[instance] = subcomponents[instance]
        return self
            
    def _add_settings_parameters(self, 
        name: Union[str, Sequence[str]], 
        settings: Settings, 
        instance: Component) -> Component:
        """[summary]

        Args:
            name (str): [description]
            settings (Settings): [description]
            instance (Component): [description]

        Returns:
            Component: [description]
        """
        kwargs = {}
        for key in name:
            try:
                kwargs.update(settings[f'{key}_parameters'])
                break
            except KeyError:
                pass
        instance.parameters.update(kwargs)
        return instance

    def _add_workflow(self, outline: amicus.project.Outline) -> None:                     
        """[summary]

        Args:
            worker (Worker): [description]
            outline (amicus.project.Outline): [description]

        Returns:
        
        """
        if self.workflow is None:
            self.workflow = self.keystones.stage.select(name = 'workflow')()
        name = self.name
        components = self._depth_first(name = name, outline = outline)
        collapsed = list(more_itertools.collapse(components))
        self.workflow.extend(nodes = collapsed)
        for item in collapsed:
            component = self.from_outline(name = item, outline = outline)
        return self

    def _depth_first(self, name: str, subcomponents: Dict[str, List[str]]) -> List:
        """

        Args:
            name (str):

        Returns:
            List[List[str]]: [description]
            
        """
        organized = []
        components = subcomponents[name]
        for item in components:
            organized.append(item)
            if item in subcomponents:
                organized_subcomponents = []
                subcomponents = self._depth_first(
                    name = item, 
                    subcomponents = subcomponents)
                organized_subcomponents.append(subcomponents)
                if len(organized_subcomponents) == 1:
                    organized.append(organized_subcomponents[0])
                else:
                    organized.append(organized_subcomponents)
        return organized
     

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
