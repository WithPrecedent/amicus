"""
analyst.steps
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0) 

Contents:

"""
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)

import numpy as np
import pandas as pd
import sklearn
import amicus
    

@dataclasses.dataclass
class Compare(amicus.project.Step):
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
    name: str = 'compare'
    contents: amicus.project.Technique = None
    iterations: Union[int, str] = 1
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = True



# @dataclasses.dataclass
# class CompareCleaves(TechniqueOutline):
#     """[summary]

#     Args:
#         step (str):
#         parameters (dict):
#         space (dict):
#     """
#     step: str
#     parameters: object
#     space: object

#     def __post_init__(self) -> None:
#         self.idea_sections = ['analyst']
#         super().__post_init__()
#         return self

#     def _cleave(self, dataset):
#         if self.step != 'all':
#             cleave = self.workers[self.step]
#             drop_list = [i for i in self.test_columns if i not in cleave]
#             for col in drop_list:
#                 if col in dataset.x_train.columns:
#                     dataset.x_train.drop(col, axis = 'columns',
#                                              inplace = True)
#                     dataset.x_test.drop(col, axis = 'columns',
#                                             inplace = True)
#         return dataset

#     def _publish_cleaves(self):
#         for group, columns in self.workers.items():
#             self.test_columns.extend(columns)
#         if self.parameters['include_all']:
#             self.workers.update({'all': self.test_columns})
#         return self

#     def add(self, cleave_group, columns):
#         """For the cleavers in amicus, this step alows users to manually
#         add a new cleave group to the cleaver dictionary.
#         """
#         self.workers.update({cleave_group: columns})
#         return self


#        self.scorers = {'f_classif': f_classif,
#                        'chi2': chi2,
#                        'mutual_class': mutual_info_classif,
#                        'mutual_regress': mutual_info_regression}
