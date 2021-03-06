"""
amicus.project.foundry:
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

Contents:


"""
from __future__ import annotations
import abc
import copy
import dataclasses
import inspect
from typing import (Any, Callable, ClassVar, Dict, Hashable, Iterable, List, 
    Mapping, Optional, Sequence, Set, Tuple, Type, Union)

import more_itertools

import amicus
from . import core


# DIRECTIVE: Type = Directive
# OUTLINE: Type = Outline
# COMPONENT: Type = Component
# RESULT: Type = Result
# SUMMARY: Type = Summary


@dataclasses.dataclass
class Workshop(amicus.framework.Keystone, abc.ABC):
    """Builds amicus project objects
    
    """
    """ Public Methods """

    product: ClassVar[str] = None
    action: ClassVar[str] = None   

    """ Public Methods """
    
    @abc.abstractmethod
    def create(self, project: amicus.Project, **kwargs) -> object:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            object
            
        """
        pass

 
@dataclasses.dataclass
class Draft(Workshop):
    """Builds Outlines and Directives from Settings.
    
    """
    product: ClassVar[str] = 'outline'
    action: ClassVar[str] = 'drafting'

    """ Public Methods """
    
    def create(self, project: amicus.Project, **kwargs) -> core.Outline:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            core.Outline: [description]
            
        """
        return self.create_outline(
            name = project.name, 
            settings = project.settings,
            **kwargs)

    def create_outline(self,
        name: str, 
        settings: amicus.options.Settings, 
        **kwargs) -> amicus.project.Outline:
        """[summary]

        Args:
            name (str): [description]
            settings (amicus.options.Settings): [description]

        Returns:
            amicus.project.Outline: [description]
            
        """
        try:
            general = settings['general']
        except KeyError:
            general = {}
        try:
            files = settings['files']
        except KeyError:
            try:
                files = settings['filer']
            except KeyError:
                files = {}
        try:
            package = settings['amicus']
        except (KeyError, TypeError):
            package = {}
        outline = amicus.project.Outline(
            general = general,
            files = files,
            package = package,
            **kwargs) 
        outline = self.add_directive(
            name = name, 
            settings = settings, 
            outline = outline)
        return outline
    
    def add_directive(self,
        name: str, 
        settings: amicus.options.Settings,
        outline: amicus.project.Outline,
        **kwargs) -> core.Directive:
        """[summary]

        Args:
            name (str): [description]
            settings (amicus.options.Settings): [description]
            library (amicus.types.Library, optional): [description]. 
                Defaults to None.

        Returns:
            amicus.project.Directive: [description]
            
        """
        edges = {}
        designs = {}
        initialization = {}
        attributes = {}        
        designs[name] = self.get_design(name = name, settings = settings)
        lookups = [name, designs[name]]
        dummy_component = self.library.component.select(name = lookups)
        possible_initialization = tuple(
            i for i in list(dummy_component.__annotations__.keys()) 
            if i not in ['name', 'contents'])
        for key, value in settings[name].items():
            prefix, suffix = amicus.tools.divide_string(key, divider = '_')
            if suffix in ['design']:
                pass
            elif suffix in self.library.component.subclasses.suffixes:
                if prefix in edges:
                    edges[prefix].extend(amicus.tools.listify(value))
                else:
                    edges[prefix] = amicus.tools.listify(value)  
                for subcomponent in more_itertools.always_iterable(value):
                    edges[subcomponent] = []
                    try:
                        subcomponent_design = self.get_design(
                            name = subcomponent, 
                            settings = settings)
                    except KeyError:
                        subcomponent_design = suffix[:-1]
                    designs.update({subcomponent: subcomponent_design})
                    if subcomponent in settings:
                        outline = self.add_directive(
                            name = subcomponent,
                            settings = settings,
                            outline = outline)
            elif suffix in possible_initialization:
                initialization[suffix] = value
            elif prefix in [name]:
                attributes[suffix] = value
            else:
                attributes[key] = value
        implementation = {}
        components = list(edges.keys())
        components.append(name)
        more_components = list(more_itertools.collapse(edges.values()))      
        components.extend(more_components)
        if components:
            for component in components:
                try:
                    implementation[component] = settings[
                        f'{component}_parameters']
                except KeyError:
                    implementation[component] = {}
        directive = amicus.project.Directive(
            name = name, 
            edges = edges,
            designs = designs,
            initialization = initialization,
            implementation = implementation,
            attributes = attributes,
            **kwargs)
        outline[name] = directive
        return outline

    def get_design(self, name: str, settings: amicus.options.Settings) -> str:
        """[summary]

        Args:
            name (str): [description]

        Raises:
            KeyError: [description]

        Returns:
            str: [description]
            
        """
        try:
            design = settings[name][f'{name}_design']
        except KeyError:
            try:
                design = settings[name][f'design']
            except KeyError:
                try:
                    design = settings['amicus']['default_design']
                except KeyError:
                    raise KeyError(f'To designate a design, a key in settings '
                                    f'must either be named "design" or '
                                    f'"{name}_design"')
        return design       
    
    
@dataclasses.dataclass
class Publish(Workshop):
    """Builds Components and Parameters.
    
    """
    product: ClassVar[str] = 'workflow'
    action: ClassVar[str] = 'publishing'
    
    """ Public Methods """
    
    def create(self, project: amicus.Project, **kwargs) -> core.Component:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            core.Component: [description]
            
        """
        print('test outline', project.outline)
        workflow = self.create_component(
            name = project.name,
            directive = project.outline[project.name],
            outline = project.outline,
            **kwargs)
        new_adjacency = {}
        for node, edges in workflow.items():
            if node != project.name:
                new_node = self.create_component(
                    name = node.name,
                    outline = project.outline)
                new_adjacency[new_node] = edges
        workflow.contents = new_adjacency
        return workflow

    def create_component(self, 
        name: Union[str, Sequence[str]] = None,
        directive: core.Directive = None,
        outline: core.Outline = None,
        **kwargs) -> core.Component:
        """[summary]

        Args:
            name (Union[str, Sequence[str]], optional): [description]. Defaults 
                to None.
            directive (core.Directive, optional): [description]. Defaults to 
                None.
            outline (core.Outline, optional): [description]. Defaults to None.

        Raises:
            ValueError: [description]

        Returns:
            core.Component: [description]
            
        """        
        if name is None and directive is None and outline is None:
            raise ValueError(
                'create needs either a name, directive, or outline argument')
        else:
            names, name, directive, outline = self._fix_arguments(
                name = name,
                directive = directive,
                outline = outline)
            if directive is None:
                component = self._from_name(name = name, **kwargs)
                print('test is leaf', component.name)
            else:  
                if name == directive.name:
                    initialization = directive.initialization
                else:
                    initialization = {}
                implementation = directive.implementation[name]
                initialization.update({'parameters': implementation}) 
                initialization.update(kwargs)
                lookups = names
                try:
                    if directive.designs[name] not in lookups:
                        lookups.append(directive.designs[name])   
                except KeyError:
                    pass
                component = self._from_name(name = lookups, **initialization)  
            if isinstance(component, Iterable):
                if isinstance(component, amicus.project.Nexus):
                    print('test is parallel', component.name)
                    method = self._organize_parallel
                else:
                    print('test is serial', component.name)
                    method = self._organize_serial
                component = method(
                    component = component,
                    directive = directive,
                    outline = outline)
            return component 

    def create_parameters(self,
        name: str,
        settings: amicus.options.Settings,
        **kwargs) -> core.Parameters:
        """[summary]

        Args:
            name (str): [description]
            settings (amicus.options.Settings): [description]

        Returns:
            core.Parameters: [description]
            
        """
        from_settings = self._parameters_from_settings(
            name = name, 
            settings = settings)      
        parameters = core.Parameters(contents = from_settings)
        return parameters
        
    """ Private Methods """

    def _fix_arguments(self,         
        name: str, 
        directive: core.Directive,
        outline: core.Outline) -> Tuple[List[str], str, str, str, str]:
        """[summary]

        Args:
            name (str): [description]
            directive (core.Directive): [description]
            outline (core.Outline): [description]

        Returns:
            Tuple[List[str], str, str, str, str]: [description]
            
        """
        names = self._get_names(
            name = name, 
            directive = directive, 
            outline = outline)
        name = names[0]
        directive = self._get_directive(
            name = name, 
            directive = directive, 
            outline = outline)
        outline = self._get_outline(
            name = name, 
            directive = directive, 
            outline = outline)
        return names, name, directive, outline
    
    def _get_names(self, 
        name: str, 
        directive: core.Directive,
        outline: core.Outline) -> str:
        """[summary]

        Args:
            outline (core.Outline): [description]
            name (str): [description]
            directive (core.Directive): [description]

        Returns:
            str: [description]
            
        """
        if name is not None:
            return amicus.tools.listify(name)
        elif directive is not None:
            return amicus.tools.listify(directive.name)
        else:
            return amicus.tools.listify(outline.name)
        
    def _get_directive(self, 
        name: str, 
        directive: core.Directive,
        outline: core.Outline) -> core.Directive:
        """[summary]

        Args:
            name (str): [description]
            directive (core.Directive): [description]
            outline (core.Outline): [description]

        Returns:
            core.Directive: [description]
            
        """
        if directive is not None:
            return directive
        elif name is not None and outline is not None:
            try:
                return outline[name]
            except KeyError:
                return None
        else:
            try:
                return outline[outline.name]   
            except KeyError:
                return None

    def _get_outline(self, 
        name: str, 
        directive: core.Directive,
        outline: core.Outline) -> core.Outline:
        """[summary]

        Args:
            name (str): [description]
            directive (core.Directive): [description]
            outline (core.Outline): [description]

        Returns:
            core.Outline: [description]
            
        """
        if outline is not None:
            return directive
        elif name is not None and directive is not None:
            return core.Outline(name = name, contents = {name: directive}) 
        else:
            return None

    def _from_name(self, 
        name: Union[str, Sequence[str]], 
        **kwargs) -> core.Component:
        """Returns instance of first match of 'name' in stored catalogs.
        
        The method prioritizes the 'instances' catalog over 'subclasses' and any
        passed names in the order they are listed.
        
        Args:
            name (Union[str, Sequence[str]]): [description]
            
        Raises:
            KeyError: [description]
            
        Returns:
            core.Component: [description]
            
        """
        names = amicus.tools.listify(name)
        primary = names[0]
        item = None
        for key in names:
            for catalog in ['instances', 'subclasses']:
                try:
                    item = getattr(self.library.component, catalog)[key]
                    break
                except KeyError:
                    pass
            if item is not None:
                break
        if item is None:
            raise KeyError(f'No matching item for {names} was found') 
        elif inspect.isclass(item):
            instance = item(name = primary, **kwargs)
        else:
            instance = copy.deepcopy(item)
            for key, value in kwargs.items():
                setattr(instance, key, value)  
        return instance 
                                       
    def _organize_serial(self, 
        component: core.Component,
        directive: core.Directive,
        outline: core.Outline) -> core.Component:
        """[summary]

        Args:
            component (Component): [description]
            directive (core.Directive): [description]
            outline (core.Outline): [description]

        Returns:
            core.Component: [description]
            
        """     
        subcomponents = self._serial_order(
            name = component.name, 
            directive = directive)
        collapsed = list(more_itertools.collapse(subcomponents))
        nodes = []
        for node in collapsed:
            subnode = self.create_component(
                name = [node, directive.designs[node]],
                directive = directive,
                outline = outline)
            nodes.append(subnode)
        if nodes:
            print('test yes nodes about to extend')
            component.extend(nodes = nodes)
        return component      

    def _organize_parallel(self, 
        component: core.Component,
        directive: core.Directive,
        outline: core.Outline) -> core.Component:
        """[summary]

        Args:
            component (Component): [description]
            directive (core.Directive): [description]
            outline (core.Outline): [description]

        Returns:
            core.Component: [description]
            
        """ 
        step_names = directive.edges[directive.name]
        print('test step names', step_names)
        possible = [directive.edges[step] for step in step_names]
        nodes = []
        print('test possible', possible)
        for i, step_options in enumerate(possible):
            permutation = []
            for option in step_options:
                t_keys = [option, directive.designs[option]]
                technique = self.create_component(
                    name = t_keys,
                    directive = directive,
                    outline = outline,
                    suffix = step_names[i])
                s_keys = [step_names[i], directive.designs[step_names[i]]]    
                step = self.create_component(
                    name = s_keys,
                    directive = directive,
                    outline = outline,
                    contents = technique)
                step.name = option
                permutation.append(step)
                print('test permutation', permutation)
            nodes.append(permutation)
        component.branchify(nodes = nodes)
        return component
    
    def _serial_order(self, 
        name: str, 
        directive: core.Directive) -> List[Hashable]:
        """[summary]

        Args:
            name (str): [description]
            directive (core.Directive): [description]

        Returns:
            List[Hashable]: [description]
            
        """        
        organized = []
        components = directive.edges[name]
        for item in components:
            organized.append(item)
            if item in directive.edges:
                organized_subcomponents = []
                subcomponents = self._serial_order(
                    name = item, 
                    directive = directive)
                organized_subcomponents.append(subcomponents)
                if len(organized_subcomponents) == 1:
                    organized.append(organized_subcomponents[0])
                else:
                    organized.append(organized_subcomponents)
        return organized   
    
    def _parameters_from_settings(self,
        name: str,
        settings: amicus.options.Settings) -> core.Parameters:
        """[summary]

        Args:
            name (str): [description]
            settings (amicus.options.Settings): [description]

        Returns:
            core.Parameters: [description]
            
        """        
        try:
            parameters = settings[f'{name}_parameters']
        except KeyError:
            suffix = name.split('_')[-1]
            prefix = name[:-len(suffix) - 1]
            try:
                parameters = settings[f'{prefix}_parameters']
            except KeyError:
                try:
                    parameters = settings[f'{suffix}_parameters']
                except KeyError:
                    parameters = {}
        return parameters
    
        
@dataclasses.dataclass
class Execute(Workshop):
    """Builds Results and Summaries from workflows.
    
    """
    product: ClassVar[str] = 'summary'
    action: ClassVar[str] = 'preparing'

    """ Public Methods """
    
    def create(self, project: amicus.Project, **kwargs) -> core.Summary:
        """[summary]

        Args:
            project (amicus.Project): [description]

        Returns:
            core.Summary: [description]
            
        """
        print('test workflow', project.workflow.contents)
        print('test parser', project.workflow.nodes['parser'].edges)
        return self.create_summary(
            name = project.name,
            settings = project.settings,
            package = project.package)   
    
     
        