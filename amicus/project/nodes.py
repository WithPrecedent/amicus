"""
amicus.project.nodes:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Step
    Technique
    Worker
    Pipeline
    Contest
    Study
    Survey

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
from . import core
from . import draft


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
class Workshop(object):
    """Builds Component instances.
    
    """
    base: Type[Component] = Component
    
    """ Public Methods """

    def create(self, 
        name: str = None, 
        directive: draft.Directive = None,
        outline: draft.Outline = None,
        **kwargs) -> Component:
        """[summary]

        Args:
            outline (draft.Outline): [description]
            directive (draft.Directive): [description]
            name (str): [description]

        Returns:
            Component: [description]
            
        """
        if name is None and directive is None and outline is None:
            raise ValueError(
                'create needs either a name, directive, or outline argument')
        else:
            name = self._get_name(
                name = name, 
                directive = directive, 
                outline = outline)
            directive = self._get_directive(
                name = name, 
                directive = directive, 
                outline = outline)
            outline = self._get_outline(
                name = name, 
                directive = directive, 
                outline = outline)
        if directive is None:
            component = self.from_name(name = name, **kwargs)
        else:  
            if name == directive.name:
                parameters = directive.initialization
            else:
                parameters = {}   
            parameters.update({'parameters': directive.implementation[name]}) 
            parameters.update(kwargs)
            lookups = [name]
            try:
                lookups.append(directive.designs[name])   
            except KeyError:
                pass
            component = self.from_name(name = lookups, **parameters)  
            if isinstance(component, Iterable):
                if hasattr(component, 'criteria'):
                    method = self._organize_parallel
                else:
                    method = self._organize_serial
                component = method(
                    component = component,
                    directive = directive,
                    outline = outline)
        return component

    def from_name(self, name: Union[str, Sequence[str]], **kwargs) -> Component:
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
                    item = getattr(self.base, catalog)[key]
                    break
                except KeyError:
                    pass
            if item is not None:
                break
        if item is None:
            raise KeyError(f'No matching item for {str(name)} was found') 
        elif inspect.isclass(item):
            instance = item(name = primary, **kwargs)
        else:
            instance = copy.deepcopy(item)
            for key, value in kwargs.items():
                setattr(instance, key, value)  
        return instance  
    
    def from_outline(self, 
        name: str = None, 
        directive: draft.Directive = None,
        outline: draft.Outline = None,
        **kwargs) -> Component:
        """[summary]

        Args:
            outline (draft.Outline): [description]
            directive (draft.Directive): [description]
            name (str): [description]

        Returns:
            Component: [description]
            
        """
        if name is None and directive is None and outline is None:
            raise ValueError(
                'create needs either a name, directive, or outline argument')
        else:
            name = self._get_name(
                name = name, 
                directive = directive, 
                outline = outline)
            directive = self._get_directive(
                name = name, 
                directive = directive, 
                outline = outline)
            outline = self._get_outline(
                name = name, 
                directive = directive, 
                outline = outline)
        if directive is None:
            component = self.from_name(name = name, **kwargs)
        else:  
            if name == directive.name:
                parameters = directive.initialization
            else:
                parameters = {}   
            parameters.update({'parameters': directive.implementation[name]}) 
            parameters.update(kwargs)
            lookups = [name]
            try:
                lookups.append(directive.designs[name])   
            except KeyError:
                pass
            component = self.from_name(name = lookups, **parameters)  
            if isinstance(component, Iterable):
                if hasattr(component, 'criteria'):
                    method = self._organize_parallel
                else:
                    method = self._organize_serial
                component = method(
                    component = component,
                    directive = directive,
                    outline = outline)
        return component
    
    """ Private Methods """
    
    def _get_name(self, 
        name: str, 
        directive: draft.Directive,
        outline: draft.Outline) -> str:
        """[summary]

        Args:
            outline (draft.Outline): [description]
            name (str): [description]
            directive (draft.Directive): [description]

        Returns:
            str: [description]
            
        """
        if name is not None:
            return name
        elif directive is not None:
            return directive.name
        else:
            return outline.name
        
    def _get_directive(self, 
        name: str, 
        directive: draft.Directive,
        outline: draft.Outline) -> draft.Directive:
        """[summary]

        Args:
            outline (draft.Outline): [description]
            name (str): [description]
            directive (draft.Directive): [description]

        Returns:
            draft.Directive: [description]
            
        """
        if directive is not None:
            return directive
        elif name is not None and outline is not None:
            try:
                return outline[name]
            except KeyError:
                return None
        else:
            try:
                return outline[outline.name]   
            except KeyError:
                return None

    def _get_outline(self, 
        name: str, 
        directive: draft.Directive,
        outline: draft.Outline) -> draft.Outline:
        """[summary]

        Args:
            outline (draft.Outline): [description]
            name (str): [description]
            directive (draft.Directive): [description]

        Returns:
            draft.Outline: [description]
            
        """
        if outline is not None:
            return directive
        elif name is not None and directive is not None:
            return draft.Outline(name = name, contents = {name: directive}) 
        else:
            return None
                                   
    def _organize_serial(self, 
        component: Component,
        directive: core.Directive,
        outline: core.Outline) -> Component:
        """[summary]

        Args:
            component (Component): [description]
            directive (core.Directive): [description]
            outline (core.Outline): [description]

        Returns:
            Component: [description]
            
        """     
        subcomponents = self._serial_order(
            name = component.name, 
            directive = directive)
        collapsed = list(more_itertools.collapse(subcomponents))
        nodes = []
        for node in collapsed:
            subnode = self.create(
                name = [node, directive.designs[node]],
                directive = directive,
                outline = outline)
            nodes.append(subnode)
        component.extend(nodes = nodes)
        return component      

    def _organize_parallel(self, 
        component: Component,
        directive: core.Directive,
        outline: core.Outline) -> Component:
        """[summary]

        Args:
            component (Component): [description]
            directive (core.Directive): [description]
            outline (core.Outline): [description]

        Returns:
            Component: [description]
            
        """ 
        step_names = directive.edges[directive.name]
        possible = [directive.edges[step] for step in step_names]
        nodes = []
        for i, step_options in enumerate(possible):
            permutation = []
            for option in step_options:
                t_keys = [option, directive.designs[option]]
                technique = self.create(
                    name = t_keys,
                    directive = directive,
                    outline = outline,
                    suffix = step_names[i])
                s_keys = [step_names[i], directive.designs[step_names[i]]]    
                step = self.create(
                    name = s_keys,
                    directive = directive,
                    outline = outline,
                    contents = technique)
                step.name = option
                permutation.append(step)
            nodes.append(permutation)
        component.branchify(nodes = nodes)
        return component
    
    def _serial_order(self, name: str, directive: core.Directive) -> List:
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
                subcomponents = self._serial_order(
                    name = item, 
                    directive = directive)
                organized_subcomponents.append(subcomponents)
                if len(organized_subcomponents) == 1:
                    organized.append(organized_subcomponents[0])
                else:
                    organized.append(organized_subcomponents)
        return organized    
    

@dataclasses.dataclass
class Leaf(Component, abc.ABC):
    """Base class for primitive leaf nodes in an amicus Workflow.

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
    parameters: Union[Mapping[Hashable, Any], Parameters] = Parameters()
    iterations: Union[int, str] = 1
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']
    
    """ Public Methods """
    
    def implement(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """Applies 'contents' to 'project'.

        Args:
            project (amicus.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            amicus.Project: with possible changes made.
            
        """
        project = self.contents.execute(project = project, **kwargs)
        return project        


@dataclasses.dataclass
class Step(amicus.types.Proxy, Leaf):
    """Wrapper for a Technique.

    Subclasses of Step can store additional methods and attributes to implement
    all possible technique instances that could be used. This is often useful 
    when creating branching, parallel workflows which test a variety of 
    strategies with similar or identical parameters and/or methods.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Technique): stored Technique instance to be used by the 
            'implement' method. Defaults to None.
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
    contents: Technique = None
    parameters: Union[Mapping[Hashable, Any], Parameters] = Parameters()
    iterations: Union[int, str] = 1
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']
                    
    """ Properties """
    
    @property
    def technique(self) -> Technique:
        return self.contents
    
    @technique.setter
    def technique(self, value: Technique) -> None:
        self.contents = value
        return self
    
    @technique.deleter
    def technique(self) -> None:
        self.contents = None
        return self

                                                  
@dataclasses.dataclass
class Technique(Leaf):
    """Keystone class for primitive objects in an amicus composite object.
    
    The 'contents' and 'parameters' attributes are combined at the last moment
    to allow for runtime alterations.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Callable): stored callable algorithm to be used by the 
            'implement' method. Defaults to None.
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
    contents: Callable = None
    parameters: Union[Mapping[Hashable, Any], Parameters] = Parameters()
    iterations: Union[int, str] = 1
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']
        
    """ Properties """
    
    @property
    def algorithm(self) -> Union[object, str]:
        return self.contents
    
    @algorithm.setter
    def algorithm(self, value: Union[object, str]) -> None:
        self.contents = value
        return self
    
    @algorithm.deleter
    def algorithm(self) -> None:
        self.contents = None
        return self
    
         
@dataclasses.dataclass
class Worker(amicus.structures.Graph, Component):
    """Keystone class for parts of an amicus workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Dict[Component, List[str]]): an adjacency list where the 
            keys are Component instances and the values are the names of nodes 
            which the key is connected to. Defaults to an empty dict.
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
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.
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
    contents: Dict[Component, List[str]] = dataclasses.field(
        default_factory = dict)
    parameters: Union[Mapping[Hashable, Any], Parameters] = Parameters()
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']

    """ Private Methods """
    
    def _implement_in_serial(self, 
        project: amicus.Project, 
        **kwargs) -> amicus.Project:
        """Applies stored nodes to 'project' in order.

        Args:
            project (Project): amicus project to apply changes to and/or
                gather needed data from.
                
        Returns:
            Project: with possible alterations made.       
        
        """
        for node in self.paths[0]:
            project = node.execute(project = project, **kwargs)
        return project
    
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
class Process(Worker):
    """A Worker with a serial Workflow.
        
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
    contents: Dict[Component, List[str]] = dataclasses.field(
        default_factory = dict)
    parameters: Union[Mapping[Hashable, Any], Parameters] = Parameters()
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['outline', 'name']
  
    """ Public Methods """  

    def implement(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """Applies 'contents' to 'project'.
        
        Args:
            project (amicus.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            amicus.Project: with possible changes made.
            
        """
        return self._implement_in_serial(project = project, **kwargs)    
    

@dataclasses.dataclass
class Nexus(Worker, abc.ABC):
    """Base class for branching and parallel Workers.
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Dict[Component, List[str]]): an adjacency list where the 
            keys are Component instances and the values are string names of 
            Components which the key is connected to. Defaults to an empty dict.
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
    contents: Dict[Component, List[str]] = dataclasses.field(
        default_factory = dict)
    parameters: Union[Mapping[Hashable, Any], Parameters] = Parameters()
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']
    
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
class Contest(Nexus):
    """Resolves a parallel workflow by selecting the best option.

    It resolves a parallel workflow based upon criteria in 'contents'
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Dict[Component, List[str]]): an adjacency list where the 
            keys are Component instances and the values are string names of 
            Components which the key is connected to. Defaults to an empty dict.
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
    contents: Dict[Component, List[str]] = dataclasses.field(
        default_factory = dict)
    parameters: Union[Mapping[Hashable, Any], Parameters] = Parameters()
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']

    
@dataclasses.dataclass
class Study(Nexus):
    """Allows parallel workflow to continue

    A Study might be wholly passive or implement some reporting or alterations
    to all parallel workflows.
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Dict[Component, List[str]]): an adjacency list where the 
            keys are Component instances and the values are string names of 
            Components which the key is connected to. Defaults to an empty dict.
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
    contents: Dict[Component, List[str]] = dataclasses.field(
        default_factory = dict)
    parameters: Union[Mapping[Hashable, Any], Parameters] = Parameters()
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']
 
    
@dataclasses.dataclass
class Survey(Nexus):
    """Resolves a parallel workflow by averaging.

    It resolves a parallel workflow based upon the averaging criteria in 
    'contents'
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Dict[Component, List[str]]): an adjacency list where the 
            keys are Component instances and the values are string names of 
            Components which the key is connected to. Defaults to an empty dict.
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
    contents: Dict[Component, List[str]] = dataclasses.field(
        default_factory = dict)
    parameters: Union[Mapping[Hashable, Any], Parameters] = Parameters()
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    suffix: ClassVar[str] = None
    needs: ClassVar[Union[Sequence[str], str]] = ['name']
    