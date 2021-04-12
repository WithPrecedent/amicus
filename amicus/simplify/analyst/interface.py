"""
analyst.base:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Analyst (SimpleManager):
    Report (SimpleSummary):
    
"""
from __future__ import annotations
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)

import numpy as np
import pandas as pd
import sklearn
import amicus

import amicus
from amicus.utilities import decorators


@dataclasses.dataclass
class Analyst(amicus.project.Worker):
    """Base class for primitive objects in an amicus composite object.
    
    The 'contents' and 'parameters' attributes are combined at the last moment
    to allow for runtime alterations.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an 
            amicus instance needs settings from a Configuration instance, 
            'name' should match the appropriate section name in a Configuration 
            instance. Defaults to None.
        contents (Any): stored item for use by a Component subclass instance.
        workflow (amicus.project.Workflow): a workflow of a project subpart 
            derived from an Outline. Defaults to None.
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
    workflow: amicus.project.Workflow = None
    iterations: Union[int, str] = 1
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = False  
        
    """ Public Methods """
    
    def implement(self, project: amicus.Project, 
                  **kwargs) -> amicus.Project:
        return project  


    @decorators.numpy_shield
    def fit(self,
            x: Optional[Union[pd.DataFrame, np.ndarray]] = None,
            y: Optional[Union[pd.Series, np.ndarray]] = None) -> None:
        """Generic fit method for partial compatibility to sklearn.

        Args:
            x (Optional[Union[pd.DataFrame, np.ndarray]]): independent
                variables/features.
            y (Optional[Union[pd.Series, np.ndarray]]): dependent
                variable/label.

        Raises:
            AttributeError if no 'fit' method exists for 'technique'.

        """
        x, y = sklearn.utils.check_X_y(X = x, y = y, accept_sparse = True)
        if self.fit_method is not None:
            if y is None:
                getattr(self.algorithm, self.fit_method)(x)
            else:
                self.algorithm = self.algorithm.fit(x, y)
        return self

    @decorators.numpy_shield
    def transform(self,
            x: Optional[Union[pd.DataFrame, np.ndarray]] = None,
            y: Optional[Union[pd.Series, np.ndarray]] = None) -> pd.DataFrame:
        """Generic transform method for partial compatibility to sklearn.

        Args:
            x (Optional[Union[pd.DataFrame, np.ndarray]]): independent
                variables/features.
            y (Optional[Union[pd.Series, np.ndarray]]): dependent
                variable/label.

        Returns:
            transformed x or data, depending upon what is passed to the
                method.

        Raises:
            AttributeError if no 'transform' method exists for local
                'process'.

        """
        if self.transform_method is not None:
            try:
                return getattr(self.algorithm, self.transform_method)(x)
            except AttributeError:
                return x
        else:
            return x



@dataclasses.dataclass
class Report(amicus.base.SimpleSummary):
    """Collects and stores results of executing a data science project workflow.
    
    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
        default (Any): default value to return when the 'get' method is used.
        prefix (str): prefix to use when storing different paths through a 
            workflow. So, for example, a prefix of 'path' will create keys of
            'path_1', 'path_2', etc. Defaults to 'experiment'.
        needs (ClassVar[Union[Sequence[str], str]]): attributes needed from 
            another instance for some method within a subclass. Defaults to 
            a list with 'workflow' and 'data'.          
              
    """
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    default: Any = None
    prefix: str = 'experiment'
    needs: ClassVar[Union[Sequence[str], str]] = ['workflow', 'data'] 




# @dataclasses.dataclass
# class Tool(Technique):
#     """Base method wrapper for applying algorithms to data.

#     Args:
#         name (Optional[str]): designates the name of the class used for internal
#             referencing throughout amicus. If the class needs settings from
#             the shared 'Idea' instance, 'name' should match the appropriate
#             section name in 'Idea'. When subclassing, it is a good idea to use
#             the same 'name' attribute as the base class for effective
#             coordination between amicus classes. 'name' is used instead of
#             __class__.__name__ to make such subclassing easier. Defaults to
#             None or __class__.__name__.lower() if super().__post_init__ is
#             called.
#         step (Optional[str]): name of step when the class instance is to be
#             applied. Defaults to None.
#         module (Optional[str]): name of module where object to use is located
#             (can either be an amicus or non-amicus module). Defaults to
#             'amicus.core'.
#         algorithm (Optional[object]): process object which executes the primary
#             method of a class instance. Defaults to None.
#         parameters (Optional[Dict[str, Any]]): parameters to be attached to
#             'algorithm' when 'algorithm' is instanced. Defaults to an empty
#             dictionary.

#     """
#     name: Optional[str] = None
#     step: Optional[str] = None
#     module: Optional[str] = None
#     algorithm: Optional[object] = None
#     parameters: Optional[Dict[str, Any]] = dataclasses.field(default_factory = dict)
#     default: Optional[Dict[str, Any]] = dataclasses.field(default_factory = dict)
#     required: Optional[Dict[str, Any]] = dataclasses.field(default_factory = dict)
#     runtime: Optional[Dict[str, str]] = dataclasses.field(default_factory = dict)
#     selected: Optional[Union[bool, List[str]]] = False
#     data_dependent: Optional[Dict[str, str]] = dataclasses.field(default_factory = dict)
#     parameter_space: Optional[Dict[str, List[Union[int, float]]]] = dataclasses.field(
#         default_factory = dict)
#     fit_method: Optional[str] = dataclasses.field(default_factory = lambda: 'fit')
#     transform_method: Optional[str] = dataclasses.field(
#         default_factory = lambda: 'transform')

#     """ Keystone amicus Methods """

#     def apply(self, data: 'Dataset') -> 'Dataset':
#         if data.stages.current in ['full']:
#             self.fit(x = data.x, y = data.y)
#             data.x = self.transform(x = data.x, y = data.y)
#         else:

#             self.fit(x = data.x_train, y = data.y_train)
#             data.x_train = self.transform(x = data.x_train, y = data.y_train)
#             data.x_test = self.transform(x = data.x_test, y = data.y_test)
#         return data

#     """ Scikit-Learn Compatibility Methods """

#     @numpy_shield
#     def fit(self,
#             x: Optional[Union[pd.DataFrame, np.ndarray]] = None,
#             y: Optional[Union[pd.Series, np.ndarray]] = None) -> None:
#         """Generic fit method for partial compatibility to sklearn.

#         Args:
#             x (Optional[Union[pd.DataFrame, np.ndarray]]): independent
#                 variables/features.
#             y (Optional[Union[pd.Series, np.ndarray]]): dependent
#                 variable/label.

#         Raises:
#             AttributeError if no 'fit' method exists for 'technique'.

#         """
#         x, y = check_X_y(X = x, y = y, accept_sparse = True)
#         if self.fit_method is not None:
#             if y is None:
#                 getattr(self.algorithm, self.fit_method)(x)
#             else:
#                 self.algorithm = self.algorithm.fit(x, y)
#         return self

#     @numpy_shield
#     def transform(self,
#             x: Optional[Union[pd.DataFrame, np.ndarray]] = None,
#             y: Optional[Union[pd.Series, np.ndarray]] = None) -> pd.DataFrame:
#         """Generic transform method for partial compatibility to sklearn.

#         Args:
#             x (Optional[Union[pd.DataFrame, np.ndarray]]): independent
#                 variables/features.
#             y (Optional[Union[pd.Series, np.ndarray]]): dependent
#                 variable/label.

#         Returns:
#             transformed x or data, depending upon what is passed to the
#                 method.

#         Raises:
#             AttributeError if no 'transform' method exists for local
#                 'process'.

#         """
#         if self.transform_method is not None:
#             try:
#                 return getattr(self.algorithm, self.transform_method)(x)
#             except AttributeError:
#                 return x
#         else:
#             return x


# """ Publisher Subclass """

# @dataclasses.dataclass
# class AnalystPublisher(Publisher):
#     """Creates 'Cookbook'

#     Args:
#         idea ('Idea'): an 'Idea' instance with project settings.

#     """

#     """ Public Methods """

#     # def add_cleaves(self,
#     #         cleave_group: str,
#     #         prefixes: Union[List[str], str] = None,
#     #         columns: Union[List[str], str] = None) -> None:
#     #     """Adds cleaves to the list of cleaves.

#     #     Args:
#     #         cleave_group (str): names the set of features in the group.
#     #         prefixes (Union[List[str], str]): name(s) of prefixes to columns to
#     #             be included within the cleave.
#     #         columns (Union[List[str], str]): name(s) of columns to be included
#     #             within the cleave.

#     #     """
#     #     # if not self._exists('cleaves'):
#     #     #     self.cleaves = []
#     #     # columns = self.dataset.make_column_list(
#     #     #     prefixes = prefixes,
#     #     #     columns = columns)
#     #     # self.workers['cleaver'].add_techniques(
#     #     #     cleave_group = cleave_group,
#     #     #     columns = columns)
#     #     # self.cleaves.append(cleave_group)
#     #     return self


# """ Scholar Subclasses """

# @dataclasses.dataclass
# class AnalystScholar(Scholar):
#     """Applies a 'Cookbook' instance to data.

#     Args:
#         worker ('Worker'): instance with information needed to apply a 'Book'
#             instance.
#         idea (Optional[Idea]): instance with project settings.

#     """
#     worker: 'Worker'
#     idea: Optional[core.Idea] = None

#     def __post_init__(self) -> None:
#         """Initializes class instance attributes."""
#         self = self.idea.apply(instance = self)
#         # Creates 'Finisher' instance to finalize 'Technique' instances.
#         self.finisher = AnalystFinisher(worker = self.worker)
#         # Creates 'Specialist' instance to apply 'Technique' instances.
#         self.specialist = AnalystSpecialist(worker = self.worker)
#         # Creates 'Parallelizer' instance to apply 'Chapter' instances, if the
#         # option to parallelize has been selected.
#         if self.parallelize:
#             self.parallelizer = Parallelizer(idea = self.idea)
#         return self

#     """ Private Methods """

#     def _get_model_type(self, data: 'Dataset') -> str:
#         """Infers 'model_type' from data type of 'label' column.

#         Args:
#             data ('Dataset'): instance with completed dataset.

#         Returns:
#             str: containing the name of one of the supported model types.

#         Raises:
#             TypeError: if 'label' attribute is neither None, 'boolean',
#                 'category', 'integer' or 'float' data type (using amicus
#                 proxy datatypes).

#         """
#         if self.label is None:
#             return 'clusterer'
#         elif data.datatypes[self.label] in ['boolean']:
#             return 'classifier'
#         elif data.datatypes[self.label] in ['category']:
#             if len(data[self.label.value_counts()]) == 2:
#                 return 'classifier'
#             else:
#                 return 'multi_classifier'
#         elif data.datatypes[self.label] in ['integer', 'float']:
#             return 'regressor'
#         else:
#             raise TypeError(
#                 'label must be boolean, category, integer, float, or None')


# @dataclasses.dataclass
# class AnalystFinisher(Finisher):
#     """Finalizes 'Technique' instances with data-dependent parameters.

#     Args:
#         worker ('Worker'): instance with information needed to apply a 'Book'
#             instance.
#         idea (Optional[Idea]): instance with project settings.

#     """
#     worker: 'Worker'
#     idea: Optional[core.Idea] = None

#     """ Private Methods """

#     def _add_model_conditionals(self,
#             technique: 'Technique',
#             data: 'Dataset') -> 'Technique':
#         """Adds any conditional parameters to 'technique'

#         Args:
#             technique ('Technique'): an instance with 'algorithm' and
#                 'parameters' not yet combined.
#             data ('Dataset'): data object used to derive hyperparameters.

#         Returns:
#             'Technique': with any applicable parameters added.

#         """
#         self._model_calculate_hyperparameters(
#             technique = technique,
#             data = data)
#         if technique.name in ['xgboost'] and self.idea['general']['gpu']:
#             technique.parameters['tree_method'] = 'gpu_exact'
#         elif step in ['tensorflow']:
#             technique.algorithm = algorithms.make_tensorflow_model(
#                 technique = technique,
#                 data = data)
#         return technique

#     def _model_calculate_hyperparameters(self,
#             technique: 'Technique',
#             data: 'Dataset') -> 'Technique':
#         """Computes hyperparameters from data.

#         This method will include any heuristics or methods for creating smart
#         algorithm parameters (without creating data leakage problems).

#         This method currently only support xgboost's scale_pos_weight
#         parameter. Future hyperparameter computations will be added as they
#         are discovered.

#         Args:
#             technique ('Technique'): an instance with 'algorithm' and
#                 'parameters' not yet combined.
#             data ('Dataset'): data object used to derive hyperparameters.

#         Returns:
#             'Technique': with any applicable parameters added.

#         """
#         if (technique.name in ['xgboost']
#                 and self.idea['analyst']['calculate_hyperparameters']):
#             technique.parameters['scale_pos_weight'] = (
#                 len(self.data.y.index) / ((self.data.y == 1).sum())) - 1
#         return self


# @dataclasses.dataclass
# class AnalystSpecialist(Specialist):
#     """Base class for applying 'Technique' instances to data.

#     Args:
#         worker ('Worker'): instance with information needed to apply a 'Book'
#             instance.
#         idea (Optional[Idea]): instance with project settings.

#     """
#     worker: 'Worker'
#     idea: Optional[core.Idea] = None

#     """ Private Methods """

#     def _apply_techniques(self,
#             manuscript: 'Chapter',
#             data: 'Dataset') -> 'Chapter':
#         """Applies a 'chapter' of 'steps' to 'data'.

#         Args:
#             chapter ('Chapter'): instance with 'steps' to apply to 'data'.
#             data (Union['Dataset', 'Book']): object for 'chapter' to be applied.

#         Return:
#             'Chapter': with any changes made. Modified 'data' is added to the
#                 'Chapter' instance with the attribute name matching the 'name'
#                 attribute of 'data'.

#         """
#         data.create_xy()
#         for i, technique in enumerate(manuscript.techniques):
#             if self.verbose:
#                 print('Applying', technique.name, 'to', data.name)
#             if technique.step in ['split']:
#                 manuscript, data = self._split_loop(
#                     chapter = manuscript,
#                     index = i,
#                     data = data)
#                 break
#             elif technique.step in ['search']:
#                 remaining = self._search_loop(
#                     steps = remaining,
#                     index = i,
#                     data = data)
#                 data = technique.apply(data = data)
#             elif not technique.name in ['none', None]:
#                 data = technique.apply(data = data)
#         setattr(manuscript, 'data', data)
#         return manuscript

#     def _split_loop(self,
#             chapter: 'Chapter',
#             index: int,
#             data: 'DataSet') -> ('Chapter', 'Dataset'):
#         """Splits 'data' and applies remaining steps in 'chapter'.

#         Args:
#             chapter ('Chapter'): instance with 'steps' to apply to 'data'.
#             index (int): number of step in 'chapter' 'steps' where split method
#                 is located. All subsequent steps are completed with data split
#                 into training and testing sets.
#             data ('Dataset'): data object for 'chapter' to be applied.

#         Return:
#             'Chapter', 'Dataset': with any changes made.

#         """
#         data.stages.change('testing')
#         split_algorithm = chapter.techniques[index].algorithm
#         for i, (train_index, test_index) in enumerate(
#             split_algorithm.split(data.x, data.y)):
#             if self.verbose:
#                 print('Testing data fold', str(i))
#             data.x_train = data.x.iloc[train_index]
#             data.x_test = data.x.iloc[test_index]
#             data.y_train = data.y[train_index]
#             data.y_test = data.y[test_index]
#             for technique in chapter.techniques[index + 1:]:
#                 if self.verbose:
#                     print('Applying', technique.name, 'to', data.name)
#                 if not technique.name in ['none', None]:
#                     data = technique.apply(data = data)
#         return chapter, data

#     def _search_loop(self,
#             chapter: 'Chapter',
#             index: int,
#             data: 'DataSet') -> ('Chapter', 'Dataset'):
#         """Searches hyperparameters for a particular 'algorithm'.

#         Args:
#             chapter ('Chapter'): instance with 'steps' to apply to 'data'.
#             index (int): number of step in 'chapter' 'steps' where the search
#                 method should be applied
#             data ('Dataset'): data object for 'chapter' to be applied.

#         Return:
#             'Chapter': with the searched step modified with the best found
#                 hyperparameters.

#         """
#         return chapter


