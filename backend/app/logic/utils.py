"""
Utility Functions for Domain Pack MCP Server

Handles:
- YAML parsing and serialization (with formatting preservation)
- JSON parsing and serialization
- Diff calculation between versions
- File type detection
"""

import json
from typing import Dict, Any, Tuple
from ruamel.yaml import YAML
from deepdiff import DeepDiff
from io import StringIO


class ParseError(Exception):
    """Raised when parsing fails"""
    pass


class SerializationError(Exception):
    """Raised when serialization fails"""
    pass


# Configure ruamel.yaml for formatting preservation
yaml = YAML()
yaml.preserve_quotes = True
yaml.default_flow_style = False
yaml.width = 4096  # Prevent line wrapping


def parse_yaml(content: str) -> Dict[str, Any]:
    """Parse YAML content to dictionary."""
    if not isinstance(content, str):
        raise ParseError(f"Content must be a string, got {type(content).__name__}")
    
    try:
        data = yaml.load(content)
        if data is None:
            raise ParseError("YAML content is empty")
        if not isinstance(data, dict):
            raise ParseError(f"YAML must contain a dictionary at root, got {type(data).__name__}")
        return dict(data)  # Convert CommentedMap to regular dict
    except Exception as e:
        raise ParseError(f"Failed to parse YAML: {str(e)}")


def parse_json(content: str) -> Dict[str, Any]:
    """Parse JSON content to dictionary."""
    if not isinstance(content, str):
        raise ParseError(f"Content must be a string, got {type(content).__name__}")
    
    try:
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ParseError(f"JSON must contain a dictionary at root, got {type(data).__name__}")
        return data
    except json.JSONDecodeError as e:
        raise ParseError(f"Failed to parse JSON: {str(e)}")


def serialize_yaml(data: Dict[str, Any]) -> str:
    """Serialize dictionary to YAML with formatting preservation."""
    if not isinstance(data, dict):
        raise SerializationError(f"Data must be a dictionary, got {type(data).__name__}")
    
    try:
        stream = StringIO()
        yaml.dump(data, stream)
        return stream.getvalue()
    except Exception as e:
        raise SerializationError(f"Failed to serialize to YAML: {str(e)}")


def serialize_json(data: Dict[str, Any], pretty: bool = True) -> str:
    """Serialize dictionary to JSON."""
    if not isinstance(data, dict):
        raise SerializationError(f"Data must be a dictionary, got {type(data).__name__}")
    
    try:
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return json.dumps(data, ensure_ascii=False)
    except Exception as e:
        raise SerializationError(f"Failed to serialize to JSON: {str(e)}")


def calculate_diff(old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate diff between two domain pack versions."""
    diff = DeepDiff(
        old_data,
        new_data,
        ignore_order=False,
        report_repetition=True,
        verbose_level=2
    )
    
    # Convert DeepDiff result to serializable dict
    result = {
        "added": {},
        "removed": {},
        "changed": {},
        "type_changes": {}
    }
    
    if "dictionary_item_added" in diff:
        result["added"] = {str(k): v for k, v in diff["dictionary_item_added"].items()}
    
    if "dictionary_item_removed" in diff:
        result["removed"] = {str(k): v for k, v in diff["dictionary_item_removed"].items()}
    
    if "values_changed" in diff:
        result["changed"] = {
            str(k): {"old": v["old_value"], "new": v["new_value"]}
            for k, v in diff["values_changed"].items()
        }
    
    if "type_changes" in diff:
        result["type_changes"] = {
            str(k): {
                "old_type": str(v["old_type"]),
                "new_type": str(v["new_type"]),
                "old_value": v["old_value"],
                "new_value": v["new_value"]
            }
            for k, v in diff["type_changes"].items()
        }
    
    # Add summary
    result["summary"] = {
        "total_changes": sum(len(v) for v in result.values() if isinstance(v, dict)),
        "has_changes": bool(diff)
    }
    
    return result
