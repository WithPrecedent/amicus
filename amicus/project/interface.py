"""
amicus.project.core: base classes for an amicus project
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
import logging
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, Optional, Sequence, Set, Tuple, Type, Union)
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

""" Primary Interface and Access Point """

@dataclasses.dataclass
class Project(amicus.quirks.Element, amicus.framework.Keystone):
    """Directs construction and execution of an amicus project.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from a Settings instance, 'name' should 
            match the appropriate section name in a Settings instance. Defaults 
            to None. 
        settings (Union[amicus.options.Settings, Type[amicus.options.Settings], 
            Mapping[str, Mapping[str, Any]]], pathlib.Path, str): a Settings-
            compatible subclass or instance, a str or pathlib.Path containing 
            the file path where a file of a supported file type with settings 
            for a Settings instance is located, or a 2-level mapping containing 
            settings. Defaults to the default Settings instance.
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
        library (ClassVar[core.Library]): a class attribute containing a 
            dot-accessible dictionary of base classes. Each base class has 
            'subclasses' and 'instances' class attributes which contain catalogs
            of subclasses and instances of those library classes. This 
            attribute is inherited from Keystone. Changing this attribute will 
            entirely replace the existing links between this instance and all 
            other base classes.
        
    """
    name: str = None
    settings: Union[
        amicus.options.Settings, 
        Type[amicus.options.Settings], 
        Mapping[str, Mapping[str, Any]],
        pathlib.Path, 
        str] = None
    filer: Union[
        amicus.options.Clerk, 
        Type[amicus.options.Clerk], 
        pathlib.Path, 
        str] = None
    identification: str = None
    outline: Union[Type[core.Outline], str] = None
    workflow: Union[Type[core.Component], str] = None
    summary: Union[Type[core.Summary], str] = None
    data: Any = None
    automatic: bool = True
    stages: ClassVar[str] = ['draft', 'publish', 'execute']
    # validations: ClassVar[Sequence[str]] = [
    #     'settings',
    #     'identification', 
    #     'filer']
    
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
        self.settings = amicus.options.Settings.create(
            file_path = self.settings)
        self.identification = self._validate_identification(
            identification = self.identification)
        self.filer = amicus.options.Clerk(settings = self.settings)
        # Adds 'general' section attributes from 'settings'.
        self.settings.inject(instance = self)
        # Sets index for iteration.
        self.index = 0
        # Calls 'execute' if 'automatic' is True.
        if self.automatic:
            self.complete()

    """ Public Methods """

    @classmethod
    def create(cls, 
        settings: amicus.options.Settings, 
        **kwargs) -> Project:
        """[summary]

        Args:
            settings (amicus.options.Settings): [description]

        Returns:
            Project: [description]
        """        
        return cls.from_settings(settings = settings, **kwargs)

    @classmethod
    def from_settings(cls, 
        settings: amicus.options.Settings, 
        **kwargs) -> Project:
        """[summary]

        Args:
            settings (amicus.options.Settings): [description]

        Returns:
            Project: [description]
        """        
        return cls(settings = settings, **kwargs)
        
    """ Public Methods """
    
    def advance(self) -> Any:
        """Iterates through next stage."""
        return self.__next__()

    def complete(self) -> Any:
        """Iterates through all stages."""
        for stage in self.stages:
            self.advance()
        return self
    
    def draft(self) -> None:
        """Creates 'outline' from 'settings'."""
        if self._check_current(stage = 'draft'):
            self.__next__()       
        return self
    
    def publish(self) -> None:
        """Creates 'workflow' from 'outline'."""
        if self._check_current(stage = 'publish'):
            self.__next__()  
        return self

    def execute(self) -> None:
        """Creates 'summary' from 'workflow'."""
        if self._check_current(stage = 'summary'):
            self.__next__()  
        return self
                        
    """ Private Methods """

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

    def _check_current(self, stage: str) -> bool:
        """[summary]

        Args:
            stage (str): [description]

        Raises:
            IndexError: [description]

        Returns:
            bool: [description]
            
        """        
        current = self.stages[self.index]
        if current != stage:
            raise IndexError(
                f'You cannot call {stage} because the current stage is '
                f'{current}')
        
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
            current = self.stages[self.index]
            builder = self.library.workshop.select(current)()
            if hasattr(self, 'verbose') and self.verbose:
                print(f'{builder.action} {builder.product}')
            kwargs = {'project': self}
            setattr(self, builder.product, builder.create(**kwargs))
            self.index += 1
        else:
            raise IndexError()
        return self
    