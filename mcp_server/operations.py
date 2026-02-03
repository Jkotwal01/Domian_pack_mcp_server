"""
Deterministic Operations for Domain Pack Manipulation

This module implements PURE, DETERMINISTIC operations for modifying domain packs.
NO database access, NO schema validation, NO YAML parsing - only pure transformations.

Supported operations:
1. add - Add a value to a path
2. delete - Delete a value at a path
3. update - Update fields in an object
4. merge - Merge objects or arrays
5. add_unique - Add only if value doesn't exist
6. batch - Execute multiple operations atomically
7. assert - Assert a condition (validation)
"""

import copy
from typing import Dict, Any, List, Union


class OperationError(Exception):
    """Raised when an operation fails"""
    pass


def _get_value_at_path(data: Dict[str, Any], path: List[str], auto_create: bool = False) -> Any:
    """
    Get value at the specified path in the data structure.
    
    Args:
        data: The data structure
        path: List of keys representing the path
        auto_create: If True, create missing intermediate containers
        
    Returns:
        Value at the path
        
    Raises:
        OperationError: If path doesn't exist and auto_create is False
    """
    current = data
    
    for i, key in enumerate(path):
        if isinstance(current, dict):
            if key not in current:
                if auto_create:
                    # Look ahead to decide whether to create a dict or list
                    if i + 1 < len(path):
                        next_key = path[i+1]
                        try:
                            int(next_key)
                            current[key] = []
                        except ValueError:
                            current[key] = {}
                    else:
                        # Leaf level - if we're here with auto_create=True 
                        # for getting parent, we need to create something.
                        # Usually parent navigation asks for path[:-1].
                        current[key] = {}
                else:
                    raise OperationError(f"Path not found: {' -> '.join(path[:i+1])}")
            current = current[key]
        elif isinstance(current, list):
            try:
                index = int(key)
                if index < 0 or index >= len(current):
                    raise OperationError(f"Index {index} out of range at {' -> '.join(path[:i])}")
                current = current[index]
            except ValueError:
                raise OperationError(f"Invalid array index '{key}' at {' -> '.join(path[:i])}")
        else:
            raise OperationError(f"Cannot traverse non-dict/list at {' -> '.join(path[:i])}")
    
    return current


def _set_value_at_path(data: Dict[str, Any], path: List[str], value: Any) -> None:
    """
    Set value at the specified path in the data structure (mutates data).
    Args:
        data: The data structure
        path: List of keys representing the path
        value: Value to set
        
    Raises:
        OperationError: If path is invalid
    """
    if not path:
        raise OperationError("Cannot set value at empty path")
    
    current = data
    
    for i, key in enumerate(path[:-1]):
        if isinstance(current, dict):
            if key not in current:
                raise OperationError(f"Path not found: {' -> '.join(path[:i+1])}")
            current = current[key]
        elif isinstance(current, list):
            try:
                index = int(key)
                if index < 0 or index >= len(current):
                    raise OperationError(f"Index {index} out of range at {' -> '.join(path[:i])}")
                current = current[index]
            except ValueError:
                raise OperationError(f"Invalid array index '{key}' at {' -> '.join(path[:i])}")
        else:
            raise OperationError(f"Cannot traverse non-dict/list at {' -> '.join(path[:i])}")
    
    # Set the final value
    final_key = path[-1]
    
    if isinstance(current, dict):
        current[final_key] = value
    elif isinstance(current, list):
        try:
            index = int(final_key)
            if index < 0 or index >= len(current):
                raise OperationError(f"Index {index} out of range")
            current[index] = value
        except ValueError:
            raise OperationError(f"Invalid array index '{final_key}'")
    else:
        raise OperationError(f"Cannot set value on non-dict/list at {' -> '.join(path[:-1])}")


def _delete_at_path(data: Dict[str, Any], path: List[str]) -> None:
    """
    Delete value at the specified path (mutates data).
    
    Args:
        data: The data structure
        path: List of keys representing the path
        
    Raises:
        OperationError: If path doesn't exist
    """
    if not path:
        raise OperationError("Cannot delete at empty path")
    
    current = data
    
    for i, key in enumerate(path[:-1]):
        if isinstance(current, dict):
            if key not in current:
                raise OperationError(f"Path not found: {' -> '.join(path[:i+1])}")
            current = current[key]
        elif isinstance(current, list):
            try:
                index = int(key)
                if index < 0 or index >= len(current):
                    raise OperationError(f"Index {index} out of range at {' -> '.join(path[:i])}")
                current = current[index]
            except ValueError:
                raise OperationError(f"Invalid array index '{key}' at {' -> '.join(path[:i])}")
        else:
            raise OperationError(f"Cannot traverse non-dict/list at {' -> '.join(path[:i])}")
    
    # Delete the final key
    final_key = path[-1]
    
    if isinstance(current, dict):
        if final_key not in current:
            raise OperationError(f"Key '{final_key}' not found at {' -> '.join(path[:-1])}")
        del current[final_key]
    elif isinstance(current, list):
        try:
            index = int(final_key)
            if index < 0 or index >= len(current):
                raise OperationError(f"Index {index} out of range")
            current.pop(index)
        except ValueError:
            raise OperationError(f"Invalid array index '{final_key}'")
    else:
        raise OperationError(f"Cannot delete from non-dict/list at {' -> '.join(path[:-1])}")


def op_add(data: Dict[str, Any], path: List[str], value: Any) -> Dict[str, Any]:
    """
    Add operation: Add a value to a path.
    - For dicts: adds new key-value pair (fails if key exists)
    - For arrays: appends value
    
    Args:
        data: Domain pack data
        path: Path where to add
        value: Value to add
        
    Returns:
        Modified data (new copy)
        
    Raises:
        OperationError: If operation fails
    """
    result = copy.deepcopy(data)
    """
    deepcopy creates a completely independent copy of an object, 
    including all nested objects inside it.

    """
    if not path:
        raise OperationError("Cannot add at empty path")
    
    if len(path) == 1:
        # Adding to root level
        key = path[0]
        if key in result:
            # Check if it's an array - if so, append
            if isinstance(result[key], list):
                result[key].append(value)
            else:
                raise OperationError(f"Key '{key}' already exists at root and is not an array")
        else:
            result[key] = value
    else:
        # Navigate to parent
        parent = _get_value_at_path(result, path[:-1], auto_create=True)
        final_key = path[-1]
        
        if isinstance(parent, dict):
            if final_key in parent:
                # Check if it's an array - if so, append
                if isinstance(parent[final_key], list):
                    parent[final_key].append(value)
                else:
                    raise OperationError(f"Key '{final_key}' already exists at {' -> '.join(path[:-1])} and is not an array")
            else:
                parent[final_key] = value
        elif isinstance(parent, list):
            # For arrays, append the value (ignore the key)
            parent.append(value)
        else:
            raise OperationError(f"Cannot add to non-dict/list at {' -> '.join(path[:-1])}")
    
    return result






def op_delete(data: Dict[str, Any], path: List[str]) -> Dict[str, Any]:
    """
    Delete operation: Remove value at path.
    
    Args:
        data: Domain pack data
        path: Path to delete
        
    Returns:
        Modified data (new copy)
        
    Raises:
        OperationError: If path doesn't exist
    """
    result = copy.deepcopy(data)
    _delete_at_path(result, path)
    return result


def op_update(data: Dict[str, Any], path: List[str], updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update operation: Update multiple fields in an object.
    
    Args:
        data: Domain pack data
        path: Path to object to update
        updates: Dictionary of updates to apply
        
    Returns:
        Modified data (new copy)
        
    Raises:
        OperationError: If path doesn't point to a dict
    """
    result = copy.deepcopy(data)
    
    if not path:
        # Update root
        if not isinstance(result, dict):
            raise OperationError("Cannot update non-dict at root")
        result.update(updates)
    else:
        target = _get_value_at_path(result, path)
        if not isinstance(target, dict):
            raise OperationError(f"Cannot update non-dict at {' -> '.join(path)}")
        target.update(updates)
    
    return result


def op_merge(data: Dict[str, Any], path: List[str], value: Any, strategy: str = "append") -> Dict[str, Any]:
    """
    Merge operation: Merge objects or arrays.
    
    Args:
        data: Domain pack data
        path: Path to merge into
        value: Value to merge
        strategy: "append" for arrays, "update" for dicts
        
    Returns:
        Modified data (new copy)
        
    Raises:
        OperationError: If types don't match


    working:
    This function:
        Supports safe, controlled merging
        Works at:
            Root level
            Nested paths
        Enforces:
            Dict ↔ dict merging via update
            List ↔ list merging via extend
            Uses strategy to control list behavior
        Raises clear errors for:
            Type mismatches
            Unsupported array strategies
    """
    result = copy.deepcopy(data)
    
    if not path:
        # Merge at root
        if isinstance(result, dict) and isinstance(value, dict):
            result.update(value)
        elif isinstance(result, list) and isinstance(value, list):
            result.extend(value)
        else:
            raise OperationError("Type mismatch for merge at root")
    else:
        target = _get_value_at_path(result, path)
        
        if isinstance(target, dict) and isinstance(value, dict):
            target.update(value)
        elif isinstance(target, list) and isinstance(value, list):
            if strategy == "append":
                target.extend(value)
            else:
                raise OperationError(f"Unknown merge strategy for arrays: {strategy}")
        else:
            raise OperationError(f"Type mismatch for merge at {' -> '.join(path)}")
    
    return result


def op_add_unique(data: Dict[str, Any], path: List[str], value: Any) -> Dict[str, Any]:
    """
    Add unique operation: Add value only if it doesn't exist.
    
    Args:
        data: Domain pack data
        path: Path to add to
        value: Value to add
        
    Returns:
        Modified data (new copy)
        
    Raises:
        OperationError: If operation fails
    """
    result = copy.deepcopy(data)
    
    if not path:
        raise OperationError("Cannot add_unique at empty path")
    
    try:
        target = _get_value_at_path(result, path[:-1]) if len(path) > 1 else result
        final_key = path[-1]
        
        if isinstance(target, dict):
            if final_key not in target:
                target[final_key] = value
        elif isinstance(target, list):
            if value not in target:
                target.append(value)
        else:
            raise OperationError(f"Cannot add_unique to non-dict/list at {' -> '.join(path[:-1])}")
    except OperationError:
        # Path doesn't exist, use regular add
        return op_add(data, path, value)
    
    return result


def op_assert(data: Dict[str, Any], path: List[str], equals: Any = None, exists: bool = None) -> Dict[str, Any]:
    """
    Assert operation: Validate a condition without modifying data.
    
    Args:
        data: Domain pack data
        path: Path to check
        equals: Expected value (optional)
        exists: Whether path should exist (optional)
        
    Returns:
        Original data (unchanged)
        
    Raises:
        OperationError: If assertion fails
    """
    if exists is not None:
        try:
            _get_value_at_path(data, path)
            if not exists:
                raise OperationError(f"Path {' -> '.join(path)} should not exist but does")
        except OperationError:
            if exists:
                raise OperationError(f"Path {' -> '.join(path)} should exist but doesn't")
    
    if equals is not None:
        try:
            actual = _get_value_at_path(data, path)
            if actual != equals:
                raise OperationError(
                    f"Assertion failed at {' -> '.join(path)}: "
                    f"expected {equals}, got {actual}"
                )
        except OperationError as e:
            raise OperationError(f"Cannot assert on non-existent path: {e}")
    
    return data


# Operation registry
OPERATIONS = {
    "add": op_add,
    "delete": op_delete,
    "update": op_update,
    "merge": op_merge,
    "add_unique": op_add_unique,
    "assert": op_assert,
}


def apply_operation(data: Dict[str, Any], operation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply a single operation to domain pack data.
    
    Operation format:
    {
        "action": "add|delete|update|merge|add_unique|assert",
        "path": ["key1", "key2", ...],
        "value": <value>,  # for add, update, merge, add_unique
        "updates": {...},  # for update
        "equals": <value>, # for assert
        "exists": true/false  # for assert
    }
    
    Args:
        data: Domain pack data
        operation: Operation specification
        
    Returns:
        Modified data (new copy)
        
    Raises:
        OperationError: If operation is invalid or fails
    """
    if not isinstance(operation, dict):
        raise OperationError(f"Operation must be a dict, got {type(operation).__name__}")
    
    action = operation.get("action")
    if not action:
        raise OperationError("Operation must have 'action' field")
    
    if action not in OPERATIONS:
        raise OperationError(f"Unknown operation: {action}. Supported: {', '.join(OPERATIONS.keys())}")
    
    path = operation.get("path", [])
    if not isinstance(path, list):
        raise OperationError(f"Path must be a list, got {type(path).__name__}")
    
    # Execute operation
    op_func = OPERATIONS[action]
    
    try:
        if action == "add":
            if "value" not in operation:
                raise OperationError("'add' operation requires 'value' field")
            return op_func(data, path, operation["value"])
        
        elif action == "delete":
            return op_func(data, path)
        
        elif action == "update":
            if "updates" not in operation:
                raise OperationError("'update' operation requires 'updates' field")
            return op_func(data, path, operation["updates"])
        
        elif action == "merge":
            if "value" not in operation:
                raise OperationError("'merge' operation requires 'value' field")
            strategy = operation.get("strategy", "append")
            return op_func(data, path, operation["value"], strategy)
        
        elif action == "add_unique":
            if "value" not in operation:
                raise OperationError("'add_unique' operation requires 'value' field")
            return op_func(data, path, operation["value"])
        
        elif action == "assert":
            equals = operation.get("equals")
            exists = operation.get("exists")
            if equals is None and exists is None:
                raise OperationError("'assert' operation requires 'equals' or 'exists' field")
            return op_func(data, path, equals=equals, exists=exists)
        
    except OperationError:
        raise
    except Exception as e:
        raise OperationError(f"Operation '{action}' failed: {str(e)}")


def apply_batch(data: Dict[str, Any], operations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Apply multiple operations atomically.
    If any operation fails, all changes are rolled back.
    
    Args:
        data: Domain pack data
        operations: List of operations
        
    Returns:
        Modified data (new copy)
        
    Raises:
        OperationError: If any operation fails
    """
    if not isinstance(operations, list):
        raise OperationError(f"Operations must be a list, got {type(operations).__name__}")
    
    result = data
    
    try:
        for i, op in enumerate(operations):
            result = apply_operation(result, op)
    except OperationError as e:
        raise OperationError(f"Batch operation failed at index {i}: {str(e)}")
    
    return result
