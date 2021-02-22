"""
components:
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
import dataclasses
import multiprocessing
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, Optional, Sequence, Tuple, Type, Union)

import more_itertools

import amicus
from . import core


@dataclasses.dataclass
class Step(core.Component):
    """Wrapper for a Technique.

    Subclasses of Step can store additional methods and attributes to implement
    all possible technique instances that could be used. This is often useful 
    when creating branching, parallel workflows which test a variety of 
    strategies with similar or identical parameters and/or methods.

    A Step instance will try to return attributes from Technique if the 
    attribute is not found in the Step instance. 

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Technique): stored Technique instance used by the 'implement' 
            method.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            True.
                                                
    """
    name: str = None
    contents: Technique = None
    iterations: Union[int, str] = 1
    parameters: Union[Mapping[str, Any], core.Parameters] = core.Parameters()
    parallel: ClassVar[bool] = True
                    
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
class Technique(core.Component):
    """Keystone class for primitive objects in an amicus composite object.
    
    The 'contents' and 'parameters' attributes are combined at the last moment
    to allow for runtime alterations.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Any): stored item for use by a Component subclass instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            False.
                                               
    """
    name: str = None
    contents: Callable = None
    iterations: Union[int, str] = 1
    parameters: Union[Mapping[str, Any], core.Parameters] = core.Parameters()
    parallel: ClassVar[bool] = False
    
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
class Worker(core.Component):
    """Keystone class for parts of an amicus Workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Any): stored item(s) for use by a Component subclass instance.
        workflow (amicus.Structure): a workflow of a project subpart derived 
            from 'outline'. Defaults to None.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            False.
                            
    """
    name: str = None
    contents: Any = None
    workflow: amicus.Structure = None
    iterations: Union[int, str] = 1
    parameters: Union[Mapping[str, Any], core.Parameters] = core.Parameters()
    parallel: ClassVar[bool] = False
    
    """ Class Methods """

    @classmethod
    def from_outline(cls, name: str,
                     outline: amicus.project.Outline, **kwargs) -> Worker:
        """[summary]

        Args:
            name (str): [description]
            outline (amicus.project.Outline): [description]

        Returns:
            Worker: [description]
            
        """        
        worker = super().from_outline(name = name, outline = outline, **kwargs)
        if hasattr(worker, 'workflow'):
            worker.workflow = cls.keystones.stage.library.select(
                names = 'workflow')()
            if worker.parallel:
                method = cls._create_parallel
            else:
                method = cls._create_serial
            worker = method(worker = worker, outline = outline)
        return worker

    @classmethod                
    def _create_parallel(cls, worker: Worker,
                         outline: amicus.project.Outline) -> Worker:
        """[summary]

        Args:
            worker (Worker): [description]
            outline (amicus.project.Outline): [description]

        Returns:
        
        """
        name = worker.name
        step_names = outline.components[name]
        possible = [outline.components[s] for s in step_names]
        worker.workflow.branchify(nodes = possible)
        for i, step_options in enumerate(possible):
            for option in step_options:
                technique = cls.from_outline(name = option, outline = outline)
                wrapper = cls.from_outline(name = step_names[i],
                                           outline = outline,
                                           contents = technique)
                worker.workflow.components[option] = wrapper
        return worker 
    
    @classmethod
    def _create_serial(cls, worker: Worker,
                       outline: amicus.project.Outline) -> Worker:                     
        """[summary]

        Args:
            worker (Worker): [description]
            outline (amicus.project.Outline): [description]

        Returns:
        
        """

        name = worker.name
        components = cls._depth_first(name = name, outline = outline)
        collapsed = list(more_itertools.collapse(components))
        worker.workflow.extend(nodes = collapsed)
        for item in collapsed:
            component = cls.from_outline(name = item, outline = outline)
            worker.workflow.components[item] = component
        return worker

    @classmethod
    def _depth_first(cls, name: str, outline: core.Stage) -> List:
        """

        Args:
            name (str):
            details (Blueprint): [description]

        Returns:
            List[List[str]]: [description]
            
        """
        organized = []
        components = outline.components[name]
        for item in components:
            organized.append(item)
            if item in outline.components:
                organized_subcomponents = []
                subcomponents = cls._depth_first(name = item, outline = outline)
                organized_subcomponents.append(subcomponents)
                if len(organized_subcomponents) == 1:
                    organized.append(organized_subcomponents[0])
                else:
                    organized.append(organized_subcomponents)
        return organized
     

@dataclasses.dataclass
class Pipeline(Worker):
    """
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Callable): stored item used by the 'implement' method.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            True.    
                        
    """
    name: str = None
    contents: Any = None
    workflow: amicus.Structure = None
    iterations: Union[int, str] = 1
    parameters: Union[Mapping[str, Any], core.Parameters] = core.Parameters()
    parallel: ClassVar[bool] = False
    

@dataclasses.dataclass
class ParallelWorker(Worker, abc.ABC):
    """Resolves a parallel workflow by selecting the best option.

    It resolves a parallel workflow based upon criteria in 'contents'
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Callable): stored item used by the 'implement' method.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            True.    
                        
    """
    name: str = None
    contents: Any = None
    workflow: amicus.Structure = None
    iterations: Union[int, str] = 1
    parameters: Union[Mapping[str, Any], core.Parameters] = core.Parameters()
    criteria: Callable = None
    parallel: ClassVar[bool] = True


@dataclasses.dataclass
class Contest(ParallelWorker):
    """Resolves a parallel workflow by selecting the best option.

    It resolves a parallel workflow based upon criteria in 'contents'
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Callable): stored item used by the 'implement' method.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            True.    
                        
    """
    name: str = None
    contents: Any = None
    workflow: amicus.Structure = None
    iterations: Union[int, str] = 1
    parameters: Union[Mapping[str, Any], core.Parameters] = core.Parameters()
    criteria: Callable = None
    parallel: ClassVar[bool] = True

    """ Public Methods """
    
    def resolve(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            amicus.Project: [description]
            
        """                
        return project 
 
    
@dataclasses.dataclass
class Study(ParallelWorker):
    """Allows parallel workflow to continue

    A Study might be wholly passive or implement some reporting or alterations
    to all parallel workflows.
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Callable): stored item used by the 'implement' method.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            True.   
                         
    """
    name: str = None
    contents: Any = None
    workflow: amicus.Structure = None
    iterations: Union[int, str] = 1
    parameters: Union[Mapping[str, Any], core.Parameters] = core.Parameters()
    criteria: Callable = None
    parallel: ClassVar[bool] = True

    """ Public Methods """
    
    def resolve(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            amicus.Project: [description]
            
        """                
        return project   

    
@dataclasses.dataclass
class Survey(ParallelWorker):
    """Resolves a parallel workflow by averaging.

    It resolves a parallel workflow based upon the averaging criteria in 
    'contents'
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        contents (Callable): stored item used by the 'implement' method.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            True.   
                          
    """
    name: str = None
    contents: Any = None
    workflow: amicus.Structure = None
    iterations: Union[int, str] = 1
    parameters: Union[Mapping[str, Any], core.Parameters] = core.Parameters()
    parallel: ClassVar[bool] = True

    """ Public Methods """
    
    def resolve(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            amicus.Project: [description]
            
        """                
        return project 
    