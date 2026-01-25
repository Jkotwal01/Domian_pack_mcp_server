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
yaml.default_flow_style = False # Forces block style instead of flow style
yaml.width = 4096  # Prevent line wrapping


def parse_yaml(content: str) -> Dict[str, Any]:
    """
    Parse YAML content to dictionary.
    
    Args:
        content: YAML string
        
    Returns:
        Parsed data as dictionary
        
    Raises:
        ParseError: If parsing fails
    """
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
    """
    Parse JSON content to dictionary.
    
    Args:
        content: JSON string
        
    Returns:
        Parsed data as dictionary
        
    Raises:
        ParseError: If parsing fails
    """
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
    """
    Serialize dictionary to YAML with formatting preservation.
    
    Args:
        data: Data to serialize
        
    Returns:
        YAML string
        
    Raises:
        SerializationError: If serialization fails
    """
    if not isinstance(data, dict):
        raise SerializationError(f"Data must be a dictionary, got {type(data).__name__}")
    
    try:
        stream = StringIO() 
        """Creates an in-memory file-like object
            Behaves like a writable text file
            No disk I/O involved
            Ideal for:
            Capturing output as a string
            Returning serialized content
            Testing or further processing"""
        yaml.dump(data, stream) # Converts the Python object data into YAML format and writes it to the stream.
        return stream.getvalue()
    except Exception as e:
        raise SerializationError(f"Failed to serialize to YAML: {str(e)}")


def serialize_json(data: Dict[str, Any], pretty: bool = True) -> str:
    """
    Serialize dictionary to JSON.
    
    Args:
        data: Data to serialize
        pretty: Whether to pretty-print (indent)
        
    Returns:
        JSON string
        
    Raises:
        SerializationError: If serialization fails
    """
    if not isinstance(data, dict):
        raise SerializationError(f"Data must be a dictionary, got {type(data).__name__}")
    
    try:
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return json.dumps(data, ensure_ascii=False)
    except Exception as e:
        raise SerializationError(f"Failed to serialize to JSON: {str(e)}")


def parse_content(content: str, file_type: str) -> Dict[str, Any]:
    """
    Parse content based on file type.
    
    Args:
        content: Content string
        file_type: "yaml" or "json"
        
    Returns:
        Parsed data as dictionary
        
    Raises:
        ParseError: If parsing fails
        ValueError: If file_type is invalid
    """
    file_type = file_type.lower().strip()
    
    if file_type in ("yaml", "yml"):
        return parse_yaml(content)
    elif file_type == "json":
        return parse_json(content)
    else:
        raise ValueError(f"Unsupported file type: {file_type}. Use 'yaml' or 'json'")


def serialize_content(data: Dict[str, Any], file_type: str) -> str:
    """
    Serialize data based on file type.
    
    Args:
        data: Data to serialize
        file_type: "yaml" or "json"
        
    Returns:
        Serialized string
        
    Raises:
        SerializationError: If serialization fails
        ValueError: If file_type is invalid
    """
    file_type = file_type.lower().strip()
    
    if file_type in ("yaml", "yml"):
        return serialize_yaml(data)
    elif file_type == "json":
        return serialize_json(data)
    else:
        raise ValueError(f"Unsupported file type: {file_type}. Use 'yaml' or 'json'")


def calculate_diff(old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate diff between two domain pack versions.
    
    Args:
        old_data: Previous version data
        new_data: New version data
        
    Returns:
        Diff as dictionary with structure:
        {
            "added": {...},
            "removed": {...},
            "changed": {...},
            "type_changes": {...}
        }
    """
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
    
    # Extract changes
    """ What this captures
        Keys that exist in new_data but not in old_data
        Example:
        old = {"a": 1}
        new = {"a": 1, "b": 2}

        Result:
        "added": {
        "root['b']": 2
        }
        Why str(k):
        DeepDiff paths are special objects (e.g., root['a']['b'])
        Converting to string makes them:
            Serializable
            Human-readable"""
    if "dictionary_item_added" in diff:
        result["added"] = {str(k): v for k, v in diff["dictionary_item_added"].items()}
    
        """
        What this captures
        Keys that existed in old_data but are missing in new_data
        Example:
        old = {"a": 1, "b": 2}
        new = {"a": 1}

        Result:
        "removed": {
        "root['b']": 2
        }
        """
    if "dictionary_item_removed" in diff:
        result["removed"] = {str(k): v for k, v in diff["dictionary_item_removed"].items()}
    
    """
    What this captures:
        Same key/path
        Same type
        Different value
        Example:
        old = {"a": 1}
        new = {"a": 2}

        Result:
        "changed": {
        "root['a']": {
            "old": 1,
            "new": 2
        }
        }
        This is the most common diff type.
        """
    if "values_changed" in diff:
        result["changed"] = {
            str(k): {"old": v["old_value"], "new": v["new_value"]}
            for k, v in diff["values_changed"].items()
        }
    

    """What this captures:
        Same path
        Different data types
        Example:
        old = {"a": "1"}
        new = {"a": 1}

        Result:
        "type_changes": {
        "root['a']": {
            "old_type": "<class 'str'>",
            "new_type": "<class 'int'>",
            "old_value": "1",
            "new_value": 1
        }
        }
        Why stringify types
        Python types are not JSON-serializable
        str(v["old_type"]) produces readable output
        """
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


def detect_file_type(filename: str) -> str:
    """
    Detect file type from filename extension.
    
    Args:
        filename: Filename or path
        
    Returns:
        "yaml" or "json"
        
    Raises:
        ValueError: If extension is not recognized
    """
    filename = filename.lower().strip()
    
    if filename.endswith(".yaml") or filename.endswith(".yml"):
        return "yaml"
    elif filename.endswith(".json"):
        return "json"
    else:
        raise ValueError(f"Cannot detect file type from filename: {filename}")


def validate_file_type(file_type: str) -> str:
    """
    Validate and normalize file type.
    
    Args:
        file_type: File type string
        
    Returns:
        Normalized file type ("yaml" or "json")
        
    Raises:
        ValueError: If file type is invalid
    """
    file_type = file_type.lower().strip()
    
    if file_type in ("yaml", "yml"):
        return "yaml"
    elif file_type == "json":
        return "json"
    else:
        raise ValueError(f"Invalid file type: {file_type}. Use 'yaml' or 'json'")
