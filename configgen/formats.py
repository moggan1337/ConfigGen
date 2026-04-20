"""
Format Registry Module

Registry for configuration format handlers.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type


logger = logging.getLogger(__name__)


class FormatHandler(ABC):
    """Abstract base class for format handlers."""
    
    @abstractmethod
    def loads(self, content: str) -> Dict[str, Any]:
        """Parse a string into a dictionary."""
        pass
    
    @abstractmethod
    def dumps(self, data: Dict[str, Any], **kwargs) -> str:
        """Serialize a dictionary to a string."""
        pass
    
    def load(self, path: str) -> Dict[str, Any]:
        """Load from a file."""
        with open(path, 'r', encoding='utf-8') as f:
            return self.loads(f.read())
    
    def dump(self, data: Dict[str, Any], path: str, **kwargs) -> None:
        """Save to a file."""
        content = self.dumps(data, **kwargs)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)


class YAMLHandler(FormatHandler):
    """YAML format handler using pyyaml."""
    
    def __init__(self):
        self._yaml = None
        self._safe_loader = None
        try:
            import yaml
            self._yaml = yaml
            self._safe_loader = yaml.SafeLoader
        except ImportError:
            logger.warning("PyYAML not installed. Using fallback parser.")
    
    def loads(self, content: str) -> Dict[str, Any]:
        if self._yaml:
            return self._yaml.safe_load(content) or {}
        return self._fallback_parse(content)
    
    def dumps(self, data: Dict[str, Any], indent: int = 2, **kwargs) -> str:
        if self._yaml:
            return self._yaml.dump(data, default_flow_style=False, indent=indent, **kwargs)
        import json
        return json.dumps(data, indent=indent)
    
    def _fallback_parse(self, content: str) -> Dict[str, Any]:
        """Simple YAML-like parser fallback."""
        result = {}
        lines = content.split('\n')
        current_indent = 0
        current_dict = result
        
        for line in lines:
            stripped = line.lstrip()
            if not stripped or stripped.startswith('#'):
                continue
            
            indent = len(line) - len(stripped)
            key, _, value = stripped.partition(':')
            key = key.strip()
            value = value.strip()
            
            if value:
                current_dict[key] = value.strip('"\'')
            else:
                current_dict[key] = {}
                current_dict = current_dict[key]
        
        return result


class JSONHandler(FormatHandler):
    """JSON format handler."""
    
    def __init__(self):
        import json
        self._json = json
    
    def loads(self, content: str) -> Dict[str, Any]:
        return self._json.loads(content)
    
    def dumps(self, data: Dict[str, Any], indent: int = 2, **kwargs) -> str:
        return self._json.dumps(data, indent=indent, **kwargs)


class TOMLHandler(FormatHandler):
    """TOML format handler."""
    
    def __init__(self):
        self._toml = None
        try:
            import tomllib
            self._toml = tomllib
        except ImportError:
            try:
                import tomli
                self._toml = tomli
            except ImportError:
                try:
                    import toml
                    self._toml = toml
                except ImportError:
                    logger.warning("TOML library not installed. Using fallback.")
    
    def loads(self, content: str) -> Dict[str, Any]:
        if self._toml:
            if hasattr(self._toml, 'loads'):
                return self._toml.loads(content)
            elif hasattr(self._toml, 'load'):
                import io
                return self._toml.load(io.StringIO(content))
        return self._fallback_parse(content)
    
    def dumps(self, data: Dict[str, Any], **kwargs) -> str:
        try:
            import tomli_w
            return tomli_w.dumps(data)
        except ImportError:
            try:
                import toml
                return toml.dumps(data)
            except ImportError:
                return self._fallback_dumps(data)
    
    def _fallback_parse(self, content: str) -> Dict[str, Any]:
        """Simple TOML-like parser."""
        result = {}
        current_section = result
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line.startswith('[') and line.endswith(']'):
                section_name = line[1:-1].strip()
                if '.' in section_name:
                    parts = section_name.split('.')
                    current = result
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current_section = current[parts[-1]] = {}
                else:
                    if section_name not in result:
                        result[section_name] = {}
                    current_section = result[section_name]
            elif '=' in line:
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip().strip('"\'')
                current_section[key] = value
        
        return result
    
    def _fallback_dumps(self, data: Dict[str, Any]) -> str:
        """Fallback TOML serializer."""
        lines = ["# Fallback TOML output"]
        self._dict_to_toml(data, lines, 0)
        return '\n'.join(lines)
    
    def _dict_to_toml(self, data: Dict[str, Any], lines: list, depth: int) -> None:
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{'    ' * depth}[{key}]")
                self._dict_to_toml(value, lines, depth + 1)
            else:
                val_str = f'"{value}"' if isinstance(value, str) else str(value)
                lines.append(f"{'    ' * depth}{key} = {val_str}")


class XMLHandler(FormatHandler):
    """XML format handler."""
    
    def __init__(self):
        self._etree = None
        try:
            import xml.etree.ElementTree as etree
            self._etree = etree
        except ImportError:
            logger.warning("xml.etree not available")
    
    def loads(self, content: str) -> Dict[str, Any]:
        if self._etree:
            root = self._etree.fromstring(content)
            return self._xml_to_dict(root)
        return {}
    
    def dumps(self, data: Dict[str, Any], indent: int = 2, **kwargs) -> str:
        if self._etree:
            root = self._dict_to_xml('config', data)
            return self._etree.tostring(root, encoding='unicode')
        return '<config/>'
    
    def _xml_to_dict(self, element) -> Dict[str, Any]:
        result = {}
        
        if element.attrib:
            result['@attributes'] = element.attrib
        
        if element.text and element.text.strip():
            if len(element) == 0:
                return element.text.strip()
            result['#text'] = element.text.strip()
        
        for child in element:
            child_data = self._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result
    
    def _dict_to_xml(self, tag: str, data: Dict[str, Any]):
        if self._etree is None:
            return None
        
        element = self._etree.Element(tag)
        
        for key, value in data.items():
            if key.startswith('@'):
                element.set(key[1:], str(value))
            elif key == '#text':
                element.text = str(value)
            elif isinstance(value, dict):
                child = self._dict_to_xml(key, value)
                element.append(child)
            elif isinstance(value, list):
                for item in value:
                    child = self._dict_to_xml(key, item if isinstance(item, dict) else {'#text': item})
                    element.append(child)
            else:
                child = self._etree.SubElement(element, key)
                child.text = str(value)
        
        return element


class ENVHandler(FormatHandler):
    """ENV/INI format handler."""
    
    def loads(self, content: str) -> Dict[str, Any]:
        result = {}
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#') or line.startswith(';'):
                continue
            
            if '=' in line:
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip()
                
                result[key] = value.strip('"\'')
        
        return result
    
    def dumps(self, data: Dict[str, Any], **kwargs) -> str:
        lines = []
        
        for key, value in data.items():
            key = key.upper().replace('.', '_').replace('-', '_')
            
            if isinstance(value, str) and (' ' in value or '"' in value):
                value = f'"{value}"'
            
            lines.append(f"{key}={value}")
        
        return '\n'.join(lines)


class FormatRegistry:
    """
    Registry for configuration format handlers.
    
    Provides unified access to different format handlers.
    """
    
    HANDLERS = {
        'yaml': YAMLHandler,
        'yml': YAMLHandler,
        'json': JSONHandler,
        'toml': TOMLHandler,
        'xml': XMLHandler,
        'env': ENVHandler,
        'ini': ENVHandler,
    }
    
    def __init__(self):
        self._handlers: Dict[str, FormatHandler] = {}
        self._load_default_handlers()
    
    def _load_default_handlers(self) -> None:
        """Load default format handlers."""
        for format_name, handler_class in self.HANDLERS.items():
            try:
                self._handlers[format_name] = handler_class()
            except Exception as e:
                logger.warning(f"Failed to load {format_name} handler: {e}")
    
    def get_handler(self, format_name: str) -> Optional[FormatHandler]:
        """
        Get a handler for the specified format.
        
        Args:
            format_name: Format name (yaml, json, toml, etc.)
            
        Returns:
            FormatHandler instance or None.
        """
        format_name = format_name.lower()
        
        if format_name not in self._handlers:
            if format_name in self.HANDLERS:
                try:
                    self._handlers[format_name] = self.HANDLERS[format_name]()
                except Exception:
                    return None
        
        return self._handlers.get(format_name)
    
    def register_handler(
        self,
        format_name: str,
        handler_class: Type[FormatHandler]
    ) -> "FormatRegistry":
        """
        Register a custom format handler.
        
        Args:
            format_name: Format identifier.
            handler_class: FormatHandler subclass.
            
        Returns:
            Self for method chaining.
        """
        self._handlers[format_name] = handler_class()
        self.HANDLERS[format_name] = handler_class
        return self
    
    def list_formats(self) -> list:
        """List all registered formats."""
        return list(self._handlers.keys())
    
    def get_extensions(self) -> list:
        """Get all supported file extensions."""
        return list(self.HANDLERS.keys())
