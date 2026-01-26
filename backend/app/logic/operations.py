"""
Deterministic Operations for Domain Pack Manipulation
This module implements PURE, DETERMINISTIC operations for modifying domain packs.
NO database access, NO schema validation, NO YAML parsing - only pure transformations.
"""

import copy
from typing import Dict, Any, List, Union

class OperationError(Exception):
    """Raised when an operation fails"""
    pass

def _get_value_at_path(data: Dict[str, Any], path: List[str]) -> Any:
    """Get value at the specified path in the data structure."""
    current = data
    
    for i, key in enumerate(path):
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
    
    return current

def _set_value_at_path(data: Dict[str, Any], path: List[str], value: Any) -> None:
    """
    Set value at the specified path in the data structure (mutates data).
    Auto-creates missing intermediate dictionaries.
    """
    if not path:
        raise OperationError("Cannot set value at empty path")
    
    current = data
    
    # Traverse to parent
    for i, key in enumerate(path[:-1]):
        if isinstance(current, list):
            try:
                index = int(key)
                if index < 0 or index >= len(current):
                    raise OperationError(f"Index {index} out of range at {' -> '.join(path[:i])}")
                current = current[index]
            except ValueError:
                raise OperationError(f"Invalid array index '{key}' at {' -> '.join(path[:i])}")
        
        elif isinstance(current, dict):
            if key not in current:
                current[key] = {} # Auto-create missing dicts
            current = current[key]
            
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
    """Delete value at the specified path (mutates data)."""
    if not path:
        raise OperationError("Cannot delete at empty path")
    
    current = data
    
    for i, key in enumerate(path[:-1]):
        if isinstance(current, dict):
            if key not in current:
                # If path is missing, deleting it is effectively done
                return 
            current = current[key]
        elif isinstance(current, list):
            try:
                index = int(key)
                if index < 0 or index >= len(current):
                    return # Out of range deletion is a no-op
                current = current[index]
            except ValueError:
                 raise OperationError(f"Invalid array index '{key}' at {' -> '.join(path[:i])}")
        else:
            raise OperationError(f"Cannot traverse non-dict/list at {' -> '.join(path[:i])}")
    
    final_key = path[-1]
    if isinstance(current, dict):
        if final_key in current:
            del current[final_key]
    elif isinstance(current, list):
        try:
            index = int(final_key)
            if 0 <= index < len(current):
                current.pop(index)
        except ValueError:
            pass

def op_add(data: Dict[str, Any], path: List[str], value: Any) -> Dict[str, Any]:
    """
    Add operation: Add a value to a path.
    Automatically creates missing intermediate dictionaries.
    If target is an array, appends the value.
    """
    result = copy.deepcopy(data)
    
    if not path:
        raise OperationError("Cannot add at empty path")
    
    # 1. Navigate/Create parents
    current = result
    for i, key in enumerate(path[:-1]):
        if isinstance(current, list):
            try:
                index = int(key)
                current = current[index]
            except (ValueError, IndexError):
                 raise OperationError(f"Navigation failed at {' -> '.join(path[:i+1])}")
        elif isinstance(current, dict):
            if key not in current:
                current[key] = {}
            current = current[key]
        else:
            raise OperationError(f"Navigation failed at non-container node: {' -> '.join(path[:i])}")

    # 2. Add to final parent
    parent = current
    final_key = path[-1]
    
    if isinstance(parent, dict):
        if final_key in parent:
            if isinstance(parent[final_key], list):
                parent[final_key].append(value)
            else:
                raise OperationError(f"Target '{final_key}' exists and is not a list")
        else:
            parent[final_key] = value
    elif isinstance(parent, list):
        parent.append(value)
    else:
        raise OperationError("Failed to add: parent is not a container")
        
    return result

def op_replace(data: Dict[str, Any], path: List[str], value: Any) -> Dict[str, Any]:
    """Replace value at path (with auto-create behavior)."""
    result = copy.deepcopy(data)
    _set_value_at_path(result, path, value)
    return result

def op_delete(data: Dict[str, Any], path: List[str]) -> Dict[str, Any]:
    """Delete value at path."""
    result = copy.deepcopy(data)
    _delete_at_path(result, path)
    return result

def op_update(data: Dict[str, Any], path: List[str], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update fields in an object (with auto-create target behavior)."""
    result = copy.deepcopy(data)
    
    current = result
    if path:
        for i, key in enumerate(path):
            if isinstance(current, dict):
                if key not in current:
                    current[key] = {}
                current = current[key]
            elif isinstance(current, list):
                try:
                    index = int(key)
                    current = current[index]
                except (ValueError, IndexError):
                    raise OperationError(f"Update failed: navigation error at {key}")
            else:
                raise OperationError("Update failed: path segment not a dict")
    
    if not isinstance(current, dict):
        raise OperationError("Update failed: target is not a dictionary")
    
    current.update(updates)
    return result

def op_merge(data: Dict[str, Any], path: List[str], value: Any, strategy: str = "append") -> Dict[str, Any]:
    """Merge structure at path (with auto-create behavior)."""
    result = copy.deepcopy(data)
    
    # Simple strategy: find or create target then apply logic
    current = result
    if path:
        # Traverse to target's parent
        for i, key in enumerate(path[:-1]):
            if isinstance(current, dict):
                if key not in current: current[key] = {}
                current = current[key]
            elif isinstance(current, list):
                try: current = current[int(key)]
                except: raise OperationError("Merge navigation error")
        
        final_key = path[-1]
        if isinstance(current, dict):
            if final_key not in current:
                current[final_key] = [] if isinstance(value, list) else {}
            target = current[final_key]
        else:
             raise OperationError("Merge failed: parent is not a dict")
    else:
        target = result

    # Perform merge logic
    if isinstance(target, dict) and isinstance(value, dict):
        target.update(value)
    elif isinstance(target, list) and isinstance(value, list):
        target.extend(value)
    else:
        raise OperationError(f"Merge type mismatch at {' -> '.join(path)}")
        
    return result

def op_add_unique(data: Dict[str, Any], path: List[str], value: Any) -> Dict[str, Any]:
    """Add unique operation: Add value only if it doesn't exist."""
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

def op_assert(data: Dict[str, Any], path: List[str], equals: Any = None, exists: bool = None) -> Dict[str, Any]: # need to study in depth.
    """Assert operation: Validate a condition without modifying data."""
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
    "replace": op_replace,
    "delete": op_delete,
    "update": op_update,
    "merge": op_merge,
    "add_unique": op_add_unique,
    "assert": op_assert,
}

def apply_operation(data: Dict[str, Any], operation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply a single operation to domain pack data.
    
    Args:
        data: Domain pack data
        operation: Operation specification
        
    Returns:
        Modified data (new copy)
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
        
        elif action == "replace":
            if "value" not in operation:
                raise OperationError("'replace' operation requires 'value' field")
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
