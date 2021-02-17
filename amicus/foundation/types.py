"""
types: amicus base types
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

All amicus types have a 'contents' attribute where an item or 'items' are
internally stored. This is used instead of the normal 'data' attribute use in
base python classes to make it easier for users to know which object they are
accessing when using either 'contents' or 'data'.

Contents:
    Proxy (collections.abc.Container): basic wrapper for a stored static or
        iterable item. Dunder methods attempt to intelligently apply access
        methods to either the wrapper or the wrapped item.
    Bunch (Iterable, ABC): abstract base class for amicus iterables. All 
        subclasses must have an 'add' method as well as store their contents in 
        the 'contents' attribute.
    Progression (MutableSequence, Bunch): amicus drop-in replacement for 
        list with additional functionality.
    Hybrid (Progression): iterable with both dict and list interfaces and 
        methods that stores items with a 'name' attribute.
    Lexicon (MutableMapping, Bunch): amicus's drop-in replacement for 
        python dicts with some added functionality.
    Catalog (Lexicon): wildcard-accepting dict which is primarily intended for 
        storing different options and strategies. It also returns lists of 
        matches if a list of keys is provided.
    Library (Lexicon): a dict that adds dot notation access for first level keys
        and includes a 'deposit' method which returns an error if the user
        passes a key that already exists in the stored dict.

"""
from __future__ import annotations
import abc
import collections.abc
import dataclasses
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Mapping, 
                    Optional, Sequence, Tuple, Type, Union)

import more_itertools


@dataclasses.dataclass
class Proxy(collections.abc.Container):
    """Container for holding single items.
    
    A Proxy differs than an ordinary container in 2 significant ways:
        1) When an 'in' call is made, the '__contains__' method first looks to
            see if the item is stored in 'contents' (if 'contents' is a 
            collection). If that check gets a TypeError, the method then checks
            if the item is equivalent to 'contents'. This allows a Proxy to be
            agnostic as to the type of item(s) in 'contents' while returning the
            expected result from an 'in' call.
        2) Access methods for getting, setting, and deleting try to 
            intelligently direct the user's call to the proxy or stored class.
            So, for example, when a user tries to set an attribute on the proxy,
            the method will replace an attribute that exists in the proxy if
            one exists. But if there is no such attribute, the set method is
            applied to 'contents'.

    Args:
        contents (Any): any stored item(s). Defaults to None.
        
    ToDo:
        Add more dunder methods to address less common and fringe cases for use
            of a Proxy class.
        
    """
    contents: Any = None

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance.
        
        Although this method ordinarily does nothing, it makes the order of the
        inherited classes less important with multiple inheritance, such as when 
        adding amicus quirks. 
        
        """
        # Calls parent initialization methods, if they exist.
        try:
            super().__post_init__()
        except AttributeError:
            pass
    
    """ Dunder Methods """
       
    def __contains__(self, item: Any) -> bool:
        """Returns whether 'item' is in or equal to 'contents'.

        Args:
            item (Any): item to check versus 'contents'
            
        Returns:
            bool: if 'item' is in or equal to 'contents' (True). Otherwise, it
                returns False.

        """
        try:
            return item in self.contents
        except TypeError:
            return item == self.contents

    def __getattr__(self, attribute: str) -> Any:
        """Looks for 'attribute' in 'contents'.

        Args:
            attribute (str): name of attribute to return.

        Raises:
            AttributeError: if 'attribute' is not found in 'contents'.

        Returns:
            Any: matching attribute.

        """
        try:
            return object.__getattr___(self.contents, attribute)
        except AttributeError:
            raise AttributeError(f'{attribute} is not in {self.__name__}') 

    def __setattr__(self, attribute: str, value: Any):
        """Sets 'attribute' to 'value'.
        
        If 'attribute' exists in this class instance, its new value is set to
        'value.' Otherwise, 'attribute' and 'value' are set in what is stored
        in 'contents'

        Args:
            attribute (str): name of attribute to set.
            value (Any): value to store in 'attribute'.

        """
        if hasattr(self, attribute):
            object.__setattr__(self, attribute, value)
        else:
            object.__setattr__(self.contents, attribute, value)

    def __delattr__(self, attribute: str):
        """Deletes 'attribute'.
        
        If 'attribute' exists in this class instance, it is deleted. Otherwise, 
        this method attempts to delete 'attribute' from what is stored in 
        'contents'

        Args:
            attribute (str): name of attribute to set.
            value (Any): value to store in 'attribute'.

        Raises:
            AttributeError: if 'attribute' is neither found in a class instance
                nor in 'contents'.
            
        """
        try:
            object.__delattr__(self, attribute)
        except AttributeError:
            try:
                object.__delattr__(self.contents, attribute)
            except AttributeError:
                raise AttributeError(f'{attribute} is not in {self.__name__}') 
                        
  
@dataclasses.dataclass
class Bunch(collections.abc.Iterable, abc.ABC):
    """Abstract base class for amicus iterables.
  
    A Bunch differs from a general python iterable in 3 ways:
        1) It must include an 'add' method which provides the default mechanism
            for adding new items to the iterable. All of the other appropriate
            methods for adding to a python iterable ('append', 'extend', 
            'update', etc.) remain, but 'add' allows a subclass to designate the
            preferred method of adding to the iterable's stored data.
        2) It allows the '+' operator to be used to join a Bunch subclass 
            instance of the same general type (Mapping, Sequence, Tuple, etc.). 
            The '+' operator calls the Bunch subclass 'add' method to implement 
            how the added item(s) is/are added to the Bunch subclass instance.
        3) The internally stored iterable is located in the 'contents' 
            attribute. This allows for consistent coordination among classes and
            mixins.
    
    Args:
        contents (Iterable[Any]): stored iterable. Defaults to None.
              
    """
    contents: Iterable[Any] = None
   
    """ Required Subclass Methods """
    
    def add(self, item: Any) -> None:
        """Adds 'item' to 'contents' in the default manner.
        
        Subclasses must provide their own methods.
        
        """
        raise NotImplementedError(
            f'{__name__} is not implemented for a {self.name} structure')
    
    """ Dunder Methods """

    def __add__(self, other: Any) -> None:
        """Combines argument with 'contents' using the 'add' method.

        Args:
            other (Any): item to add to 'contents' using the 'add' method.

        """
        self.add(other)
        return self

    def __iadd__(self, other: Any) -> None:
        """Combines argument with 'contents' using the 'add' method.

        Args:
            other (Any): item to add to 'contents' using the 'add' method.

        """
        self.add(other)
        return self

    def __iter__(self) -> Iterable[Any]:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: of 'contents'.

        """
        return iter(self.contents)


@dataclasses.dataclass
class Progression(Bunch, collections.abc.MutableSequence):
    """Basic amicus list replacement.
    
    A Progression differs from an ordinary python list only in ways inherited
    from Bunch ('add' method, storage of data in 'contents', and allowing the
    '+' operator to join Progressions with other lists and Progressions).
    
    The 'add' method attempts to extend 'contents' with the item to be added.
    If this fails, it appends the item to 'contents'.
            
    Args:
        contents (Sequence[Any]): items to store in a list. Defaults to an empty 
            list.
        
    """
    contents: Sequence[Any] = dataclasses.field(default_factory = list)

    """ Public Methods """

    def add(self, item: Sequence[Any], **kwargs) -> None:
        """Tries to extend 'contents' with 'item'. Otherwise, appends.

        Args:
            item (Sequence[Any]): items to add to the 'contents' attribute.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.
                
        """
        if isinstance(item, Iterable) and not isinstance(item, str):
            self.contents.extend(item)
        else:
            self.contents.append(item)
        return self  

    def insert(self, index: int, item: Any) -> None:
        """Inserts 'item' at 'index' in 'contents'.

        Args:
            index (int): index to insert 'item' at.
            item (Any): object to be inserted.
            
        """
        self.contents.insert(index, item)
        return self
                        
    """ Dunder Methods """

    def __getitem__(self, key: int) -> Any:
        """Returns value(s) for 'key' in 'contents'.

        Args:
            key (int): index to search for in 'contents'.

        Returns:
            Any: item stored in 'contents' at key.

        """
        return self.contents[key]
            
    def __setitem__(self, key: int, value: Any) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (int): index to set 'value' to in 'contents'.
            value (Any): value to be set at 'key' in 'contents'.

        """
        self.contents[key] = value

    def __delitem__(self, key: Union[Any, int]) -> None:
        """Deletes item at 'key' index in 'contents'.

        Args:
            key (int): index in 'contents' to delete.

        """
        del self.contents[key]

    def __iter__(self) -> Iterable[Any]:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: of 'contents'.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of iterable of 'contents'.

        Returns:
            int: length of iterable of 'contents'.

        """
        return len(self.contents)
    
   
@dataclasses.dataclass
class Hybrid(Progression):
    """Core class for ordered iterables in amicus composite objects.
    
    Hybrid combines the functionality and interfaces of python dicts and lists.
    It allows duplicate keys and list-like iteration while supporting the easier
    access methods of dictionaries. In order to support this hybrid approach to
    iterables, Hybrid can only store items with a 'name' attribute or property.
    
    Hybrid is the primary iterable base class used in amicus composite objects.
    
    A Hybrid inherits the differences between a Progression and an ordinary 
    python list.
    
    A Hybrid differs from a Progression in 3 significant ways:
        1) It only store items with 'name' attributes or properties.
        2) Hybrid has an interface of both a dict and a list, but stores a list. 
            Hybrid does this by taking advantage of the 'name' attribute of 
            stored items. A 'name' acts as a key to create the facade of a dict
            with the items in the stored list serving as values. This allows for 
            duplicate keys for storing class instances, easier iteration, and 
            returning multiple matching items. This design comes at the expense 
            of lookup speed. As a result, Hybrid should only be used if a high 
            volume of access calls is not anticipated. Ordinarily, the loss of 
            lookup speed should have negligible effect on overall performance.
        3) It includes "excludify" and "subsetify" methods which return new
            instances with a subset of 'contents' based upon the 'subset'
            argument passed to the method. 'excludify' returns all 'contents'
            that do not have names matching items in the 'subset' argument.
            'subsetify' returns all 'contents' that have names matching items
            in the 'subset' argument.

    Args:
        contents (Sequence[Any]): items with 'name' attributes to store. If a 
            dict is passed, the keys will be ignored and only the values will be 
            added to 'contents'. If a single item is passed, it will be placed 
            in a list. Defaults to an empty list.
            
    """
    contents: Sequence[Any] = dataclasses.field(default_factory = list)
    default: Any = None
        
    """ Public Methods """

    def append(self, item: List[Any]) -> None:
        """Appends 'item' to 'contents'.
        
        Args:
            items (List[Any]): items to append to 'contents'.

        """
        self.contents.append(item)
        return self    

    def clear(self) -> None:
        """Removes all items from 'contents'."""
        self.contents = []
        return self

    def excludify(self, 
        subset: Union[Any, Sequence[Any]], 
        **kwargs) -> Hybrid[Any]:
        """Returns a new instance without a subset of 'contents'.

        Args:
            subset (Union[Any, Sequence[Any]]): name(s) for which items from 
                'contents' should not be returned.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.

        Returns:
            Hybrid: with items without names in 'subset'.

        """
        subset = more_itertools.always_iterable(subset)
        contents = [c for c in self.contents if not c.name in subset]
        return self.__class__(contents = contents)  
           
    def extend(self, item: Any) -> None:
        """Extends 'items' to 'contents'.
        
        Args:
            items (Any): instance(s) to add to the 'contents' attribute.

        Raises:
            TypeError: if 'item' does not have a name attribute.
            
        """
        self.contents.extend(item)
        return self  

    def get(self, key: Union[Any, int]) -> Union[Any, Sequence[Any]]:
        """Returns value(s) in 'contents' or value in 'default' attribute.
        
        Args:
            key (Union[Any, int]): index or key for value in 'contents'.
                
        Returns:
            Union[Any, Sequence[Any]]: items in 'contents' or value in 'default' 
                attribute. 
        """
        try:
            return self[key]
        except KeyError:
            return self.default

    def items(self) -> Iterable:
        """Emulates python dict 'items' method.
        
        Returns:
            Iterable: tuple of Any names and Anys.
            
        """
        return tuple(zip(self.keys(), self.values()))

    def keys(self) -> Sequence[Any]:
        """Emulates python dict 'keys' method.
        
        Returns:
            Sequence[Any]: list of names of stored in 'contents'
            
        """
        return tuple([c.name for c in self.contents])

    def pop(self, key: Union[Any, int]) -> Union[Any, Sequence[Any]]:
        """Pops item(s) from 'contents'.

        Args:
            key (Union[Any, int]): index or key for value in 'contents'.
                
        Returns:
            Union[Any, Sequence[Any]]: item(s) popped from 'contents'.
            
        """
        popped = self[key]
        del self[key]
        return popped
        
    def remove(self, key: Union[Any, int]) -> None:
        """Removes item(s) from 'contents'.

        Args:
            key (Union[Any, int]): index or key for value in 'contents'.
            
        """
        del self[key]
        return self
     
    def setdefault(self, value: Any) -> None:
        """Sets default value to return when 'get' method is used.
        
        Args:
            value (Any): default value to return.
            
        """
        self.default = value 
            
    def subsetify(self, 
        subset: Union[Any, Sequence[Any]], 
        **kwargs) -> Hybrid[Any]:
        """Returns a new instance with a subset of 'contents'.

        Args:
            subset (Union[Any, Sequence[Any]]): name(s) for which items from 
                'contents' should be returned.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.

        Returns:
            Hybrid: with items with names in 'subset'.

        """
        subset = more_itertools.always_iterable(subset)
        return self.__class__(
            contents = [c for c in self.contents if c.name in subset])     
     
    def update(self, items: Any) -> None:
        """Mimics the dict 'update' method by appending 'items'.
        
        Args:
            items (Any): Any items to add to the 'contents' attribute. If a 
                Mapping is passed, the values are added to 'contents' and the 
                keys become the 'name' attributes of those values. To mimic 
                'update', the passed 'items' are added to 'contents' by the 
                'append' method.           
        
        """
        if isinstance(items, Mapping):
            for key, value in items.items():
                new_item = value
                new_item.name = key
                self.append(item = new_item)
        else:
            self.append(item = items)
        return self

    def values(self) -> Sequence[Any]:
        """Emulates python dict 'values' method.
        
        Returns:
            Sequence[Any]: list of items stored in 'contents'
            
        """
        return tuple(self.contents)
          
    """ Dunder Methods """

    def __getitem__(self, key: Union[Any, int]) -> Any:
        """Returns value(s) for 'key' in 'contents'.
        
        If 'key' is not an int type, this method looks for a matching 'name'
        attribute in the stored instances.
        
        If 'key' is an int type, this method returns the stored item at the
        corresponding index.
        
        If only one match is found, a single item is returned. If more are 
        found, a Hybrid or Hybrid subclass with the matching 'name' attributes 
        is returned.

        Args:
            key (Union[Any, int]): key or index to search for in 'contents'.

        Returns:
            Any: value(s) stored in 'contents' that correspond to 'key'. If 
                there is more than one match, the return is a Hybrid or Hybrid 
                subclass with that matching stored items.

        """
        if isinstance(key, int):
            return self.contents[key]
        else:
            matches = [c for c in self.contents if c.name == key]
            if len(matches) == 0:
                raise KeyError(f'{key} is not in {self.__class__.__name__}')
            elif len(matches) == 1:
                return matches[0]
            else:
                return self.__class__(contents = matches)
            
    def __setitem__(self, key: Union[Any, int], value: Any) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (Union[Any, int]): if key isn't an int, it is ignored (since the
                'name' attribute of the value will be acting as the key). In
                such a case, the 'value' is added to the end of 'contents'. If
                key is an int, 'value' is assigned at the that index number in
                'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        if isinstance(key, int):
            self.contents[key] = value
        else:
            self.add(value)
        return self

    def __delitem__(self, key: Union[Any, int]) -> None:
        """Deletes item matching 'key' in 'contents'.

        If 'key' is not an int type, this method looks for a matching 'name'
        attribute in the stored instances and deletes all such items. If 'key'
        is an int type, only the item at that index is deleted.

        Args:
            key (Union[Any, int]): name or index in 'contents' to delete.

        """
        if isinstance(key, int):
            del self.contents[key]
        else:
            self.contents = [c for c in self.contents if c.name != key]
        return self

    def __iter__(self) -> Iterable:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: 'contents'.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of iterable of 'contents'

        Returns:
            int: length of iterable 'contents'.

        """
        return len(self.contents)

 
@dataclasses.dataclass
class Lexicon(Bunch, collections.abc.MutableMapping):
    """Basic amicus dict replacement.
    
    A Lexicon differs from an ordinary python dict in 1 additional way than
    a Bunch:
        1) It includes "excludify" and "subsetify" methods which return new
            instances with a subset of 'contents' based upon the 'subset'
            argument passed to the method. 'excludify' returns all 'contents'
            that do not have keys matching items in the 'subset' argument.
            'subsetify' returns all 'contents' that have keys matching items
            in the 'subset' argument.
    
    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
        default (Any): default value to return when the 'get' method is used.
              
    """
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    default: Any = None

    """ Public Methods """
     
    def add(self, item: Mapping[Any, Any], **kwargs) -> None:
        """Adds 'item' to the 'contents' attribute.
        
        Args:
            item (Mapping[Any, Any]): items to add to 'contents' attribute.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.
                
        """
        self.contents.update(item)
        return self
       
    def excludify(self, subset: Union[Any, Sequence[Any]], **kwargs) -> Lexicon:
        """Returns a new instance without a subset of 'contents'.

        Args:
            subset (Union[Any, Sequence[Any]]): key(s) for which key/value pairs 
                from 'contents' should not be returned.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.

        Returns:
            Lexicon: with only key/value pairs with keys not in 'subset'.

        """
        subset = more_itertools.always_iterable(subset)
        contents = {k: v for k, v in self.contents.items() if k not in subset}
        instance = self.__class__(contents = contents, **kwargs)
        for key, value in kwargs.items():
            setattr(instance, key, value)
        return instance

    def fromkeys(self, keys: Sequence[str], value: Any) -> Lexicon:
        """Emulates the 'fromkeys' method from a python dict.

        Args:
            keys (Sequence[str]): items to be keys in a new Lexicon.
            value (Any): the value to use for all values in a new Lexicon.

        Returns:
            Lexicon: formed from 'keys' and 'value'.
            
        """
        return self.__class__(
            contents = dict.fromkeys(keys, value),
            default = self.default)
    
    def get(self, key: Any) -> Any:
        """Returns value in 'contents' or value in 'default' attribute.
        
        Args:
            key (Any): key for value in 'contents'.
                
        Returns:
            Any: value matching key in 'contents' or 'default' value. 
            
        """
        try:
            return self[key]
        except KeyError:
            return self.default
      
    def setdefault(self, value: Any) -> None:
        """Sets default value to return when 'get' method is used.
        
        Args:
            value (Any): default value to return.
            
        """
        self.default = value 
                   
    def subsetify(self, subset: Union[Any, Sequence[Any]], **kwargs) -> Lexicon:
        """Returns a new instance with a subset of 'contents'.

        Args:
            subset (Union[Any, Sequence[Any]]): key(s) for which key/value pairs 
                from 'contents' should be returned.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.

        Returns:
            Lexicon: with only key/value pairs with keys in 'subset'.

        """
        subset = more_itertools.always_iterable(subset)
        contents = {k: self.contents[k] for k in subset}
        instance = self.__class__(contents = contents, **kwargs)
        for key, value in kwargs.items():
            setattr(instance, key, value)
        return instance

    """ Dunder Methods """

    def __getitem__(self, key: Any) -> Any:
        """Returns value for 'key' in 'contents'.

        Args:
            key (Any): key in 'contents' for which a value is sought.

        Returns:
            Any: value stored in 'contents'.

        """
        return self.contents[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (Any): key to set in 'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        self.contents[key] = value
        return self

    def __delitem__(self, key: Any) -> None:
        """Deletes 'key' in 'contents'.

        Args:
            key (Any): key in 'contents' to delete the key/value pair.

        """
        del self.contents[key]
        return self
    
    def __iter__(self) -> Iterable[Any]:
        """Returns iterable of 'contents'.

        Returns:
            Iterable: of 'contents'.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of iterable of 'contents'

        Returns:
            int: length of iterable 'contents'.

        """
        return len(self.contents)


@dataclasses.dataclass
class Catalog(Lexicon):
    """Core class for a wildcard and list-accepting dictionary.

    A Catalog inherits the differences between a Lexicon and an ordinary python
    dict.

    A Catalog differs from a Lexicon in 6 significant ways:
        1) It recognizes an 'all' key which will return a list of all values
            stored in a Catalog instance.
        2) It recognizes a 'default' key which will return all values matching
            keys listed in the 'defaults' attribute. 'default' can also be set
            using the 'catalog['default'] = new_default' assignment. If 
            'defaults' is not passed when the instance is initialized, the 
            initial value of 'defaults' is 'all'.
        3) It recognizes a 'none' key which will return an empty list.
        4) It supports a list of keys being accessed with the matching values 
            returned. For example, 'catalog[['first_key', 'second_key']]' will 
            return the values for those keys in a list ['first_value',
            'second_value'].
        5) If a single key is sought, a Catalog can either return the stored
            value or a stored value in a list (if 'always_return_list' is
            True). The latter option is available to make iteration easier
            when the iterator assumes a single datatype will be returned.
        6) It includes an 'instance' method which return instances or stored 
            classes, respectively.

    Args:
        contents (Mapping[Any, Any]]): stored dictionary. Defaults to an empty 
            dict.
        default (Any): default value to return when the 'get' method is used.
        defaults (Sequence[Any]]): a list of keys in 'contents' which will be 
            used to return items when 'default' is sought. If not passed, 
            'default' will be set to all keys.
        always_return_list (bool): whether to return a list even when the key 
            passed is not a list or special access key (True) or to return a 
            list only when a list or special access key is used (False). 
            Defaults to False.
                     
    """
    contents: Mapping[Any, Any] = dataclasses.field(default_factory = dict)
    default: Any = None
    defaults: Sequence[Any] = dataclasses.field(default_factory = list)
    always_return_list: bool = False
    
    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Initializes class instance."""
        # Calls parent initialization methods, if they exist.
        try:
            super().__post_init__()
        except AttributeError:
            pass   
        # Sets 'default' to all keys of 'contents', if not passed.
        self.defaults = self.defaults or 'all'

    """ Public Methods """

    def excludify(self, subset: Union[Any, Sequence[Any]], **kwargs) -> Catalog:
        """Returns a new instance without a subset of 'contents'.

        Args:
            subset (Union[Any, Sequence[Any]]): key(s) for which key/value pairs 
                from 'contents' should not be returned.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.

        Returns:
            Catalog: with only key/value pairs without keys in 'subset'.

        """
        if not isinstance(self.defaults, list):
            new_defaults = self.defaults
        else:
            new_defaults = [i for i in self.defaults if i not in subset] 
        return super().excludify(
            subset = subset, 
            default = self.default,
            defaults = new_defaults,
            always_return_list = self.always_return_list,
            **kwargs)

    def instance(self, 
        key: Union[Any, Sequence[Any]], **kwargs) -> Union[Any, Sequence[Any]]:
        """Returns instance(s) of (a) stored class(es).
        
        This method acts as a factory for instancing stored classes.
        
        Args:
            key (Union[Any, Sequence[Any]]): key(s) in 'contents'.
            kwargs: arguments to pass to the selected item(s) when instanced.
                    
        Returns:
            Union[Any, Sequence[Any]]: stored value(s).
            
        """
        items = self[key]
        if isinstance(items, Sequence) and not isinstance(items, str):
            instances = []
            for item in items:
                instances.append(item(**kwargs))
        else:
            instances = items(**kwargs)
        return instances
                   
    def subsetify(self, subset: Union[Any, Sequence[Any]], **kwargs) -> Catalog:
        """Returns a new instance with a subset of 'contents'.

        Args:
            subset (Union[Any, Sequence[Any]]): key(s) for which key/value pairs 
                from 'contents' should be returned.
            kwargs: creates a consistent interface even when subclasses have
                additional parameters.

        Returns:
            Catalog: with only key/value pairs with keys in 'subset'.

        """
        if not isinstance(self.defaults, list):
            new_defaults = self.defaults
        else:
            new_defaults = [i for i in self.defaults if i in subset] 
        return super().subsetify(
            subset = subset, 
            default = self.default,
            defaults = new_defaults,
            always_return_list = self.always_return_list,
            **kwargs)

    """ Dunder Methods """

    def __getitem__(self, 
        key: Union[Any, Sequence[Any]]) -> Union[Any, Sequence[Any]]:
        """Returns value(s) for 'key' in 'contents'.

        The method searches for 'all', 'default', and 'none' matching wildcard
        options before searching for direct matches in 'contents'.

        Args:
            key (Union[Any, Sequence[Any]]): key(s) in 'contents'.

        Returns:
            Union[Any, Sequence[Any]]: value(s) stored in 'contents'.

        """
        # Returns a list of all values if the 'all' key is sought.
        if key in ['all', ['all']]:
            return list(self.contents.values())
        # Returns a list of values for keys listed in 'defaults' attribute.
        elif key in ['default', ['default'], 'defaults', ['defaults']]:
            try:
                return self[self.defaults]
            except KeyError:
                return list(
                    {k: self.contents[k] for k in self.defaults}.values())
        # Returns an empty list if a null value is sought.
        elif key in ['none', ['none'], 'None', ['None']]:
            return []
        # Returns list of matching values if 'key' is list-like.        
        elif isinstance(key, Sequence) and not isinstance(key, str):
            return [self.contents[k] for k in key if k in self.contents]
        # Returns matching value if key is not a non-str Sequence or wildcard.
        else:
            try:
                if self.always_return_list:
                    return [self.contents[key]]
                else:
                    return self.contents[key]
            except KeyError:
                raise KeyError(f'{key} is not in {self.__class__.__name__}')

    def __setitem__(self,
        key: Union[Any, Sequence[Any]], 
        value: Union[Any, Sequence[Any]]) -> None:
        """Sets 'key' in 'contents' to 'value'.

        Args:
            key (Union[Any, Sequence[Any]]): key(s) to set in 'contents'.
            value (Union[Any, Sequence[Any]]): value(s) to be paired with 'key' 
                in 'contents'.

        """
        if key in ['default', ['default'], 'defaults', ['defaults']]:
            self.defaults = more_itertools.always_iterable(value)
        else:
            try:
                self.contents[key] = value
            except TypeError:
                self.contents.update(dict(zip(key, value)))
        return self

    def __delitem__(self, key: Union[Any, Sequence[Any]]) -> None:
        """Deletes 'key' in 'contents'.

        Args:
            key (Union[Any, Sequence[Any]]): name(s) of key(s) in 'contents' to
                delete the key/value pair.

        """
        self.contents = {
            i: self.contents[i] for i in self.contents 
            if i not in more_itertools.always_iterable(key)}
        return self


@dataclasses.dataclass
class Library(Lexicon):
    """Stores items with first-level dot notation access.
    
    A Library inherits the differences between a Lexicon and an ordinary python
    dict.

    A Library differs from a Lexicon in 2 significant ways:
        1) It adds on dot access for first level keys. Ordinary dict access
            methods are still available, inherited from Lexicon.
        2) It has a 'deposit' method which returns an error if the passed key
            already exists in the stored dict.
    
    Args:
        contents (Mapping[str, Any]]): stored dictionary. Defaults to an empty 
            dict.
        default (Any): default value to return when the 'get' method is used.
              
    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    default: Any = None
    
    """ Public Methods """
    
    def deposit(self, name: str, item: Union[Type, object]) -> None:
        """Adds 'item' at 'name' to 'contents' if 'name' isn't in 'contents'.
        
        Args:
            name (str): key to use to store 'item'.
            item (Union[Type, object]): item to store in 'contents'.
            
        Raises:
            ValueError: if 'name' matches an existing key in 'contents'.
            
        """
        if name in dir(self):
            raise ValueError(f'{name} is already in {self.__class__.__name__}')
        else:
            self[name] = item
        return self

    """ Dunder Methods """
    
    def __getattr__(self, key: str) -> Any:
        """Returns an item in 'contents' matching 'key'.

        Args:
            key (str): name of item in 'contents' to return.

        Raises:
            AttributeError: if 'key' doesn't match an item in 'contents'.

        Returns:
            Any: item stored in 'contents'.
            
        """
        try:
            return self[key]
        except KeyError as key_error:
            raise AttributeError(key_error)

    def __setattr__(self, key: str, value: Any) -> None:
        """Stores 'value' in 'contents' at 'key'.

        Args:
            key (str): name of item to store in 'contents'.
            value (Any): item to store in 'contents'.
            
        """
        self[key] = value
        return self

    def __delattr__(self, key: str) -> None:
        """Deletes item in 'contents' corresponding to 'key'

        Args:
            key (str): name of item in 'contents' to delete.

        Raises:
            AttributeError: if 'key' doesn't match an item in 'contents'.
           
        """
        try:
            del self[key]
        except KeyError as key_error:
            raise AttributeError(key_error)
