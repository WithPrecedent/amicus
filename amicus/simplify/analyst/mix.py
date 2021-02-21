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
class Mix(amicus.project.Step):
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
    name: str = 'mix'
    contents: amicus.project.Technique = None
    iterations: Union[int, str] = 1
    parameters: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    parallel: ClassVar[bool] = True


'polynomial': Tool(
    name = 'polynomial_mixer',
    module = 'sklearn.preprocessing',
    algorithm = 'PolynomialFeatures',
    default = {
        'degree': 2,
        'interaction_only': True,
        'include_bias': True}),
'quotient': Tool(
    name = 'quotient',
    module = None,
    algorithm = 'QuotientFeatures'),
'sum': Tool(
    name = 'sum',
    module = None,
    algorithm = 'SumFeatures'),
'difference': Tool(
    name = 'difference',
    module = None,
    algorithm = 'DifferenceFeatures')},  