"""
amicus.project.configuration:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

This module stores universally accessible configuration options in the form of
module-level constants.
 
"""
from __future__ import annotations
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)

from . import nodes
from . import core

""" General Default Settings """

CONSERVE_MEMORY: bool = False
PARALLELIZE: bool = False
SEED: int = 42
VERBOSE: bool = True

""" Default Classes and Related Options """

COMPONENT: Type = nodes.Component
COOKBOOK: Type = core.Cookbook
DESIGN: str = 'technique'
LIBRARY: Type = nodes.Component.library
RECIPE: Type = core.Recipe
RESULT: Type = core.Result
SUMMARY: Type = core.Summary
WORKFLOW: Type = core.Workflow