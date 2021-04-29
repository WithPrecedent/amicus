"""
simplify.analyst.encode
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0) 

Contents:

"""
from __future__ import annotations
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)

import amicus
from amicus import project


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
    container: str = 'encode'
    iterations: Union[int, str] = 1
    parameters: Union[Mapping[str, Any], project.Parameters] = (
        project.Parameters())   
    module: str = None

    """ Public Methods """
    
    def implement(self, project: amicus.Project) -> amicus.Project:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            amicus.Project: [description]
            
        """
        self.contents = self.contents(**self.parameters)
        data = project.data
        data.x_train = self.contents.fit(data.x_train, data.y_train)
        data.x_train = self.contents.transform(data.x_train)
        if data.x_test is not None:
            data.x_test = self.contents.transform(data.x_test)
        if data.x_validate is not None:
            data.x_validate = self.contents.transform(data.x_validate)
        project.data = data
        return project

                    
catalog = amicus.base.Catalog(
    contents = {  
        'backward_encode': Encoder(
            name = 'backward encoder',
            contents = 'BackwardDifferenceEncoder',
            parameters = project.Parameters(
                name = 'backward_encode',
                implementation = {'cols': 'data.categoricals'}),
            module = 'category_encoders'),
        'base_n_encode': Encoder(
            name = 'base n encoder',
            contents = 'BaseNEncoder',
            parameters = project.Parameters(
                name = 'base_n_encode',
                implementation = {'cols': 'data.categoricals'}),
            module = 'category_encoders'),
        'binary_encode': Encoder(
            name = 'binary encoder',
            contents = 'BinaryEncoder',
            parameters = project.Parameters(
                name = 'binary_encode',
                implementation = {'cols': 'data.categoricals'}),
            module = 'category_encoders'),
        'cat_boost_encode': Encoder(
            name = 'category boost encoder',
            contents = 'CatBoostEncoder',
            parameters = project.Parameters(
                name = 'cat_boost_encode',
                implementation = {'cols': 'data.categoricals'}),
            module = 'category_encoders'),
        'count_encode': Encoder(
            name = 'count encoder',
            contents = 'CountEncoder',
            parameters = project.Parameters(
                name = 'count_encode',
                implementation = {'cols': 'data.categoricals'}),
            module = 'category_encoders'),
        'glmm_encode': Encoder(
            name = 'glmm encoder',
            contents = 'GLMMEncoder',
            parameters = project.Parameters(
                name = 'glmm_encode',
                implementation = {'cols': 'data.categoricals'}),
            module = 'category_encoders'),
        'hashing_encode': Encoder(
            name = 'hashing encoder',
            contents = 'HashingEncoder',
            parameters = project.Parameters(
                name = 'hashing_encode',
                implementation = {'cols': 'data.categoricals'}),
            module = 'category_encoders'),
        'helmert_encode': Encoder(
            name = 'helmert encoder',
            contents = 'HelmertEncoder',
            parameters = project.Parameters(
                name = 'helmert_encode',
                implementation = {'cols': 'data.categoricals'}),
            module = 'category_encoders'),
        'james_stein_encode': Encoder(
            name = 'james stein encoder',
            contents = 'JamesSteinEncoder',
            parameters = project.Parameters(
                name = 'james_stein_encode',
                implementation = {'cols': 'data.categoricals'}),
            module = 'category_encoders'),
        'leave_one_out': Encoder(
            name = 'leave one encoder',
            contents = 'LeaveOneOutEncoder',
            parameters = project.Parameters(
                name = 'leave_one_out_encode',
                implementation = {'cols': 'data.categoricals'}),
            module = 'category_encoders'),
        'm_estimate_encode': Encoder(
            name = 'm estimate encoder',
            contents = 'MEstimateEncoder',
            parameters = project.Parameters(
                name = 'm_estimate_encode',
                implementation = {'cols': 'data.categoricals'}),
            module = 'category_encoders'),
        'one_hot_encode': Encoder(
            name = 'backward encoder',
            contents = 'OneHotEncoder',
            parameters = project.Parameters(
                name = 'one_hot_encode',
                implementation = {'cols': 'data.categoricals'}),
            module = 'category_encoders'),
        'ordinal_encode': Encoder(
            name = 'ordinal encoder',
            contents = 'OrdinalEncoder',
            parameters = project.Parameters(
                name = 'ordinal_encode',
                implementation = {'cols': 'data.categoricals'}),
            module = 'category_encoders'),
        'sum_encode': Encoder(
            name = 'sum encoder',
            contents = 'SumEncoder',
            parameters = project.Parameters(
                name = 'sum_encode',
                implementation = {'cols': 'data.categoricals'}),
            module = 'category_encoders'),
        'polynomial_encode': Encoder(
            name = 'polynomial encoder',
            contents = 'PolynomialEncoder',
            parameters = project.Parameters(
                name = 'polynomial_encode',
                implementation = {'cols': 'data.categoricals'}),
            module = 'category_encoders'),
        'target_encode': Encoder(
            name = 'target encoder',
            contents = 'TargetEncoder',
            parameters = project.Parameters(
                name = 'target_encode',
                implementation = {'cols': 'data.categoricals'}),
            module = 'category_encoders'),
        'weight_of_evidence_encode': Encoder(
            name = 'weight of evidence encoder',
            contents = 'WOEEncoder',
            parameters = project.Parameters(
                name = 'weight_of_evidence_encode',
                implementation = {'cols': 'data.categoricals'}),
            module = 'category_encoders')})
