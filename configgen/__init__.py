"""
ConfigGen - Dynamic Configuration File Generator

A powerful, flexible configuration generator supporting multiple formats,
template inheritance, schema validation, and environment-specific configurations.
"""

__version__ = "1.0.0"
__author__ = "ConfigGen Contributors"

from configgen.core import ConfigGenerator
from configgen.template import TemplateEngine
from configgen.validator import SchemaValidator
from configgen.environment import EnvironmentManager
from configgen.formats import FormatRegistry

__all__ = [
    "ConfigGenerator",
    "TemplateEngine", 
    "SchemaValidator",
    "EnvironmentManager",
    "FormatRegistry",
]
