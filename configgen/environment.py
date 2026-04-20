"""
Environment Manager Module

Handles environment-specific configuration and variable loading.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field


logger = logging.getLogger(__name__)


@dataclass
class EnvironmentConfig:
    """Configuration for a specific environment."""
    name: str
    variables: Dict[str, Any] = field(default_factory=dict)
    extends: Optional[str] = None
    priority: int = 0


class EnvironmentManager:
    """
    Manages environment-specific configurations.
    
    Features:
    - Multiple environment support (dev, staging, prod, etc.)
    - Environment inheritance
    - Priority-based variable resolution
    - Environment variable loading
    - Dotenv file support
    """
    
    DEFAULT_ENVIRONMENTS = {
        'development': EnvironmentConfig(name='development', priority=10),
        'staging': EnvironmentConfig(name='staging', priority=20),
        'production': EnvironmentConfig(name='production', priority=30),
    }
    
    def __init__(self, prefix: str = "CONFIGGEN"):
        """
        Initialize the environment manager.
        
        Args:
            prefix: Environment variable prefix for loading.
        """
        self._prefix = prefix
        self._environments: Dict[str, EnvironmentConfig] = self.DEFAULT_ENVIRONMENTS.copy()
        self._current_env: Optional[str] = None
        self._dotenv_files: List[Path] = []
        
        logger.debug(f"EnvironmentManager initialized (prefix={prefix})")
    
    def set_environment(self, name: str) -> "EnvironmentManager":
        """
        Set the active environment.
        
        Args:
            name: Environment name.
            
        Returns:
            Self for method chaining.
        """
        if name not in self._environments:
            self._environments[name] = EnvironmentConfig(name=name)
        
        self._current_env = name
        logger.info(f"Environment set to: {name}")
        return self
    
    def add_environment(
        self,
        name: str,
        variables: Optional[Dict[str, Any]] = None,
        extends: Optional[str] = None,
        priority: int = 0
    ) -> "EnvironmentManager":
        """
        Add a new environment configuration.
        
        Args:
            name: Environment name.
            variables: Environment-specific variables.
            extends: Parent environment to inherit from.
            priority: Resolution priority (higher wins).
            
        Returns:
            Self for method chaining.
        """
        self._environments[name] = EnvironmentConfig(
            name=name,
            variables=variables or {},
            extends=extends,
            priority=priority
        )
        return self
    
    def update_environment(
        self,
        name: str,
        variables: Dict[str, Any]
    ) -> "EnvironmentManager":
        """
        Update variables for an existing environment.
        
        Args:
            name: Environment name.
            variables: Variables to add/update.
            
        Returns:
            Self for method chaining.
        """
        if name not in self._environments:
            self._environments[name] = EnvironmentConfig(name=name)
        
        self._environments[name].variables.update(variables)
        return self
    
    def get_environment_variables(
        self,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get resolved variables for an environment.
        
        Applies inheritance chain and returns all variables.
        
        Args:
            name: Environment name (uses current if None).
            
        Returns:
            Dictionary of resolved variables.
        """
        name = name or self._current_env or 'development'
        
        if name not in self._environments:
            logger.warning(f"Unknown environment: {name}")
            return {}
        
        env = self._environments[name]
        resolved = {}
        
        if env.extends:
            parent_vars = self.get_environment_variables(env.extends)
            resolved.update(parent_vars)
        
        resolved.update(env.variables)
        
        return resolved
    
    def get_current_variables(self) -> Dict[str, Any]:
        """
        Get variables for the current environment.
        
        Returns:
            Dictionary of current environment variables.
        """
        return self.get_environment_variables(self._current_env)
    
    def load_from_environment(self) -> Dict[str, Any]:
        """
        Load variables from environment variables.
        
        Filters variables with the configured prefix.
        
        Returns:
            Dictionary of matching environment variables.
        """
        result = {}
        prefix = self._prefix.upper()
        
        for key, value in os.environ.items():
            if key.startswith(f"{prefix}_"):
                var_name = key[len(prefix) + 1:].lower()
                result[var_name] = self._parse_value(value)
            elif key.startswith(f"{prefix}"):
                var_name = key[len(prefix):].lower()
                if var_name:
                    var_name = var_name[1:].lower() if var_name[0] == '_' else var_name
                    result[var_name] = self._parse_value(value)
        
        logger.debug(f"Loaded {len(result)} variables from environment")
        return result
    
    def load_dotenv(
        self,
        path: Optional[str] = None,
        override: bool = False
    ) -> Dict[str, Any]:
        """
        Load variables from a .env file.
        
        Args:
            path: Path to .env file. Uses default locations if None.
            override: If True, existing variables are overridden.
            
        Returns:
            Dictionary of loaded variables.
        """
        paths_to_try = []
        
        if path:
            paths_to_try.append(Path(path))
        else:
            default_locations = [
                Path.cwd() / '.env',
                Path.cwd() / 'config' / '.env',
                Path(__file__).parent.parent.parent / '.env',
            ]
            paths_to_try.extend(default_locations)
        
        result = {}
        
        for env_path in paths_to_try:
            if env_path.exists():
                variables = self._parse_dotenv_file(env_path)
                result.update(variables)
                self._dotenv_files.append(env_path)
                logger.info(f"Loaded .env from: {env_path}")
        
        return result
    
    def _parse_dotenv_file(self, path: Path) -> Dict[str, Any]:
        """Parse a .env file."""
        result = {}
        
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue
                
                if '=' in line:
                    key, _, value = line.partition('=')
                    key = key.strip()
                    value = value.strip()
                    
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    result[key.lower()] = self._parse_value(value)
        
        return result
    
    def _parse_value(self, value: str) -> Any:
        """Parse a string value to appropriate type."""
        value = value.strip()
        
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        elif value.lower() == 'null' or value.lower() == 'none':
            return None
        
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            return value
    
    def merge_environments(
        self,
        *env_names: str
    ) -> Dict[str, Any]:
        """
        Merge variables from multiple environments.
        
        Later environments override earlier ones.
        
        Args:
            *env_names: Environment names to merge.
            
        Returns:
            Merged variables dictionary.
        """
        result = {}
        
        for name in env_names:
            env_vars = self.get_environment_variables(name)
            result.update(env_vars)
        
        return result
    
    def list_environments(self) -> List[str]:
        """List all configured environment names."""
        return list(self._environments.keys())
    
    def get_environment_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an environment.
        
        Args:
            name: Environment name.
            
        Returns:
            Environment info dict or None.
        """
        if name not in self._environments:
            return None
        
        env = self._environments[name]
        return {
            'name': env.name,
            'extends': env.extends,
            'priority': env.priority,
            'variable_count': len(env.variables),
        }
    
    def remove_environment(self, name: str) -> bool:
        """
        Remove an environment configuration.
        
        Args:
            name: Environment name.
            
        Returns:
            True if removed, False if not found.
        """
        if name in self._environments:
            del self._environments[name]
            return True
        return False
    
    def export_to_dotenv(
        self,
        variables: Dict[str, Any],
        path: Path,
        include_prefix: bool = True
    ) -> "EnvironmentManager":
        """
        Export variables to a .env file.
        
        Args:
            variables: Variables to export.
            path: Output file path.
            include_prefix: Include environment prefix in keys.
            
        Returns:
            Self for method chaining.
        """
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"# Generated by ConfigGen\n")
            f.write(f"# Environment: {self._current_env or 'default'}\n")
            f.write(f"# Generated at: {__import__('datetime').datetime.now().isoformat()}\n\n")
            
            for key, value in sorted(variables.items()):
                if include_prefix:
                    key = f"{self._prefix}_{key.upper()}"
                
                if isinstance(value, str):
                    if ' ' in value or '"' in value:
                        value = f'"{value}"'
                
                f.write(f"{key}={value}\n")
        
        logger.info(f"Exported {len(variables)} variables to: {path}")
        return self
