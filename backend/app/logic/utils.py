"""
Utility Functions for Domain Pack Backend

Responsibilities:
- YAML parsing & serialization (format-preserving)
- JSON parsing & serialization
- Deterministic diff calculation
- File-type-safe helpers

Constraints:
- Pure functions
- No schema validation
- No I/O
"""

import json
from typing import Dict, Any
from io import StringIO

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from deepdiff import DeepDiff


# ─────────────────────────────────────────────
# Exceptions
# ─────────────────────────────────────────────

class ParseError(Exception):
    """Raised when parsing fails."""


class SerializationError(Exception):
    """Raised when serialization fails."""


class DiffError(Exception):
    """Raised when diff calculation fails."""


# ─────────────────────────────────────────────
# YAML configuration (deterministic & safe)
# ─────────────────────────────────────────────

_yaml = YAML(typ="rt")  # round-trip
_yaml.preserve_quotes = True
_yaml.default_flow_style = False
_yaml.width = 4096
_yaml.allow_duplicate_keys = False


# ─────────────────────────────────────────────
# Parsing
# ─────────────────────────────────────────────

def parse_yaml(content: str) -> Dict[str, Any]:
    """
    Parse YAML content into a Python dictionary.

    Strict rules:
    - Input must be a string
    - Root must be a mapping
    """
    if not isinstance(content, str):
        raise ParseError(
            f"YAML content must be a string, got {type(content).__name__}"
        )

    try:
        data = _yaml.load(content)
    except Exception as e:
        raise ParseError(f"Failed to parse YAML: {e}")

    if data is None:
        raise ParseError("YAML content is empty")

    if not isinstance(data, CommentedMap):
        raise ParseError(
            f"YAML root must be a mapping, got {type(data).__name__}"
        )

    # Preserve ordering but normalize type
    return dict(data)


def parse_json(content: str) -> Dict[str, Any]:
    """
    Parse JSON content into a Python dictionary.

    Strict rules:
    - Input must be a string
    - Root must be an object
    """
    if not isinstance(content, str):
        raise ParseError(
            f"JSON content must be a string, got {type(content).__name__}"
        )

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ParseError(f"Failed to parse JSON: {e.msg}")

    if not isinstance(data, dict):
        raise ParseError(
            f"JSON root must be an object, got {type(data).__name__}"
        )

    return data


# ─────────────────────────────────────────────
# Serialization
# ─────────────────────────────────────────────

def _order_domain_pack_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reorder domain pack fields to ensure name, version, description appear first.
    This ensures consistent YAML output with metadata at the top.
    """
    if not isinstance(data, dict):
        return data
    
    # Define the desired order for top-level fields
    field_order = ["name", "description", "version"]
    
    # Create ordered dict with priority fields first
    ordered = {}
    
    # Add priority fields in order (if they exist)
    for field in field_order:
        if field in data:
            ordered[field] = data[field]
    
    # Add remaining fields in their original order
    for key, value in data.items():
        if key not in field_order:
            ordered[key] = value
    
    return ordered


def serialize_yaml(data: Dict[str, Any]) -> str:
    """
    Serialize dictionary into YAML (format-stable).
    Ensures name, version, description appear first.
    """
    if not isinstance(data, dict):
        raise SerializationError(
            f"YAML serialization requires dict, got {type(data).__name__}"
        )

    try:
        # Reorder fields to ensure metadata appears first
        ordered_data = _order_domain_pack_fields(data)
        
        stream = StringIO()
        _yaml.dump(ordered_data, stream)
        return stream.getvalue()
    except Exception as e:
        raise SerializationError(f"Failed to serialize YAML: {e}")


def serialize_json(data: Dict[str, Any], pretty: bool = True) -> str:
    """
    Serialize dictionary into JSON.
    """
    if not isinstance(data, dict):
        raise SerializationError(
            f"JSON serialization requires dict, got {type(data).__name__}"
        )

    try:
        if pretty:
            return json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
                sort_keys=True
            )
        return json.dumps(
            data,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True
        )
    except Exception as e:
        raise SerializationError(f"Failed to serialize JSON: {e}")


# ─────────────────────────────────────────────
# Diff calculation
# ─────────────────────────────────────────────

def calculate_diff(
    old_data: Dict[str, Any],
    new_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate deterministic diff between two domain pack versions.

    Output is fully JSON-serializable and stable.
    """
    if not isinstance(old_data, dict):
        raise DiffError(
            f"old_data must be dict, got {type(old_data).__name__}"
        )

    if not isinstance(new_data, dict):
        raise DiffError(
            f"new_data must be dict, got {type(new_data).__name__}"
        )

    try:
        diff = DeepDiff(
            old_data,
            new_data,
            ignore_order=False,
            report_repetition=True,
            view="tree"
        )
    except Exception as e:
        raise DiffError(f"Diff calculation failed: {e}")

    result = {
        "added": {},
        "removed": {},
        "changed": {},
        "type_changes": {},
        "summary": {
            "total_changes": 0,
            "has_changes": False
        }
    }

    if not diff:
        return result

    # Added
    for item in diff.get("dictionary_item_added", []):
        result["added"][item.path()] = item.t2

    # Removed
    for item in diff.get("dictionary_item_removed", []):
        result["removed"][item.path()] = item.t1

    # Value changes
    for item in diff.get("values_changed", []):
        result["changed"][item.path()] = {
            "old": item.t1,
            "new": item.t2
        }

    # Type changes
    for item in diff.get("type_changes", []):
        result["type_changes"][item.path()] = {
            "old_type": type(item.t1).__name__,
            "new_type": type(item.t2).__name__,
            "old_value": item.t1,
            "new_value": item.t2
        }

    # Summary
    result["summary"]["total_changes"] = (
        len(result["added"])
        + len(result["removed"])
        + len(result["changed"])
        + len(result["type_changes"])
    )
    result["summary"]["has_changes"] = True

    return result


# ─────────────────────────────────────────────
# File-type-safe helpers
# ─────────────────────────────────────────────

def validate_file_type(file_type: str) -> str:
    """
    Normalize and validate supported file types.
    Supported: 'yaml', 'json'
    """
    if not file_type:
        raise ValueError("File type must be specified")
    
    ft = file_type.lower().strip()
    if ft.endswith('.yaml') or ft.endswith('.yml') or ft == 'yaml':
        return 'yaml'
    if ft.endswith('.json') or ft == 'json':
        return 'json'
    
    raise ValueError(f"Unsupported file type: {file_type}. Use 'yaml' or 'json'.")


def detect_file_type(filename: str) -> str:
    """
    Infer file type from filename extension.
    Defaults to 'yaml' if unknown but extension suggests it, otherwise raises ValueError.
    """
    if not filename:
        return 'yaml'  # Default for unsaved content
    
    fn = filename.lower()
    if fn.endswith(('.yaml', '.yml')):
        return 'yaml'
    if fn.endswith('.json'):
        return 'json'
    
    # Default to yaml for domain packs if no clear extension
    return 'yaml'


def parse_content(content: str, file_type: str) -> Dict[str, Any]:
    """
    Unified content parser.
    Dispatches to specific type handlers.
    """
    ft = validate_file_type(file_type)
    
    if ft == 'yaml':
        return parse_yaml(content)
    elif ft == 'json':
        return parse_json(content)
    
    raise ParseError(f"Cannot parse content of type: {file_type}")
