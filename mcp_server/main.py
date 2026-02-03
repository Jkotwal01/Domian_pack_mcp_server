"""
Domain Pack MCP Server - Pure Transformation Interface

This is a pure, deterministic document transformer following the compiler model.

Architecture:
- NO sessions, NO version history, NO database
- Pure function: (document, operations) → (updated_document, diff, errors)
- All-or-nothing execution
- Deterministic behavior
"""

import sys
from fastmcp import FastMCP
from typing import Dict, Any, List, Optional

# Import pure transformation engine
from executor import (
    execute_transformation,
    preview_transformation,
    ExecutionOptions,
    TransformationResult
)
from schema import DOMAIN_PACK_SCHEMA, validate_schema, ValidationError
from utils import parse_content, serialize_content, ParseError, SerializationError


# Create FastMCP instance
mcp = FastMCP("Domain Pack MCP Server - Pure Transformation Engine")


@mcp.tool()
def transform_document(
    document: str,
    format: str,
    operations: List[Dict[str, Any]],
    schema: Optional[Dict[str, Any]] = None,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Pure document transformation.
    
    Takes a document and operations, returns updated document with diff and errors.
    NO state, NO sessions, NO versions - pure transformation only.
    
    Args:
        document: YAML or JSON string of the document
        format: "yaml" or "json"
        operations: List of operations to apply
        schema: Optional custom schema (uses DOMAIN_PACK_SCHEMA if not provided)
        options: Optional execution options:
            - strict_mode: bool (default True) - Fail on warnings
            - auto_create_paths: bool (default False) - Auto-create missing paths
            - preserve_formatting: bool (default True) - Preserve YAML formatting
            - max_operations: int (default 100) - Maximum operations per batch
            - bulk_threshold: int (default 10) - Warning threshold for bulk ops
            - forbidden_paths: List[str] - Paths that cannot be modified
    
    Returns:
        {
            "success": bool,
            "document": dict,  # Updated document (or original if failed)
            "serialized": str,  # Serialized output in requested format
            "diff": dict,  # Changes made
            "errors": list,  # Blocking errors
            "warnings": list,  # Non-blocking warnings
            "affected_paths": list,  # Paths that were modified
            "execution_metadata": dict  # Execution stats
        }
    
    Example:
        transform_document(
            document='''
name: Legal
description: Legal domain
version: 1.0.0
entities: []
            ''',
            format="yaml",
            operations=[
                {
                    "action": "add",
                    "path": ["entities"],
                    "value": {"name": "Attorney", "type": "ATTORNEY", "attributes": ["name", "bar_number"]}
                }
            ]
        )
    """
    try:
        # Parse input document
        try:
            parsed_doc = parse_content(document, format)
        except ParseError as e:
            return {
                "success": False,
                "document": {},
                "serialized": "",
                "diff": None,
                "errors": [{
                    "code": "PARSE_ERROR",
                    "message": str(e),
                    "phase": "parsing"
                }],
                "warnings": [],
                "affected_paths": [],
                "execution_metadata": {}
            }
        
        # Use default schema if not provided
        if schema is None:
            schema = DOMAIN_PACK_SCHEMA
        
        # Parse options
        exec_options = ExecutionOptions()
        if options:
            exec_options.strict_mode = options.get("strict_mode", True)
            exec_options.auto_create_paths = options.get("auto_create_paths", False)
            exec_options.preserve_formatting = options.get("preserve_formatting", True)
            exec_options.max_operations = options.get("max_operations", 100)
            exec_options.bulk_threshold = options.get("bulk_threshold", 10)
            exec_options.forbidden_paths = options.get("forbidden_paths")
        
        # Execute transformation
        result = execute_transformation(
            document=parsed_doc,
            schema=schema,
            operations=operations,
            options=exec_options
        )
        
        # Serialize output if successful
        if result.success:
            try:
                result.serialized = serialize_content(result.document, format)
            except SerializationError as e:
                return {
                    "success": False,
                    "document": parsed_doc,
                    "serialized": "",
                    "diff": None,
                    "errors": [{
                        "code": "SERIALIZATION_ERROR",
                        "message": str(e),
                        "phase": "serialization"
                    }],
                    "warnings": result.warnings,
                    "affected_paths": result.affected_paths,
                    "execution_metadata": result.execution_metadata
                }
        
        return result.to_dict()
    
    except Exception as e:
        return {
            "success": False,
            "document": {},
            "serialized": "",
            "diff": None,
            "errors": [{
                "code": "UNEXPECTED_ERROR",
                "message": f"Unexpected error: {str(e)}",
                "phase": "unknown"
            }],
            "warnings": [],
            "affected_paths": [],
            "execution_metadata": {}
        }


@mcp.tool()
def validate_document(document: str, format: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Validate document against schema without transformation.
    
    Args:
        document: YAML or JSON string
        format: "yaml" or "json"
        schema: Optional custom schema (uses DOMAIN_PACK_SCHEMA if not provided)
    
    Returns:
        {
            "valid": bool,
            "errors": list,
            "warnings": list
        }
    
    Example:
        validate_document(
            document='name: Legal\\ndescription: Legal domain\\nversion: 1.0.0',
            format="yaml"
        )
    """
    try:
        # Parse document
        try:
            parsed_doc = parse_content(document, format)
        except ParseError as e:
            return {
                "valid": False,
                "errors": [{
                    "code": "PARSE_ERROR",
                    "message": str(e)
                }],
                "warnings": []
            }
        
        # Use default schema if not provided
        if schema is None:
            schema = DOMAIN_PACK_SCHEMA
        
        # Validate
        try:
            validate_schema(parsed_doc, schema)
            return {
                "valid": True,
                "errors": [],
                "warnings": []
            }
        except ValidationError as e:
            return {
                "valid": False,
                "errors": [{
                    "code": "VALIDATION_ERROR",
                    "message": str(e)
                }],
                "warnings": []
            }
    
    except Exception as e:
        return {
            "valid": False,
            "errors": [{
                "code": "UNEXPECTED_ERROR",
                "message": str(e)
            }],
            "warnings": []
        }


@mcp.tool()
def preview_operations(
    document: str,
    format: str,
    operations: List[Dict[str, Any]],
    schema: Optional[Dict[str, Any]] = None,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Preview what would change without applying operations (dry-run mode).
    
    Args:
        document: YAML or JSON string
        format: "yaml" or "json"
        operations: List of operations to preview
        schema: Optional custom schema
        options: Optional execution options
    
    Returns:
        {
            "would_succeed": bool,
            "diff": dict,  # What would change
            "errors": list,
            "warnings": list,
            "affected_paths": list,
            "operations_count": int
        }
    
    Example:
        preview_operations(
            document='name: Legal\\nversion: 1.0.0',
            format="yaml",
            operations=[{"action": "replace", "path": ["version"], "value": "2.0.0"}]
        )
    """
    try:
        # Parse document
        try:
            parsed_doc = parse_content(document, format)
        except ParseError as e:
            return {
                "would_succeed": False,
                "diff": None,
                "errors": [{
                    "code": "PARSE_ERROR",
                    "message": str(e)
                }],
                "warnings": [],
                "affected_paths": [],
                "operations_count": len(operations)
            }
        
        # Use default schema if not provided
        if schema is None:
            schema = DOMAIN_PACK_SCHEMA
        
        # Parse options
        exec_options = ExecutionOptions()
        if options:
            exec_options.strict_mode = options.get("strict_mode", True)
            exec_options.auto_create_paths = options.get("auto_create_paths", False)
            exec_options.max_operations = options.get("max_operations", 100)
            exec_options.bulk_threshold = options.get("bulk_threshold", 10)
            exec_options.forbidden_paths = options.get("forbidden_paths")
        
        # Preview
        return preview_transformation(
            document=parsed_doc,
            schema=schema,
            operations=operations,
            options=exec_options
        )
    
    except Exception as e:
        return {
            "would_succeed": False,
            "diff": None,
            "errors": [{
                "code": "UNEXPECTED_ERROR",
                "message": str(e)
            }],
            "warnings": [],
            "affected_paths": [],
            "operations_count": len(operations)
        }


@mcp.tool()
def get_schema() -> Dict[str, Any]:
    """
    Get the default domain pack schema.
    
    Returns:
        The DOMAIN_PACK_SCHEMA definition
    
    Example:
        get_schema()
    """
    return DOMAIN_PACK_SCHEMA


def main():
    """
    Main entry point.
    Runs the pure MCP transformation server.
    """
    try:
        print("=" * 60, file=sys.stderr)
        print("Domain Pack MCP Server - Pure Transformation Engine", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print("", file=sys.stderr)
        print("Architecture: Pure, Deterministic Document Transformer", file=sys.stderr)
        print("- NO sessions, NO version history, NO database", file=sys.stderr)
        print("- Pure function: (document, operations) → (result, diff, errors)", file=sys.stderr)
        print("- All-or-nothing execution", file=sys.stderr)
        print("", file=sys.stderr)
        print("Available Tools:", file=sys.stderr)
        print("  1. transform_document - Apply operations to document", file=sys.stderr)
        print("  2. validate_document - Validate document against schema", file=sys.stderr)
        print("  3. preview_operations - Preview changes without applying", file=sys.stderr)
        print("  4. get_schema - Get domain pack schema definition", file=sys.stderr)
        print("", file=sys.stderr)
        print("Starting server...", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        
        mcp.run()
    
    except Exception as e:
        print(f"Server failed to start: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
