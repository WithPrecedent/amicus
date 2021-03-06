"""
amicus.project.interface: access points for an amicus project
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
import collections.abc
import dataclasses
import inspect
import logging
import pathlib
from types import ModuleType
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)
import warnings

import amicus
from . import configuration

if configuration.PARALLELIZE:
    import multiprocessing
    multiprocessing.set_start_method('spawn')
    

"""Initializes the amicus project logger."""

LOGGER = logging.getLogger('amicus')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
LOGGER.addHandler(console_handler)
file_handler = logging.FileHandler('amicus.log')
file_handler.setLevel(logging.DEBUG)
LOGGER.addHandler(file_handler)
LOGGER.info(f'amicus version is: {amicus.__version__}')


""" Iterator for Constructing Project Stages """
 
@dataclasses.dataclass
class Builder(collections.abc.Iterator):
    
    project: Project = None
    stages: Sequence[str] = dataclasses.field(default_factory = dict)
    workshop: ModuleType = amicus.project.workshop

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Sets index for iteration.
        self.index = 0
        
    """ Properties """
    
    @property
    def current(self) -> str:
        return list(self.stages.keys())[self.index]
    
    @property
    def subsequent(self) -> str:
        try:
            return list(self.stages.keys())[self.index + 1]
        except IndexError:
            return None
       
    """ Public Methods """
    
    def advance(self) -> None:
        """Iterates through next stage."""
        return self.__next__()

    def complete(self) -> None:
        """Iterates through all stages."""
        for stage in self.stages:
            self.advance()
        return self
        
    # def functionify(self, source: str, product: str) -> str:
    #     """[summary]

    #     Args:
    #         source (str): [description]
    #         product (str): [description]

    #     Returns:
    #         str: [description]
            
    #     """        
    #     name = f'{source}_to_{product}'
    #     return getattr(self.workshop, name)

    # def kwargify(self, func: Callable) -> Dict[Hashable, Any]:
    #     """[summary]

    #     Args:
    #         func (Callable): [description]

    #     Returns:
    #         Dict[Hashable, Any]: [description]
            
    #     """        
    #     parameters = inspect.signature(func).parameters.keys()
    #     kwargs = {}
    #     for parameter in parameters:
    #         try:
    #             kwargs[parameter] = getattr(self.project, parameter)
    #         except AttributeError:
    #             pass
    #     return kwargs
    
    """ Dunder Methods """

    # def __getattr__(self, attribute: str) -> Any:
    #     """[summary]

    #     Args:
    #         attribute (str): [description]

    #     Raises:
    #         IndexError: [description]

    #     Returns:
    #         Any: [description]
            
    #     """
    #     if attribute in self.stages:
    #         if attribute == self.subsequent:
    #             self.__next__()
    #         else:
    #             raise IndexError(
    #                 f'You cannot call {attribute} because the current stage is '
    #                 f'{self.current} and the next callable stage is '
    #                 f'{self.subsequent}')  
    #     else:
    #         raise KeyError(f'{attribute} is not in {self.__class__.__name__}')             
            
    def __iter__(self) -> Iterable:
        """Returns iterable of a Project instance.
        
        Returns:
            Iterable: of the Project instance.
            
        """
        return self
 
    def __next__(self) -> None:
        """Completes a Stage instance."""
        if self.index + 1 < len(self.stages):
            source = self.stages[self.current]
            product = self.stages[self.subsequent]
            # builder = self.functionify(source = source, product = product)
            builder = getattr(self.workshop, f'create_{product}')
            if hasattr(configuration, 'VERBOSE') and configuration.VERBOSE:
                print(f'Creating {product}')
            kwargs = {'project': self.project}
            setattr(self.project, product, builder(**kwargs))
            self.index += 1
            if hasattr(configuration, 'VERBOSE') and configuration.VERBOSE:
                print(f'Completed {product}')
        else:
            raise StopIteration
        return self


basic_builder = Builder(stages = {
    'initialize': 'settings', 
    'draft': 'workflow', 
    'execute': 'summary'})


""" Primary Interface and Access Point """

@dataclasses.dataclass
class Project(amicus.quirks.Element):
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
        library (ClassVar[nodes.Library]): a class attribute containing a 
            dot-accessible dictionary of base classes. Each base class has 
            'subclasses' and 'instances' class attributes which contain catalogs
            of subclasses and instances of those library classes. This 
            attribute is inherited from Keystone. Changing this attribute will 
            entirely replace the existing links between this instance and all 
            other base classes.
        workflow (core.Stage): a workflow of a project derived from 'outline'. 
            Defaults to None.
        summary (core.Stage): a summary of a project execution derived from 
            'workflow'. Defaults to None.
            
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
    builder: Builder = basic_builder
    data: Any = None
    automatic: bool = True
    
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
        self._validate_settings()
        self._validate_identification()
        self.filer = amicus.options.Clerk(settings = self.settings)
        self.builder.project = self
        # Reconciles 'settings' with 'configuration'
        self.harmonize()
        # Sets multiprocessing technique, if necessary.
        if configuration.PARALLELIZE and not locals()['multiprocessing']:
            import multiprocessing
            multiprocessing.set_start_method('spawn')
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
    
    def advance(self) -> None:
        """Iterates through next stage."""
        return self.__next__()

    def complete(self) -> None:
        """Iterates through all stages."""
        for stage in self.builder.stages:
            self.advance()
        return self
    
    def harmonize(self) -> None:
        """Reconciles internal and external configuration settings.
        
        If there is any discrepany between the external settings in 'settings'
        and the default settings in 'configuration', the external settings will
        override the default internal settings.
        
        Following python conventions, all settings in 'configuration' are in all
        caps and so, the names of the external settings are checked and applied
        by converting the external settings keys into all uppercase.
        
        """
        sections = ['general', 'files', 'filer', 'amicus']
        for name in sections:
            if name in self.settings:
                for key, value in self.settings[name].items():
                    if key.upper() in dir(configuration):
                        setattr(configuration, key.upper(), value)
        return self
                     
    """ Private Methods """
    
    def _validate_settings(self) -> None:
        """Validates the 'settings' attribute.
        
        If 'settings' is None, the default 'settings' in 'configuration' is
        used.
        
        """
        if self.settings is None:
            self.settings = configuration.settings
        elif isinstance(self.settings, (str, pathlib.Path)):
            self.settings = configuration.bases.settings.create(
                file_path = self.settings)
        elif isinstance(self.settings, dict):
            self.settings = configuration.bases.settings.create(
                dictionary = self.settings)
        elif not isinstance(self.settings, configuration.bases.settings):
            raise TypeError(
                'settings must be a str, pathlib.Path, dict, None type')
        return self      
    
    def _validate_identification(self) -> None:
        """Creates unique 'identification' if one doesn't exist.
        
        By default, 'identification' is set to the 'name' attribute followed by
        an underscore and the date and time.
        
        """
        if self.identification is None:
            self.identification = amicus.tools.datetime_string(
                prefix = self.name)
        return self
    
    def _validate_settings(self) -> None:
        """Validates the 'filer' attribute.
        
        If 'filer' is None, the default 'filer' in 'configuration.bases' is
        used.
        
        """
        if self.settings is None:
            self.settings = configuration.settings
        elif isinstance(self.settings, (str, pathlib.Path)):
            self.settings = configuration.bases.settings.create(
                file_path = self.settings)
        elif isinstance(self.settings, dict):
            self.settings = configuration.bases.settings.create(
                dictionary = self.settings)
        elif not isinstance(self.settings, configuration.bases.settings):
            raise TypeError(
                'settings must be a str, pathlib.Path, dict, None type')
        self.settings.project = self
        return self      
              
    """ Dunder Methods """

    # def __getattr__(self, attribute: str) -> Any:
    #     """[summary]

    #     Args:
    #         attribute (str): [description]

    #     Raises:
    #         KeyError: [description]

    #     Returns:
    #         Any: [description]
            
    #     """
    #     if attribute in self.builder.stages:
    #         getattr(self.builder, attribute)
    #     else:
    #         raise KeyError(f'{attribute} is not in {self.name}') 
            
    def __iter__(self) -> Iterable:
        """Returns iterable of a Project's Builder instance.
        
        Returns:
            Iterable: of a Project's Builder instance.
            
        """
        return iter(self.builder)
 
    def __next__(self) -> None:
        """Completes a stage in 'builder'."""
        try:
            next(self.builder)
        except StopIteration:
            pass
        return self
