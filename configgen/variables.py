"""
Variable Resolver Module

Handles variable resolution, substitution, and sensitive value management.
"""

import re
import logging
from typing import Dict, Any, Optional, Set, Callable
from copy import deepcopy


logger = logging.getLogger(__name__)


class VariableResolutionError(Exception):
    """Raised when variable resolution fails."""
    pass


class VariableResolver:
    """
    Resolves variables with support for:
    - Default values
    - Conditional expressions
    - Nested references
    - Sensitive value masking
    - Custom functions
    """
    
    VAR_PATTERN = re.compile(r'\$\{([^}]+)\}')
    COND_PATTERN = re.compile(r'\$\{([^:]+):\s*([^}]+)\}')
    
    def __init__(self, allow_missing: bool = False):
        """
        Initialize the variable resolver.
        
        Args:
            allow_missing: If True, unresolved variables return empty string.
        """
        self._variables: Dict[str, Any] = {}
        self._sensitive: Set[str] = set()
        self._allow_missing = allow_missing
        self._functions: Dict[str, Callable] = {
            'upper': str.upper,
            'lower': str.lower,
            'trim': str.strip,
            'int': int,
            'float': float,
            'str': str,
            'bool': lambda v: v.lower() in ('true', '1', 'yes') if isinstance(v, str) else bool(v),
            'default': lambda v, d='': v if v else d,
            'env': __import__('os').getenv,
        }
    
    def update_variables(self, variables: Dict[str, Any]) -> None:
        """Update multiple variables at once."""
        self._variables.update(variables)
    
    def add_variable(
        self, 
        key: str, 
        value: Any, 
        sensitive: bool = False
    ) -> None:
        """
        Add a single variable.
        
        Args:
            key: Variable name.
            value: Variable value.
            sensitive: Mark as sensitive (hidden from logs).
        """
        self._variables[key] = value
        if sensitive:
            self._sensitive.add(key)
    
    def get_variable(self, key: str, default: Any = None) -> Any:
        """Get a variable value."""
        return self._variables.get(key, default)
    
    def remove_variable(self, key: str) -> bool:
        """Remove a variable."""
        if key in self._variables:
            del self._variables[key]
            self._sensitive.discard(key)
            return True
        return False
    
    def register_function(self, name: str, func: Callable) -> None:
        """Register a custom function for variable expressions."""
        self._functions[name] = func
    
    def resolve(self, data: Any, max_depth: int = 10) -> Any:
        """
        Resolve all variables in data.
        
        Args:
            data: Data to resolve (dict, list, string, etc.)
            max_depth: Maximum recursion depth.
            
        Returns:
            Data with resolved variables.
        """
        return self._resolve_impl(data, set(), max_depth)
    
    def _resolve_impl(
        self, 
        data: Any, 
        resolved: Set[str],
        depth: int
    ) -> Any:
        """Internal resolution implementation."""
        if depth <= 0:
            return data
        
        if isinstance(data, dict):
            return {
                k: self._resolve_impl(v, resolved, depth - 1)
                for k, v in data.items()
            }
        
        if isinstance(data, list):
            return [
                self._resolve_impl(item, resolved, depth - 1)
                for item in data
            ]
        
        if isinstance(data, str):
            return self._resolve_string(data, resolved, depth)
        
        return data
    
    def _resolve_string(
        self, 
        value: str, 
        resolved: Set[str],
        depth: int
    ) -> str:
        """Resolve variables in a string."""
        result = value
        
        for match in self.COND_PATTERN.finditer(result):
            full_match = match.group(0)
            var_expr = match.group(1).strip()
            default_val = match.group(2).strip()
            
            resolved_val = self._resolve_expression(var_expr, resolved, depth)
            
            if resolved_val is None or resolved_val == '':
                result = result.replace(full_match, default_val)
            else:
                result = result.replace(full_match, str(resolved_val))
        
        for match in self.VAR_PATTERN.finditer(result):
            full_match = match.group(0)
            var_expr = match.group(1).strip()
            
            if self.COND_PATTERN.search(full_match):
                continue
            
            resolved_val = self._resolve_expression(var_expr, resolved, depth)
            
            if resolved_val is not None:
                result = result.replace(full_match, str(resolved_val))
            elif not self._allow_missing:
                raise VariableResolutionError(f"Unresolved variable: {var_expr}")
        
        return result
    
    def _resolve_expression(
        self, 
        expr: str, 
        resolved: Set[str],
        depth: int
    ) -> Any:
        """Resolve a single variable expression."""
        expr = expr.strip()
        
        if '|' in expr:
            var_name, *funcs = expr.split('|')
            var_name = var_name.strip()
            
            value = self._get_nested_value(var_name, depth)
            
            for func_expr in funcs:
                func_expr = func_expr.strip()
                value = self._apply_function(func_expr, value, depth)
            
            return value
        
        if '(' in expr and expr.endswith(')'):
            func_name = expr[:expr.index('(')]
            args_str = expr[len(func_name) + 1:-1]
            args = [a.strip() for a in args_str.split(',')]
            resolved_args = [self._resolve_expression(a, resolved, depth) for a in args]
            
            if func_name in self._functions:
                return self._functions[func_name](*resolved_args)
            return None
        
        return self._get_nested_value(expr, depth)
    
    def _get_nested_value(self, key: str, depth: int) -> Any:
        """Get a potentially nested variable value."""
        parts = key.split('.')
        current = self._variables
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        if isinstance(current, str):
            return self._resolve_impl(current, set(), depth - 1)
        
        return current
    
    def _apply_function(
        self, 
        func_expr: str, 
        value: Any, 
        depth: int
    ) -> Any:
        """Apply a function to a value."""
        if '(' in func_expr and func_expr.endswith(')'):
            func_name = func_expr[:func_expr.index('(')]
            arg_str = func_expr[len(func_name) + 1:-1]
            arg = self._resolve_expression(arg_str, set(), depth)
            
            if func_name in self._functions:
                return self._functions[func_name](value, arg)
            return value
        
        if func_expr in self._functions:
            return self._functions[func_expr](value)
        
        return value
    
    def get_safe_variables(self) -> Dict[str, Any]:
        """Get variables with sensitive values masked."""
        result = {}
        
        for key, value in self._variables.items():
            if key in self._sensitive:
                result[key] = '***MASKED***'
            else:
                result[key] = deepcopy(value)
        
        return result
    
    def list_sensitive(self) -> Set[str]:
        """List sensitive variable names."""
        return self._sensitive.copy()
    
    def mark_sensitive(self, *keys: str) -> None:
        """Mark variables as sensitive."""
        self._sensitive.update(keys)
    
    def unmark_sensitive(self, *keys: str) -> None:
        """Unmark variables as sensitive."""
        self._sensitive.difference_update(keys)
