"""
Pre-Mutation Safety Checks for MCP Server

This module provides safety checks to catch dangerous operations before execution.
All checks are deterministic and operate on the operation + document + schema.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum


class ErrorLevel(Enum):
    """Severity level for safety issues"""
    WARNING = "warning"  # Non-blocking, requires acknowledgment
    ERROR = "error"      # Blocking, prevents execution


@dataclass
class SafetyIssue:
    """Represents a safety concern"""
    level: ErrorLevel
    code: str
    message: str
    path: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "code": self.code,
            "message": self.message,
            "path": self.path,
            "context": self.context or {}
        }


@dataclass
class SafetyCheckResult:
    """Result of safety checks"""
    passed: bool
    errors: List[SafetyIssue]
    warnings: List[SafetyIssue]
    
    def has_blocking_errors(self) -> bool:
        return len(self.errors) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings]
        }


def check_required_field_deletion(
    operation: Dict[str, Any],
    schema: Dict[str, Any],
    document: Dict[str, Any]
) -> Optional[SafetyIssue]:
    """
    Check if operation attempts to delete a required field.
    
    Args:
        operation: The operation to check
        schema: JSON schema definition
        document: Current document state
        
    Returns:
        SafetyIssue if violation detected, None otherwise
    """
    if operation.get("action") != "delete":
        return None
    
    path = operation.get("path", [])
    if not path:
        return None
    
    # Check if the field being deleted is in the required list
    required_fields = schema.get("required", [])
    
    # For top-level deletions
    if len(path) == 1 and path[0] in required_fields:
        return SafetyIssue(
            level=ErrorLevel.ERROR,
            code="REQUIRED_FIELD_DELETION",
            message=f"Cannot delete required field: {path[0]}",
            path=".".join(str(p) for p in path),
            context={"field": path[0], "required_fields": required_fields}
        )
    
    return None


def check_type_compatibility(
    operation: Dict[str, Any],
    document: Dict[str, Any],
    schema: Dict[str, Any]
) -> Optional[SafetyIssue]:
    """
    Check if type change is compatible with schema.
    
    Args:
        operation: The operation to check
        document: Current document state
        schema: JSON schema definition
        
    Returns:
        SafetyIssue if incompatibility detected, None otherwise
    """
    action = operation.get("action")
    
    # Check different operation types
    if action == "add":
        path = operation.get("path", [])
        new_value = operation.get("value")
        
        if not path or new_value is None:
            return None
        
        # Get schema definition for this path
        field_name = path[0] if path else None
        if not field_name:
            return None
        
        properties = schema.get("properties", {})
        field_schema = properties.get(field_name, {})
        expected_type = field_schema.get("type")
        
        if not expected_type:
            return None
        
        # Map Python types to JSON schema types
        type_mapping = {
            str: "string",
            int: "number",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
            type(None): "null"
        }
        
        actual_type = type_mapping.get(type(new_value))
        
        # For top-level field type changes
        if len(path) == 1 and actual_type and actual_type != expected_type:
            return SafetyIssue(
                level=ErrorLevel.ERROR,
                code="TYPE_MISMATCH",
                message=f"Type mismatch for field '{field_name}': expected {expected_type}, got {actual_type}",
                path=".".join(str(p) for p in path),
                context={
                    "expected_type": expected_type,
                    "actual_type": actual_type,
                    "field": field_name
                }
            )
    
    elif action == "update":
        # For update operations, check each field in updates
        updates = operation.get("updates", {})
        properties = schema.get("properties", {})
        
        type_mapping = {
            str: "string",
            int: "number",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
            type(None): "null"
        }
        
        for field_name, new_value in updates.items():
            field_schema = properties.get(field_name, {})
            expected_type = field_schema.get("type")
            
            if not expected_type:
                continue
            
            actual_type = type_mapping.get(type(new_value))
            
            if actual_type and actual_type != expected_type:
                return SafetyIssue(
                    level=ErrorLevel.ERROR,
                    code="TYPE_MISMATCH",
                    message=f"Type mismatch for field '{field_name}': expected {expected_type}, got {actual_type}",
                    path=field_name,
                    context={
                        "expected_type": expected_type,
                        "actual_type": actual_type,
                        "field": field_name
                    }
                )
    
    return None


def check_bulk_change_threshold(
    operations: List[Dict[str, Any]],
    threshold: int = 10
) -> Optional[SafetyIssue]:
    """
    Check if number of operations exceeds safety threshold.
    
    Args:
        operations: List of operations to check
        threshold: Maximum number of operations before warning
        
    Returns:
        SafetyIssue if threshold exceeded, None otherwise
    """
    if len(operations) > threshold:
        return SafetyIssue(
            level=ErrorLevel.WARNING,
            code="BULK_CHANGE_WARNING",
            message=f"Large number of operations ({len(operations)}) exceeds threshold ({threshold})",
            context={
                "operation_count": len(operations),
                "threshold": threshold
            }
        )
    
    return None


def check_key_overwrite(
    operation: Dict[str, Any],
    document: Dict[str, Any]
) -> Optional[SafetyIssue]:
    """
    Check if operation will overwrite an existing key unintentionally.
    
    Args:
        operation: The operation to check
        document: Current document state
        
    Returns:
        SafetyIssue if unintentional overwrite detected, None otherwise
    """
    if operation.get("action") != "add":
        return None
    
    path = operation.get("path", [])
    if not path:
        return None
    
    # Navigate to the target location
    current = document
    for i, key in enumerate(path[:-1]):
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and isinstance(key, int) and 0 <= key < len(current):
            current = current[key]
        else:
            # Path doesn't exist yet, no overwrite possible
            return None
    
    # Check if final key exists
    final_key = path[-1]
    if isinstance(current, dict) and final_key in current:
        return SafetyIssue(
            level=ErrorLevel.WARNING,
            code="KEY_OVERWRITE_WARNING",
            message=f"Add operation will overwrite existing key: {final_key}",
            path=".".join(str(p) for p in path),
            context={"key": final_key, "existing_value": current[final_key]}
        )
    
    return None


def check_circular_references(
    operation: Dict[str, Any],
    document: Dict[str, Any]
) -> Optional[SafetyIssue]:
    """
    Check if operation would create circular references.
    
    Args:
        operation: The operation to check
        document: Current document state
        
    Returns:
        SafetyIssue if circular reference detected, None otherwise
    """
    # This is a simplified check - full cycle detection would require graph traversal
    # For now, we check if trying to add/replace with a reference to parent
    
    if operation.get("action") not in ["add", "replace"]:
        return None
    
    value = operation.get("value")
    
    # Check if value is the document itself (direct circular reference)
    if value is document:
        return SafetyIssue(
            level=ErrorLevel.ERROR,
            code="CIRCULAR_REFERENCE",
            message="Operation would create circular reference to document root",
            path=".".join(str(p) for p in operation.get("path", [])),
            context={"operation": operation.get("action")}
        )
    
    return None


def check_array_index_bounds(
    operation: Dict[str, Any],
    document: Dict[str, Any]
) -> Optional[SafetyIssue]:
    """
    Check if array index operations are within bounds.
    
    Args:
        operation: The operation to check
        document: Current document state
        
    Returns:
        SafetyIssue if out of bounds access detected, None otherwise
    """
    path = operation.get("path", [])
    if not path:
        return None
    
    # Navigate to check array indices
    current = document
    for i, key in enumerate(path):
        if isinstance(key, int):
            # Array index
            if not isinstance(current, list):
                return SafetyIssue(
                    level=ErrorLevel.ERROR,
                    code="INVALID_ARRAY_ACCESS",
                    message=f"Attempted array access on non-array at path segment {i}",
                    path=".".join(str(p) for p in path[:i+1]),
                    context={"expected": "array", "actual": type(current).__name__}
                )
            
            # For delete/replace, index must exist
            if operation.get("action") in ["delete", "replace"]:
                if key < 0 or key >= len(current):
                    return SafetyIssue(
                        level=ErrorLevel.ERROR,
                        code="ARRAY_INDEX_OUT_OF_BOUNDS",
                        message=f"Array index {key} out of bounds (length: {len(current)})",
                        path=".".join(str(p) for p in path[:i+1]),
                        context={"index": key, "array_length": len(current)}
                    )
            
            if key < len(current):
                current = current[key]
            else:
                break
        elif isinstance(current, dict) and key in current:
            current = current[key]
        else:
            break
    
    return None


def check_forbidden_operations(
    operation: Dict[str, Any],
    forbidden_paths: Optional[List[str]] = None
) -> Optional[SafetyIssue]:
    """
    Check if operation targets a forbidden path.
    
    Args:
        operation: The operation to check
        forbidden_paths: List of paths that cannot be modified
        
    Returns:
        SafetyIssue if forbidden operation detected, None otherwise
    """
    if not forbidden_paths:
        # Default forbidden paths - only name is truly protected
        # Version changes are common and expected
        forbidden_paths = ["name"]
    
    path = operation.get("path", [])
    if not path:
        return None
    
    path_str = ".".join(str(p) for p in path)
    
    for forbidden in forbidden_paths:
        if path_str.startswith(forbidden):
            return SafetyIssue(
                level=ErrorLevel.WARNING,
                code="FORBIDDEN_PATH_MODIFICATION",
                message=f"Modifying protected path: {path_str}",
                path=path_str,
                context={"forbidden_paths": forbidden_paths}
            )
    
    return None


def run_safety_checks(
    operations: List[Dict[str, Any]],
    document: Dict[str, Any],
    schema: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None
) -> SafetyCheckResult:
    """
    Run all safety checks on operations.
    
    Args:
        operations: List of operations to check
        document: Current document state
        schema: JSON schema definition
        options: Optional configuration (threshold, forbidden_paths, etc.)
        
    Returns:
        SafetyCheckResult with all detected issues
    """
    options = options or {}
    errors = []
    warnings = []
    
    # Check bulk operations threshold
    threshold = options.get("bulk_threshold", 10)
    bulk_issue = check_bulk_change_threshold(operations, threshold)
    if bulk_issue:
        warnings.append(bulk_issue)
    
    # Check each operation
    for operation in operations:
        # Required field deletion
        issue = check_required_field_deletion(operation, schema, document)
        if issue:
            errors.append(issue)
        
        # Type compatibility
        issue = check_type_compatibility(operation, document, schema)
        if issue:
            errors.append(issue)
        
        # Key overwrite
        issue = check_key_overwrite(operation, document)
        if issue:
            warnings.append(issue)
        
        # Circular references
        issue = check_circular_references(operation, document)
        if issue:
            errors.append(issue)
        
        # Array bounds
        issue = check_array_index_bounds(operation, document)
        if issue:
            errors.append(issue)
        
        # Forbidden operations
        forbidden_paths = options.get("forbidden_paths")
        issue = check_forbidden_operations(operation, forbidden_paths)
        if issue:
            warnings.append(issue)
    
    return SafetyCheckResult(
        passed=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )
