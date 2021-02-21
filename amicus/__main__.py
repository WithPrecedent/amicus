"""
amicus main: a friend to your python projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

"""
from __future__ import annotations
import sys
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
                    Mapping, Optional, Sequence, Tuple, Type, Union)

import amicus


def _args_to_dict() -> Dict[str, str]:
    """Converts command line arguments into 'arguments' dict.

    The dictionary conversion is more forgiving than the typical argparse
    construction. It allows the package to check default options and give
    clearer error coding.

    This handy bit of code, as an alternative to argparse, was found here:
        https://stackoverflow.com/questions/54084892/
        how-to-convert-commandline-key-value-args-to-dictionary

    Returns:
        Dict[str, str]: dictionary of command line options when the options are 
            separated by '='.

    """
    arguments = {}
    for argument in sys.argv[1:]:
        if '=' in argument:
            separated = argument.find('=')
            key, value = argument[:separated], argument[separated + 1:]
            arguments[key] = value
    return arguments

if __name__ == '__main__':
    # Gets command line arguments and converts them to dict.
    arguments = _args_to_dict()
    # Calls Project with passed command-line arguments.
    amicus.Project(
        settings = arguments.get('-settings'),
        clerk = arguments.get('-clerk', None),
        data = arguments.get('-data', None))