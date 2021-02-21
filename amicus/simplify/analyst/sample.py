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
class Sample(amicus.project.Step):
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
    name: str = 'sample'
    contents: amicus.project.Technique = None
    iterations: Union[int, str] = 1
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = True


'adasyn': Tool(
    name = 'adasyn',
    module = 'imblearn.over_sampling',
    algorithm = 'ADASYN',
    default = {'sampling_strategy': 'auto'},
    runtime = {'random_state': 'seed'},
    fit_method = None,
    transform_method = 'fit_resample'),
'cluster': Tool(
    name = 'cluster',
    module = 'imblearn.under_sampling',
    algorithm = 'ClusterCentroids',
    default = {'sampling_strategy': 'auto'},
    runtime = {'random_state': 'seed'},
    fit_method = None,
    transform_method = 'fit_resample'),
'knn': Tool(
    name = 'knn',
    module = 'imblearn.under_sampling',
    algorithm = 'AllKNN',
    default = {'sampling_strategy': 'auto'},
    runtime = {'random_state': 'seed'},
    fit_method = None,
    transform_method = 'fit_resample'),
'near_miss': Tool(
    name = 'near_miss',
    module = 'imblearn.under_sampling',
    algorithm = 'NearMiss',
    default = {'sampling_strategy': 'auto'},
    runtime = {'random_state': 'seed'},
    fit_method = None,
    transform_method = 'fit_resample'),
'random_over': Tool(
    name = 'random_over',
    module = 'imblearn.over_sampling',
    algorithm = 'RandomOverSampler',
    default = {'sampling_strategy': 'auto'},
    runtime = {'random_state': 'seed'},
    fit_method = None,
    transform_method = 'fit_resample'),
'random_under': Tool(
    name = 'random_under',
    module = 'imblearn.under_sampling',
    algorithm = 'RandomUnderSampler',
    default = {'sampling_strategy': 'auto'},
    runtime = {'random_state': 'seed'},
    fit_method = None,
    transform_method = 'fit_resample'),
'smote': Tool(
    name = 'smote',
    module = 'imblearn.over_sampling',
    algorithm = 'SMOTE',
    default = {'sampling_strategy': 'auto'},
    runtime = {'random_state': 'seed'},
    fit_method = None,
    transform_method = 'fit_resample'),
'smotenc': Tool(
    name = 'smotenc',
    module = 'imblearn.over_sampling',
    algorithm = 'SMOTENC',
    default = {'sampling_strategy': 'auto'},
    runtime = {'random_state': 'seed'},
    data_dependent = {
        'categorical_features': 'categoricals_indices'},
    fit_method = None,
    transform_method = 'fit_resample'),
'smoteenn': Tool(
    name = 'smoteenn',
    module = 'imblearn.combine',
    algorithm = 'SMOTEENN',
    default = {'sampling_strategy': 'auto'},
    runtime = {'random_state': 'seed'},
    fit_method = None,
    transform_method = 'fit_resample'),
'smotetomek': Tool(
    name = 'smotetomek',
    module = 'imblearn.combine',
    algorithm = 'SMOTETomek',
    default = {'sampling_strategy': 'auto'},
    runtime = {'random_state': 'seed'},
    fit_method = None,
    transform_method = 'fit_resample')},   