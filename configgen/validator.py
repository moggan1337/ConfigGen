"""
Schema Validator Module

JSON Schema validation with detailed error reporting.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Represents a single validation error."""
    path: str
    message: str
    value: Any = None
    expected: Optional[Any] = None
    
    def __str__(self) -> str:
        base = f"'{self.path}': {self.message}"
        if self.expected:
            base += f" (expected: {self.expected})"
        return base


@dataclass 
class ValidationResult:
    """Result of schema validation."""
    valid: bool
    errors: List[ValidationError]
    
    def raise_if_invalid(self) -> None:
        """Raise ValidationError if validation failed."""
        if not self.valid:
            raise SchemaValidationError(self.errors)


class SchemaValidationError(Exception):
    """Raised when schema validation fails."""
    
    def __init__(self, errors: List[ValidationError]):
        self.errors = errors
        message = "\n".join(f"  - {err}" for err in errors)
        super().__init__(f"Schema validation failed:\n{message}")


class SchemaValidator:
    """
    JSON Schema-based configuration validator.
    
    Features:
    - Type checking
    - Required fields validation
    - Range/constraint validation
    - Pattern matching
    - Enum validation
    - Nested object validation
    - Array validation
    - Custom validation rules
    """
    
    PRIMITIVE_TYPES = {
        'string', 'number', 'integer', 'boolean', 
        'null', 'array', 'object'
    }
    
    def __init__(self, strict: bool = True):
        """
        Initialize the validator.
        
        Args:
            strict: If True, raise on first error. If False, collect all errors.
        """
        self._schema: Optional[Dict[str, Any]] = None
        self._strict = strict
        self._errors: List[ValidationError] = []
        self._custom_validators: Dict[str, callable] = {}
        
        logger.debug(f"SchemaValidator initialized (strict={strict})")
    
    def set_schema(self, schema: Dict[str, Any]) -> "SchemaValidator":
        """
        Set the JSON Schema for validation.
        
        Args:
            schema: JSON Schema definition.
            
        Returns:
            Self for method chaining.
        """
        self._schema = schema
        return self
    
    def register_validator(
        self, 
        name: str, 
        validator: callable
    ) -> "SchemaValidator":
        """
        Register a custom validator function.
        
        Args:
            name: Validator name (matches 'x-validator' in schema).
            validator: Callable that takes (value, schema_fragment, path).
            
        Returns:
            Self for method chaining.
        """
        self._custom_validators[name] = validator
        return self
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate data against the schema.
        
        Args:
            data: Configuration data to validate.
            
        Returns:
            True if valid.
            
        Raises:
            SchemaValidationError: If validation fails.
        """
        if self._schema is None:
            logger.warning("No schema set, skipping validation")
            return True
        
        self._errors = []
        self._validate_node(data, self._schema, "")
        
        result = ValidationResult(valid=len(self._errors) == 0, errors=self._errors)
        
        if self._strict:
            result.raise_if_invalid()
        
        return result.valid
    
    def _validate_node(
        self,
        value: Any,
        schema: Dict[str, Any],
        path: str
    ) -> None:
        """Recursively validate a node against its schema."""
        if not isinstance(schema, dict):
            return
        
        if '$ref' in schema:
            schema = self._resolve_ref(schema['$ref'])
        
        type_name = schema.get('type')
        
        if 'x-validator' in schema:
            self._run_custom_validator(value, schema, path)
            return
        
        if type_name:
            if isinstance(type_name, list):
                if not any(self._check_type(value, t) for t in type_name):
                    self._add_error(
                        path,
                        f"expected type in {type_name}, got {type(value).__name__}",
                        value,
                        type_name
                    )
                    return
            elif not self._check_type(value, type_name):
                self._add_error(
                    path,
                    f"expected {type_name}, got {type(value).__name__}",
                    value,
                    type_name
                )
                return
        
        if type_name == 'object' or isinstance(value, dict):
            self._validate_object(value, schema, path)
        elif type_name == 'array' or isinstance(value, list):
            self._validate_array(value, schema, path)
        elif type_name == 'string':
            self._validate_string(value, schema, path)
        elif type_name in ('number', 'integer'):
            self._validate_number(value, schema, path)
    
    def _check_type(self, value: Any, type_name: str) -> bool:
        """Check if value matches expected type."""
        if value is None:
            return type_name == 'null'
        
        type_map = {
            'string': str,
            'number': (int, float),
            'integer': int,
            'boolean': bool,
            'array': list,
            'object': dict,
            'null': type(None),
        }
        
        expected = type_map.get(type_name)
        if expected is None:
            return True
        
        return isinstance(value, expected)
    
    def _validate_object(
        self,
        value: Dict[str, Any],
        schema: Dict[str, Any],
        path: str
    ) -> None:
        """Validate an object against schema."""
        if not isinstance(value, dict):
            return
        
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        additional_props = schema.get('additionalProperties')
        
        for req_field in required:
            if req_field not in value:
                self._add_error(
                    f"{path}.{req_field}" if path else req_field,
                    "required field missing",
                    None,
                    "present"
                )
        
        for field_name, field_value in value.items():
            field_path = f"{path}.{field_name}" if path else field_name
            
            if field_name in properties:
                self._validate_node(field_value, properties[field_name], field_path)
            elif additional_props is False:
                self._add_error(field_path, "additional property not allowed", field_value)
            elif isinstance(additionalProps, dict):
                self._validate_node(field_value, additional_props, field_path)
        
        if 'patternProperties' in schema:
            self._validate_pattern_props(value, schema['patternProperties'], path)
        
        if 'minProperties' in schema and len(value) < schema['minProperties']:
            self._add_error(path, f"minProperties: {schema['minProperties']}", len(value))
        
        if 'maxProperties' in schema and len(value) > schema['maxProperties']:
            self._add_error(path, f"maxProperties: {schema['maxProperties']}", len(value))
    
    def _validate_array(
        self,
        value: List[Any],
        schema: Dict[str, Any],
        path: str
    ) -> None:
        """Validate an array against schema."""
        if not isinstance(value, list):
            return
        
        items_schema = schema.get('items')
        if items_schema:
            for i, item in enumerate(value):
                item_path = f"{path}[{i}]"
                self._validate_node(item, items_schema, item_path)
        
        unique = schema.get('uniqueItems', False)
        if unique and len(value) != len(set(str(v) for v in value)):
            self._add_error(path, "uniqueItems constraint violated", value)
        
        if 'minItems' in schema and len(value) < schema['minItems']:
            self._add_error(path, f"minItems: {schema['minItems']}", len(value))
        
        if 'maxItems' in schema and len(value) > schema['maxItems']:
            self._add_error(path, f"maxItems: {schema['maxItems']}", len(value))
        
        if 'contains' in schema:
            if not any(self._matches_contains(item, schema['contains']) for item in value):
                self._add_error(path, "no array item matches 'contains' schema")
    
    def _validate_string(
        self,
        value: str,
        schema: Dict[str, Any],
        path: str
    ) -> None:
        """Validate a string against schema constraints."""
        if 'minLength' in schema and len(value) < schema['minLength']:
            self._add_error(path, f"minLength: {schema['minLength']}", len(value))
        
        if 'maxLength' in schema and len(value) > schema['maxLength']:
            self._add_error(path, f"maxLength: {schema['maxLength']}", len(value))
        
        if 'pattern' in schema:
            import re
            if not re.match(schema['pattern'], value):
                self._add_error(path, f"pattern mismatch: {schema['pattern']}", value)
        
        if 'format' in schema:
            self._validate_format(value, schema['format'], path)
        
        if 'enum' in schema and value not in schema['enum']:
            self._add_error(path, f"enum constraint: {schema['enum']}", value)
    
    def _validate_number(
        self,
        value: Union[int, float],
        schema: Dict[str, Any],
        path: str
    ) -> None:
        """Validate a number against schema constraints."""
        try:
            val = float(value)
        except (ValueError, TypeError):
            self._add_error(path, "invalid number", value)
            return
        
        if 'minimum' in schema and val < schema['minimum']:
            self._add_error(path, f"minimum: {schema['minimum']}", val)
        
        if 'maximum' in schema and val > schema['maximum']:
            self._add_error(path, f"maximum: {schema['maximum']}", val)
        
        if 'exclusiveMinimum' in schema and val <= schema['exclusiveMinimum']:
            self._add_error(path, f"exclusiveMinimum: {schema['exclusiveMinimum']}", val)
        
        if 'exclusiveMaximum' in schema and val >= schema['exclusiveMaximum']:
            self._add_error(path, f"exclusiveMaximum: {schema['exclusiveMaximum']}", val)
        
        if 'multipleOf' in schema:
            if isinstance(value, int):
                remainder = value % schema['multipleOf']
            else:
                remainder = val % schema['multipleOf']
            if abs(remainder) > 1e-9:
                self._add_error(path, f"multipleOf: {schema['multipleOf']}", val)
        
        if 'enum' in schema and val not in schema['enum']:
            self._add_error(path, f"enum constraint: {schema['enum']}", val)
    
    def _validate_format(self, value: str, format_name: str, path: str) -> None:
        """Validate string format."""
        import re
        
        formats = {
            'date': r'^\d{4}-\d{2}-\d{2}$',
            'date-time': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            'email': r'^[\w\.-]+@[\w\.-]+\.\w+$',
            'uri': r'^[a-zA-Z][a-zA-Z0-9+.-]*://',
            'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            'hostname': r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$',
            'ipv4': r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',
            'ipv6': r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$',
        }
        
        if format_name in formats:
            if not re.match(formats[format_name], value):
                self._add_error(path, f"format: {format_name}", value)
    
    def _validate_pattern_props(
        self,
        value: Dict[str, Any],
        patterns: Dict[str, Dict[str, Any]],
        path: str
    ) -> None:
        """Validate properties matching regex patterns."""
        import re
        
        for prop_name, prop_value in value.items():
            prop_path = f"{path}.{prop_name}"
            
            for pattern, schema in patterns.items():
                if re.match(pattern, prop_name):
                    self._validate_node(prop_value, schema, prop_path)
                    break
    
    def _matches_contains(self, value: Any, contains_schema: Dict[str, Any]) -> bool:
        """Check if a value matches the contains schema."""
        temp_errors = []
        original_errors = self._errors
        self._errors = []
        
        self._validate_node(value, contains_schema, "contains_check")
        
        result = len(self._errors) == 0
        self._errors = original_errors
        
        return result
    
    def _resolve_ref(self, ref: str) -> Dict[str, Any]:
        """Resolve a $ref reference."""
        if not self._schema:
            return {}
        
        if ref.startswith('#/'):
            parts = ref[2:].split('/')
            current = self._schema
            
            for part in parts:
                part = part.replace('~1', '/').replace('~0', '~')
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return {}
            
            return current
        
        return {}
    
    def _run_custom_validator(
        self,
        value: Any,
        schema: Dict[str, Any],
        path: str
    ) -> None:
        """Run a custom validator function."""
        validator_name = schema['x-validator']
        
        if validator_name in self._custom_validators:
            try:
                self._custom_validators[validator_name](value, schema, path)
            except Exception as e:
                self._add_error(path, f"custom validator '{validator_name}' failed: {e}")
    
    def _add_error(
        self,
        path: str,
        message: str,
        value: Any = None,
        expected: Any = None
    ) -> None:
        """Add a validation error."""
        error = ValidationError(path=path, message=message, value=value, expected=expected)
        self._errors.append(error)
        logger.debug(f"Validation error: {error}")
    
    def get_errors(self) -> List[ValidationError]:
        """Get collected validation errors."""
        return self._errors.copy()
