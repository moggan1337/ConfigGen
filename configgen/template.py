"""
Template Engine Module

Handles template loading, caching, and rendering with variable substitution.
"""

import re
import logging
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


logger = logging.getLogger(__name__)


class TemplateSyntax(Enum):
    """Supported template syntaxes."""
    JINJA2 = "jinja2"
    MUSTACHE = "mustache"
    SIMPLE = "simple"


@dataclass
class Template:
    """Represents a compiled template."""
    name: str
    content: str
    syntax: TemplateSyntax = TemplateSyntax.JINJA2
    compiled: Optional[Any] = None


class TemplateEngine:
    """
    Template processing engine with support for multiple syntaxes.
    
    Features:
    - Jinja2-style syntax with extensions
    - Template inheritance
    - Custom filters and functions
    - Output formatting control
    - Include directive support
    """
    
    DEFAULT_filters = {
        'upper': str.upper,
        'lower': str.lower,
        'title': str.title,
        'capitalize': str.capitalize,
        'default': lambda v, d=None: v if v else d,
        'length': len,
        'int': int,
        'float': float,
        'str': str,
        'bool': lambda v: str(v).lower() in ('true', '1', 'yes'),
        'tojson': lambda v: str(v),
        'toyaml': lambda v: str(v),
        'quote': lambda v: f'"{v}"' if isinstance(v, str) else v,
        'single_quote': lambda v: f"'{v}'" if isinstance(v, str) else v,
    }
    
    def __init__(self, cache: bool = True, syntax: TemplateSyntax = TemplateSyntax.JINJA2):
        """
        Initialize the template engine.
        
        Args:
            cache: Enable template caching.
            syntax: Default template syntax.
        """
        self._templates: Dict[str, Template] = {}
        self._cache_enabled = cache
        self._syntax = syntax
        self._filters: Dict[str, Callable] = self.DEFAULT_filters.copy()
        self._custom_filters: Dict[str, Callable] = {}
        self._globals: Dict[str, Any] = {}
        self._includes_path: list = []
        
        try:
            from jinja2 import Environment, BaseLoader, TemplateError
            self._jinja2_available = True
            self._jinja_env = Environment(
                loader=BaseLoader(),
                autoescape=False,
                keep_trailing_newline=True,
                trim_blocks=True,
                lstrip_blocks=True,
            )
            self._jinja_env.filters.update(self._filters)
        except ImportError:
            logger.warning("Jinja2 not available, using simple template engine")
            self._jinja2_available = False
            self._jinja_env = None
        
        logger.debug(f"TemplateEngine initialized (Jinja2: {self._jinja2_available})")
    
    def register_template(
        self, 
        name: str, 
        content: str,
        syntax: Optional[TemplateSyntax] = None
    ) -> "TemplateEngine":
        """
        Register a template for later use.
        
        Args:
            name: Unique template identifier.
            content: Template content.
            syntax: Template syntax (uses default if None).
            
        Returns:
            Self for method chaining.
        """
        syntax = syntax or self._syntax
        
        template = Template(
            name=name,
            content=content,
            syntax=syntax
        )
        
        if self._cache_enabled and self._jinja2_available:
            try:
                template.compiled = self._jinja_env.from_string(content)
            except Exception as e:
                logger.warning(f"Failed to compile template '{name}': {e}")
                template.compiled = None
        
        self._templates[name] = template
        return self
    
    def register_filter(self, name: str, func: Callable) -> "TemplateEngine":
        """
        Register a custom filter function.
        
        Args:
            name: Filter name.
            func: Filter function.
            
        Returns:
            Self for method chaining.
        """
        self._custom_filters[name] = func
        
        if self._jinja2_available and self._jinja_env:
            self._jinja_env.filters[name] = func
        
        return self
    
    def register_function(self, name: str, func: Callable) -> "TemplateEngine":
        """
        Register a global function.
        
        Args:
            name: Function name.
            func: Function object.
            
        Returns:
            Self for method chaining.
        """
        self._globals[name] = func
        
        if self._jinja2_available and self._jinja_env:
            self._jinja_env.globals[name] = func
        
        return self
    
    def add_include_path(self, path: str) -> "TemplateEngine":
        """
        Add a directory to search for included templates.
        
        Args:
            path: Directory path.
            
        Returns:
            Self for method chaining.
        """
        self._includes_path.append(str(Path(path).absolute()))
        return self
    
    def load_template(self, path: str) -> Optional[str]:
        """
        Load a template file from include paths.
        
        Args:
            path: Relative or absolute path.
            
        Returns:
            Template content or None.
        """
        path_obj = Path(path)
        
        if path_obj.exists():
            return path_obj.read_text(encoding='utf-8')
        
        for include_path in self._includes_path:
            full_path = Path(include_path) / path_obj
            if full_path.exists():
                return full_path.read_text(encoding='utf-8')
        
        return None
    
    def render(
        self,
        name: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Render a template with variables.
        
        Args:
            name: Template name.
            variables: Variables for substitution.
            
        Returns:
            Rendered template string.
            
        Raises:
            ValueError: If template not found.
        """
        if name not in self._templates:
            raise ValueError(f"Template not found: {name}")
        
        template = self._templates[name]
        variables = variables or {}
        
        all_globals = {
            **self._globals,
            'include': self.load_template,
            'now': self._get_current_time,
            'env': self._get_environment,
        }
        
        if self._jinja2_available and template.compiled:
            try:
                return template.compiled.render(**variables, **all_globals)
            except Exception as e:
                logger.error(f"Jinja2 render failed for '{name}': {e}")
                return self._render_simple(template.content, variables)
        else:
            return self._render_simple(template.content, variables)
    
    def _render_simple(self, content: str, variables: Dict[str, Any]) -> str:
        """
        Simple variable substitution without full templating.
        
        Supports {{ variable }} and {{ variable | filter }} syntax.
        """
        def replace_var(match):
            expr = match.group(1).strip()
            
            if '|' in expr:
                var_name, *filters = expr.split('|')
                var_name = var_name.strip()
                
                value = variables.get(var_name, '')
                
                for f in filters:
                    f = f.strip()
                    if f in self._filters:
                        value = self._filters[f](value)
                    elif f in self._custom_filters:
                        value = self._custom_filters[f](value)
                
                return str(value)
            else:
                value = variables.get(expr, '')
                return str(value) if value is not None else ''
        
        pattern = r'\{\{\s*(.+?)\s*\}\}'
        return re.sub(pattern, replace_var, content)
    
    def _get_current_time(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_environment(self) -> Dict[str, str]:
        """Get environment information."""
        import os
        return dict(os.environ)
    
    def clear_cache(self) -> "TemplateEngine":
        """
        Clear the template cache.
        
        Returns:
            Self for method chaining.
        """
        self._templates.clear()
        return self
    
    def list_templates(self) -> list:
        """List registered template names."""
        return list(self._templates.keys())
    
    def get_template_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a template.
        
        Args:
            name: Template name.
            
        Returns:
            Template info dict or None.
        """
        if name not in self._templates:
            return None
        
        template = self._templates[name]
        return {
            'name': template.name,
            'syntax': template.syntax.value,
            'size': len(template.content),
            'cached': template.compiled is not None,
        }
