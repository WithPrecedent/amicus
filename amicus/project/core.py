"""
amicus.project.core: base classes for an amicus project
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
import dataclasses
import multiprocessing
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, Optional, Sequence, Set, Tuple, Type, Union)
import warnings

import amicus
from . import foundry


@dataclasses.dataclass
class Directive(amicus.quirks.Needy):
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
    implementation: Dict[str, Dict[str, Any]] = dataclasses.field(
        default_factory = dict)
    attributes: Dict[str, Any] = dataclasses.field(default_factory = dict)
    needs: ClassVar[Sequence[str]] = ['settings', 'name', 'library']
    workshop: ClassVar[foundry.Workshop] = foundry.Draft()

    """ Public Methods """
    
    @classmethod   
    def from_settings(cls, 
        settings: amicus.options.Settings,
        name: str, 
        library: amicus.types.Library = None,
        **kwargs) -> Directive:
        """[summary]

        Args:
            name (str): [description]
            settings (amicus.options.Settings): [description]
            library (amicus.types.Library, optional): [description]. 
                Defaults to None.
                
        Returns:
            Directive: [description]
            
        """  
        return cls.workshop.create_directive( 
            settings = settings,
            name = name,
            library = library,
            **kwargs)


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
    name: str = None
    contents: Dict[str, Directive] = dataclasses.field(default_factory = dict)
    default: Any = Directive()
    general: Dict[str, Any] = dataclasses.field(default_factory = dict)
    files: Dict[str, Any] = dataclasses.field(default_factory = dict)
    package: Dict[str, Any] = dataclasses.field(default_factory = dict)
    needs: ClassVar[Sequence[str]] = ['settings', 'name', 'library']
    workshop: ClassVar[foundry.Workshop] = foundry.Draft()
    
    """ Public Methods """
    
    @classmethod
    def from_settings(cls, 
        settings: amicus.options.Settings, 
        name: str, 
        library: amicus.types.Library = None,
        **kwargs) -> Outline:
        """[summary]

        Args:
            name (str): [description]
            settings (amicus.options.Settings): [description]
            library (amicus.types.Library): [description]

        Returns:
            Outline: [description]
            
        """
        return cls.workshop.create(
            settings = settings, 
            name = name, 
            library = library,
            **kwargs)


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
class Component(amicus.structures.Node, abc.ABC):
    """Base Keystone class for nodes in a project workflow.

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
    instances: ClassVar[amicus.types.Catalog] = amicus.types.Catalog()
    subclasses: ClassVar[amicus.types.Catalog] = amicus.types.Catalog()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, **kwargs):
        """Adds 'cls' to appropriate class libraries."""
        super().__init_subclass__(**kwargs)
        # Creates a snakecase key of the class name.
        if cls.suffix is None:
            key = amicus.tools.snakify(cls.__name__)
        else: 
            key = f'{amicus.tools.snakify(cls.__name__)}_{cls.suffix}'
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
        if self.suffix is None:
            key = self.name
        else:
            key = f'{self.name}_{self.suffix}'
        self.instances[key] = self

    """ Properties """
    
    @property
    def suffixes(self) -> tuple[str]:
        """Returns all Component subclass names with an 's' added to the end.
        
        Returns:
            tuple[str]: all subclass names with an 's' added in order to create
                simple plurals.
                
        """
        return tuple(key + 's' for key in self.subclasses.keys())
    
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


@dataclasses.dataclass
class Project(
    amicus.quirks.Element, 
    amicus.framework.Keystone, 
    amicus.framework.Validator):
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
    data: Any = None
    automatic: bool = True
    stages: ClassVar[str] = ['draft', 'publish', 'execute']
    validations: ClassVar[Sequence[str]] = [
        'settings',
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
        self.settings = amicus.options.Settings.create(
            file_path = self.settings)
        self.identification = self._validate_identification(
            identification = self.identification)
        self.filer = amicus.options.Clerk(settings = self.settings)
        # Adds 'general' section attributes from 'settings'.
        self.settings.inject(instance = self)
        # Sets index for iteration.
        self.index = 0
        # Calls 'execute' if 'automatic' is True.
        if self.automatic:
            self.complete()

    """ Public Methods """

    @classmethod
    def create(cls, 
        settings: amicus.options.Settings, 
        **kwargs) -> Project:
        """[summary]

        Args:
            settings (amicus.options.Settings): [description]

        Returns:
            Project: [description]
        """        
        return cls.from_settings(settings = settings, **kwargs)

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
    
    def advance(self) -> Any:
        """Iterates through next stage."""
        return self.__next__()

    def complete(self) -> Any:
        """Iterates through all stages."""
        for stage in self.stages:
            self.advance()
        return self
    
    def draft(self) -> None:
        """Creates 'outline' from 'settings'."""
        if self._check_current(stage = 'draft'):
            self.__next__()       
        return self
    
    def publish(self) -> None:
        """Creates 'workflow' from 'outline'."""
        # print('test outline', self.outline)
        if self._check_current(stage = 'publish'):
            self.__next__()  
        return self

    def execute(self) -> None:
        """Creates 'summary' from 'workflow'."""
        if self._check_current(stage = 'summary'):
            self.__next__()  
        return self
                        
    """ Private Methods """

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

    def _check_current(self, stage: str) -> bool:
        current = self.stages[self.index]
        if current != stage:
            raise IndexError(
                f'You cannot call {stage} because the current stage is '
                f'{current}')
        
    """ Dunder Methods """

    def __iter__(self) -> Iterable:
        """Returns iterable of a Project instance.
        
        Returns:
            Iterable: of the Project instance.
            
        """
        return iter(self)
 
    def __next__(self) -> None:
        """Completes a Stage instance."""
        if self.index < len(self.stages):
            current = self.stages[self.index]
            builder = amicus.project.Workshop.instance(current)
            if hasattr(self, 'verbose') and self.verbose:
                print(f'{builder.action} {builder.product}')
            kwargs = builder.needify(instance = self)
            setattr(self, builder.product, builder.create(**kwargs))
            self.index += 1
        else:
            raise IndexError()
        return self
    