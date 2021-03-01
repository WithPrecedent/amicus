"""
simplify.analyst.sample
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0) 

Contents:

"""
from __future__ import annotations
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, Optional, Sequence, Set, Tuple, Type, Union)

import amicus
from amicus import project


@dataclasses.dataclass
class Sample(amicus.project.Step):
    """Wrapper for a Technique.

    An instance will try to return attributes from 'contents' if the attribute 
    is not found in the Step instance. 

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an 
            amicus instance needs settings from a Settings instance, 
            'name' should match the appropriate section name in a Settings 
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
    name: str = 'sample'
    contents: Sampler = None
    container: str = 'analyst'
    parameters: Union[Mapping[str, Any], project.Parameters] = (
        project.Parameters())   
    
    
@dataclasses.dataclass
class Sampler(amicus.quirks.Loader, amicus.project.Technique):
    """Wrapper for an encoder from category-encoders.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an 
            amicus instance needs settings from a Settings instance, 
            'name' should match the appropriate section name in a Settings 
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
    container: str = 'sampler'
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
        self.contents.fit(data.x_train, data.y_train)
        data.x_test, data.y_test = self.contents.fit_resample(
            data.x_test, 
            data.y_test)
        project.data = data
        return project


catalog = amicus.types.Catalog(
    contents = {
        'adasyn': Sampler(
            name = 'adasyn',
            contents = 'ADASYN',
            parameters = project.Parameters(
                default = {'sampling_strategy': 'auto'},
                implementation = {'random_state': 'seed'}),
            module = 'imblearn.over_sampling'),
        'cluster': Sampler(
            name = 'cluster',
            contents = 'ClusterCentroids',
            parameters = project.Parameters(
                default = {'sampling_strategy': 'auto'},
                implementation = {'random_state': 'seed'}),
            module = 'imblearn.under_sampling'),
        'knn': Sampler(
            name = 'knn',
            contents = 'AllKNN',
            parameters = project.Parameters(
                default = {'sampling_strategy': 'auto'},
                implementation = {'random_state': 'seed'}),
            module = 'imblearn.under_sampling'),
        'near_miss': Sampler(
            name = 'near_miss',
            contents = 'NearMiss',
            parameters = project.Parameters(
                default = {'sampling_strategy': 'auto'},
                implementation = {'random_state': 'seed'}),
            module = 'imblearn.under_sampling'),
        'random_over': Sampler(
            name = 'random_over',
            contents = 'RandomOverSampler',
            parameters = project.Parameters(
                default = {'sampling_strategy': 'auto'},
                implementation = {'random_state': 'seed'}),
            module = 'imblearn.over_sampling'),
        'random_under': Sampler(
            name = 'random_under',
            contents = 'RandomUnderSampler',
            parameters = project.Parameters(
                default = {'sampling_strategy': 'auto'},
                implementation = {'random_state': 'seed'}),
            module = 'imblearn.under_sampling'),
        'smote': Sampler(
            name = 'smote',
            contents = 'SMOTE',
            parameters = project.Parameters(
                default = {'sampling_strategy': 'auto'},
                implementation = {'random_state': 'seed'}),
            module = 'imblearn.over_sampling'),
        'smotenc': Sampler(
            name = 'smotenc',
            contents = 'SMOTENC',
            parameters = project.Parameters(
                default = {'sampling_strategy': 'auto'},
                implementation = {
                    'random_state': 'seed',
                    'categorical_features': 'data.categoricals'}),
            module = 'imblearn.over_sampling'),
        'smoteenn': Sampler(
            name = 'smoteenn',
            contents = 'SMOTEENN',
            parameters = project.Parameters(
                default = {'sampling_strategy': 'auto'},
                implementation = {'random_state': 'seed'}),
            module = 'imblearn.combine'),
        'smotetomek': Sampler(
            name = 'smotetomek',
            contents = 'SMOTETomek',
            parameters = project.Parameters(
                default = {'sampling_strategy': 'auto'},
                implementation = {'random_state': 'seed'}),
            module = 'imblearn.combine')})