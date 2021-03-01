"""
amicus.project.core: essential classes for an amicus project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Parameters
    Directive
    Outline
    Component
    Result
    Summary

"""
from __future__ import annotations
import abc
import copy
import dataclasses
import inspect
import logging
import multiprocessing
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, Optional, Sequence, Set, Tuple, Type, Union)
import warnings

import more_itertools

import amicus


"""Initializes the amicus project logger."""

LOGGER = logging.getLogger('amicus')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
LOGGER.addHandler(console_handler)
file_handler = logging.FileHandler('amicus.log')
file_handler.setLevel(logging.DEBUG)
LOGGER.addHandler(file_handler)


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
        settings: amicus.options.Settings) -> Dict[str, Any]: 
        """Returns any applicable parameters from 'settings'.

        Args:
            settings (amicus.options.Settings): instance with possible 
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
class Directive(object):
    """Information needed to construct a Worker.
    
    A Directive is typically created from a section of a Settings instance.

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
    def create(cls, name: str, settings: Settings) -> Directive:
        """[summary]

        Args:
            name (str): [description]
            settings (Settings): [description]

        Returns:
            Directive: [description]
            
        """        
        return amicus.project.create_directive(
            name = name, 
            settings = settings)

    
@dataclasses.dataclass
class Outline(amicus.quirks.Needy, amicus.types.Lexicon):
    """Creates and stores Directive instances.
    
    An Outline is typically derived from a Settings instance.
    
    Args:
        contents (Mapping[str, Directive]]): stored dictionary of Directive 
            instances. Defaults to an empty dict.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty Directive.
        general (Dict[str, Any]): general settings for an amicus project. This
            is typically the 'general' section of a Settings instance. Defaults
            to an empty dict.
        files (Dict[str, Any]): general settings for an amicus project. This
            is typically the 'files' or 'filer' section of a Settings instance. 
            Defaults to an empty dict.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. The first item
            in 'needs' to correspond to an internal factory classmethod named
            f'from_{first item in needs}'. Defaults to a list with 'settings',
            'name', and 'library'.
                   
    """
    contents: Dict[str, Directive] = dataclasses.field(default_factory = dict)
    default: Any = Directive()
    general: Dict[str, Any] = dataclasses.field(default_factory = dict)
    files: Dict[str, Any] = dataclasses.field(default_factory = dict)
    package: Dict[str, Any] = dataclasses.field(default_factory = dict)
    needs: ClassVar[Sequence[str]] = ['settings', 'name', 'library']
    
    """ Public Methods """
    
    def from_settings(cls, 
        settings: amicus.options.Settings, 
        name: str, 
        library: amicus.types.Library) -> Outline:
        """[summary]

        Args:
            name (str): [description]
            settings (amicus.options.Settings): [description]
            library (amicus.types.Library): [description]

        Returns:
            Outline: [description]
            
        """
        return amicus.project.create_outline(
            name = name, 
            settings = settings, 
            library = library)


@dataclasses.dataclass
class Component(
    amicus.framework.Keystone, 
    amicus.quirks.Needy,
    amicus.structures.Node, 
    abc.ABC):
    """Keystone class for nodes in a project workflow.

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
        suffix (ClassVar[str]): string to use at the end of 'name' when storing
            an instance in the 'instances' class attribute. This is entirely
            optional, but it can be useful when there are similarly named
            instances in a large Component library. siMpLify uses this to
            associate certain components with Worker instances without 
            fragmenting the Component 'instances' catalog.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. The first item
            in 'needs' to correspond to an internal factory classmethod named
            f'from_{first item in needs}'. Defaults to an empty list.        
    
    Attributes:
        library (ClassVar[amicus.framework.Library]): library that stores 
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
        return amicus.project.create_component(
            name = name, 
            library = cls.library,
            **kwargs)       
  
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
        return amicus.project.create_component(
            name = name, 
            directive = directive,
            library = cls.library,
            **kwargs)                
        
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
                    component = self.library.component.instance(name = node)
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


@dataclasses.dataclass
class Project(amicus.quirks.Needy, amicus.framework.Validator):
    """Directs construction and execution of an amicus project.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        settings (Union[amicus.options.Settings, Type[amicus.options.Settings], 
            Mapping[str, Mapping[str, Any]]], pathlib.Path, str): a Settings-
            compatible subclass or instance, a str or pathlib.Path containing 
            the file path where a file of a supported file type with settings 
            for a Settings instance is located, or a 2-level mapping containing 
            settings. Defaults to the default Settings instance.
        filer (Union[core.Filer, Type[core.Filer], pathlib.Path, str]): a Filer-
            compatible class or a str or pathlib.Path containing the full path 
            of where the root folder should be located for file input and 
            output. A 'filer' must contain all file path and import/export 
            methods for use throughout amicus. Defaults to the default Clerk 
            instance. 
        identification (str): a unique identification name for an amicus 
            Project. The name is used for creating file folders related to the 
            project. If it is None, a str will be created from 'name' and the 
            date and time. Defaults to None.   
        outline (core.Stage): an outline of a project workflow derived from 
            'settings'. Defaults to None.
        workflow (core.Stage): a workflow of a project derived from 'outline'. 
            Defaults to None.
        summary (core.Stage): a summary of a project execution derived from 
            'workflow'. Defaults to None.
        automatic (bool): whether to automatically iterate through the project
            stages (True) or whether it must be iterating manually (False). 
            Defaults to True.
        data (Any): any data object for the project to be applied. If it is 
            None, an instance will still execute its workflow, but it won't
            apply it to any external data. Defaults to None.  
        stages (ClassVar[Sequence[Union[str, core.Stage]]]): a list of Stages or 
            strings corresponding to keys in 'core.library'. Defaults to a list 
            of strings listed in the dataclass field.
        validations (ClassVar[Sequence[str]]): a list of attributes that need 
            validating. Defaults to a list of strings listed in the dataclass 
            field.
    
    Attributes:
        library (ClassVar[core.Library]): a class attribute containing a 
            dot-accessible dictionary of base classes. Each base class has 
            'subclasses' and 'instances' class attributes which contain catalogs
            of subclasses and instances of those library classes. This 
            attribute is inherited from Keystone. Changing this attribute will 
            entirely replace the existing links between this instance and all 
            other base classes.
        
    """
    name: str = None
    settings: Union[
        amicus.options.Settings, 
        Type[amicus.options.Settings], 
        Mapping[str, Mapping[str, Any]],
        pathlib.Path, 
        str] = None
    filer: Union[
        amicus.options.Clerk, 
        Type[amicus.options.Clerk], 
        pathlib.Path, 
        str] = None
    identification: str = None
    outline: Union[Type[Outline], str] = None
    workflow: Union[Type[Component], str] = None
    summary: Union[Type[Summary], str] = None
    automatic: bool = True
    data: Any = None
    needs: ClassVar[Sequence[str]] = ['settings']
    stages: ClassVar[str] = ['draft', 'publish', 'execute']
    validations: ClassVar[Sequence[str]] = [
        'name', 
        'identification', 
        'filer']
    
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
        self.settings = self._validate_settings(settings = self.settings)
        self.validate(validations = self.validations)
        # Adds 'general' section attributes from 'settings'.
        self.settings.inject(instance = self)
        # Sets index for iteration.
        self.index = 0
        # Automatically creates 'workflow' from 'settings'.
        self.workflow = self.library.workflow.from_settings(
            settings = self.settings, 
            name = self.name)
        # Calls 'execute' if 'automatic' is True.
        if self.automatic:
            self.execute()

    """ Class Methods """

    @classmethod
    def from_settings(cls, 
        settings: amicus.options.Settings, 
        **kwargs) -> Project:
        """[summary]

        Args:
            settings (amicus.options.Settings): [description]

        Returns:
            Project: [description]
        """        
        return cls(settings = settings, **kwargs)
        
    """ Public Methods """
    
    # def advance(self) -> Any:
    #     """Returns next product created in iterating a Director instance."""
    #     return self.__next__()

    def draft(self) -> None:
        """[summary]"""
        kwargs = Outline.needify(instance = self)
        self.outline = Outline.create(**kwargs)
        return self
    
    def publish(self) -> None:
        """[summary]"""
        kwargs = Component.needify(instance = self)
        self.workflow = Component.create(**kwargs)
        return self

    def execute(self) -> None:
        """[summary]"""
        kwargs = Summary.needify(instance = self)
        self.summary = Summary.create(**kwargs)
        return self
                        
    """ Private Methods """

    def _validate_settings(self, settings: Any) -> amicus.options.Settings:
        return self.library.settings.create(file_path = settings)
    
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

    def _validate_workflow(self, 
        workflow: Union[str, Type[core.Workflow]]) -> core.Workflow:
        """[summary]

        Args:
            settings (Settings): [description]
            name (str, optional): [description]. Defaults to None.

        Raises:
            ValueError: [description]

        Returns:
            Workflow: [description]
            
        """        
        section = self._get_primary()
        directive = Directive.create(
            settings = self.settings,
            name = self.name,
            library = self.library)
        suffixes = self.library.component.subclasses.suffixes
        matches = [v for k, v in section.items() if k.endswith(suffixes)]
        keys = more_itertools.chain(matches)  
        directives = {} 
        for key in keys:
            directives[key] = core.Directive.create(
                name = key,
                settings = self.settings, 
                library = cls.library)
        workflow = cls.from_directives(directives = directives, name = name) 
        return workflow 
        
    def _get_primary(self) -> Dict[str, Any]:
        """[summary]

        Returns:
            Dict[str, Any]: [description]
        """        
        try:
            primary = self.settings[self.name]
        except KeyError:
            try:
                first_key = list(self.settings.keys())[0]
                primary = self.settings[first_key]
            except IndexError:
                ValueError(
                    'No settings indicate how to construct a project workflow')
        return primary
 
    # """ Dunder Methods """

    # def __iter__(self) -> Iterable:
    #     """Returns iterable of a Project instance.
        
    #     Returns:
    #         Iterable: of the Project instance.
            
    #     """
    #     return iter(self)
 
    # def __next__(self) -> None:
    #     """Completes a Stage instance."""
    #     if self.index < len(self.stages):
    #         base = self.library.stage
    #         current = self.stages[self.index]
    #         if isinstance(current, str):
    #             name = amicus.tools.snakify(current)
    #             stage = base.select(name = name)
    #         elif inspect.isclass(current) and issubclass(current, base):
    #             stage = current
    #             name = amicus.tools.snakify(stage.__name__)
    #         else:
    #             raise TypeError(
    #                 f'Items in stages must be str or {base.__name__} '
    #                 f'subclasses (not instances)') 
    #         if hasattr(self, 'verbose') and self.verbose:
    #             print(f'Creating {name}')
    #         kwargs = stage.needify(instance = self)
    #         setattr(self, name, stage.create(**kwargs))
    #         if hasattr(self, 'verbose') and self.verbose:
    #             print(f'Completed {name}')
    #         self.index += 1
    #     else:
    #         raise IndexError()
    #     return self
    