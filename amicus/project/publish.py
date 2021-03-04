"""
amicus.project.draft: classes and functions for creating a project outline
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Parameters
    Directive
    Outline
    Component
    Result
    Summary

"""
from __future__ import annotations
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, Optional, Sequence, Set, Tuple, Type, Union)

import more_itertools

import amicus


def create_workflow(
    name: str, 
    outline: amicus.project.Outline,
    library: amicus.framework.Library, 
    **kwargs) -> amicus.project.Component:
    """[summary]

    Args:
        name (str): [description]. Defaults to None.
        outline (amicus.project.Outline): [description]. 
            Defaults to None.
        library (amicus.framework.Library): [description]. 
            Defaults to None.

    Returns:
        amicus.project.Component: [description]
        
    """
    directive = outline[name]
    print('test first directive', directive)
    component = amicus.project.Component.create(
        name = name, 
        directive = directive,
        outline = outline,
        library = library,
        **kwargs)
    print('test workflow adjacency', component.contents)
    component.name = name
    return component
 