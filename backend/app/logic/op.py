"""
Deterministic Operations for Domain Pack Manipulation

PURE, DETERMINISTIC operations for modifying domain packs.
NO database access
NO schema validation
NO YAML parsing
Only pure JSON-like (dict / list / scalar) transformations.
"""

import copy
from typing import Dict, Any, List


# ============================================================
# Exceptions
# ============================================================

class OperationError(Exception):
    """Raised when an operation fails"""
    pass


# ============================================================
# Path Utilities
# ============================================================

def _get_value_at_path(data: Any, path: List[str]) -> Any:
    """Retrieve value at path."""
    current = data
    for i, key in enumerate(path):
        if isinstance(current, dict):
            if key not in current:
                raise OperationError(f"Path not found: {' -> '.join(path[:i+1])}")
            current = current[key]
        elif isinstance(current, list):
            try:
                idx = int(key)
                current = current[idx]
            except Exception:
                raise OperationError(f"Invalid list index at {' -> '.join(path[:i])}")
        else:
            raise OperationError(f"Cannot traverse non-container at {' -> '.join(path[:i])}")
    return current


def _set_value_at_path(data: Any, path: List[str], value: Any) -> None:
    """Set value at path, auto-creating intermediate dicts."""
    if not path:
        raise OperationError("Empty path not allowed")

    current = data
    for i, key in enumerate(path[:-1]):
        if isinstance(current, dict):
            if key not in current:
                current[key] = {}
            current = current[key]
        elif isinstance(current, list):
            try:
                current = current[int(key)]
            except Exception:
                raise OperationError(f"Invalid list index at {' -> '.join(path[:i])}")
        else:
            raise OperationError(f"Cannot traverse non-container at {' -> '.join(path[:i])}")

    final = path[-1]
    if isinstance(current, dict):
        current[final] = value
    elif isinstance(current, list):
        try:
            current[int(final)] = value
        except Exception:
            raise OperationError("Invalid list index for set")
    else:
        raise OperationError("Cannot set value on non-container")


def _delete_at_path(data: Any, path: List[str]) -> None:
    """Delete value at path."""
    if not path:
        raise OperationError("Empty path not allowed")

    current = data
    for key in path[:-1]:
        if isinstance(current, dict):
            if key not in current:
                return
            current = current[key]
        elif isinstance(current, list):
            try:
                current = current[int(key)]
            except Exception:
                return
        else:
            return

    final = path[-1]
    if isinstance(current, dict):
        current.pop(final, None)
    elif isinstance(current, list):
        try:
            current.pop(int(final))
        except Exception:
            pass


# ============================================================
# Field Operations (Dicts)
# ============================================================

def op_add_field(data: Dict[str, Any], path: List[str], value: Any) -> Dict[str, Any]:
    result = copy.deepcopy(data)
    parent = _get_value_at_path(result, path[:-1]) if path[:-1] else result
    if not isinstance(parent, dict):
        raise OperationError("ADD_FIELD target is not a dict")
    key = path[-1]
    if key in parent:
        raise OperationError(f"Field '{key}' already exists")
    parent[key] = value
    return result


def op_update_field(data: Dict[str, Any], path: List[str], value: Any) -> Dict[str, Any]:
    result = copy.deepcopy(data)
    parent = _get_value_at_path(result, path[:-1]) if path[:-1] else result
    key = path[-1]
    if not isinstance(parent, dict) or key not in parent:
        raise OperationError("UPDATE_FIELD requires existing field")
    parent[key] = value
    return result


def op_remove_field(data: Dict[str, Any], path: List[str]) -> Dict[str, Any]:
    result = copy.deepcopy(data)
    parent = _get_value_at_path(result, path[:-1]) if path[:-1] else result
    if not isinstance(parent, dict):
        raise OperationError("REMOVE_FIELD target is not a dict")
    parent.pop(path[-1], None)
    return result


def op_rename_field(data: Dict[str, Any], path: List[str], new_name: str) -> Dict[str, Any]:
    result = copy.deepcopy(data)
    parent = _get_value_at_path(result, path[:-1]) if path[:-1] else result
    old = path[-1]
    if not isinstance(parent, dict) or old not in parent:
        raise OperationError("RENAME_FIELD failed")
    parent[new_name] = parent.pop(old)
    return result


def op_merge_object(data: Dict[str, Any], path: List[str], value: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise OperationError("MERGE_OBJECT requires dict value")
    result = copy.deepcopy(data)
    target = _get_value_at_path(result, path) if path else result
    if not isinstance(target, dict):
        raise OperationError("MERGE_OBJECT target is not a dict")
    target.update(value)
    return result


# ============================================================
# List Operations
# ============================================================

def op_add_item(data: Dict[str, Any], path: List[str], value: Any) -> Dict[str, Any]:
    result = copy.deepcopy(data)
    target = _get_value_at_path(result, path)
    if not isinstance(target, list):
        raise OperationError("ADD_ITEM target is not a list")
    target.append(value)
    return result


def op_insert_item(data: Dict[str, Any], path: List[str], index: int, value: Any) -> Dict[str, Any]:
    result = copy.deepcopy(data)
    target = _get_value_at_path(result, path)
    if not isinstance(target, list):
        raise OperationError("INSERT_ITEM target is not a list")
    target.insert(index, value)
    return result


def op_remove_item(data: Dict[str, Any], path: List[str], index: int) -> Dict[str, Any]:
    result = copy.deepcopy(data)
    target = _get_value_at_path(result, path)
    if not isinstance(target, list):
        raise OperationError("REMOVE_ITEM target is not a list")
    target.pop(index)
    return result


def op_update_item(data: Dict[str, Any], path: List[str], index: int, value: Any) -> Dict[str, Any]:
    result = copy.deepcopy(data)
    target = _get_value_at_path(result, path)
    if not isinstance(target, list):
        raise OperationError("UPDATE_ITEM target is not a list")
    target[index] = value
    return result


def op_replace_list(data: Dict[str, Any], path: List[str], value: List[Any]) -> Dict[str, Any]:
    if not isinstance(value, list):
        raise OperationError("REPLACE_LIST requires list value")
    result = copy.deepcopy(data)
    _set_value_at_path(result, path, value)
    return result


def op_add_unique_item(data: Dict[str, Any], path: List[str], value: Any) -> Dict[str, Any]:
    result = copy.deepcopy(data)
    target = _get_value_at_path(result, path)
    if not isinstance(target, list):
        raise OperationError("ADD_UNIQUE_ITEM target is not a list")
    if value not in target:
        target.append(value)
    return result


def op_reorder_list(data: Dict[str, Any], path: List[str], order: List[int]) -> Dict[str, Any]:
    result = copy.deepcopy(data)
    target = _get_value_at_path(result, path)
    if not isinstance(target, list):
        raise OperationError("REORDER_LIST target is not a list")
    if len(order) != len(target):
        raise OperationError("Order length mismatch")
    reordered = [target[i] for i in order]
    _set_value_at_path(result, path, reordered)
    return result


# ============================================================
# Node Operations
# ============================================================

def op_replace_node(data: Dict[str, Any], path: List[str], value: Any) -> Dict[str, Any]:
    result = copy.deepcopy(data)
    _set_value_at_path(result, path, value)
    return result


def op_move_node(data: Dict[str, Any], from_path: List[str], to_path: List[str]) -> Dict[str, Any]:
    result = copy.deepcopy(data)
    value = _get_value_at_path(result, from_path)
    _delete_at_path(result, from_path)
    _set_value_at_path(result, to_path, value)
    return result


# ============================================================
# Conditional / Assertion
# ============================================================

def op_conditional_update(
    data: Dict[str, Any],
    condition_path: List[str],
    equals: Any,
    target_path: List[str],
    updates: Dict[str, Any],
) -> Dict[str, Any]:
    actual = _get_value_at_path(data, condition_path)
    if actual != equals:
        return data
    result = copy.deepcopy(data)
    target = _get_value_at_path(result, target_path)
    if not isinstance(target, dict):
        raise OperationError("CONDITIONAL_UPDATE target is not a dict")
    target.update(updates)
    return result


def op_assert_exists(data: Dict[str, Any], path: List[str]) -> Dict[str, Any]:
    _get_value_at_path(data, path)
    return data


# ============================================================
# Batch
# ============================================================

def apply_batch(data: Dict[str, Any], operations: List[Dict[str, Any]]) -> Dict[str, Any]:
    result = data
    for i, op in enumerate(operations):
        try:
            result = apply_operation(result, op)
        except OperationError as e:
            raise OperationError(f"Batch failed at index {i}: {e}")
    return result


# ============================================================
# Operation Registry
# ============================================================

OPERATIONS = {
    "ADD_FIELD": op_add_field,
    "UPDATE_FIELD": op_update_field,
    "REMOVE_FIELD": op_remove_field,
    "RENAME_FIELD": op_rename_field,
    "MERGE_OBJECT": op_merge_object,

    "ADD_ITEM": op_add_item,
    "INSERT_ITEM": op_insert_item,
    "REMOVE_ITEM": op_remove_item,
    "UPDATE_ITEM": op_update_item,
    "REPLACE_LIST": op_replace_list,
    "ADD_UNIQUE_ITEM": op_add_unique_item,
    "REORDER_LIST": op_reorder_list,

    "REPLACE_NODE": op_replace_node,
    "MOVE_NODE": op_move_node,

    "CONDITIONAL_UPDATE": op_conditional_update,
    "ASSERT_EXISTS": op_assert_exists,
    "BATCH": apply_batch,
}


# ============================================================
# Dispatcher
# ============================================================

def apply_operation(data: Dict[str, Any], operation: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(operation, dict):
        raise OperationError("Operation must be a dict")

    action = operation.get("action")
    if action not in OPERATIONS:
        raise OperationError(f"Unknown operation '{action}'")

    func = OPERATIONS[action]

    if action == "BATCH":
        return func(data, operation.get("operations", []))

    return func(
        data,
        **{k: v for k, v in operation.items() if k != "action"}
    )
