"""
analyst.steps
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0) 

Contents:

"""
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, Optional, Sequence, Tuple, Type, Union)

import numpy as np
import pandas as pd
import sklearn
import amicus


@dataclasses.dataclass
class Reduce(amicus.project.Step):
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
    name: str = 'reduce'
    contents: amicus.project.Technique = None
    iterations: Union[int, str] = 1
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = True

    """ Public Methods """

    def adjust_parameters(self, project: amicus.Project) -> None:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            [type]: [description]
            
        """
        if 'estimator' in self.parameters:
            key = self.parameters['estimator']
            self.parameters['estimator'] = self.keystones.component[key]
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


sklearn_reducers = {
    'kbest': 'SelectKBest',
    'fdr': 'SelectFdr',
    'fpt': 'SelectFpr',
    'estimator': 'SelectFromModel',
    'rfe': 'RFE',
    'rfe_cv': 'RFECV'}

sklearn_reducer_parameters = {
    'kbest': amicus.project.Parameters(
        default = {'k': 10, 'score_func': 'f_classif'},
        selected = ['k', 'score_func']),
    'fdr': amicus.project.Parameters(
        default = {'alpha': 0.05, 'score_func': 'f_classif'},
        selected = ['k', 'score_func']),
    'fpr': amicus.project.Parameters(
        default = {'alpha': 0.05, 'score_func': 'f_classif'},
        selected = ['k', 'score_func']),  
    'estimator': amicus.project.Parameters(     
        default = {'threshold': 'mean'},
        runtime = {'estimator': 'algorithm'},
        selected = ['threshold', 'estimator']),
    'rfe': amicus.project.Parameters(   
        default = {'n_features_to_select': 10, 'step': 1},
        runtime = {'estimator': 'algorithm'},
        selected = ['threshold', 'estimator']), 
    'rfe_cv': amicus.project.Parameters(   
        default = {'n_features_to_select': 10, 'step': 1},
        runtime = {'estimator': 'algorithm'},
        selected = ['threshold', 'estimator'])}

for reducer, algorithm in sklearn_reducers:
    kwargs = {
        'name': reducer, 
        'contents': algorithm,
        'module': 'sklearn.feature_selection',
        'parameters': sklearn_reducer_parameters[reducer]}
    Reduce.keystones.component[reducer] = amicus.project.SklearnTransformer(
        **kwargs) 