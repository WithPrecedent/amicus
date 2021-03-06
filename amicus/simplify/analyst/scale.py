"""
simplify.analyst.scale
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
class Scale(amicus.project.Step):
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
    name: str = 'scale'
    contents: Scaler = None
    container: str = 'analyst'
    parameters: Union[Mapping[str, Any], project.Parameters] = (
        project.Parameters())   
    
    
@dataclasses.dataclass
class Scaler(amicus.quirks.Loader, amicus.project.Technique):
    """Wrapper for an scaler from category-scalers.

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
    container: str = 'scale'
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
        data.x_train = self.contents.fit(data.x_train)
        data.x_train = self.contents.transform(data.x_train)
        if data.x_test is not None:
            data.x_test = self.contents.transform(data.x_test)
        if data.x_validate is not None:
            data.x_validate = self.contents.transform(data.x_validate)
        project.data = data
        return project


catalog = amicus.base.Catalog(
    contents = {  
        'max_absolute_scale': Scaler(
            name = 'maximum absolute scaler',
            contents = 'MaxAbsScaler',
            parameters = project.Parameters(
                name = 'max_absolute_scale',
                default = {'copy': False}),
            module = 'sklearn.preprocessing'),
        'min_max_scale': Scaler(
            name = 'minimum maximum scaler',
            contents = 'MinMaxScaler',
            parameters = project.Parameters(
                name = 'min_max_scale',
                default = {'copy': False}),
            module = 'sklearn.preprocessing'),
        'normalize_scale': Scaler(
            name = 'normalizer scaler',
            contents = 'Normalizer',
            parameters = project.Parameters(
                name = 'normalize_scale',
                default = {'copy': False}),
            module = 'sklearn.preprocessing'),      
        'quantile_scale': Scaler(
            name = 'quantile scaler',
            contents = 'QuantileTransformer',
            parameters = project.Parameters(
                name = 'quantile_scale',
                default = {'copy': False}),
            module = 'sklearn.preprocessing'),   
        'robust_scale': Scaler(
            name = 'robust scaler',
            contents = 'RobustScaler',
            parameters = project.Parameters(
                name = 'robust_scale',
                default = {'copy': False}),
            module = 'sklearn.preprocessing'),   
        'standard_scale': Scaler(
            name = 'standard scaler',
            contents = 'StandardScaler',
            parameters = project.Parameters(
                name = 'min_max_scale',
                default = {'copy': False}),
            module = 'sklearn.preprocessing')})


# @dataclasses.dataclass
# class GaussScale(amicus.components.SklearnTransformer):
#     """Transforms data columns to more gaussian distribution.

#     The particular method applied is chosen between 'box-cox' and 'yeo-johnson'
#     based on whether the particular data column has values below zero.

#     Args:
#         step(str): name of step used.
#         parameters(dict): dictionary of parameters to pass to selected
#             algorithm.
#         name(str): name of class for matching settings in the Idea instance
#             and for labeling the columns in files exported by Critic.
#         auto_draft(bool): whether 'finalize' method should be called when
#             the class is instanced. This should generally be set to True.
#     """
#     name: str = 'box-cox & yeo-johnson'
#     contents: str = None
#     iterations: Union[int, str] = 1
#     parameters: Union[Mapping[str, Any]. 
#                       base.Parameters] = base.Parameters(
#                           name = 'gauss_scale',
#                           default = {'rescaler': 'standard'})
#     module: str = None
#     parallel: ClassVar[bool] = False
    

#     def __post_init__(self) -> None:
#         self.idea_sections = ['analyst']
#         super().__post_init__()
#         return self

#     def draft(self) -> None:
#         self.rescaler = self.parameters['rescaler'](
#                 copy = self.parameters['copy'])
#         del self.parameters['rescaler']
#         self._publish_parameters()
#         self.positive_tool = self.workers['box_cox'](
#                 method = 'box_cox', **self.parameters)
#         self.negative_tool = self.workers['yeo_johnson'](
#                 method = 'yeo_johnson', **self.parameters)
#         return self

#     def publish(self, dataset, columns = None):
#         if not columns:
#             columns = dataset.numerics
#         for column in columns:
#             if dataset.x[column].min() >= 0:
#                 dataset.x[column] = self.positive_tool.fit_transform(
#                         dataset.x[column])
#             else:
#                 dataset.x[column] = self.negative_tool.fit_transform(
#                         dataset.x[column])
#             dataset.x[column] = self.rescaler.fit_transform(
#                     dataset.x[column])
#         return dataset
