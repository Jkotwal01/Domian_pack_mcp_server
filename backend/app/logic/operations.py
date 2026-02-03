"""
Primitive CRUD Operations for Nested Dictionaries

4 rock-solid operations that everything else builds on:
- CREATE: Create a key / insert into list
- READ: Fetch value (for validation/debug)
- UPDATE: Replace value at path
- DELETE: Remove key / list item

Core invariants:
- Data is a dict
- Operations are pure (input → output)
- Paths are explicit
- No auto-magic
- Fail loudly if path is wrong
"""

import copy
from typing import Dict, Any, List, Union


# ============================================================
# Exceptions
# ============================================================

class CRUDError(Exception):
    """Raised when a CRUD operation fails"""
    pass


class PathNotFoundError(CRUDError):
    """Raised when a path does not exist"""
    pass


class PathExistsError(CRUDError):
    """Raised when trying to CREATE at an existing path"""
    pass


class InvalidPathError(CRUDError):
    """Raised when path is invalid for the operation"""
    pass


# Alias for backward compatibility
OperationError = CRUDError


# ============================================================
# Path Navigation Helpers
# ============================================================

def _navigate_to_parent(data: Any, path: List[str], auto_create: bool = False) -> tuple[Any, str]:
    """
    Navigate to the parent container of the target path.
    
    Returns: (parent_container, final_key)
    Raises: PathNotFoundError if any intermediate path doesn't exist (unless auto_create=True)
    """
    if not path:
        raise InvalidPathError("Path cannot be empty")
    
    current = data
    
    # Navigate to parent
    for i, key in enumerate(path[:-1]):
        if isinstance(current, dict):
            if key not in current:
                if auto_create:
                    # Look ahead to see what to create
                    next_key = path[i+1]
                    try:
                        # If next key is an integer or "-", create a list
                        int(next_key) if next_key != "-" else None
                        current[key] = []
                    except ValueError:
                        current[key] = {}
                else:
                    raise PathNotFoundError(f"Path not found: {' -> '.join(path[:i+1])}")
            current = current[key]
        elif isinstance(current, list):
            try:
                idx = int(key)
                if idx < 0 or idx >= len(current):
                    raise PathNotFoundError(f"List index {idx} out of range at {' -> '.join(path[:i+1])}")
                current = current[idx]
            except ValueError:
                raise InvalidPathError(f"Invalid list index '{key}' at {' -> '.join(path[:i+1])}")
        else:
            raise InvalidPathError(f"Cannot traverse into non-container (type: {type(current).__name__}) at {' -> '.join(path[:i+1])}")
    
    return current, path[-1]


def _navigate_to_target(data: Any, path: List[str]) -> Any:
    """
    Navigate to the target value at path.
    
    Returns: value at path
    Raises: PathNotFoundError if path doesn't exist
    """
    if not path:
        return data
    
    current = data
    
    for i, key in enumerate(path):
        if isinstance(current, dict):
            if key not in current:
                raise PathNotFoundError(f"Path not found: {' -> '.join(path[:i+1])}")
            current = current[key]
        elif isinstance(current, list):
            try:
                idx = int(key)
                if idx < 0 or idx >= len(current):
                    raise PathNotFoundError(f"List index {idx} out of range at {' -> '.join(path[:i+1])}")
                current = current[idx]
            except ValueError:
                raise InvalidPathError(f"Invalid list index '{key}' at {' -> '.join(path[:i+1])}")
        else:
            raise InvalidPathError(f"Cannot traverse into non-container (type: {type(current).__name__}) at {' -> '.join(path[:i+1])}")
    
    return current


# ============================================================
# CREATE Operation
# ============================================================

def create(data: Dict[str, Any], path: List[str], value: Any) -> Dict[str, Any]:
    """
    CREATE a new key in a dict or append/insert into a list.
    
    For dicts: Creates a new key. Fails if key already exists.
    For lists: If final path is an integer, inserts at that index.
               If final path is "-", appends to end.
               Otherwise fails.
    
    Args:
        data: The root data dictionary
        path: List of keys/indices to navigate (e.g., ["entities", "0", "fields"])
        value: The value to create
    
    Returns:
        New data dict with the value created
    
    Raises:
        PathNotFoundError: If intermediate path doesn't exist
        PathExistsError: If trying to create an existing dict key
        InvalidPathError: If path is invalid for the container type
    
    Examples:
        # Create a new top-level key
        create({}, ["name"], "John")  # {"name": "John"}
        
        # Create a nested key
        create({"user": {}}, ["user", "age"], 30)  # {"user": {"age": 30}}
        
        # Append to list
        create({"items": [1, 2]}, ["items", "-"], 3)  # {"items": [1, 2, 3]}
        
        # Insert into list at index
        create({"items": [1, 3]}, ["items", "1"], 2)  # {"items": [1, 2, 3]}
    """
    if not isinstance(data, dict):
        raise InvalidPathError("Root data must be a dict")
    
    if not path:
        raise InvalidPathError("Path cannot be empty for CREATE")
    
    result = copy.deepcopy(data)
    parent, final_key = _navigate_to_parent(result, path, auto_create=True)
    
    if isinstance(parent, dict):
        # Dict: key must not exist
        if final_key in parent:
            raise PathExistsError(f"Key '{final_key}' already exists at {' -> '.join(path)}")
        parent[final_key] = value
    
    elif isinstance(parent, list):
        # List: support append ("-") or insert at index
        if final_key == "-":
            parent.append(value)
        else:
            try:
                idx = int(final_key)
                if idx < 0 or idx > len(parent):
                    raise InvalidPathError(f"Insert index {idx} out of range (0-{len(parent)}) at {' -> '.join(path)}")
                parent.insert(idx, value)
            except ValueError:
                raise InvalidPathError(f"Invalid list index '{final_key}' for CREATE at {' -> '.join(path)}")
    
    else:
        raise InvalidPathError(f"Cannot CREATE in non-container (type: {type(parent).__name__}) at {' -> '.join(path[:-1])}")
    
    return result


# ============================================================
# READ Operation
# ============================================================

def read(data: Dict[str, Any], path: List[str]) -> Any:
    """
    READ the value at a path.
    
    This is a pure read operation for validation/debugging.
    Does NOT modify data.
    
    Args:
        data: The root data dictionary
        path: List of keys/indices to navigate
    
    Returns:
        The value at the path
    
    Raises:
        PathNotFoundError: If path doesn't exist
        InvalidPathError: If path is invalid
    
    Examples:
        read({"name": "John"}, ["name"])  # "John"
        read({"user": {"age": 30}}, ["user", "age"])  # 30
        read({"items": [1, 2, 3]}, ["items", "1"])  # 2
        read({"data": {...}}, [])  # returns entire data dict
    """
    if not isinstance(data, dict):
        raise InvalidPathError("Root data must be a dict")
    
    return _navigate_to_target(data, path)


# ============================================================
# UPDATE Operation
# ============================================================

def update(data: Dict[str, Any], path: List[str], value: Any) -> Dict[str, Any]:
    """
    UPDATE (replace) the value at a path.
    
    The path MUST already exist. This is a pure replacement operation.
    
    Args:
        data: The root data dictionary
        path: List of keys/indices to navigate
        value: The new value to set
    
    Returns:
        New data dict with the value updated
    
    Raises:
        PathNotFoundError: If path doesn't exist
        InvalidPathError: If path is invalid
    
    Examples:
        update({"name": "John"}, ["name"], "Jane")  # {"name": "Jane"}
        update({"user": {"age": 30}}, ["user", "age"], 31)  # {"user": {"age": 31}}
        update({"items": [1, 2, 3]}, ["items", "1"], 99)  # {"items": [1, 99, 3]}
    """
    if not isinstance(data, dict):
        raise InvalidPathError("Root data must be a dict")
    
    if not path:
        raise InvalidPathError("Cannot UPDATE root data (use a specific path)")
    
    result = copy.deepcopy(data)
    
    # First verify path exists
    _navigate_to_target(result, path)
    
    # Now update it
    parent, final_key = _navigate_to_parent(result, path)
    
    if isinstance(parent, dict):
        parent[final_key] = value
    elif isinstance(parent, list):
        try:
            idx = int(final_key)
            parent[idx] = value
        except ValueError:
            raise InvalidPathError(f"Invalid list index '{final_key}' at {' -> '.join(path)}")
    else:
        raise InvalidPathError(f"Cannot UPDATE in non-container at {' -> '.join(path[:-1])}")
    
    return result


# ============================================================
# DELETE Operation
# ============================================================

def delete(data: Dict[str, Any], path: List[str]) -> Dict[str, Any]:
    """
    DELETE a key from dict or item from list.
    
    The path MUST exist. Fails loudly if it doesn't.
    
    Args:
        data: The root data dictionary
        path: List of keys/indices to navigate
    
    Returns:
        New data dict with the value deleted
    
    Raises:
        PathNotFoundError: If path doesn't exist
        InvalidPathError: If path is invalid or trying to delete root
    
    Examples:
        delete({"name": "John", "age": 30}, ["age"])  # {"name": "John"}
        delete({"user": {"age": 30}}, ["user", "age"])  # {"user": {}}
        delete({"items": [1, 2, 3]}, ["items", "1"])  # {"items": [1, 3]}
    """
    if not isinstance(data, dict):
        raise InvalidPathError("Root data must be a dict")
    
    if not path:
        raise InvalidPathError("Cannot DELETE root data (use a specific path)")
    
    result = copy.deepcopy(data)
    
    # First verify path exists
    _navigate_to_target(result, path)
    
    # Now delete it
    parent, final_key = _navigate_to_parent(result, path)
    
    if isinstance(parent, dict):
        del parent[final_key]
    elif isinstance(parent, list):
        try:
            idx = int(final_key)
            del parent[idx]
        except ValueError:
            raise InvalidPathError(f"Invalid list index '{final_key}' at {' -> '.join(path)}")
    else:
        raise InvalidPathError(f"Cannot DELETE from non-container at {' -> '.join(path[:-1])}")
    
    return result


# ============================================================
# Operation Dispatcher
# ============================================================

def apply_operation(data: Dict[str, Any], operation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply a CRUD operation to data.
    
    Operation format:
    {
        "op": "CREATE" | "READ" | "UPDATE" | "DELETE",
        "path": ["key1", "key2", ...],
        "value": <any>  # only for CREATE and UPDATE
    }
    
    Args:
        data: The root data dictionary
        operation: The operation specification
    
    Returns:
        New data dict (or original for READ)
    
    Raises:
        InvalidPathError: If operation format is invalid
        CRUDError: If operation fails
    """
    if not isinstance(operation, dict):
        raise InvalidPathError("Operation must be a dict")
    
    op = operation.get("op")
    if not op:
        raise InvalidPathError("Operation must have 'op' field")
    
    path = operation.get("path")
    if not isinstance(path, list):
        raise InvalidPathError("Operation 'path' must be a list")
    
    if op == "CREATE":
        if "value" not in operation:
            raise InvalidPathError("CREATE operation requires 'value' field")
        return create(data, path, operation["value"])
    
    elif op == "READ":
        return read(data, path)
    
    elif op == "UPDATE":
        if "value" not in operation:
            raise InvalidPathError("UPDATE operation requires 'value' field")
        return update(data, path, operation["value"])
    
    elif op == "DELETE":
        return delete(data, path)
    
    else:
        raise InvalidPathError(f"Unknown operation: {op}")


# ============================================================
# Batch Operations
# ============================================================

def apply_batch(data: Dict[str, Any], operations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Apply multiple CRUD operations in sequence.
    
    Operations are applied in order. If any operation fails, the entire batch fails.
    
    Args:
        data: The root data dictionary
        operations: List of operation specifications
    
    Returns:
        New data dict with all operations applied
    
    Raises:
        CRUDError: If any operation fails (with index information)
    """
    result = data
    for i, op in enumerate(operations):
        try:
            result = apply_operation(result, op)
        except CRUDError as e:
            raise CRUDError(f"Batch operation failed at index {i}: {e}")
    
    return result


# ============================================================
# Registry for backward compatibility
# ============================================================

OPERATIONS = {
    "CREATE": create,
    "READ": read,
    "UPDATE": update,
    "DELETE": delete,
}


# ============================================================
# Exports
# ============================================================

__all__ = [
    # Operations
    "create",
    "read",
    "update",
    "delete",
    
    # Dispatcher
    "apply_operation",
    "apply_batch",
    
    # Exceptions
    "CRUDError",
    "OperationError",  # Alias
    "PathNotFoundError",
    "PathExistsError",
    "InvalidPathError",
    
    # Registry
    "OPERATIONS",
]
