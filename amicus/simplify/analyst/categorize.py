"""
analyst.categorize:
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

from . import base
import amicus


@dataclasses.dataclass
class Categorize(amicus.project.Step):
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
    name: str = 'encode'
    contents: amicus.project.Technique = None
    parameters: Union[Mapping[str, Any], base.Parameters] = base.Parameters()
    parallel: ClassVar[bool] = True
    

'automatic': Tool(
    name = 'automatic',
    module = 'amicus.analyst.algorithms',
    algorithm = 'auto_categorize',
    default = {'threshold': 10}),
'binary': Tool(
    name = 'binary',
    module = 'sklearn.preprocessing',
    algorithm = 'Binarizer',
    default = {'threshold': 0.5}),
'bins': Tool(
    name = 'bins',
    module = 'sklearn.preprocessing',
    algorithm = 'KBinsDiscretizer',
    default = {
        'strategy': 'uniform',
        'n_bins': 5},
    selected = True,
    required = {'encode': 'onehot'})},