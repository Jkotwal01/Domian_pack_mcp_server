"""
Version Management for Domain Pack

Handles automatic version bumping for domain pack version field.
"""

from typing import Dict, Any


class VersionError(Exception):
    """Raised when version operations fail"""
    pass


def bump_version(data: Dict[str, Any], bump_type: str = "patch") -> None:
    """
    Auto-increment version field (major.minor.patch) in place.
    
    Args:
        data: Domain pack data (must have 'version' field)
        bump_type: Type of bump - "major", "minor", or "patch" (default)
        
    Raises:
        VersionError: If version field is missing or invalid
        
    Examples:
        >>> data = {"version": "1.2.3"}
        >>> bump_version(data, "patch")
        >>> data["version"]
        '1.2.4'
        
        >>> bump_version(data, "minor")
        >>> data["version"]
        '1.3.0'
        
        >>> bump_version(data, "major")
        >>> data["version"]
        '2.0.0'
    """
    if "version" not in data:
        raise VersionError("Domain pack data must have 'version' field")
    
    version_str = data["version"]
    
    if not isinstance(version_str, str):
        raise VersionError(f"Version must be a string, got {type(version_str).__name__}")
    
    # Parse version
    parts = version_str.split(".")
    if len(parts) != 3:
        raise VersionError(f"Version must be in format 'major.minor.patch', got '{version_str}'")
    
    try:
        major, minor, patch = map(int, parts)
    except ValueError:
        raise VersionError(f"Version parts must be integers, got '{version_str}'")
    
    # Bump version based on type
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise VersionError(f"Invalid bump type '{bump_type}'. Must be 'major', 'minor', or 'patch'")
    
    # Update in place
    data["version"] = f"{major}.{minor}.{patch}"


def parse_version(version_str: str) -> tuple[int, int, int]:
    """
    Parse semantic version string into (major, minor, patch) tuple.
    
    Args:
        version_str: Version string in format "major.minor.patch"
        
    Returns:
        Tuple of (major, minor, patch) as integers
        
    Raises:
        VersionError: If version format is invalid
    """
    if not isinstance(version_str, str):
        raise VersionError(f"Version must be a string, got {type(version_str).__name__}")
    
    parts = version_str.split(".")
    if len(parts) != 3:
        raise VersionError(f"Version must be in format 'major.minor.patch', got '{version_str}'")
    
    try:
        return tuple(map(int, parts))
    except ValueError:
        raise VersionError(f"Version parts must be integers, got '{version_str}'")


def compare_versions(v1: str, v2: str) -> int:
    """
    Compare two semantic versions.
    
    Args:
        v1: First version string
        v2: Second version string
        
    Returns:
        -1 if v1 < v2
         0 if v1 == v2
         1 if v1 > v2
         
    Raises:
        VersionError: If version format is invalid
    """
    major1, minor1, patch1 = parse_version(v1)
    major2, minor2, patch2 = parse_version(v2)
    
    if (major1, minor1, patch1) < (major2, minor2, patch2):
        return -1
    elif (major1, minor1, patch1) > (major2, minor2, patch2):
        return 1
    else:
        return 0
