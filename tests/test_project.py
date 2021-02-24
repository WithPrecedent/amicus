"""
test_project: tests Project class and created composite objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""

import dataclasses
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import amicus


@dataclasses.dataclass
class Parser(amicus.project.Contest):

    pass


@dataclasses.dataclass
class Search(amicus.project.Step):

    pass   


@dataclasses.dataclass
class Divide(amicus.project.Step):

    pass   
    
    
@dataclasses.dataclass
class Destroy(amicus.project.Step):

    pass   
    

@dataclasses.dataclass
class Slice(amicus.project.Technique):

    pass  


@dataclasses.dataclass
class Dice(amicus.project.Technique):

    pass 
    
    
@dataclasses.dataclass
class Find(amicus.project.Technique):

    pass 

    
@dataclasses.dataclass
class Locate(amicus.project.Technique):

    pass 

    
@dataclasses.dataclass
class Explode(amicus.project.Technique):

    pass 

    
@dataclasses.dataclass
class Dynamite(amicus.project.Technique):
    
    name: str = 'annihilate'

    pass 
    

def test_project():
    project = amicus.Project.create(
        name = 'cool_project',
        settings = pathlib.Path('tests') / 'project_settings.py',
        automatic = True)
    # Tests base libraries.
    assert 'parser' in amicus.project.Component.subclasses
    dynamite = Dynamite()
    assert 'annihilate' in amicus.project.Component.instances
    
    # Tests workflow construction.
    print('test project workflow', project.workflow)
    print('test workflow paths', len(project.workflow.paths))
    print('test workflow endpoints', str(project.workflow.endpoints))
    print('test workflow roots', str(project.workflow.roots))
    return


if __name__ == '__main__':
    test_project()
    