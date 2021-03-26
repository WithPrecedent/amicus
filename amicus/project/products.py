"""
amicus.project.products
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:

"""
from __future__ import annotations
import abc
import dataclasses
import multiprocessing
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)
import warnings

import amicus
from . import nodes

