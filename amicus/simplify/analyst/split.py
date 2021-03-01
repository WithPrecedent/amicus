"""
simplify.analyst.split
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

import amicus
from amicus import project


@dataclasses.dataclass
class Split(amicus.project.Worker):
    """Wrapper for a Technique.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an 
            amicus instance needs settings from a Settings instance, 
            'name' should match the appropriate section name in a Settings 
            instance. Defaults to None.
        contents (Technique): stored Technique instance used by the 'implement' 
            method.
        parameters (Mapping[Any, Any]]): parameters to be attached to 'contents' 
            when the 'implement' method is called. Defaults to an empty dict.
        parallel (ClassVar[bool]): indicates whether this Component design is
            meant to be at the end of a parallel workflow structure. Defaults to 
            True.
                                                
    """    
    name: str = 'split'
    contents: Splitter = None
    container: str = 'analyst'
    parameters: Union[Mapping[str, Any], project.Parameters] = (
        project.Parameters())   


@dataclasses.dataclass
class Splitter(amicus.project.Technique):
    """Wrapper for a scikit-learn data splitter.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an 
            amicus instance needs settings from a Settings instance, 
            'name' should match the appropriate section name in a Settings 
            instance. Defaults to None.
        contents (Technique): stored Technique instance used by the 'implement' 
            method.
        module (str): name of module where 'contents' is located.
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
    container: str = 'split'
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
        project.data.splits = tuple(self.contents.split(project.data.x))
        project.data.split()
        return project


catalog = amicus.types.Catalog(
    contents = {
        'train_test_split': Splitter(
            name = 'train test',
            contents = 'ShuffleSplit',
            parameters = project.Parameters(
                name = 'train_test',
                default = {'n_splits': 1, 'test_size': 0.33, 'shuffle': True}, 
                implementation = {'random_state': 'seed'}),
            module = 'sklearn.model_selection'),
        'kfold_split': Splitter(
            name = 'kfold',
            contents = 'Kfold',
            parameters = project.Parameters(
                name = 'kfold',
                default = {'n_splits': 5, 'shuffle': True},  
                implementation = {'random_state': 'seed'}),
            module = 'sklearn.model_selection'),
        'stratified_kfold_split': Splitter(
            name = 'stratified kfold',
            contents = 'Stratified_KFold',
            parameters = project.Parameters(
                name = 'stratified_kfold',
                default = {'n_splits': 5, 'shuffle': True},  
                implementation = {'random_state': 'seed'}),
            module = 'sklearn.model_selection'),
        'group_kfold_split': Splitter(
            name = 'group kfold',
            contents = 'GroupKFold',
            parameters = project.Parameters(
                name = 'group_kfold',
                default = {'n_splits': 5, 'shuffle': True},  
                implementation = {'random_state': 'seed'}),
            module = 'sklearn.model_selection'),
        'time_series_split': Splitter(
            name = 'time series split',
            contents = 'Group_KFold',
            parameters = project.Parameters(
                name = 'time_series_split',
                default = {'n_splits': 5, 'shuffle': True},  
                implementation = {'random_state': 'seed'}),
            module = 'sklearn.model_selection')})
