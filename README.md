# ConfigGen - Dynamic Configuration File Generator

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/moggan1337/ConfigGen)

**ConfigGen** is a powerful, flexible configuration generator that supports multiple formats, template inheritance, schema validation, and environment-specific configurations.

[Features](#features) • [Architecture](#architecture) • [Installation](#installation) • [Quick Start](#quick-start) • [Usage](#usage) • [API Reference](#api-reference) • [Configuration Options](#configuration-options) • [Troubleshooting](#troubleshooting)

</div>

---

## 🎬 Demo
![ConfigGen Demo](demo.gif)

*Generate configs from templates with inheritance*

## Screenshots
| Component | Preview |
|-----------|---------|
| Template Editor | ![template](screenshots/template-editor.png) |
| Config Preview | ![preview](screenshots/config-preview.png) |
| Environment Diff | ![diff](screenshots/env-diff.png) |

## Visual Description
Template editor shows inheritance hierarchies with nested variable substitution. Config preview renders final output with syntax highlighting. Environment diff highlights differences between dev/staging/prod.

---


## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Templates](#templates)
  - [Variables](#variables)
  - [Environment-Specific Configs](#environment-specific-configs)
  - [Schema Validation](#schema-validation)
  - [Format Conversion](#format-conversion)
- [API Reference](#api-reference)
- [Configuration Options](#configuration-options)
- [CLI Reference](#cli-reference)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### 🔧 Core Features

| Feature | Description |
|---------|-------------|
| **Multi-Format Support** | Generate configs in YAML, JSON, TOML, XML, and ENV formats |
| **Template Engine** | Jinja2-style templates with custom filters and functions |
| **Variable Inheritance** | Hierarchical config inheritance with deep merging |
| **Schema Validation** | JSON Schema-based validation with detailed error reporting |
| **Environment Management** | Environment-specific configs (dev, staging, prod, custom) |
| **Sensitive Value Handling** | Mask sensitive values in logs and output |
| **CLI Interface** | Full command-line tool for scripting and automation |

### 🎯 Advanced Features

- **Variable Interpolation**: `${variable}` and `${variable:default}` syntax
- **Custom Filters**: Register custom template filters for transformations
- **Deep Merging**: Smart merging of nested configurations
- **Conflict Detection**: Identify conflicting keys in inheritance chains
- **Dotenv Support**: Load variables from `.env` files
- **Cache Management**: Template caching for improved performance
- **Config Diff**: Compare two configurations and show differences

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ConfigGen Architecture                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────┐                   │
│  │   CLI       │───▶│ ConfigGenerator│───▶│ Output Handler │                   │
│  │   Input     │    │   (Orchestrator)│    │  (Multi-format)│                   │
│  └─────────────┘    └──────────────┘    └────────────────┘                   │
│                            │                                                  │
│         ┌──────────────────┼──────────────────┐                              │
│         ▼                  ▼                  ▼                              │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────┐                      │
│  │  Template   │    │   Variable   │    │ Environment │                      │
│  │   Engine    │    │   Resolver   │    │   Manager   │                      │
│  └─────────────┘    └──────────────┘    └─────────────┘                      │
│         │                  │                  │                              │
│         ▼                  ▼                  ▼                              │
│  ┌──────────────────────────────────────────────────────┐                    │
│  │               Inheritance Engine                      │                    │
│  │         (Hierarchical Config Merging)                 │                    │
│  └──────────────────────────────────────────────────────┘                    │
│                            │                                                  │
│                            ▼                                                  │
│                   ┌────────────────┐                                        │
│                   │ Schema         │                                        │
│                   │ Validator      │                                        │
│                   └────────────────┘                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Descriptions

#### 1. **ConfigGenerator** (`core.py`)

The main orchestrator class that coordinates all components:

```
ConfigGenerator
├── TemplateEngine    → Template loading, rendering, caching
├── VariableResolver  → Variable substitution, expression evaluation
├── EnvironmentManager → Environment-specific configs
├── InheritanceEngine → Configuration merging and inheritance
├── SchemaValidator   → JSON Schema validation
└── FormatRegistry    → Multi-format serialization
```

#### 2. **TemplateEngine** (`template.py`)

Handles template processing with support for:

- **Jinja2 Syntax**: `{{ variable }}`, `{% if %}`, `{% for %}`
- **Custom Filters**: `{{ name | upper }}`, `{{ value | default:'N/A' }}`
- **Includes**: `{% include 'partial.j2' %}`
- **Globals**: `{{ now() }}`, `{{ env('VAR') }}`

#### 3. **VariableResolver** (`variables.py`)

Provides flexible variable substitution:

- **Basic Substitution**: `${variable}`
- **Default Values**: `${variable:default}`
- **Nested Access**: `${config.database.host}`
- **Pipes/Filters**: `${email | lower}`
- **Functions**: `${count | int}`, `${name | default:'Guest'}`

#### 4. **EnvironmentManager** (`environment.py`)

Manages environment-specific configurations:

- **Built-in Environments**: development, staging, production
- **Custom Environments**: Define your own
- **Inheritance**: `staging extends development`
- **Priority-based Resolution**: Higher priority wins in conflicts
- **Dotenv Loading**: `.env` file support

#### 5. **SchemaValidator** (`validator.py`)

JSON Schema-based validation supporting:

- **Type Checking**: string, number, integer, boolean, array, object, null
- **Required Fields**: Enforce mandatory properties
- **Constraints**: minLength, maxLength, minimum, maximum, pattern, enum
- **Format Validation**: date, email, uri, uuid, hostname, ipv4, ipv6
- **Custom Validators**: Register custom validation functions
- **Detailed Errors**: Path, message, expected value, actual value

#### 6. **FormatRegistry** (`formats.py`)

Unified interface for multiple config formats:

| Format | Extension | Handler Class |
|--------|-----------|---------------|
| YAML | `.yaml`, `.yml` | `YAMLHandler` |
| JSON | `.json` | `JSONHandler` |
| TOML | `.toml` | `TOMLHandler` |
| XML | `.xml` | `XMLHandler` |
| ENV | `.env`, `.ini` | `ENVHandler` |

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Standard Installation

```bash
# Install from PyPI (when published)
pip install configgen

# Or install from source
git clone https://github.com/moggan1337/ConfigGen.git
cd ConfigGen
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/moggan1337/ConfigGen.git
cd ConfigGen
pip install -e ".[dev]"
```

### Optional Dependencies

```bash
# TOML support (recommended for production)
pip install configgen[toml]

# All optional dependencies
pip install configgen[dev,toml]
```

---

## Quick Start

### 1. Create a Simple Template

Create `app.yaml.j2`:

```yaml
application:
  name: ${app_name}
  version: ${version}
  environment: ${environment:development}

database:
  host: ${db_host:localhost}
  port: ${db_port:5432}
  name: ${db_name:myapp}
  user: ${db_user}
  password: ${db_password}

server:
  host: ${server_host:0.0.0.0}
  port: ${server_port:8080}
  debug: ${debug:false}

logging:
  level: ${log_level:INFO}
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### 2. Generate Configuration

```python
from configgen import ConfigGenerator

generator = ConfigGenerator()
generator.load_template("app.yaml.j2")
generator.set_variables({
    "app_name": "MyApplication",
    "version": "2.0.0",
    "db_host": "db.example.com",
    "db_user": "admin",
    "db_password": "secret123",
    "server_port": 9000,
    "debug": True
})

config = generator.generate()
print(config)
```

**Output:**

```yaml
application:
  name: MyApplication
  version: 2.0.0
  environment: development

database:
  host: db.example.com
  port: 5432
  name: myapp
  user: admin
  password: secret123

server:
  host: 0.0.0.0
  port: 9000
  debug: true

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### 3. Write to File

```python
generator.write("config/production.yaml", format="yaml")
```

---

## Usage

### Templates

#### Basic Template Syntax

```jinja2
# Variables
{{ variable_name }}
{{ nested.variable.path }}

# With default value
{{ variable_name:default_value }}

# Filters
{{ name | upper }}
{{ count | int }}
{{ value | default:'N/A' }}

# Conditionals
{% if debug %}
debug: true
{% else %}
debug: false
{% endif %}

# Loops
{% for item in items %}
- {{ item }}
{% endfor %}

# Comments
{# This is a comment #}
```

#### Template with Logic

```yaml
# config.yaml.j2
database:
  {% if environment == 'production' %}
  host: prod-db.internal
  ssl: true
  {% else %}
  host: localhost
  ssl: false
  {% endif %}
  port: {{ db_port | default:5432 }}

features:
  {% for feature in enabled_features %}
  - name: {{ feature.name }}
    enabled: {{ feature.enabled | default:true }}
  {% endfor %}

metadata:
  generated: "{{ now() }}"
  environment: "{{ environment }}"
```

### Variables

#### Variable Sources

```python
from configgen import ConfigGenerator

generator = ConfigGenerator()

# 1. Direct assignment
generator.set_variables({
    "app_name": "MyApp",
    "version": "1.0.0"
})

# 2. Individual variable
generator.add_variable("debug", True, sensitive=False)

# 3. From file (YAML, JSON, TOML, ENV)
generator.load_variables_from_file("vars.yaml")

# 4. From environment variables (CONFIGGEN_* prefix)
generator.load_environment_variables()

# 5. From environment (development, staging, production)
generator.set_environment("production")
```

#### Variable Interpolation

```python
# Basic substitution
generator.set_variables({
    "base_url": "https://api.example.com",
    "endpoint": "/users",
    "full_url": "${base_url}${endpoint}"  # Resolved automatically
})

# With defaults
template_content = """
database:
  host: ${db_host:localhost}
  port: ${db_port:5432}
"""

# Nested access
generator.set_variables({
    "config": {
        "database": {
            "host": "db.example.com"
        }
    }
})
# Access as ${config.database.host}

# Filters in variables
# ${name | upper} - Convert to uppercase
# ${count | int} - Convert to integer
# ${value | default:'N/A'} - Use default if empty
```

#### Sensitive Variables

```python
# Mark sensitive variables (masked in logs)
generator.add_variable("api_key", "secret-key-12345", sensitive=True)
generator.add_variable("password", "supersecret", sensitive=True)

# Access safe version (values masked)
safe_vars = generator.variables
# {'api_key': '***MASKED***', 'password': '***MASKED***', ...}
```

### Environment-Specific Configs

#### Setting Up Environments

```python
from configgen import EnvironmentManager

env_manager = EnvironmentManager(prefix="MYAPP")

# Add environments with variables
env_manager.add_environment(
    name="development",
    variables={
        "debug": True,
        "log_level": "DEBUG",
        "db_host": "localhost"
    }
)

env_manager.add_environment(
    name="staging",
    extends="development",  # Inherit from development
    variables={
        "debug": False,
        "log_level": "INFO",
        "db_host": "staging-db.internal"
    },
    priority=20
)

env_manager.add_environment(
    name="production",
    extends="staging",
    variables={
        "debug": False,
        "log_level": "WARNING",
        "db_host": "prod-db.internal",
        "enable_ssl": True
    },
    priority=30
)
```

#### Using Environments

```python
from configgen import ConfigGenerator

generator = ConfigGenerator()

# Set environment
generator.set_environment("production")

# Or manually load environment variables
env_vars = env_manager.get_environment_variables("production")
generator.set_variables(env_vars)
```

#### Loading from Environment Variables

```bash
# Set environment variables with prefix
export CONFIGGEN_DB_HOST=db.example.com
export CONFIGGEN_DB_PORT=5432
export CONFIGGEN_API_KEY=your-api-key
```

```python
# Load all CONFIGGEN_* variables
generator.load_environment_variables()
```

#### Dotenv Support

```python
# Load from .env file
env_manager.load_dotenv()

# Load from specific path
env_manager.load_dotenv("/path/to/custom.env")

# Export variables to .env
env_manager.export_to_dotenv(
    variables={"DEBUG": True, "PORT": 8080},
    path=Path(".env")
)
```

### Schema Validation

#### Defining a Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ApplicationConfig",
  "type": "object",
  "required": ["application", "database", "server"],
  "properties": {
    "application": {
      "type": "object",
      "required": ["name", "version"],
      "properties": {
        "name": {
          "type": "string",
          "minLength": 1,
          "maxLength": 100
        },
        "version": {
          "type": "string",
          "pattern": "^\\d+\\.\\d+\\.\\d+$"
        },
        "environment": {
          "type": "string",
          "enum": ["development", "staging", "production"]
        }
      }
    },
    "database": {
      "type": "object",
      "required": ["host", "port", "name"],
      "properties": {
        "host": {
          "type": "string",
          "format": "hostname"
        },
        "port": {
          "type": "integer",
          "minimum": 1,
          "maximum": 65535
        },
        "name": {
          "type": "string"
        },
        "ssl": {
          "type": "boolean",
          "default": false
        }
      }
    },
    "server": {
      "type": "object",
      "properties": {
        "host": {
          "type": "string",
          "default": "0.0.0.0"
        },
        "port": {
          "type": "integer",
          "minimum": 1024,
          "maximum": 65535
        }
      }
    }
  }
}
```

#### Using Schema Validation

```python
from configgen import ConfigGenerator

generator = ConfigGenerator()

# Load schema from file
generator.load_schema("schema.json")

# Or set directly
generator.set_schema({
    "type": "object",
    "required": ["name"],
    "properties": {
        "name": {"type": "string"}
    }
})

# Generate config (validation runs automatically)
try:
    config = generator.generate()
    print("Configuration is valid!")
except Exception as e:
    print(f"Validation failed: {e}")

# Manual validation
is_valid = generator.validate(config_data)
```

#### Custom Validators

```python
from configgen import SchemaValidator

validator = SchemaValidator(strict=True)

# Register custom validator
def validate_port_range(value, schema, path):
    if value < 1024 or value > 65535:
        raise ValueError(f"{path}: Port must be between 1024 and 65535")

validator.register_validator("port-range", validate_port_range)

# Use in schema with x-validator
schema = {
    "type": "object",
    "properties": {
        "port": {
            "type": "integer",
            "x-validator": "port-range"
        }
    }
}
```

### Format Conversion

```python
from configgen import ConfigGenerator
from configgen.formats import FormatRegistry

generator = ConfigGenerator()
generator.load_template("config.yaml.j2")
generator.set_variables({"name": "MyApp"})

# Generate as different formats
yaml_output = generator.generate_to_string(format="yaml")
json_output = generator.generate_to_string(format="json")
toml_output = generator.generate_to_string(format="toml")
xml_output = generator.generate_to_string(format="xml")
env_output = generator.generate_to_string(format="env")

# Direct format registry usage
registry = FormatRegistry()
yaml_handler = registry.get_handler("yaml")
json_handler = registry.get_handler("json")

# Load from any format
config = yaml_handler.load("config.yaml")
```

---

## API Reference

### ConfigGenerator

```python
from configgen import ConfigGenerator

# Initialization
generator = ConfigGenerator(config=None)

# Configuration
generator.config  # GeneratorConfig instance

# Template Management
generator.load_template(path, name=None)      # Load from file
generator.load_template_string(content, name) # Load from string
generator.templates  # List loaded templates

# Variable Management
generator.set_variables(variables)            # Set multiple variables
generator.add_variable(key, value, sensitive=False)  # Add single variable
generator.load_variables_from_file(path, format=None)  # Load from file
generator.variables  # Get current variables (safe)

# Environment Management
generator.set_environment(env_name)           # Set target environment
generator.load_environment_variables()        # Load from env vars

# Schema/Validation
generator.set_schema(schema)                 # Set JSON Schema
generator.load_schema(path)                  # Load schema from file
generator.validate(config)                   # Validate config

# Generation
generator.generate(template_name=None, variables=None)      # Generate dict
generator.generate_to_string(format="yaml", **kwargs)        # Generate string
generator.write(output_path, format=None, **kwargs)          # Write to file

# Utility
generator.diff(config1, config2)            # Compare configs
generator.reset()                            # Reset state
```

### GeneratorConfig

```python
from configgen import GeneratorConfig

config = GeneratorConfig(
    default_format="yaml",       # Default output format
    strict_validation=True,      # Raise on validation errors
    allow_missing_variables=False,  # Allow unresolved variables
    auto_create_dirs=True,       # Create output directories
    cache_templates=True,        # Cache compiled templates
    output_indent=2,             # Indentation for output
    include_comments=True,       # Include generated comments
    env_prefix="CONFIGGEN",     # Environment variable prefix
    default_environment="development"  # Default environment
)
```

### TemplateEngine

```python
from configgen import TemplateEngine
from configgen.template import TemplateSyntax

engine = TemplateEngine(cache=True, syntax=TemplateSyntax.JINJA2)

# Template Management
engine.register_template(name, content, syntax=None)  # Register template
engine.render(name, variables=None)                     # Render template
engine.list_templates()                                 # List templates
engine.get_template_info(name)                          # Get template info

# Customization
engine.register_filter(name, function)                  # Add filter
engine.register_function(name, function)              # Add global function
engine.add_include_path(path)                           # Add include path

# Cache
engine.clear_cache()                                    # Clear template cache
```

### SchemaValidator

```python
from configgen import SchemaValidator

validator = SchemaValidator(strict=True)

# Schema Management
validator.set_schema(schema)                 # Set JSON Schema
validator.register_validator(name, func)     # Register custom validator

# Validation
validator.validate(data)                      # Validate data
validator.get_errors()                        # Get validation errors
```

### EnvironmentManager

```python
from configgen import EnvironmentManager

manager = EnvironmentManager(prefix="CONFIGGEN")

# Environment Management
manager.add_environment(name, variables=None, extends=None, priority=0)
manager.set_environment(name)
manager.remove_environment(name)
manager.list_environments()

# Variable Access
manager.get_environment_variables(name=None)       # Get env variables
manager.get_current_variables()                     # Current env variables
manager.load_from_environment()                      # Load from system env
manager.load_dotenv(path=None, override=False)     # Load .env file

# Export
manager.export_to_dotenv(variables, path, include_prefix=True)
```

### VariableResolver

```python
from configgen import VariableResolver

resolver = VariableResolver(allow_missing=False)

# Variable Management
resolver.update_variables(variables)
resolver.add_variable(key, value, sensitive=False)
resolver.get_variable(key, default=None)
resolver.remove_variable(key)

# Resolution
resolver.resolve(data, max_depth=10)

# Sensitive Values
resolver.get_safe_variables()      # Get with masked values
resolver.mark_sensitive(*keys)      # Mark as sensitive
resolver.unmark_sensitive(*keys)   # Unmark sensitive
resolver.list_sensitive()          # List sensitive keys

# Custom Functions
resolver.register_function(name, func)
```

### InheritanceEngine

```python
from configgen import InheritanceEngine

engine = InheritanceEngine()

# Parent Management
engine.add_parent(parent_dict)
engine.add_parent_override(key)     # Mark key as override-only
engine.set_merge_strategy("deep")    # deep, shallow, or replace

# Merging
engine.merge_variables(variables)    # Merge with parents

# Utility
engine.resolve_inheritance_chain()   # Get parent chain
engine.detect_conflicts(parent, child)
engine.clear()
```

---

## Configuration Options

### Generator Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `default_format` | str | `"yaml"` | Default output format |
| `strict_validation` | bool | `True` | Raise on validation errors |
| `allow_missing_variables` | bool | `False` | Allow unresolved variables |
| `auto_create_dirs` | bool | `True` | Create output directories |
| `cache_templates` | bool | `True` | Cache compiled templates |
| `output_indent` | int | `2` | Indentation spaces |
| `include_comments` | bool | `True` | Include generation comments |
| `env_prefix` | str | `"CONFIGGEN"` | Env variable prefix |
| `default_environment` | str | `"development"` | Default environment |

### Template Filters

| Filter | Description | Example |
|--------|-------------|---------|
| `upper` | Uppercase | `{{ name \| upper }}` |
| `lower` | Lowercase | `{{ name \| lower }}` |
| `title` | Title case | `{{ name \| title }}` |
| `capitalize` | Capitalize | `{{ name \| capitalize }}` |
| `default` | Default value | `{{ value \| default:'N/A' }}` |
| `length` | Length | `{{ items \| length }}` |
| `int` | To integer | `{{ count \| int }}` |
| `float` | To float | `{{ price \| float }}` |
| `str` | To string | `{{ value \| str }}` |
| `bool` | To boolean | `{{ flag \| bool }}` |
| `quote` | Add quotes | `{{ name \| quote }}` |
| `single_quote` | Add single quotes | `{{ name \| single_quote }}` |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `CONFIGGEN_*` | Generic prefix for all variables |
| `CONFIGGEN_DEBUG` | Enable debug mode |
| `CONFIGGEN_FORMAT` | Default output format |
| `CONFIGGEN_ENV` | Default environment |

---

## CLI Reference

### Global Options

```bash
configgen [-v, --verbose] <command>
```

### Commands

#### generate

Generate a configuration file.

```bash
configgen generate [OPTIONS]

Options:
  -t, --template PATH      Template file path
  -o, --output PATH       Output file path
  -f, --format FORMAT     Output format (yaml, json, toml, xml, env)
  -V, --variables PATHS  Variable files (multiple allowed)
  -e, --env NAME          Target environment
  -s, --schema PATH       Schema file for validation
  -d, --define KV         Define variables (key=value, multiple allowed)
```

**Examples:**

```bash
# Basic generation
configgen generate -t template.yaml.j2 -o config.yaml

# With variables
configgen generate -t app.yaml.j2 -V vars.yaml -o output.yaml

# Environment-specific
configgen generate -t app.yaml.j2 -e production -o prod.yaml

# Inline variables
configgen generate -t app.yaml.j2 -d app_name=MyApp -d version=1.0.0

# Different output format
configgen generate -t app.yaml.j2 -f json -o config.json

# With validation
configgen generate -t app.yaml.j2 -s schema.json -o config.yaml
```

#### validate

Validate a configuration file against a schema.

```bash
configgen validate CONFIG_FILE -s, --schema SCHEMA_FILE
```

**Examples:**

```bash
configgen validate config.yaml -s schema.json
configgen validate app.json --schema schema.json
```

#### diff

Compare two configuration files.

```bash
configgen diff CONFIG1 CONFIG2
```

**Examples:**

```bash
configgen diff dev.yaml prod.yaml
```

#### env

Manage environment variables.

```bash
configgen env [OPTIONS]

Options:
  -p, --prefix PREFIX     Variable prefix (default: CONFIGGEN)
  --load-dotenv PATH      Load from .env file
```

**Examples:**

```bash
# List current env vars
configgen env

# With custom prefix
configgen env -p MYAPP

# Load from .env
configgen env --load-dotenv .env
```

---

## Troubleshooting

### Common Issues

#### 1. Template Not Found

```
Error: Template not found: /path/to/template.yaml.j2
```

**Solution:** Ensure the template path is correct and the file exists.

```python
from pathlib import Path
template_path = Path("templates/app.yaml.j2")
if template_path.exists():
    generator.load_template(template_path)
else:
    print(f"Template not found: {template_path.absolute()}")
```

#### 2. Unresolved Variable

```
Error: Unresolved variable: missing_var
```

**Solution:** Set the variable before generating or use a default value.

```python
# Option 1: Set the variable
generator.add_variable("missing_var", "default_value")

# Option 2: Use default in template
# {{ missing_var:default_value }}

# Option 3: Allow missing variables
config = GeneratorConfig(allow_missing_variables=True)
generator = ConfigGenerator(config=config)
```

#### 3. Validation Failed

```
SchemaValidationError: validation failed:
  - 'port': expected integer, got string
```

**Solution:** Check your configuration matches the schema types.

```python
# Ensure correct types in variables
generator.set_variables({
    "port": 8080,  # Integer, not "8080"
    "debug": True,  # Boolean, not "true"
})

# Or use filters in template
# port: {{ port | int }}
```

#### 4. YAML Formatting Issues

**Solution:** Ensure PyYAML is installed for proper YAML formatting.

```bash
pip install pyyaml
```

#### 5. TOML Not Working

**Solution:** Install TOML library.

```bash
pip install tomli tomli-w
```

### Debug Mode

Enable verbose output for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or in CLI
configgen -v generate -t template.yaml.j2
```

### Getting Help

```bash
# CLI help
configgen --help
configgen generate --help

# Python API help
from configgen import ConfigGenerator
help(ConfigGenerator)
```

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone repository
git clone https://github.com/moggan1337/ConfigGen.git
cd ConfigGen

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=configgen --cov-report=html

# Format code
black configgen tests

# Type checking
mypy configgen
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**ConfigGen** — Dynamic Configuration Made Simple

*Built with ❤️ for developers who love clean, maintainable configurations*

</div>
