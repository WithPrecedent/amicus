"""
interface: user interface for amicus project construction and iteration
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents: 
    Manager (Element, Validator):
    Project (Workflow, Element): access point and interface for creating and 
        implementing amicus projects.

"""
from __future__ import annotations
import dataclasses
import inspect
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Set, Tuple, Type, Union)
import warnings

import amicus
from . import base


@dataclasses.dataclass
class Project(amicus.quirks.Core, amicus.Validator, 
              amicus.types.Lexicon):
    """Directs construction and execution of a amicus project.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if a 
            amicus instance needs settings from a Configuration 
            instance, 'name' should match the appropriate section name in a 
            Configuration instance. Defaults to None. 
        settings (Union[base.Settings, Type[base.Settings], pathlib.Path, str, 
            Mapping[str, Mapping[str, Any]]]): a Settings-compatible subclass or 
            instance, a str or pathlib.Path containing the file path where a 
            file of a supported file type with settings for a Configuration 
            instance is located, or a 2-level mapping containing settings. 
            Defaults to the default Configuration instance.
        filer (Union[base.Filer, Type[base.Filer], pathlib.Path, str]): a 
            Clerk-compatible class or a str or pathlib.Path containing the full 
            path of where the root folder should be located for file input and 
            output. A 'filer' must contain all file path and import/export 
            methods for use throughout amicus. Defaults to the default Clerk 
            instance. 
        identification (str): a unique identification name for a amicus
            Project. The name is used for creating file folders related to the 
            project. If it is None, a str will be created from 'name' and the 
            date and time. Defaults to None.   
        outline (amicus.project.Stage): an outline of a project workflow 
            derived from 'settings'. Defaults to None.
        workflow (amicus.project.Stage): a workflow of a project derived from 
            'outline'. Defaults to None.
        summary (amicus.project.Stage): a summary of a project execution
            derived from 'workflow'. Defaults to None.
        automatic (bool): whether to automatically advance 'worker' (True) or 
            whether the worker must be advanced manually (False). Defaults to 
            True.
        data (Any): any data object for the project to be applied. If it is
            None, an instance will still execute its workflow, but it won't
            apply it to any external data. Defaults to None.  
        states (ClassVar[Sequence[Union[str, amicus.project.Stage]]]): a
            list of Stages or strings corresponding to keys in 
            'bases.stage.library'. Defaults to a list containing 'outline',
            'workflow', and 'summary'.
        validations (ClassVar[Sequence[str]]): a list of attributes that need 
            validating. Defaults to a list of attributes in the dataclass field.
    
    Attributes:
        bases (ClassVar[amicus.types.Lexicon]): a class attribute containing
            a dictionary of base classes with libraries of subclasses of those 
            bases classes. This attribute is inherited from 
            'amicus.base.Quirks'. Changing this attribute will entirely
            replace the existing links between this instance and all other base
            classes.
        
    """
    name: str = None
    settings: Union[base.Settings, Type[base.Settings], pathlib.Path, str, 
                    Mapping[str, Mapping[str, Any]]] = None
    filer: Union[base.Filer, Type[base.Filer], pathlib.Path, str] = None
    identification: str = None
    outline: base.Stage = None
    workflow: base.Stage = None
    summary: base.Stage = None
    automatic: bool = True
    data: Any = None
    stages: ClassVar[Sequence[Union[str, base.Stage]]] = [
        'outline', 'workflow', 'summary']
    validations: ClassVar[Sequence[str]] = [
        'settings', 'name', 'identification', 'filer']
    
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
        self.validate(validations = self.validations)
        # Adds 'general' section attributes from 'settings'.
        self.settings.inject(instance = self)
        # Calls 'create' and 'execute' if 'automatic' is True.
        if self.automatic:
            self.create()

    """ Public Methods """

    def create(self) -> None:
        """[summary]

        Raises:
            TypeError: [description]

        Returns:
            [type]: [description]
            
        """
        for item in self.stages:
            if isinstance(item, str):
                stage = self.bases.stage.library.borrow(names = item)
            elif inspect.isclass(item) and issubclass(item, self.bases.stage):
                stage = item
            else:
                raise TypeError(
                    f'Items in stages must be str or {self.bases.stage} '
                    f'subclasses (not instances)')
            kwargs = stage.needify(instance = self)
            setattr(self, item, stage.create(**kwargs))
            print('test product', getattr(self, item))
        return self 

    def execute(self, **kwargs) -> None:
        """ """
        pass
                        
    """ Private Methods """

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
