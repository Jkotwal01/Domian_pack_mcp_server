"""
Path Resolution Tool for MCP Server

This module provides deterministic path resolution for document transformations.
It converts string paths into concrete references inside the document tree.

Supported path formats:
- Dot notation: "entities.Patient.fields.age"
- Array indexing: "fields[0].name"
- Mixed: "entities.Patient.fields[2].constraints.min"
"""

from typing import Dict, Any, List, Union, Tuple, Optional
import re
from dataclasses import dataclass


class PathError(Exception):
    """Raised when path resolution fails"""
    pass


@dataclass
class PathSegment:
    """Represents a single segment in a path"""
    key: Optional[str] = None  # For object keys
    index: Optional[int] = None  # For array indices
    is_array_access: bool = False
    
    def __repr__(self):
        if self.is_array_access:
            return f"[{self.index}]"
        return f".{self.key}" if self.key else ""


@dataclass
class NodeReference:
    """Reference to a node in the document tree"""
    parent: Any  # Parent container (dict or list)
    key: Union[str, int]  # Key or index in parent
    value: Any  # Current value at this location
    path: List[PathSegment]  # Full path to this node
    exists: bool  # Whether the node currently exists
    
    def __repr__(self):
        path_str = "".join(str(seg) for seg in self.path).lstrip(".")
        return f"NodeReference({path_str}, exists={self.exists})"


def parse_path(path_string: str) -> List[PathSegment]:
    """
    Parse a path string into segments.
    
    Supports:
    - Dot notation: "a.b.c"
    - Array indexing: "a[0].b[1]"
    - Mixed: "entities.Patient.fields[2].name"
    
    Args:
        path_string: Path string to parse
        
    Returns:
        List of PathSegment objects
        
    Raises:
        PathError: If path syntax is invalid
        
    Examples:
        >>> parse_path("entities.Patient.name")
        [PathSegment(key='entities'), PathSegment(key='Patient'), PathSegment(key='name')]
        
        >>> parse_path("fields[0].name")
        [PathSegment(key='fields'), PathSegment(index=0, is_array_access=True), PathSegment(key='name')]
    """
    if not path_string:
        raise PathError("Path cannot be empty")
    
    segments = []
    
    # Pattern to match: key, [index], or .key
    # Matches: word characters, array access [digits], or dot followed by word
    pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)|(\[\d+\])|(\.[a-zA-Z_][a-zA-Z0-9_]*)'
    
    position = 0
    for match in re.finditer(pattern, path_string):
        # Check for gaps in matching (invalid syntax)
        if match.start() != position:
            invalid_part = path_string[position:match.start()]
            raise PathError(f"Invalid path syntax near: '{invalid_part}'")
        
        matched_text = match.group(0)
        
        if matched_text.startswith('[') and matched_text.endswith(']'):
            # Array index
            index_str = matched_text[1:-1]
            try:
                index = int(index_str)
                segments.append(PathSegment(index=index, is_array_access=True))
            except ValueError:
                raise PathError(f"Invalid array index: {matched_text}")
                
        elif matched_text.startswith('.'):
            # Dot notation
            key = matched_text[1:]
            segments.append(PathSegment(key=key))
            
        else:
            # Plain key (first segment or after array access)
            segments.append(PathSegment(key=matched_text))
        
        position = match.end()
    
    # Check if we consumed the entire string
    if position != len(path_string):
        invalid_part = path_string[position:]
        raise PathError(f"Invalid path syntax at end: '{invalid_part}'")
    
    if not segments:
        raise PathError("Path resulted in no segments")
    
    return segments


def resolve_path(
    document: Dict[str, Any],
    path: Union[str, List[str], List[PathSegment]],
    auto_create: bool = False
) -> NodeReference:
    """
    Resolve a path to a node reference in the document.
    
    Args:
        document: The document to search
        path: Path as string, list of strings, or list of PathSegments
        auto_create: If True, create missing intermediate containers
        
    Returns:
        NodeReference to the target node
        
    Raises:
        PathError: If path cannot be resolved
        
    Examples:
        >>> doc = {"entities": [{"name": "Patient"}]}
        >>> ref = resolve_path(doc, "entities[0].name")
        >>> ref.value
        'Patient'
    """
    # Normalize path to segments
    if isinstance(path, str):
        segments = parse_path(path)
    elif isinstance(path, list) and path and isinstance(path[0], str):
        # List of strings - convert to dot notation and parse
        segments = parse_path(".".join(path))
    elif isinstance(path, list) and path and isinstance(path[0], PathSegment):
        segments = path
    else:
        raise PathError(f"Invalid path type: {type(path)}")
    
    if not segments:
        raise PathError("Empty path")
    
    # Traverse the document
    current = document
    parent = None
    parent_key = None
    
    for i, segment in enumerate(segments):
        parent = current
        
        if segment.is_array_access:
            # Array indexing
            if not isinstance(current, list):
                if auto_create and i == len(segments) - 1:
                    # Last segment - can't auto-create array access
                    raise PathError(
                        f"Cannot auto-create array index {segment.index} at path segment {i}"
                    )
                raise PathError(
                    f"Expected array at path segment {i}, got {type(current).__name__}"
                )
            
            if segment.index < 0 or segment.index >= len(current):
                raise PathError(
                    f"Array index {segment.index} out of bounds (length: {len(current)}) "
                    f"at path segment {i}"
                )
            
            parent_key = segment.index
            current = current[segment.index]
            
        else:
            # Object key access
            if not isinstance(current, dict):
                raise PathError(
                    f"Expected object at path segment {i}, got {type(current).__name__}"
                )
            
            parent_key = segment.key
            
            if segment.key not in current:
                if auto_create and i < len(segments) - 1:
                    # Create intermediate container
                    next_segment = segments[i + 1]
                    if next_segment.is_array_access:
                        current[segment.key] = []
                    else:
                        current[segment.key] = {}
                    current = current[segment.key]
                elif auto_create and i == len(segments) - 1:
                    # Last segment doesn't exist - return reference with exists=False
                    return NodeReference(
                        parent=parent,
                        key=parent_key,
                        value=None,
                        path=segments,
                        exists=False
                    )
                else:
                    raise PathError(
                        f"Key '{segment.key}' not found at path segment {i}"
                    )
            else:
                current = current[segment.key]
    
    return NodeReference(
        parent=parent,
        key=parent_key,
        value=current,
        path=segments,
        exists=True
    )


def validate_path_exists(document: Dict[str, Any], path: Union[str, List[str]]) -> bool:
    """
    Check if a path exists in the document.
    
    Args:
        document: The document to check
        path: Path to validate
        
    Returns:
        True if path exists, False otherwise
    """
    try:
        ref = resolve_path(document, path, auto_create=False)
        return ref.exists
    except PathError:
        return False


def get_value_at_path(
    document: Dict[str, Any],
    path: Union[str, List[str]],
    default: Any = None
) -> Any:
    """
    Get value at path, returning default if not found.
    
    Args:
        document: The document to search
        path: Path to the value
        default: Default value if path doesn't exist
        
    Returns:
        Value at path or default
    """
    try:
        ref = resolve_path(document, path, auto_create=False)
        return ref.value if ref.exists else default
    except PathError:
        return default


def set_value_at_path(
    document: Dict[str, Any],
    path: Union[str, List[str]],
    value: Any,
    auto_create: bool = False
) -> None:
    """
    Set value at path (mutates document).
    
    Args:
        document: The document to modify
        path: Path where to set the value
        value: Value to set
        auto_create: If True, create missing intermediate containers
        
    Raises:
        PathError: If path is invalid or doesn't exist (when auto_create=False)
    """
    ref = resolve_path(document, path, auto_create=auto_create)
    
    if ref.parent is None:
        raise PathError("Cannot set value at root")
    
    ref.parent[ref.key] = value


def delete_at_path(document: Dict[str, Any], path: Union[str, List[str]]) -> Any:
    """
    Delete value at path (mutates document).
    
    Args:
        document: The document to modify
        path: Path to delete
        
    Returns:
        The deleted value
        
    Raises:
        PathError: If path doesn't exist
    """
    ref = resolve_path(document, path, auto_create=False)
    
    if not ref.exists:
        raise PathError(f"Cannot delete non-existent path: {path}")
    
    if ref.parent is None:
        raise PathError("Cannot delete root")
    
    if isinstance(ref.parent, dict):
        return ref.parent.pop(ref.key)
    elif isinstance(ref.parent, list):
        return ref.parent.pop(ref.key)
    else:
        raise PathError(f"Cannot delete from {type(ref.parent).__name__}")


def path_to_string(segments: List[PathSegment]) -> str:
    """
    Convert path segments back to string representation.
    
    Args:
        segments: List of path segments
        
    Returns:
        String representation of path
        
    Examples:
        >>> segments = [PathSegment(key='entities'), PathSegment(index=0, is_array_access=True)]
        >>> path_to_string(segments)
        'entities[0]'
    """
    if not segments:
        return ""
    
    result = []
    for i, segment in enumerate(segments):
        if segment.is_array_access:
            result.append(f"[{segment.index}]")
        else:
            if i == 0:
                result.append(segment.key)
            else:
                result.append(f".{segment.key}")
    
    return "".join(result)
