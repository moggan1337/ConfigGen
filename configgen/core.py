"""
ConfigGen Core Module

Main entry point for configuration generation.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field

from configgen.template import TemplateEngine
from configgen.validator import SchemaValidator
from configgen.environment import EnvironmentManager
from configgen.formats import FormatRegistry
from configgen.variables import VariableResolver
from configgen.inheritance import InheritanceEngine


logger = logging.getLogger(__name__)


@dataclass
class GeneratorConfig:
    """Configuration options for the ConfigGenerator."""
    default_format: str = "yaml"
    strict_validation: bool = True
    allow_missing_variables: bool = False
    auto_create_dirs: bool = True
    cache_templates: bool = True
    output_indent: int = 2
    include_comments: bool = True
    env_prefix: str = "CONFIGGEN"
    default_environment: str = "development"


class ConfigGenerator:
    """
    Main configuration generator class.
    
    Orchestrates template processing, variable resolution,
    inheritance, and validation to generate final configurations.
    
    Example:
        >>> generator = ConfigGenerator()
        >>> generator.load_template("app.yaml.j2")
        >>> generator.set_variables({"app_name": "myapp"})
        >>> config = generator.generate()
        >>> generator.write("output/app.yaml")
    """
    
    def __init__(self, config: Optional[GeneratorConfig] = None):
        """
        Initialize the ConfigGenerator.
        
        Args:
            config: Optional GeneratorConfig instance with customization options.
        """
        self.config = config or GeneratorConfig()
        self.template_engine = TemplateEngine(cache=self.config.cache_templates)
        self.validator = SchemaValidator(strict=self.config.strict_validation)
        self.env_manager = EnvironmentManager(prefix=self.config.env_prefix)
        self.format_registry = FormatRegistry()
        self.variable_resolver = VariableResolver(
            allow_missing=self.config.allow_missing_variables
        )
        self.inheritance_engine = InheritanceEngine()
        
        self._templates: Dict[str, str] = {}
        self._variables: Dict[str, Any] = {}
        self._schema: Optional[Dict[str, Any]] = None
        self._inheritance_chain: List[str] = []
        
        logger.info("ConfigGenerator initialized")
    
    def load_template(
        self, 
        path: Union[str, Path], 
        name: Optional[str] = None
    ) -> "ConfigGenerator":
        """
        Load a template from a file path.
        
        Args:
            path: Path to the template file.
            name: Optional name for the template (defaults to filename).
            
        Returns:
            Self for method chaining.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {path}")
        
        name = name or path.stem
        with open(path, 'r', encoding='utf-8') as f:
            self._templates[name] = f.read()
        
        self.template_engine.register_template(name, self._templates[name])
        logger.debug(f"Loaded template: {name} from {path}")
        
        return self
    
    def load_template_string(
        self, 
        content: str, 
        name: str
    ) -> "ConfigGenerator":
        """
        Load a template from a string.
        
        Args:
            content: Template content as string.
            name: Name identifier for the template.
            
        Returns:
            Self for method chaining.
        """
        self._templates[name] = content
        self.template_engine.register_template(name, content)
        return self
    
    def set_variables(self, variables: Dict[str, Any]) -> "ConfigGenerator":
        """
        Set variables for template rendering.
        
        Args:
            variables: Dictionary of variable key-value pairs.
            
        Returns:
            Self for method chaining.
        """
        self._variables.update(variables)
        self.variable_resolver.update_variables(self._variables)
        return self
    
    def add_variable(
        self, 
        key: str, 
        value: Any, 
        sensitive: bool = False
    ) -> "ConfigGenerator":
        """
        Add a single variable.
        
        Args:
            key: Variable name.
            value: Variable value.
            sensitive: Mark as sensitive (hidden from logs).
            
        Returns:
            Self for method chaining.
        """
        self._variables[key] = value
        self.variable_resolver.add_variable(key, value, sensitive=sensitive)
        return self
    
    def load_variables_from_file(
        self, 
        path: Union[str, Path],
        format: Optional[str] = None
    ) -> "ConfigGenerator":
        """
        Load variables from a file.
        
        Args:
            path: Path to variables file.
            format: File format (yaml, json, toml, env). Auto-detected if None.
            
        Returns:
            Self for method chaining.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Variables file not found: {path}")
        
        format = format or path.suffix[1:]
        content = path.read_text(encoding='utf-8')
        
        if format == 'yaml' or format == 'yml':
            from configgen.formats.yaml_handler import YAMLHandler
            vars_data = YAMLHandler().loads(content)
        elif format == 'json':
            from configgen.formats.json_handler import JSONHandler
            vars_data = JSONHandler().loads(content)
        elif format == 'toml':
            from configgen.formats.toml_handler import TOMLHandler
            vars_data = TOMLHandler().loads(content)
        elif format == 'env':
            from configgen.formats.env_handler import ENVHandler
            vars_data = ENVHandler().loads(content)
        else:
            raise ValueError(f"Unsupported variables format: {format}")
        
        self.set_variables(vars_data)
        return self
    
    def set_schema(self, schema: Dict[str, Any]) -> "ConfigGenerator":
        """
        Set a JSON Schema for validation.
        
        Args:
            schema: JSON Schema definition.
            
        Returns:
            Self for method chaining.
        """
        self._schema = schema
        self.validator.set_schema(schema)
        return self
    
    def load_schema(self, path: Union[str, Path]) -> "ConfigGenerator":
        """
        Load a JSON Schema from file.
        
        Args:
            path: Path to schema file.
            
        Returns:
            Self for method chaining.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Schema file not found: {path}")
        
        import json
        with open(path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        return self.set_schema(schema)
    
    def add_inheritance(
        self, 
        parent: Union[str, Path, Dict[str, Any]]
    ) -> "ConfigGenerator":
        """
        Add a parent configuration for inheritance.
        
        Args:
            parent: Parent template path, name, or dict.
            
        Returns:
            Self for method chaining.
        """
        if isinstance(parent, dict):
            self.inheritance_engine.add_parent(parent)
        elif isinstance(parent, (str, Path)):
            if Path(parent).exists():
                path = Path(parent)
                name = path.stem
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.inheritance_engine.add_parent({name: content})
            else:
                self.inheritance_engine.add_parent(parent)
        
        self._inheritance_chain.append(str(parent))
        return self
    
    def set_environment(self, env: str) -> "ConfigGenerator":
        """
        Set the target environment.
        
        Args:
            env: Environment name (development, staging, production, etc.)
            
        Returns:
            Self for method chaining.
        """
        self.env_manager.set_environment(env)
        env_vars = self.env_manager.get_environment_variables(env)
        self.set_variables(env_vars)
        return self
    
    def load_environment_variables(self) -> "ConfigGenerator":
        """
        Load variables from environment variables.
        
        Returns:
            Self for method chaining.
        """
        env_vars = self.env_manager.load_from_environment()
        self.set_variables(env_vars)
        return self
    
    def generate(
        self, 
        template_name: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate the final configuration.
        
        Args:
            template_name: Name of template to use. Uses first if None.
            variables: Additional variables to merge.
            
        Returns:
            Generated configuration as dictionary.
        """
        if not template_name and not self._templates:
            raise ValueError("No template loaded")
        
        template_name = template_name or list(self._templates.keys())[0]
        
        all_vars = self._variables.copy()
        if variables:
            all_vars.update(variables)
        
        merged_vars = self.inheritance_engine.merge_variables(all_vars)
        resolved_vars = self.variable_resolver.resolve(merged_vars)
        
        rendered = self.template_engine.render(template_name, resolved_vars)
        
        format_hint = self._detect_format(rendered, template_name)
        
        if format_hint == 'yaml':
            from configgen.formats.yaml_handler import YAMLHandler
            result = YAMLHandler().loads(rendered)
        elif format_hint == 'json':
            from configgen.formats.json_handler import JSONHandler
            result = JSONHandler().loads(rendered)
        elif format_hint == 'toml':
            from configgen.formats.toml_handler import TOMLHandler
            result = TOMLHandler().loads(rendered)
        elif format_hint == 'xml':
            from configgen.formats.xml_handler import XMLHandler
            result = XMLHandler().loads(rendered)
        else:
            raise ValueError(f"Could not detect format for: {template_name}")
        
        if self._schema:
            self.validator.validate(result)
        
        return result
    
    def _detect_format(self, content: str, template_name: str) -> str:
        """Detect configuration format from content or filename."""
        import re
        
        if template_name.endswith('.yaml') or template_name.endswith('.yml'):
            return 'yaml'
        elif template_name.endswith('.json'):
            return 'json'
        elif template_name.endswith('.toml'):
            return 'toml'
        elif template_name.endswith('.xml'):
            return 'xml'
        
        if content.strip().startswith('{') or content.strip().startswith('['):
            return 'json'
        elif content.strip().startswith('<'):
            return 'xml'
        elif content.strip().startswith('[') and '=' in content:
            return 'toml'
        
        return 'yaml'
    
    def generate_to_string(
        self,
        format: str,
        **kwargs
    ) -> str:
        """
        Generate configuration and return as formatted string.
        
        Args:
            format: Output format (yaml, json, toml, env, xml).
            **kwargs: Additional arguments passed to generate().
            
        Returns:
            Formatted configuration string.
        """
        config = self.generate(**kwargs)
        
        if format == 'yaml':
            from configgen.formats.yaml_handler import YAMLHandler
            return YAMLHandler().dumps(config, indent=self.config.output_indent)
        elif format == 'json':
            from configgen.formats.json_handler import JSONHandler
            return JSONHandler().dumps(config, indent=self.config.output_indent)
        elif format == 'toml':
            from configgen.formats.toml_handler import TOMLHandler
            return TOMLHandler().dumps(config)
        elif format == 'xml':
            from configgen.formats.xml_handler import XMLHandler
            return XMLHandler().dumps(config, indent=self.config.output_indent)
        elif format == 'env':
            from configgen.formats.env_handler import ENVHandler
            return ENVHandler().dumps(config)
        else:
            raise ValueError(f"Unsupported output format: {format}")
    
    def write(
        self,
        output_path: Union[str, Path],
        format: Optional[str] = None,
        **kwargs
    ) -> "ConfigGenerator":
        """
        Generate and write configuration to file.
        
        Args:
            output_path: Destination file path.
            format: Output format. Auto-detected from extension if None.
            **kwargs: Additional arguments passed to generate().
            
        Returns:
            Self for method chaining.
        """
        output_path = Path(output_path)
        
        if self.config.auto_create_dirs:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        format = format or output_path.suffix[1:] or self.config.default_format
        
        content = self.generate_to_string(format=format, **kwargs)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Configuration written to: {output_path}")
        return self
    
    def validate(self, config: Dict[str, Any]) -> bool:
        """
        Validate a configuration against the schema.
        
        Args:
            config: Configuration dictionary to validate.
            
        Returns:
            True if valid, raises ValidationError if not.
        """
        return self.validator.validate(config)
    
    def diff(
        self,
        config1: Dict[str, Any],
        config2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare two configurations and return differences.
        
        Args:
            config1: First configuration.
            config2: Second configuration.
            
        Returns:
            Dictionary containing added, removed, and changed keys.
        """
        return self._deep_diff(config1, config2)
    
    def _deep_diff(
        self,
        dict1: Dict[str, Any],
        dict2: Dict[str, Any],
        path: str = ""
    ) -> Dict[str, Any]:
        """Recursively compare two dictionaries."""
        result = {"added": {}, "removed": {}, "changed": {}}
        
        all_keys = set(dict1.keys()) | set(dict2.keys())
        
        for key in all_keys:
            current_path = f"{path}.{key}" if path else key
            
            if key not in dict1:
                result["added"][current_path] = dict2[key]
            elif key not in dict2:
                result["removed"][current_path] = dict1[key]
            elif dict1[key] != dict2[key]:
                if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                    nested = self._deep_diff(dict1[key], dict2[key], current_path)
                    result["added"].update(nested["added"])
                    result["removed"].update(nested["removed"])
                    result["changed"].update(nested["changed"])
                else:
                    result["changed"][current_path] = {
                        "old": dict1[key],
                        "new": dict2[key]
                    }
        
        return result
    
    def reset(self) -> "ConfigGenerator":
        """
        Reset the generator to initial state.
        
        Returns:
            Self for method chaining.
        """
        self._templates.clear()
        self._variables.clear()
        self._schema = None
        self._inheritance_chain.clear()
        self.template_engine.clear_cache()
        self.inheritance_engine.clear()
        return self
    
    @property
    def templates(self) -> List[str]:
        """List loaded template names."""
        return list(self._templates.keys())
    
    @property
    def variables(self) -> Dict[str, Any]:
        """Get current variables (sensitive values hidden)."""
        return self.variable_resolver.get_safe_variables()
