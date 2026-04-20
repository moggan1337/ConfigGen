#!/usr/bin/env python3
"""
ConfigGen CLI

Command-line interface for ConfigGen.
"""

import argparse
import sys
import logging
import json
from pathlib import Path


def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s'
    )


def cmd_generate(args) -> int:
    """Handle generate command."""
    from configgen import ConfigGenerator
    
    setup_logging(args.verbose)
    
    generator = ConfigGenerator()
    
    if args.template:
        generator.load_template(args.template)
    
    if args.variables:
        for var_file in args.variables:
            generator.load_variables_from_file(var_file)
    
    if args.env:
        generator.set_environment(args.env)
    
    generator.load_environment_variables()
    
    if args.schema:
        generator.load_schema(args.schema)
    
    for key_value in args.define or []:
        if '=' in key_value:
            key, _, value = key_value.partition('=')
            generator.add_variable(key.strip(), value.strip())
    
    output_format = args.format or 'yaml'
    
    try:
        if args.output:
            generator.write(args.output, format=output_format)
            print(f"✓ Generated: {args.output}")
        else:
            content = generator.generate_to_string(format=output_format)
            print(content)
        
        return 0
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_validate(args) -> int:
    """Handle validate command."""
    from configgen import ConfigGenerator
    
    setup_logging(args.verbose)
    
    generator = ConfigGenerator()
    
    if args.schema:
        generator.load_schema(args.schema)
    else:
        print("Error: --schema is required for validation", file=sys.stderr)
        return 1
    
    try:
        if args.config.endswith(('.yaml', '.yml')):
            from configgen.formats import YAMLHandler
            data = YAMLHandler().load(args.config)
        elif args.config.endswith('.json'):
            from configgen.formats import JSONHandler
            data = JSONHandler().load(args.config)
        else:
            print(f"Error: Unsupported file type: {args.config}", file=sys.stderr)
            return 1
        
        generator.validate(data)
        print(f"✓ {args.config} is valid")
        return 0
    except Exception as e:
        print(f"✗ Validation failed: {e}", file=sys.stderr)
        return 1


def cmd_diff(args) -> int:
    """Handle diff command."""
    from configgen import ConfigGenerator
    
    setup_logging(args.verbose)
    
    generator = ConfigGenerator()
    
    try:
        if args.format1.endswith(('.yaml', '.yml')):
            from configgen.formats import YAMLHandler
            data1 = YAMLHandler().load(args.format1)
            data2 = YAMLHandler().load(args.format2)
        elif args.format1.endswith('.json'):
            from configgen.formats import JSONHandler
            data1 = JSONHandler().load(args.format1)
            data2 = JSONHandler().load(args.format2)
        else:
            print(f"Error: Unsupported file type", file=sys.stderr)
            return 1
        
        diff = generator.diff(data1, data2)
        
        if not any(diff.values()):
            print("No differences found")
            return 0
        
        if diff['added']:
            print("\nAdded:")
            for key, value in diff['added'].items():
                print(f"  + {key}: {value}")
        
        if diff['removed']:
            print("\nRemoved:")
            for key, value in diff['removed'].items():
                print(f"  - {key}: {value}")
        
        if diff['changed']:
            print("\nChanged:")
            for key, change in diff['changed'].items():
                print(f"  ~ {key}:")
                print(f"      old: {change['old']}")
                print(f"      new: {change['new']}")
        
        return 0
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def cmd_env(args) -> int:
    """Handle env command."""
    from configgen import EnvironmentManager
    
    setup_logging(args.verbose)
    
    manager = EnvironmentManager(prefix=args.prefix)
    
    if args.load_dotenv:
        manager.load_dotenv(args.load_dotenv)
    
    env_vars = manager.load_from_environment()
    
    if env_vars:
        print(f"Environment variables ({args.prefix}_*):")
        for key, value in sorted(env_vars.items()):
            print(f"  {key}={value}")
    else:
        print(f"No environment variables found with prefix: {args.prefix}")
    
    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='configgen',
        description='Dynamic Configuration File Generator'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    gen_parser = subparsers.add_parser('generate', help='Generate a configuration')
    gen_parser.add_argument('-t', '--template', help='Template file path')
    gen_parser.add_argument('-o', '--output', help='Output file path')
    gen_parser.add_argument('-f', '--format', choices=['yaml', 'json', 'toml', 'xml', 'env'],
                          help='Output format')
    gen_parser.add_argument('-V', '--variables', nargs='+', help='Variable files')
    gen_parser.add_argument('-e', '--env', help='Target environment')
    gen_parser.add_argument('-s', '--schema', help='Schema file for validation')
    gen_parser.add_argument('-d', '--define', nargs='+', help='Define variables (key=value)')
    gen_parser.set_defaults(func=cmd_generate)
    
    val_parser = subparsers.add_parser('validate', help='Validate a configuration')
    val_parser.add_argument('config', help='Configuration file to validate')
    val_parser.add_argument('-s', '--schema', help='JSON Schema file')
    val_parser.set_defaults(func=cmd_validate)
    
    diff_parser = subparsers.add_parser('diff', help='Compare two configurations')
    diff_parser.add_argument('format1', help='First configuration file')
    diff_parser.add_argument('format2', help='Second configuration file')
    diff_parser.set_defaults(func=cmd_diff)
    
    env_parser = subparsers.add_parser('env', help='Manage environment variables')
    env_parser.add_argument('-p', '--prefix', default='CONFIGGEN', help='Variable prefix')
    env_parser.add_argument('--load-dotenv', help='Load from .env file')
    env_parser.set_defaults(func=cmd_env)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
