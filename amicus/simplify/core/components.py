"""
components: core components of a data science workflow
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    
    
"""
from __future__ import annotations
import abc
import dataclasses
import multiprocessing
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, Optional, Sequence, Tuple, Type, Union)

import more_itertools
import amicus

from . import base
from . import stages


@dataclasses.dataclass
class SimpleProcess(base.Component, abc.ABC):
    """Base class for parts of an amicus Workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs options from a Configuration instance, 'name' should match 
            the appropriate section name in a Configuration instance. Defaults to 
            None. 
        contents (Union[Callable, Type, object, str]): stored item(s) for use by 
            a Component subclass instance. If it is Type or str, an instance 
            will be created. If it is a str, that instance will be drawn from 
            the 'instances' or 'subclasses' attributes.
        parameters (Union[Mapping[str, Any], base.Parameters]): parameters, in 
            the form of an ordinary dict or a Parameters instance, to be 
            attached to 'contents'  when the 'implement' method is called.
            Defaults to an empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be part of a parallel workflow structure. Defaults to 
            False.

    Attributes:
        keystones (ClassVar[Keystones]): library that stores amicus base classes 
            and allows runtime access and instancing of those stored subclasses.
        subclasses (ClassVar[amicus.types.Catalog]): catalog that stores 
            concrete subclasses and allows runtime access and instancing of 
            those stored subclasses. 
        instances (ClassVar[amicus.types.Catalog]): catalog that stores
            subclass instances and allows runtime access of those stored 
            subclass instances.
                
    """
    name: str = None
    contents: Union[Callable, Type, object, str] = None
    parameters: Union[Mapping[str, Any], base.Parameters] = base.Parameters()
    iterations: Union[int, str] = 1
    parallel: ClassVar[bool] = False
    
    """ Public Methods """
    
    def execute(self, project: amicus.Project, 
                **kwargs) -> amicus.Project:
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

    def implement(self, project: amicus.Project, 
                  **kwargs) -> amicus.Project:
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
            project = self.contents.execute(project = project, **parameters)
        return project


@dataclasses.dataclass
class Step(SimpleProcess):
    """Wrapper for a Technique.

    Subclasses of Step can store additional methods and attributes to implement
    all possible technique instances that could be used. This is often useful 
    when using parallel Worklow instances which test a variety of strategies 
    with similar or identical parameters and/or methods.

    A Step instance will try to return attributes from Technique if the
    attribute is not found in the Step instance. 

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs options from a Configuration instance, 'name' should match 
            the appropriate section name in a Configuration instance. Defaults to 
            None. 
        contents (Union[Callable, Type, object, str]): stored item(s) for use by 
            a Component subclass instance. If it is Type or str, an instance 
            will be created. If it is a str, that instance will be drawn from 
            the 'instances' or 'subclasses' attributes.
        parameters (Union[Mapping[str, Any], base.Parameters]): parameters, in 
            the form of an ordinary dict or a Parameters instance, to be 
            attached to 'contents'  when the 'implement' method is called.
            Defaults to an empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be part of a parallel workflow structure. Because Steps
            are generally part of a parallel-structured workflow, the attribute
            defaults to True.
                                                
    """
    name: str = None
    contents: Union[Callable, Type, object, str] = None
    parameters: Union[Mapping[str, Any], base.Parameters] = base.Parameters()
    iterations: Union[int, str] = 1
    parallel: ClassVar[bool] = True

    
@dataclasses.dataclass
class Technique(amicus.quirks.Loader, SimpleProcess):
    """Primitive object for executing algorithms in an amicus workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs options from a Configuration instance, 'name' should match 
            the appropriate section name in a Configuration instance. Defaults to 
            None. 
        contents (Union[Callable, Type, object, str]): stored item(s) for use by 
            a Component subclass instance. If it is Type or str, an instance 
            will be created. If it is a str, that instance will be found in 
            'module'. Defaults to None.
        parameters (Union[Mapping[str, Any], base.Parameters]): parameters, in 
            the form of an ordinary dict or a Parameters instance, to be 
            attached to 'contents'  when the 'implement' method is called.
            Defaults to an empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        module (str): name of module where 'contents' is located if 'contents'
            is a string. It can either be an amicus or external module, as
            long as it is available to the python environment. Defaults to None.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be part of a parallel workflow structure. Defaults to 
            False.
                                                
    """  
    name: str = None
    contents: Union[Callable, Type, object, str] = None
    parameters: Union[Mapping[str, Any], base.Parameters] = base.Parameters()
    iterations: Union[int, str] = 1
    module: str = None
    parallel: ClassVar[bool] = False   

              
@dataclasses.dataclass
class Worker(SimpleProcess):
    """An iterable in an amicus workflow that maintains its own workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs options from a Configuration instance, 'name' should match 
            the appropriate section name in a Configuration instance. Defaults to 
            None. 
        contents (Union[Callable, Type, object, str]): stored item(s) for use by 
            a Component subclass instance. If it is Type or str, an instance 
            will be created. If it is a str, that instance will be drawn from 
            the 'instances' or 'subclasses' attributes.
        parameters (Union[Mapping[str, Any], base.Parameters]): parameters, in 
            the form of an ordinary dict or a Parameters instance, to be 
            attached to 'contents'  when the 'implement' method is called.
            Defaults to an empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        workflow (stages.Workflow): a workflow of other amicus Components.
            Defaults to an empty Workflow.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be part of a parallel workflow structure. Because Steps
            are generally part of a parallel-structured workflow, the attribute
            defaults to True.
                                                
    """
    name: str = None
    contents: Union[Callable, Type, object, str] = None
    parameters: Union[Mapping[str, Any], base.Parameters] = base.Parameters()
    iterations: Union[int, str] = 1
    workflow: stages.Workflow = stages.Workflow()
    parallel: ClassVar[bool] = True
    
    """ Public Class Methods """

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
                  
    """ Private Class Methods """ 

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
    def _depth_first(cls, name: str, outline: base.Stage) -> List:
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
            instance needs options from a Configuration instance, 'name' should match 
            the appropriate section name in a Configuration instance. Defaults to 
            None. 
        contents (Union[Callable, Type, object, str]): stored item(s) for use by 
            a Component subclass instance. If it is Type or str, an instance 
            will be created. If it is a str, that instance will be drawn from 
            the 'instances' or 'subclasses' attributes.
        parameters (Union[Mapping[str, Any], base.Parameters]): parameters, in 
            the form of an ordinary dict or a Parameters instance, to be 
            attached to 'contents'  when the 'implement' method is called.
            Defaults to an empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        workflow (stages.Workflow): a workflow of other amicus Components.
            Defaults to an empty Workflow.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be part of a parallel workflow structure. Because Steps
            are generally part of a parallel-structured workflow, the attribute
            defaults to True.
                                                
    """
    name: str = None
    contents: Union[Callable, Type, object, str] = None
    parameters: Union[Mapping[str, Any], base.Parameters] = base.Parameters()
    iterations: Union[int, str] = 1
    workflow: stages.Workflow = stages.Workflow()
    parallel: ClassVar[bool] = True
    

@dataclasses.dataclass
class ParallelWorker(Worker, abc.ABC):
    """Resolves a parallel workflow by selecting the best option.

    It resolves a parallel workflow based upon the criteria in 'contents'.
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs options from a Configuration instance, 'name' should match 
            the appropriate section name in a Configuration instance. Defaults to 
            None. 
        contents (Union[Callable, Type, object, str]): stored item(s) for use by 
            a Component subclass instance. If it is Type or str, an instance 
            will be created. If it is a str, that instance will be drawn from 
            the 'instances' or 'subclasses' attributes.
        parameters (Union[Mapping[str, Any], base.Parameters]): parameters, in 
            the form of an ordinary dict or a Parameters instance, to be 
            attached to 'contents'  when the 'implement' method is called.
            Defaults to an empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        workflow (stages.Workflow): a workflow of other amicus Components.
            Defaults to an empty Workflow.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be part of a parallel workflow structure. Because Steps
            are generally part of a parallel-structured workflow, the attribute
            defaults to True.
                                                
    """
    name: str = None
    contents: Union[Callable, Type, object, str] = None
    parameters: Union[Mapping[str, Any], base.Parameters] = base.Parameters()
    iterations: Union[int, str] = 1
    workflow: stages.Workflow = stages.Workflow()
    parallel: ClassVar[bool] = True

    """ Public Methods """
    
    def implement(self, data: Any, **kwargs) -> Any:
        """[summary]

        Args:
            data (Any): [description]

        Returns:
            Any: [description]
            
        """        
        if hasattr(data, 'parallelize') and data.parallelize:
            method = self._implement_in_parallel
        else:
            method = self._implement_in_serial
        return method(data = data, **kwargs)

    """ Private Methods """
   
    def _implement_in_parallel(self, data: Any, **kwargs) -> Any:
        """Applies 'implementation' to 'project' using multiple cores.

        Args:
            project (Project): amicus project to apply changes to and/or
                gather needed data from.
                
        Returns:
            Project: with possible alterations made.       
        
        """
        multiprocessing.set_start_method('spawn')
        with multiprocessing.Pool() as pool:
            data = pool.starmap(self._implement_in_serial, data, **kwargs)
        return data 

    def _implement_in_serial(self, data: Any, **kwargs) -> Any:
        """Applies 'implementation' to 'project' using multiple cores.

        Args:
            project (Project): amicus project to apply changes to and/or
                gather needed data from.
                
        Returns:
            Project: with possible alterations made.       
        
        """
        for path in self.workflow.permutations:
            data = self._implement_path(data = data, path = path, **kwargs)
        return data
    
    def _implement_path(self, data: Any, path: List[str], **kwargs) -> Any:  
        for node in path:
            component = self.workflow.components[node]
            data = component.execute(data = data, **kwargs)
        return data
    
       
@dataclasses.dataclass
class Contest(ParallelWorker):
    """Resolves a parallel workflow by selecting the best option.

    It resolves a parallel workflow based upon criteria in 'contents'
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs options from a Configuration instance, 'name' should match 
            the appropriate section name in a Configuration instance. Defaults to 
            None. 
        contents (Union[Callable, Type, object, str]): stored item(s) for use by 
            a Component subclass instance. If it is Type or str, an instance 
            will be created. If it is a str, that instance will be drawn from 
            the 'instances' or 'subclasses' attributes.
        parameters (Union[Mapping[str, Any], base.Parameters]): parameters, in 
            the form of an ordinary dict or a Parameters instance, to be 
            attached to 'contents'  when the 'implement' method is called.
            Defaults to an empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        workflow (stages.Workflow): a workflow of other amicus Components.
            Defaults to an empty Workflow.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be part of a parallel workflow structure. Because Steps
            are generally part of a parallel-structured workflow, the attribute
            defaults to True.
                                                
    """
    name: str = None
    contents: Union[Callable, Type, object, str] = None
    parameters: Union[Mapping[str, Any], base.Parameters] = base.Parameters()
    iterations: Union[int, str] = 1
    workflow: stages.Workflow = stages.Workflow()
    parallel: ClassVar[bool] = True

    """ Public Methods """
    
    def implement(self, data: Any, **kwargs) -> Any:
        """[summary]

        Args:
            data (Any): [description]

        Returns:
            Any: [description]
        """
                
        return data   
 
    
@dataclasses.dataclass
class Study(ParallelWorker):
    """Allows parallel workflow to continue

    A Study might be wholly passive or implement some reporting or alterations
    to all parallel workflows.
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs options from a Configuration instance, 'name' should match 
            the appropriate section name in a Configuration instance. Defaults to 
            None. 
        contents (Union[Callable, Type, object, str]): stored item(s) for use by 
            a Component subclass instance. If it is Type or str, an instance 
            will be created. If it is a str, that instance will be drawn from 
            the 'instances' or 'subclasses' attributes.
        parameters (Union[Mapping[str, Any], base.Parameters]): parameters, in 
            the form of an ordinary dict or a Parameters instance, to be 
            attached to 'contents'  when the 'implement' method is called.
            Defaults to an empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        workflow (stages.Workflow): a workflow of other amicus Components.
            Defaults to an empty Workflow.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be part of a parallel workflow structure. Because Steps
            are generally part of a parallel-structured workflow, the attribute
            defaults to True.
                                                
    """
    name: str = None
    contents: Union[Callable, Type, object, str] = None
    parameters: Union[Mapping[str, Any], base.Parameters] = base.Parameters()
    iterations: Union[int, str] = 1
    workflow: stages.Workflow = stages.Workflow()
    parallel: ClassVar[bool] = True

    """ Public Methods """
    
    def implement(self, data: Any, **kwargs) -> Any:
        """[summary]

        Args:
            data (Any): [description]

        Returns:
            Any: [description]
        """           
        return data    

    
@dataclasses.dataclass
class Survey(ParallelWorker):
    """Resolves a parallel workflow by averaging.

    It resolves a parallel workflow based upon the averaging criteria in 
    'contents'
        
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs options from a Configuration instance, 'name' should match 
            the appropriate section name in a Configuration instance. Defaults to 
            None. 
        contents (Union[Callable, Type, object, str]): stored item(s) for use by 
            a Component subclass instance. If it is Type or str, an instance 
            will be created. If it is a str, that instance will be drawn from 
            the 'instances' or 'subclasses' attributes.
        parameters (Union[Mapping[str, Any], base.Parameters]): parameters, in 
            the form of an ordinary dict or a Parameters instance, to be 
            attached to 'contents'  when the 'implement' method is called.
            Defaults to an empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        workflow (stages.Workflow): a workflow of other amicus Components.
            Defaults to an empty Workflow.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be part of a parallel workflow structure. Because Steps
            are generally part of a parallel-structured workflow, the attribute
            defaults to True.
                                                
    """
    name: str = None
    contents: Union[Callable, Type, object, str] = None
    parameters: Union[Mapping[str, Any], base.Parameters] = base.Parameters()
    iterations: Union[int, str] = 1
    workflow: stages.Workflow = stages.Workflow()
    parallel: ClassVar[bool] = True

    """ Public Methods """
    
    def implement(self, data: Any, **kwargs) -> Any:
        """[summary]

        Args:
            data (Any): [description]

        Returns:
            Any: [description]
        """           
        return data   
    