"""
interface: external access point for amicus projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    LOGGER: the amicus project logger.
    Project: the interface for amicus projects.
     
"""
from __future__ import annotations
import collections.abc
import dataclasses
import inspect
import logging
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Set, Tuple, Type, Union)
import warnings

import amicus
from . import core


"""Initializes the amicus project logger."""

LOGGER = logging.getLogger('amicus')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
LOGGER.addHandler(console_handler)
file_handler = logging.FileHandler('amicus.log')
file_handler.setLevel(logging.DEBUG)
LOGGER.addHandler(file_handler)


""" Interface Class """

@dataclasses.dataclass
class Project(
    amicus.quirks.Needy,
    amicus.framework.Validator, 
    amicus.framework.Keystone, 
    collections.abc.Iterator):
    """Directs construction and execution of an amicus project.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        settings (Union[core.Settings, Type[core.Settings], Mapping[str, 
            Mapping[str, Any]]], pathlib.Path, str): a Settings-compatible 
            subclass or instance, a str or pathlib.Path containing the file path 
            where a file of a supported file type with settings for a Settings 
            instance is located, or a 2-level mapping containing settings. 
            Defaults to the default Settings instance.
        filer (Union[core.Filer, Type[core.Filer], pathlib.Path, str]): a Filer-
            compatible class or a str or pathlib.Path containing the full path 
            of where the root folder should be located for file input and 
            output. A 'filer' must contain all file path and import/export 
            methods for use throughout amicus. Defaults to the default Clerk 
            instance. 
        identification (str): a unique identification name for an amicus 
            Project. The name is used for creating file folders related to the 
            project. If it is None, a str will be created from 'name' and the 
            date and time. Defaults to None.   
        outline (core.Stage): an outline of a project workflow derived from 
            'settings'. Defaults to None.
        workflow (core.Stage): a workflow of a project derived from 'outline'. 
            Defaults to None.
        summary (core.Stage): a summary of a project execution derived from 
            'workflow'. Defaults to None.
        automatic (bool): whether to automatically iterate through the project
            stages (True) or whether it must be iterating manually (False). 
            Defaults to True.
        data (Any): any data object for the project to be applied. If it is 
            None, an instance will still execute its workflow, but it won't
            apply it to any external data. Defaults to None.  
        stages (ClassVar[Sequence[Union[str, core.Stage]]]): a list of Stages or 
            strings corresponding to keys in 'core.library'. Defaults to a list 
            of strings listed in the dataclass field.
        validations (ClassVar[Sequence[str]]): a list of attributes that need 
            validating. Defaults to a list of strings listed in the dataclass 
            field.
    
    Attributes:
        keystones (ClassVar[core.Library]): a class attribute containing a 
            dot-accessible dictionary of base classes. Each base class has 
            'subclasses' and 'instances' class attributes which contain catalogs
            of subclasses and instances of those keystones classes. This 
            attribute is inherited from Keystone. Changing this attribute will 
            entirely replace the existing links between this instance and all 
            other base classes.
        
    """
    name: str = None
    settings: Union[
        core.Settings, 
        Type[core.Settings], 
        Mapping[str, Mapping[str, Any]],
        pathlib.Path, 
        str] = None
    filer: Union[core.Filer, Type[core.Filer], pathlib.Path, str] = None
    identification: str = None
    outline: Union[Type[core.Stage], str] = core.Outline
    workflow: Union[Type[core.Stage], str] = core.Workflow
    summary: Union[Type[core.Stage], str] = core.Summary
    automatic: bool = True
    data: Any = None
    needs: ClassVar[Sequence[str]] = ['settings']
    stages: ClassVar[Union[Type[core.Stage], str]] = [
        'outline', 
        'workflow', 
        'summary']
    validations: ClassVar[Sequence[str]] = [
        'name', 
        'identification', 
        'filer']
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Calls validation methods.
        self.settings = self._validate_settings(settings = self.settings)
        self.validate(validations = self.validations)
        # Adds 'general' section attributes from 'settings'.
        self.settings.inject(instance = self)
        # Sets index for iteration.
        self.index = 0
        # Calls 'create' and 'execute' if 'automatic' is True.
        if self.automatic:
            self.execute()

    """ Class Methods """

    @classmethod
    def from_settings(cls, settings: core.Settings, **kwargs) -> Project:
        return cls(settings = settings, **kwargs)
        
    """ Public Methods """
    
    def advance(self) -> Any:
        """Returns next product created in iterating a Director instance."""
        return self.__next__()
    
    def execute(self ) -> None:
        """Iterates through all stages."""
        for stage in self.stages:
            self.advance()
        return self
                        
    """ Private Methods """

    def _validate_settings(self, settings: Any) -> core.Settings:
        return self.keystones.settings.create(file_path = settings)
    
    def _validate_name(self, name: str) -> str:
        """Creates 'name' if one doesn't exist.
        
        If 'name' was not passed, this method first tries to infer 'name' as the 
        first appropriate section name in 'settings'. If that doesn't work, it 
        uses the snakecase name of the class.
        
        Args:
            name (str): name of the project, if passed.
            
        Returns:
            str: a default name, if none was passed. But if the passed 'name'
                exists, it is returned unchanged. 
            
        """
        if not name:
            sections = self.settings.excludify(subset = self.settings.skip)
            try:
                name = sections.keys()[0]
            except IndexError:
                name = amicus.tools.snakify(self.__class__)
        return name

    def _validate_identification(self, identification: str) -> str:
        """Creates unique 'identification' if one doesn't exist.
        
        By default, 'identification' is set to the 'name' attribute followed by
        an underscore and the date and time.
        
        Args:
            identification (str): unique identification string for a project.
            
        Returns:
            str: a default identification, derived from the project's 'name'
                attribute and the date and time.
        
        """
        if not identification:
            identification = amicus.tools.datetime_string(prefix = self.name)
        return identification
  
    """ Dunder Methods """

    def __iter__(self) -> Iterable:
        """Returns iterable of a Project instance.
        
        Returns:
            Iterable: of the Project instance.
            
        """
        return iter(self)
 
    def __next__(self) -> None:
        """Completes a Stage instance."""
        if self.index < len(self.stages):
            base = self.keystones.stage
            current = self.stages[self.index]
            if isinstance(current, str):
                name = amicus.tools.snakify(current)
                stage = base.select(name = name)
            elif inspect.isclass(current) and issubclass(current, base):
                stage = current
                name = amicus.tools.snakify(stage.__name__)
            else:
                raise TypeError(
                    f'Items in stages must be str or {base.__name__} '
                    f'subclasses (not instances)') 
            if hasattr(self, 'verbose') and self.verbose:
                print(f'Creating {name}')
            kwargs = stage.needify(instance = self)
            print('test name current', name, current, kwargs.keys())
            setattr(self, name, stage.create(**kwargs))
            if hasattr(self, 'verbose') and self.verbose:
                print(f'Completed {name}')
            self.index += 1
        else:
            raise IndexError()
        return self
    