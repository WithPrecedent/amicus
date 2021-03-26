"""
amicus.project.configuration:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

This module stores universally accessible configuration options in the form of
module-level constants.
 
"""

from . import nodes
from . import core


VERBOSE: bool = True
SEED: int = 42
CONSERVE_MEMORY: bool = False
PARALLELIZE: bool = False

DESIGN = 'technique'
LIBRARY = nodes.Component.library
SUMMARY = core.Summary
RESULT = core.Result