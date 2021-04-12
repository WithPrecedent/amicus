"""
analyst.scale
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

import numpy as np
import pandas as pd

import amicus


@dataclasses.dataclass
class Search(amicus.project.Technique):
    """Searches hyperparameters for the best options.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an 
            amicus instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        contents (Technique): stored Technique instance used by the 'implement' 
            method.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            True.
                                                
    """    
    name: str = 'search'
    contents: amicus.project.Technique = None
    parameters: Union[Mapping[str, Any], amicus.project.Parameters] = (
        amicus.project.Parameters())
    parallel: ClassVar[bool] = True
    

# @dataclasses.dataclass
# class SearchComposer(AnalystComposer):
#     """Searches for optimal model hyperparameters using specified step.

#     Args:

#     Returns:
#         [type]: [description]
#     """
#     name: str = 'search_composer'
#     algorithm_class: object = SearchAnalystTechnique
#     step_class: object = SearchTechnique

#     def __post_init__(self) -> None:
#         self.idea_sections = ['analyst']
#         super().__post_init__()
#         return self

#     """ Private Methods """

#     def _build_conditional(self, step: AnalystTechnique, parameters: dict):
#         """[summary]

#         Args:
#             step (namedtuple): [description]
#             parameters (dict): [description]
#         """
#         if 'refit' in parameters and isinstance(parameters['scoring'], list):
#             parameters['scoring'] = parameters['scoring'][0]
#         return parameters
#         self.space = {}
#         if step.hyperparameter_search:
#             new_parameters = {}
#             for parameter, values in parameters.items():
#                 if isinstance(values, list):
#                     if self._datatype_in_list(values, float):
#                         self.space.update(
#                             {parameter: uniform(values[0], values[1])})
#                     elif self._datatype_in_list(values, int):
#                         self.space.update(
#                             {parameter: randint(values[0], values[1])})
#                 else:
#                     new_parameters.update({parameter: values})
#             parameters = new_parameters
#         return parameters

#     def _search_hyperparameter(self, dataset: Dataset,
#                                data_to_use: str):
#         search = SearchComposer()
#         search.space = self.space
#         search.estimator = self.algorithm
#         return search.publish(data = dataset)

#     """ Keystone amicus Methods """

#     def draft(self) -> None:
#         self.bayes = Technique(
#             name = 'bayes',
#             module = 'bayes_opt',
#             algorithm = 'BayesianOptimization',
#             runtime = {
#                 'f': 'estimator',
#                 'pbounds': 'space',
#                 'random_state': 'seed'})
#         self.grid = Technique(
#             name = 'grid',
#             module = 'sklearn.model_selection',
#             algorithm = 'GridSearchCV',
#             runtime = {
#                 'estimator': 'estimator',
#                 'param_distributions': 'space',
#                 'random_state': 'seed'})
#         self.random = Technique(
#             name = 'random',
#             module = 'sklearn.model_selection',
#             algorithm = 'RandomizedSearchCV',
#             runtime = {
#                 'estimator': 'estimator',
#                 'param_distributions': 'space',
#                 'random_state': 'seed'})
#         super().draft()
#         return self


# @dataclasses.dataclass
# class SearchAnalystTechnique(AnalystTechnique):
#     """[summary]

#     Args:
#         object ([type]): [description]
#     """
#     step: str
#     algorithm: object
#     parameters: object
#     data_dependent: object = None
#     hyperparameter_search: bool = False
#     space: object = None
#     name: str = 'search'

#     def __post_init__(self) -> None:
#         super().__post_init__()
#         return self

#     @numpy_shield
#     def publish(self, dataset: Dataset, data_to_use: str):
#         """[summary]

#         Args:
#             dataset ([type]): [description]
#             data_to_use ([type]): [description]
#         """
#         if self.step in ['random', 'grid']:
#             return self.algorithm.fit(
#                 X = getattr(dataset, ''.join(['x_', data_to_use])),
#                 Y = getattr(dataset, ''.join(['y_', data_to_use])),
#                 **kwargs)


#     # @numpy_shield
#     def publish_reduce(self, dataset, plan = None, estimator = None):
#         if not estimator:
#             estimator = plan.model.algorithm
#         self._set_parameters(estimator)
#         self.algorithm = self.workers[self.step](**self.parameters)
#         if len(dataset.x_train.columns) > self.num_features:
#             self.algorithm.fit(dataset.x_train, dataset.y_train)
#             mask = ~self.algorithm.get_support()
#             dataset.drop_columns(df = dataset.x_train, mask = mask)
#             dataset.drop_columns(df = dataset.x_test, mask = mask)
#         return dataset


#     def _set_reduce_parameters(self, estimator):
#        if self.step in ['rfe', 'rfecv']:
#            self.default = {'n_features_to_select': 10,
#                                       'step': 1}
#            self.runtime_parameters = {'estimator': estimator}
#        elif self.step == 'kbest':
#            self.default = {'k': 10,
#                                       'score_func': f_classif}
#            self.runtime_parameters = {}
#        elif self.step in ['fdr', 'fpr']:
#            self.default = {'alpha': 0.05,
#                                       'score_func': f_classif}
#            self.runtime_parameters = {}
#        elif self.step == 'custom':
#            self.default = {'threshold': 'mean'}
#            self.runtime_parameters = {'estimator': estimator}
#        self._publish_parameters()
#        self._select_parameters()
#        self.parameters.update({'estimator': estimator})
#        if 'k' in self.parameters:
#            self.num_features = self.parameters['k']
#        else:
#            self.num_features = self.parameters['n_features_to_select']
#         return self
