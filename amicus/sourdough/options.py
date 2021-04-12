"""
options: base configuration and file management classes for amicus projects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:
    Configuration (Lexicon): stores configuration settings after either loading 
        them from disk or by the passed arguments.    
    Clerk (object): interface for amicus file management classes and methods.
         
"""
from __future__ import annotations
import abc
import configparser
import dataclasses
import importlib
import importlib.util
import json
import pathlib
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, MutableMapping, MutableSequence, Optional, Sequence, Set, Tuple, 
    Type, Union)

import more_itertools

import amicus


@dataclasses.dataclass
class Configuration(amicus.types.Lexicon):
    """Loads and stores configuration settings.

    To create Configuration instance, a user can pass a:
        1) file path to a compatible file type;
        2) string containing a a file path to a compatible file type;
                                or,
        3) 2-level nested dict.

    If 'contents' is imported from a file, Configuration creates a dict and can 
    convert the dict values to appropriate datatypes. Currently, supported file 
    types are: ini, json, toml, and python.

    If 'infer_types' is set to True (the default option), str dict values are 
    automatically converted to appropriate datatypes (str, list, float, bool, 
    and int are currently supported). Type conversion is automatically disabled
    if the source file is a python module (assuming the user has properly set
    the types of the stored python dict).

    Because Configuration uses ConfigParser for .ini files, by default it stores 
    a 2-level dict. The desire for accessibility and simplicity amicusted this 
    limitation. A greater number of levels can be achieved by having separate
    sections with names corresponding to the strings in the values of items in 
    other sections. This is implemented in the 'project' subpackage.

    Args:
        contents (Mapping[str, Mapping[str, Any]]): a two-level nested dict for
            storing configuration options. Defaults to en empty dict.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty dict.
        standard (Mapping[str, Mapping[str]]): any standard options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to an empty dict.
        infer_types (bool): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, all values will be strings. Defaults to True.

    """
    contents: Mapping[str, Mapping[str, Any]] = dataclasses.field(
        default_factory = dict)
    default: Any = dataclasses.field(default_factory = dict)
    standard: Mapping[str, Mapping[str, Any]] = dataclasses.field(
        default_factory = dict)
    infer_types: bool = True

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Infers types for values in 'contents', if the 'infer_types' option is 
        # selected.
        if self.infer_types:
            self.contents = self._infer_types(contents = self.contents)
        # Adds default settings as backup settings to 'contents'.
        self.contents = self._add_standard(contents = self.contents)

    """ Class Methods """

    @classmethod
    def create(cls, **kwargs) -> Configuration:
        """Calls corresponding creation class method to instance a subclass.

        Raises:
            TypeError: If there is no corresponding method.

        Returns:
            Needy: instance of a Needy subclass.
            
        """
        if 'file_path' in kwargs:
            return cls.from_file_path(**kwargs)
        elif 'dictionary' in kwargs:
            if (isinstance(kwargs['dictionary'], Mapping) 
                    and all(isinstance(v, Mapping) 
                            for v in kwargs['dictionary'].values())):
                return cls.from_dictionary(**kwargs)
            else:
                raise TypeError(f'dictionary must be nested dict type')
        else:
            raise TypeError(
                f'create method requires a str, pathlib.Path, or dict type')   

    @classmethod
    def from_dictionary(cls, 
        dictionary: Mapping[str, Mapping[str, Any]], 
        **kwargs) -> Configuration:
        """[summary]

        Args:
            path (Union[str, pathlib.Path]): [description]

        Returns:
            Configuration: [description]
            
        """        
        return cls(contents = dictionary, **kwargs)
    
    @classmethod
    def from_file_path(cls, 
        file_path: Union[str, pathlib.Path], 
        **kwargs) -> Configuration:
        """[summary]

        Args:
            path (Union[str, pathlib.Path]): [description]

        Returns:
            Configuration: [description]
            
        """        
        extension = str(pathlib.Path(file_path).suffix)[1:]
        load_method = getattr(cls, f'from_{extension}')
        return load_method(file_path = file_path, **kwargs)
    
    @classmethod
    def from_ini(cls, 
        file_path: Union[str, pathlib.Path], 
        **kwargs) -> Configuration:
        """Returns settings dictionary from an .ini file.

        Args:
            file_path (str): path to configparser-compatible .ini file.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a file.

        """
        if 'infer_types' not in kwargs:
            kwargs['infer_types'] = True
        try:
            contents = configparser.ConfigParser(dict_type = dict)
            contents.optionxform = lambda option: option
            contents.read(str(file_path))
            return cls(contents = dict(contents._sections), **kwargs)
        except (KeyError, FileNotFoundError):
            raise FileNotFoundError(f'settings file {file_path} not found')

    @classmethod
    def from_json(cls, 
        file_path: Union[str, pathlib.Path], 
        **kwargs) -> Configuration:
        """Returns settings dictionary from an .json file.

        Args:
            file_path (str): path to configparser-compatible .json file.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a file.

        """
        if 'infer_types' not in kwargs:
            kwargs['infer_types'] = True
        try:
            with open(pathlib.Path(file_path)) as settings_file:
                contents = json.load(settings_file)
            return cls(contents = contents, **kwargs)
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')

    @classmethod
    def from_py(cls, 
        file_path: Union[str, pathlib.Path], 
        **kwargs) -> Configuration:
        """Returns a settings dictionary from a .py file.

        Args:
            file_path (str): path to python module with '__dict__' dict
                defined.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a
                file.

        """
        if 'infer_types' not in kwargs:
            kwargs['infer_types'] = False
        try:
            file_path = pathlib.Path(file_path)
            import_path = importlib.util.spec_from_file_location(
                file_path.name,
                file_path)
            import_module = importlib.util.module_from_spec(import_path)
            import_path.loader.exec_module(import_module)
            return cls(contents = import_module.configuration, **kwargs)
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')

    @classmethod
    def from_toml(cls, 
        file_path: Union[str, pathlib.Path], 
        **kwargs) -> Configuration:
        """Returns settings dictionary from a .toml file.

        Args:
            file_path (str): path to configparser-compatible .toml file.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a file.

        """
        import toml
        if 'infer_types' not in kwargs:
            kwargs['infer_types'] = True
        try:
            return cls(contents = toml.load(file_path), **kwargs)
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')
   
    @classmethod
    def from_yaml(cls, 
        file_path: Union[str, pathlib.Path], 
        **kwargs) -> Configuration:
        """Returns settings dictionary from a .yaml file.

        Args:
            file_path (str): path to configparser-compatible .toml file.

        Returns:
            Mapping[Any, Any] of contents.

        Raises:
            FileNotFoundError: if the file_path does not correspond to a file.

        """
        import yaml
        if 'infer_types' not in kwargs:
            kwargs['infer_types'] = False
        try:
            with open(file_path, 'r') as config:
                return cls(contents = yaml.safe_load(config, **kwargs))
        except FileNotFoundError:
            raise FileNotFoundError(f'settings file {file_path} not found')
        

    """ Public Methods """

    def add(self, section: str, contents: Mapping[str, Any]) -> None:
        """Adds 'settings' to 'contents'.

        Args:
            section (str): name of section to add 'contents' to.
            contents (Mapping[str, Any]): a dict to store in 'section'.

        """
        try:
            self[section].update(contents)
        except KeyError:
            self[section] = contents
        return self

    def inject(self, instance: object,
               additional: Union[Sequence[str], str] = None, 
               overwrite: bool = False) -> object:
        """Injects appropriate items into 'instance' from 'contents'.

        Args:
            instance (object): amicus class instance to be modified.
            additional (Union[Sequence[str], str]]): other section(s) in 
                'contents' to inject into 'instance'. Defaults to None.
            overwrite (bool]): whether to overwrite a local attribute in 
                'instance' if there are values stored in that attribute. 
                Defaults to False.

        Returns:
            instance (object): amicus class instance with modifications made.

        """
        sections = ['general']
        try:
            sections.append(instance.name)
        except AttributeError:
            pass
        if additional:
            sections.extend(more_itertools.always_iterable(additional))
        for section in sections:
            try:
                for key, value in self.contents[section].items():
                    if (not hasattr(instance, key)
                            or not getattr(instance, key)
                            or overwrite):
                        setattr(instance, key, value)
            except KeyError:
                pass
        return instance

    """ Private Methods """

    def _infer_types(self,
        contents: Mapping[str, Mapping[str, Any]]) -> Mapping[
            str, Mapping[str, Any]]:
        """Converts stored values to appropriate datatypes.

        Args:
            contents (Mapping[str, Mapping[str, Any]]): a nested contents dict
                to review.

        Returns:
            Mapping[str, Mapping[str, Any]]: with the nested values converted to 
                the appropriate datatypes.

        """
        new_contents = {}
        for key, value in contents.items():
            if isinstance(value, dict):
                inner_bundle = {
                    inner_key: amicus.tools.typify(inner_value)
                    for inner_key, inner_value in value.items()}
                new_contents[key] = inner_bundle
            else:
                new_contents[key] = amicus.tools.typify(value)
        return new_contents

    def _add_standard(self, 
        contents: Mapping[str, Mapping[str, Any]]) -> (
            Mapping[str, Mapping[str, Any]]):
        """Creates a backup set of mappings for amicus settings lookup.


        Args:
            contents (MutableMapping[Any, Mapping[Any, Any]]): a nested contents 
                dict to add standard to.

        Returns:
            Mapping[Any, Mapping[Any, Any]]: with stored standard added.

        """
        new_contents = self.standard
        new_contents.update(contents)
        return new_contents

    """ Dunder Methods """

    def __setitem__(self, key: str, value: Mapping[str, Any]) -> None:
        """Creates new key/value pair(s) in a section of the active dictionary.

        Args:
            key (str): name of a section in the active dictionary.
            value (Mapping[str, Any]): the dictionary to be placed in that 
                section.

        Raises:
            TypeError if 'key' isn't a str or 'value' isn't a dict.

        """
        try:
            self.contents[key].update(value)
        except KeyError:
            try:
                self.contents[key] = value
            except TypeError:
                raise TypeError(
                    'key must be a str and value must be a dict type')
        return self


@dataclasses.dataclass
class Clerk(object):
    """File and folder management for amicus.

    Creates and stores dynamic and static file paths, properly formats files
    for import and export, and provides methods for loading and saving
    amicus, pandas, and numpy objects.

    Args:
        settings (Configuration): a Configuration instance, preferably with a section 
            named 'filer' or 'files' with file-management related settings. If 
            'settings' does not have file configuration options or if 'settings' 
            is None, internal defaults will be used. Defaults to None.
        root_folder (Union[str, pathlib.Path]): the complete path from which the 
            other paths and folders used by Clerk are ordinarily derived 
            (unless you decide to use full paths for all other options). 
            Defaults to None. If not passed, the parent folder of the current 
            working workery is used.
        input_folder (Union[str, pathlib.Path]]): the input_folder subfolder 
            name or a complete path if the 'input_folder' is not off of
            'root_folder'. Defaults to 'input'.
        output_folder (Union[str, pathlib.Path]]): the output_folder subfolder
            name or a complete path if the 'output_folder' is not off of
            'root_folder'. Defaults to 'output'.

    ToDo:
        Refactor and amicus with accompanying classes.

    """
    settings: Configuration = None
    root_folder: Union[str, pathlib.Path] = None
    input_folder: Union[str, pathlib.Path] = 'input'
    output_folder: Union[str, pathlib.Path] = 'output'
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Attempots to Inject attributes from 'settings'.
        try:
            self.settings.inject(
                instance = self, 
                additional = ['files', 'filer'])
        except (AttributeError, TypeError):
            pass
        # Validates core folder paths and writes them to disk.
        self.root_folder = self.root_folder or pathlib.Path('..')
        self.root_folder = self.validate(path = self.root_folder)
        self.input_folder = self._validate_io_folder(path = self.input_folder)
        self.output_folder = self._validate_io_folder(path = self.output_folder)
        # Sets default file formats in a dictionary of FileFormat instances.
        self.file_formats = self._get_default_file_formats()
        # Gets default parameters for file transfers from 'settings'.
        self.default_parameters = self._get_default_parameters(
            settings = self.settings)
        # Creates FileImporter and FileSaver instances for loading and saving
        # files.
        self.loader = FileImporter(filer = self)
        self.saver = FileSaver(filer = self)
        return self

    """ Public Methods """
    
    def validate(self, 
        path: Union[str, pathlib.Path],
        test: bool = True,
        create: bool = True) -> pathlib.Path:
        """Turns 'file_path' into a pathlib.Path.

        Args:
            path (Union[str, pathlib.Path]): str or Path to be validated. If
                a str is passed, the method will see if an attribute matching
                'path' exists and if that attribute contains a Path.
            test (bool): whether to test if the path exists. Defaults to True.
            create (bool): whether to create the folder path if 'test' is True,
                but the folder does not exist. Defaults to True.

        Raises:
            TypeError: if 'path' is neither a str nor Path.
            FileNotFoundError: if the validated path does not exist and 'create'
                is False.

        Returns:
            pathlib.Path: derived from 'path'.

        """
        if isinstance(path, str):
            if (hasattr(self, path) 
                    and isinstance(getattr(self, path), pathlib.Path)):
                validated = getattr(self, path)
            else:
                validated = pathlib.Path(path)
        elif isinstance(path, pathlib.Path):
            validated = path
        else:
            raise TypeError(f'path must be a str or Path type')
        if test and not validated.exists():
            if create:
                self._write_folder(folder = validated)
            else:
                raise FileNotFoundError(f'{validated} does not exist')
        return validated
        
    def load(self,
            file_path: Union[str, pathlib.Path] = None,
            folder: Union[str, pathlib.Path] = None,
            file_name: str = None,
            file_format: Union[str, 'FileFormat'] = None,
            **kwargs) -> Any:
        """Imports file by calling appropriate method based on file_format.

        If needed arguments are not passed, default values are used. If
        'file_path' is passed, 'folder' and 'file_name' are ignored.

        Args:
            file_path (Union[str, Path]]): a complete file path.
                Defaults to None.
            folder (Union[str, Path]]): a complete folder path or the
                name of a folder stored in 'filer'. Defaults to None.
            file_name (str): file name without extension. Defaults to
                None.
            file_format (Union[str, FileFormat]]): object with
                information about how the file should be loaded or the key to
                such an object stored in 'filer'. Defaults to None
            **kwargs: can be passed if additional options are desired specific
                to the pandas or python method used internally.

        Returns:
            Any: depending upon method used for appropriate file format, a new
                variable of a supported type is returned.

        """
        return self.loader.transfer(
            file_path = file_path,
            folder = folder,
            file_name = file_name,
            file_format = file_format,
            **kwargs)

    def save(self,
            variable: Any,
            file_path: Union[str, pathlib.Path] = None,
            folder: Union[str, pathlib.Path] = None,
            file_name: str = None,
            file_format: Union[str, 'FileFormat'] = None,
            **kwargs) -> None:
        """Exports file by calling appropriate method based on file_format.

        If needed arguments are not passed, default values are used. If
        file_path is passed, folder and file_name are ignored.

        Args:
            variable (Any): object to be save to disk.
            file_path (Union[str, pathlib.Path]]): a complete file path.
                Defaults to None.
            folder (Union[str, pathlib.Path]]): a complete folder path or the
                name of a folder stored in 'filer'. Defaults to None.
            file_name (str): file name without extension. Defaults to
                None.
            file_format (Union[str, 'FileFormat']]): object with
                information about how the file should be loaded or the key to
                such an object stored in 'filer'. Defaults to None
            **kwargs: can be passed if additional options are desired specific
                to the pandas or python method used internally.

        """
        self.saver.transfer(
            variable = variable,
            file_path = file_path,
            folder = folder,
            file_name = file_name,
            file_format = file_format,
            **kwargs)
        return self

    def pathlibify(self,
            folder: str,
            file_name: str = None,
            extension: str = None) -> pathlib.Path:
        """Converts strings to pathlib Path object.

        If 'folder' matches an attribute, the value stored in that attribute
        is substituted for 'folder'.

        If 'name' and 'extension' are passed, a file path is created. Otherwise,
        a folder path is created.

        Args:
            folder (str): folder for file location.
            name (str): the name of the file.
            extension (str): the extension of the file.

        Returns:
            Path: formed from string arguments.

        """
        try:
            folder = getattr(self, folder)
        except (AttributeError, TypeError):
            pass
        if file_name and extension:
            return pathlib.Path(folder).joinpath(f'{file_name}.{extension}')
        else:
            return pathlib.Path(folder)

    """ Private Methods """

    def _validate_io_folder(self, 
            path: Union[str, pathlib.Path]) -> pathlib.Path:
        """[summary]

        Args:
            path (Union[str, pathlib.Path]): [description]

        Returns:
            [type]: [description]
            
        """
        try:
            return self.validate(path = path, create = False)
        except FileNotFoundError:
            return self.validate(path = self.root_folder / path)
                
    def _get_default_file_formats(self) -> Mapping[Any, 'FileFormat']:
        """Returns supported file formats.

        Returns:
            Mapping: with string keys and FileFormat instances as values.

        """
        return {
            'csv': FileFormat(
                name = 'csv',
                modules =  'pandas',
                extension = '.csv',
                load_method = 'read_csv',
                save_method = 'to_csv',
                shared_parameters = {
                    'encoding': 'file_encoding',
                    'index_col': 'index_column',
                    'header': 'include_header',
                    'usecols': 'included_columns',
                    'low_memory': 'conserve_memory',
                    'nrows': 'test_size'}),
            'excel': FileFormat(
                name = 'excel',
                modules =  'pandas',
                extension = '.xlsx',
                load_method = 'read_excel',
                save_method = 'to_excel',
                shared_parameters = {
                    'index_col': 'index_column',
                    'header': 'include_header',
                    'usecols': 'included_columns',
                    'nrows': 'test_size'}),
            'feather': FileFormat(
                name = 'feather',
                modules =  'pandas',
                extension = '.feather',
                load_method = 'read_feather',
                save_method = 'to_feather',
                required_parameters = {'nthreads': -1}),
            'hdf': FileFormat(
                name = 'hdf',
                modules =  'pandas',
                extension = '.hdf',
                load_method = 'read_hdf',
                save_method = 'to_hdf',
                shared_parameters = {
                    'columns': 'included_columns',
                    'chunksize': 'test_size'}),
            'json': FileFormat(
                name = 'json',
                modules =  'pandas',
                extension = '.json',
                load_method = 'read_json',
                save_method = 'to_json',
                shared_parameters = {
                    'encoding': 'file_encoding',
                    'columns': 'included_columns',
                    'chunksize': 'test_size'}),
            'stata': FileFormat(
                name = 'stata',
                modules =  'pandas',
                extension = '.dta',
                load_method = 'read_stata',
                save_method = 'to_stata',
                shared_parameters = {'chunksize': 'test_size'}),
            'text': FileFormat(
                name = 'text',
                modules =  None,
                extension = '.txt',
                load_method = '_import_text',
                save_method = '_export_text'),
            'png': FileFormat(
                name = 'png',
                modules =  'seaborn',
                extension = '.png',
                save_method = 'save_fig',
                required_parameters = {
                    'bbox_inches': 'tight', 
                    'format': 'png'}),
            'pickle': FileFormat(
                name = 'pickle',
                modules =  None,
                extension = '.pickle',
                load_method = '_pickle_object',
                save_method = '_unpickle_object')}

    def _get_default_parameters(self, 
                                settings: Configuration) -> Mapping[Any, Any]:
        """Returns default parameters for file transfers from 'settings'.

        Args:
            settings (Configuration): an instance with a section named 'files' which
                contains default parameters for file transfers.

        Returns:
            Mapping: with default parameters from settings.

        """
        return self.settings['files']

    def _write_folder(self, folder: Union[str, pathlib.Path]) -> None:
        """Writes folder to disk.

        Parent folders are created as needed.

        Args:
            folder (Union[str, Path]): intended folder to write to disk.

        """
        pathlib.Path.mkdir(folder, parents = True, exist_ok = True)
        return self

    def _make_unique_path(self,
            folder: Union[pathlib.Path, str],
            name: str) -> pathlib.Path:
        """Creates a unique path to avoid overwriting a file or folder.

        Thanks to RealPython for this bit of code:
        https://realpython.com/python-pathlib/.

        Args:
            folder (Path): the folder where the file or folder will be located.
            name (str): the basic name that should be used.

        Returns:
            Path: with a unique name. If the original name conflicts with an
                existing file/folder, a counter is used to find a unique name
                with the counter appended as a suffix to the original name.

        """
        counter = 0
        while True:
            counter += 1
            path = pathlib.Path(folder) / name.format(counter)
            if not path.exists():
                return path


@dataclasses.dataclass
class Distributor(abc.ABC):
    """Keystone class for amicus FileImporter and FileSaver.

    Args:
        filer (Clerk): a related Clerk instance.

    """

    filer: Clerk

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""

        return self

    """ Private Methods """

    def _check_required_parameters(self,
            file_format: FileFormat,
            passed_kwargs: Mapping[Any, Any]) -> Mapping[Any, Any]:
        """Adds requited parameters if not passed.

        Args:
            file_format (FileFormat): an instance with information about
                additional kwargs to search for.
            passed_kwargs (MutableMapping[Any, Any]): kwargs passed to method.

        Returns:
            Mapping[Any, Any]: kwargs with only relevant parameters.

        """
        new_kwargs = passed_kwargs
        if file_format.required_parameters:
            for key, value in file_format.required_parameters:
                if value not in new_kwargs:
                    new_kwargs[key] = value
        return new_kwargs

    def _check_shared_parameters(self,
            file_format: FileFormat,
            passed_kwargs: Mapping[Any, Any]) -> Mapping[Any, Any]:
        """Selects kwargs for particular methods.

        If a needed argument was not passed, default values are used.

        Args:
            file_format (FileFormat): an instance with information about
                additional kwargs to search for.
            passed_kwargs (MutableMapping[Any, Any]): kwargs passed to method.

        Returns:
            Mapping[Any, Any]: kwargs with only relevant parameters.

        """
        new_kwargs = passed_kwargs
        if file_format.shared_parameters:
            for key, value in file_format.shared_parameters:
                if (value not in new_kwargs
                        and value in self.filer.default_parameters):
                    new_kwargs[key] = self.filer.default_parameters[value]
        return new_kwargs

    def _check_file_format(self,
            file_format: Union[str, 'FileFormat']) -> 'FileFormat':
        """Selects 'file_format' or returns FileFormat instance intact.

        Args:
            file_format (Union[str, FileFormat]): name of file format or a
                FileFormat instance.

        Raises:
            TypeError: if 'file_format' is neither a str nor FileFormat type.

        Returns:
            FileFormat: appropriate instance.

        """
        if isinstance(file_format, FileFormat):
            return file_format
        elif isinstance(file_format, str):
            return self.filer.file_formats[file_format]
        else:
            raise TypeError('file_format must be a str or FileFormat type')

    def _get_parameters(self,
            file_format: FileFormat,
            **kwargs) -> Mapping[Any, Any]:
        """Creates complete parameters for a file input/output method.

        Args:
            file_format (FileFormat): an instance with information about the
                needed and optional parameters.
            kwargs: additional parameters to pass to an input/output method.

        Returns:
            Mapping[Any, Any]: parameters to be passed to an input/output 
                method.

        """
        parameters = self._check_required_parameters(
            file_format = file_format,
            passed_kwargs = kwargs)
        parameters = self._check_shared_parameters(
            file_format = file_format,
            passed_kwargs = kwargs)
        return parameters

    def _prepare_transfer(self,
            file_path: Union[str, pathlib.Path],
            folder: Union[str, pathlib.Path],
            file_name: str,
            file_format: Union[str, 'FileFormat']) -> Sequence[Union[
                pathlib.Path,
                'FileFormat']]:
        """Prepares file path related arguments for loading or saving a file.

        Args:
            file_path (Union[str, Path]): a complete file path.
            folder (Union[str, Path]): a complete folder path or the name of a
                folder stored in 'filer'.
            file_name (str): file name without extension.
            file_format (Union[str, FileFormat]): object with information about
                how the file should be loaded or the key to such an object
                stored in 'filer'.
            **kwargs: can be passed if additional options are desired specific
                to the pandas or python method used internally.

        Returns:
            Sequence: of a completed Path instance and FileFormat instance.

        """
        if file_path:
            file_path = pathlib.Path(file_path)
            if not file_format:
                file_format = [
                    f for f in self.filer.file_formats.values()
                    if f.extension == file_path.suffix[1:]][0]
        file_format = self._check_file_format(file_format = file_format)
        extension = file_format.extension
        if not file_path:
            file_path = self.filer.pathlibify(
                folder = folder,
                file_name = file_name,
                extension = extension)
        return file_path, file_format


@dataclasses.dataclass
class FileImporter(Distributor):
    """Manages file importing for amicus.

    Args:
        filer (Clerk): related Clerk instance.

    """
    filer: Clerk

    """ Public Methods """

    def load(self, **kwargs):
        """Calls 'transfer' method with **kwergs."""
        return self.transfer(**kwargs)

    def transfer(self,
            file_path: Union[str, pathlib.Path] = None,
            folder: Union[str, pathlib.Path] = None,
            file_name: str = None,
            file_format: Union[str, 'FileFormat'] = None,
            **kwargs) -> Any:
        """Imports file by calling appropriate method based on file_format.

        If needed arguments are not passed, default values are used. If
        file_path is passed, folder and file_name are ignored.

        Args:
            file_path (Union[str, Path]]): a complete file path.
                Defaults to None.
            folder (Union[str, Path]]): a complete folder path or the
                name of a folder stored in 'filer'. Defaults to None.
            file_name (str): file name without extension. Defaults to
                None.
            file_format (Union[str, FileFormat]]): object with
                information about how the file should be loaded or the key to
                such an object stored in 'filer'. Defaults to None
            **kwargs: can be passed if additional options are desired specific
                to the pandas or python method used internally.

        Returns:
            Any: depending upon method used for appropriate file format, a new
                variable of a supported type is returned.

        """
        file_path, file_format = self._prepare_transfer(
            file_path = file_path,
            folder = folder,
            file_name = file_name,
            file_format = file_format)
        parameters = self._get_parameters(file_format = file_format, **kwargs)
        if file_format.module:
            tool = file_format.load('import_method')
        else:
            tool = getattr(self, file_format.import_method)
        return tool(file_path, **parameters)


@dataclasses.dataclass
class FileSaver(Distributor):
    """Manages file exporting for amicus.

    Args:
        filer (Clerk): related Clerk instance.

    """
    filer: Clerk

    """ Public Methods """

    def save(self, **kwargs):
        """Calls 'transfer' method with **kwargs."""
        return self.transfer(**kwargs)

    """ Keystone amicus Methods """

    def transfer(self,
            variable: Any,
            file_path: Union[str, pathlib.Path] = None,
            folder: Union[str, pathlib.Path] = None,
            file_name: str = None,
            file_format: Union[str, 'FileFormat'] = None,
            **kwargs) -> None:
        """Exports file by calling appropriate method based on file_format.

        If needed arguments are not passed, default values are used. If
        file_path is passed, folder and file_name are ignored.

        Args:
            variable (Any): object to be save to disk.
            file_path (Union[str, Path]]): a complete file path.
                Defaults to None.
            folder (Union[str, Path]]): a complete folder path or the
                name of a folder stored in 'filer'. Defaults to None.
            file_name (str): file name without extension. Defaults to
                None.
            file_format (Union[str, FileFormat]]): object with
                information about how the file should be loaded or the key to
                such an object stored in 'filer'. Defaults to None
            **kwargs: can be passed if additional options are desired specific
                to the pandas or python method used internally.

        """
        file_path, file_format = self._prepare_transfer(
            file_path = file_path,
            folder = folder,
            file_name = file_name,
            file_format = file_format)
        parameters = self._get_parameters(file_format = file_format, **kwargs)
        if file_format.module:
            getattr(variable, file_format.export_method)(variable, **parameters)
        else:
            getattr(self, file_format.export_method)(variable, **parameters)
        return self


@dataclasses.dataclass
class FileFormat(object):
    """File format information.

    Args:
        name (str): designates the name of the class instance used
            for internal referencing throughout amicus. If the class instance
            needs settings from the shared Configuration instance, 'name' should
            match the appropriate section name in that Configuration instance. When
            subclassing, it is a good settings to use the same 'name' attribute
            as the base class for effective coordination between amicus
            classes. Defaults to None or __class__.__name__.lower().
        module (str): name of module where object to incorporate is located
            (can either be an amicus or non-amicus module).
        extension (str): actual file extension to use. Defaults to
            None.
        load_method (str): name of import method in 'module' to
            use. If module is None, the Distributor looks for the method
            as a local attribute. Defaults to None.
        save_method (str): name of export method in 'module' to
            use. If module is None, the Distributor looks for the method
            as a local attribute. Defaults to None.
        shared_parameters (Sequence[str]]): names of commonly used kwargs
            for either the import or export method. Defaults to None.
        required_parameters (Mapping[Any, Any]]): any required parameters
            that should be passed to the import or export methods. Defaults to
            None.

    """

    name: str = None
    modules: str = 'amicus'
    _loaded: Mapping[Any, Any] = dataclasses.field(
        default_factory = dict)
    extension: str = None
    load_method: str = None
    save_method: str = None
    shared_parameters: Sequence[str] = None
    required_parameters: Mapping[Any, Any] = None
    