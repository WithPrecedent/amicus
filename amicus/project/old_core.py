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
    Outline
    Workflow
    Summary

"""
from __future__ import annotations
import abc
import copy
import dataclasses
import inspect
import multiprocessing
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Set, Tuple, Type, Union)

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
class Component(amicus.framework.Keystone, amicus.structures.SimpleNode, abc.ABC):
    """Keystone class for parts of an  Workflow.

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
    
    """ Public Class Methods """

    @classmethod
    def create(cls, **kwargs) -> Component:
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
        if 'name' in kwargs:
            if 'outline' in kwargs:
                return cls.from_outline(**kwargs)
            else:
                return cls.from_name(**kwargs)
        else:
            raise ValueError('create method requires a name keyword parameter')
            
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
    def from_outline(cls, name: str, outline: Outline, **kwargs) -> Component:
        """[summary]

        Args:
            name (str): [description]
            section (str): [description]
            outline (Outline): [description]

        Returns:
            Component: [description]
            
        """              
        if name in outline.initialization:
            parameters = outline.initialization[name]
            parameters.update(kwargs)
        else:
            parameters = kwargs
        if name in outline.designs:
            keys = [name, outline.designs[name]]
        else:
            keys = name
        instance = cls.from_name(name = keys, **parameters)
        try:
            instance._add_attributes(attributes = outline.attributes[name])
        except KeyError:
            pass
        instance._add_extras(outline = outline)
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

    def _add_extras(self, outline: amicus.project.Outline) -> None:
        """Hook to allow subclasses to add functionality to base Component.

        Args:
            outline (amicus.project.Outline): [description]

        """
        return self
    

@dataclasses.dataclass
class Stage(amicus.framework.Keystone, amicus.quirks.Needy, abc.ABC):
    """Creates an amicus object.
    
    Args:
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. Defaults to an
            empty list.     
                
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
    needs: ClassVar[Union[Sequence[str], str]] = []


@dataclasses.dataclass
class Outline(Stage):
    """Information needed to construct and execute a Workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an 
            amicus instance needs settings from a Settings instance, 
            'name' should match the appropriate section name in a Settings 
            instance. Defaults to None.
        structure (str): the name matching the type of workflow to be used in a
            project. Defaults to None.
        adjacency (Dict[str, List]): a dictionary with keys that are names of
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
    adjacency: Dict[str, List] = dataclasses.field(default_factory = dict)
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
            source (base.Settings): [description]

        Returns:
            Outline: [description]
            
        """  
        structure = cls._get_structure(name = name, settings = settings) 
        outline = cls(name = name, structure = structure)  
        skips = [k for k in settings.keys() if k.endswith(tuple(settings.skip))]
        component_keys = [k for k in settings.keys() if k not in skips]
        if name is None:
            try:
                name = component_keys[0]
            except IndexError:
                raise ValueError(
                    'No sections in settings indicate how to construct a ' 
                    'project outline')   
        for section in component_keys:
            outline = outline._parse_section(
                name = section, 
                settings = settings,
                outline = outline)
        outline = outline._get_runtime_parameters(
            outline = outline, 
            settings = settings)
        return outline 
    
    """ Private Methods """

    @classmethod
    def _get_structure(cls, name: str, settings: Settings) -> str:
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
  
    def _parse_section(self, 
        name: str, 
        settings: Settings, 
        outline: Outline) -> Outline:
        """[summary]

        Args:
            name (str): [description]
            settings (base.Settings): [description]
            outline (Outline): [description]

        Returns:
            Outline: [description]
        """        
        section = settings[name]
        design = self._get_design(name = name, settings = settings)
        outline.designs[name] = design
        outline.initialization[name] = {}
        outline.attributes[name] = {}
        component = self.keystones.component.create(name = [name, design])
        parameters = tuple(
            i for i in list(component.__annotations__.keys()) 
            if i not in ['name', 'contents'])
        for key, value in section.items():
            suffix = key.split('_')[-1]
            prefix = key[:-len(suffix) - 1]
            if suffix in ['design', 'workflow']:
                pass
            elif suffix in self.keystones.component.subclasses.suffixes:
                outline.designs.update(dict.fromkeys(value, suffix[:-1]))
                outline.adjacency[prefix] = value 
            elif suffix in parameters:
                outline.initialization[name][suffix] = value 
            elif prefix in [name]:
                outline.attributes[name][suffix] = value
            else:
                outline.attributes[name][key] = value
        return outline   

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

    def _get_runtime_parameters(self, 
        outline: Outline, 
        settings: Settings) -> Outline:
        """[summary]

        Args:
            outline (Outline): [description]
            settings (base.Settings): [description]

        Returns:
            Outline: [description]
            
        """
        for component in outline.adjacency.keys():
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
class Workflow(Stage, amicus.structures.Graph):
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
    
    ToDo:
        Move current methods to a Pipeline type Workflow and make
            a true Graph Workflow here.
                     
    """
    contents: Dict[str, List[str]] = dataclasses.field(default_factory = dict)
    default: Any = dataclasses.field(default_factory = list)
    needs: ClassVar[Union[Sequence[str], str]] = ['outline', 'name']

    """ Class Methods """
            
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
        print('test workflow creation', name)
        for component in outline.adjacency[name]:
            print('test workflow subcomponents', component)
            workflow = cls.add_component(
                name = component,
                outline = outline,
                workflow = workflow)
        return workflow
    
    @classmethod
    def add_component(cls, 
        name: str, 
        outline: Outline, 
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
        component = cls.keystones.component.from_outline(
            name = name, 
            outline = outline)
        if hasattr(component, 'workflow'):        
            for subcomponent in outline.adjacency[name]:
                print('test workflow subcomponents', component)
                workflow = cls.add_component(
                    name = component,
                    outline = outline,
                    workflow = component.workflow)
        return workflow


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
class Summary(amicus.types.Lexicon, Stage):
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