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
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)

import more_itertools
import amicus

from . import base
from . import components
from . import stages


@dataclasses.dataclass
class SklearnModel(amicus.base.Quirk):
    """Wrapper for a scikit-learn model (an algorithm that doesn't transform).

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
    
    """ Public Methods """
    
    def implement(self, project: amicus.Project) -> amicus.Project:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            amicus.Project: [description]
            
        """
        try:
            self.parameters = self.parameters.finalize(project = project)
        except AttributeError:
            pass
        self.contents = self.contents(**self.parameters)
        self.contents.fit[project.data.x_train]
        return project


@dataclasses.dataclass
class SklearnSplitter(amicus.base.Quirk):
    """Wrapper for a scikit-learn data splitter.

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

    """ Public Methods """
    
    def implement(self, project: amicus.Project) -> amicus.Project:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            amicus.Project: [description]
            
        """
        try:
            self.parameters = self.parameters.finalize(project = project)
        except AttributeError:
            pass
        self.contents = self.contents(**self.parameters)
        project.data.splits = tuple(self.contents.split(project.data.x))
        project.data.split()
        return project
    
    
@dataclasses.dataclass
class SklearnTransformer(amicus.base.Quirk):
    """Wrapper for a scikit-learn transformer.

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
    
    """ Public Methods """

    def adjust_parameters(self, project: amicus.Project) -> None:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            [type]: [description]
            
        """
        return self
    
    def implement(self, project: amicus.Project, **kwargs) -> amicus.Project:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            amicus.Project: [description]
            
        """
        try:
            self.contents.parameters = self.contents.parameters.finalize(
                project = project)
        except AttributeError:
            pass
        self.adjust_parameters(project = project)    
        self.contents = self.contents(**self.parameters)
        data = project.data
        data.x_train = self.contents.fit[data.x_train]
        data.x_train = self.contents.transform(data.x_train)
        if data.x_test is not None:
            data.x_test = self.contents.transform(data.x_test)
        if data.x_validate is not None:
            data.x_validate = self.contents.transform(data.x_validate)
        project.data = data
        return project
               