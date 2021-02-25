"""
analyst.steps
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0) 

Contents:

"""
from __future__ import annotations
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, Optional, Sequence, Tuple, Type, Union)

import amicus
from amicus import project
from amicus import simplify


@dataclasses.dataclass
class Encode(amicus.project.Step):
    """Wrapper for a Technique.

    An instance will try to return attributes from 'contents' if the attribute 
    is not found in the Step instance. 

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an 
            amicus instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
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
    name: str = 'encode'
    contents: Encoder = None
    container: str = 'analyst'
    parameters: Union[Mapping[str, Any], project.Parameters] = (
        project.Parameters())
    

@dataclasses.dataclass
class Encoder(amicus.quirks.Loader, amicus.project.Technique):
    """Wrapper for a Technique.

    An instance will try to return attributes from 'contents' if the attribute 
    is not found in the Step instance. 

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an 
            amicus instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
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
    name: str = 'encoder'
    contents: Union[Callable, Type, object, str] = None
    container: str = 'encode'
    parameters: Union[Mapping[str, Any], project.Parameters] = (
        project.Parameters())
    module: str = None
    
    
@dataclasses.dataclass
class CategoryEncoder(Encoder):
    """Wrapper for an encoder from category-encoders.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an 
            amicus instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
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
            False.
            
    """
    name: str = None
    contents: Union[Callable, Type, object, str] = None
    iterations: Union[int, str] = 1
    parameters: Union[Mapping[str, Any], project.Parameters] = project.Parameters()
    module: str = 'category_encoders'
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
        data = project.data
        data.x_train = self.contents.fit[data.x_train, data.y_train]
        data.x_train = self.contents.transform(data.x_train)
        if data.x_test is not None:
            data.x_test = self.contents.transform(data.x_test)
        if data.x_validate is not None:
            data.x_validate = self.contents.transform(data.x_validate)
        project.data = data
        return project
                      

category_encoders = {
    'backward': 'BackwardDifferenceEncoder',
    'base_n': 'BaseNEncoder',
    'binary': 'BinaryEncoder',
    'cat_boost': 'CatBoostEncoder',
    'count': 'CountEncoder',
    'glmm': 'GLMMEncoder',
    'hashing': 'HashingEncoder',
    'helmert': 'HelmertEncoder',
    'james_stein': 'JamesSteinEncoder',
    'leave_one_out': 'LeaveOneOutEncoder',
    'm_estimate': 'MEstimateEncoder',
    'one_hot': 'OneHotEncoder',
    'ordinal': 'OrdinalEncoder',
    'sum': 'SumEncoder',
    'polynomial': 'PolynomialEncoder',
    'target': 'TargetEncoder',
    'weight_of_evidence': 'WOEEncoder'}


def instancify() -> None:
    for encoder, algorithm in category_encoders:
        kwargs = {
            'name': encoder, 
            'contents': algorithm,
            'parameters': amicus.project.Parameters(
                name = encoder,
                implementation = {'cols': 'data.categoricals'})}
        CategoryEncoder(**kwargs)
    return
