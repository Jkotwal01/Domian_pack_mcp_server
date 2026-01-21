"""
MCP Tools for Domain Pack Management

This module orchestrates all operations:
1. Parse content
2. Validate schema
3. Apply operations
4. Validate result
5. Calculate diff
6. Store version

NO business logic here - only orchestration.
"""

from typing import Dict, Any, List
import traceback

# Import from other modules
from schema import validate_domain_pack
from operations import apply_operation, apply_batch, OperationError
from utils import parse_content, serialize_content, calculate_diff
from db import (
    create_session as db_create_session,
    get_session,
    get_latest_version,
    get_version,
    insert_version,
    list_versions,
    SessionNotFoundError,
    VersionNotFoundError,
    DatabaseError
)


class ToolError(Exception):
    """Raised when a tool operation fails"""
    pass


def create_session_tool(initial_content: str, file_type: str) -> Dict[str, Any]:
    """
    Create a new domain pack session.
    
    Args:
        initial_content: YAML or JSON string
        file_type: "yaml" or "json"
        
    Returns:
        {
            "success": true,
            "session_id": "uuid",
            "version": 1,
            "message": "Session created successfully"
        }
        
    Raises:
        ToolError: If creation fails
    """
    try:
        # Step 1: Parse content
        data = parse_content(initial_content, file_type)
        
        # Step 2: Validate schema
        validate_domain_pack(data)
        
        # Step 3: Create session in DB
        session_id = db_create_session(data, file_type)
        
        return {
            "success": True,
            "session_id": session_id,
            "version": 1,
            "message": "Session created successfully"
        }
        
    except Exception as e:
        raise ToolError(f"Failed to create session: {str(e)}")


def apply_change_tool(session_id: str, operation: Dict[str, Any], reason: str) -> Dict[str, Any]:
    """
    Apply a change operation to a domain pack.
    
    STRICT FLOW:
    1. Get latest version
    2. Parse content
    3. Validate current schema
    4. Apply operation
    5. Validate result schema
    6. Calculate diff
    7. Store new version
    
    If ANY step fails, abort without writing to DB.
    
    Args:
        session_id: Session UUID
        operation: Operation specification
        reason: Human-readable reason for change
        
    Returns:
        {
            "success": true,
            "session_id": "uuid",
            "version": 2,
            "diff": {...},
            "message": "Change applied successfully"
        }
        
    Raises:
        ToolError: If operation fails
    """
    try:
        # Step 1: Get latest version
        try:
            latest = get_latest_version(session_id)
            old_data = latest["content"]
        except SessionNotFoundError as e:
            raise ToolError(f"Session not found: {session_id}")
        
        # Step 2: Validate current schema
        try:
            validate_domain_pack(old_data)
        except Exception as e:
            raise ToolError(f"Current version has invalid schema: {str(e)}")
        
        # Step 3: Apply operation
        try:
            new_data = apply_operation(old_data, operation)
        except OperationError as e:
            raise ToolError(f"Operation failed: {str(e)}")
        
        # Step 4: Validate result schema
        try:
            validate_domain_pack(new_data)
        except Exception as e:
            raise ToolError(f"Result validation failed: {str(e)}")
        
        # Step 5: Calculate diff
        diff = calculate_diff(old_data, new_data)
        
        # Step 6: Store new version
        try:
            new_version = insert_version(session_id, new_data, diff, reason)
        except DatabaseError as e:
            raise ToolError(f"Failed to store version: {str(e)}")
        
        return {
            "success": True,
            "session_id": session_id,
            "version": new_version,
            "diff": diff,
            "message": "Change applied successfully"
        }
        
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")


def apply_batch_tool(session_id: str, operations: List[Dict[str, Any]], reason: str) -> Dict[str, Any]:
    """
    Apply multiple operations atomically.
    
    Args:
        session_id: Session UUID
        operations: List of operations
        reason: Human-readable reason for changes
        
    Returns:
        {
            "success": true,
            "session_id": "uuid",
            "version": 2,
            "diff": {...},
            "operations_count": 5,
            "message": "Batch applied successfully"
        }
        
    Raises:
        ToolError: If any operation fails
    """
    try:
        # Step 1: Get latest version
        try:
            latest = get_latest_version(session_id)
            old_data = latest["content"]
        except SessionNotFoundError:
            raise ToolError(f"Session not found: {session_id}")
        
        # Step 2: Validate current schema
        try:
            validate_domain_pack(old_data)
        except Exception as e:
            raise ToolError(f"Current version has invalid schema: {str(e)}")
        
        # Step 3: Apply batch (atomic)
        try:
            new_data = apply_batch(old_data, operations)
        except OperationError as e:
            raise ToolError(f"Batch operation failed: {str(e)}")
        
        # Step 4: Validate result schema
        try:
            validate_domain_pack(new_data)
        except Exception as e:
            raise ToolError(f"Result validation failed: {str(e)}")
        
        # Step 5: Calculate diff
        diff = calculate_diff(old_data, new_data)
        
        # Step 6: Store new version
        try:
            new_version = insert_version(session_id, new_data, diff, reason)
        except DatabaseError as e:
            raise ToolError(f"Failed to store version: {str(e)}")
        
        return {
            "success": True,
            "session_id": session_id,
            "version": new_version,
            "diff": diff,
            "operations_count": len(operations),
            "message": "Batch applied successfully"
        }
        
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")


def rollback_tool(session_id: str, target_version: int) -> Dict[str, Any]:
    """
    Rollback to a previous version.
    
    Creates a NEW version with the content from target_version.
    Never deletes history.
    
    Args:
        session_id: Session UUID
        target_version: Version number to rollback to
        
    Returns:
        {
            "success": true,
            "session_id": "uuid",
            "version": 5,
            "rolled_back_to": 3,
            "message": "Rolled back successfully"
        }
        
    Raises:
        ToolError: If rollback fails
    """
    try:
        # Step 1: Get target version
        try:
            target = get_version(session_id, target_version)
            target_data = target["content"]
        except VersionNotFoundError:
            raise ToolError(f"Version {target_version} not found")
        except SessionNotFoundError:
            raise ToolError(f"Session not found: {session_id}")
        
        # Step 2: Get current version for diff
        try:
            current = get_latest_version(session_id)
            current_data = current["content"]
        except Exception as e:
            raise ToolError(f"Failed to get current version: {str(e)}")
        
        # Step 3: Validate target schema
        try:
            validate_domain_pack(target_data)
        except Exception as e:
            raise ToolError(f"Target version has invalid schema: {str(e)}")
        
        # Step 4: Calculate diff
        diff = calculate_diff(current_data, target_data)
        
        # Step 5: Store as new version
        reason = f"Rollback to version {target_version}"
        try:
            new_version = insert_version(session_id, target_data, diff, reason)
        except DatabaseError as e:
            raise ToolError(f"Failed to store rollback version: {str(e)}")
        
        return {
            "success": True,
            "session_id": session_id,
            "version": new_version,
            "rolled_back_to": target_version,
            "message": f"Rolled back to version {target_version}"
        }
        
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")


def export_domain_pack_tool(session_id: str, file_type: str, version: int = None) -> Dict[str, Any]:
    """
    Export domain pack as YAML or JSON.
    
    Args:
        session_id: Session UUID
        file_type: "yaml" or "json"
        version: Optional version number (default: latest)
        
    Returns:
        {
            "success": true,
            "session_id": "uuid",
            "version": 3,
            "file_type": "yaml",
            "content": "...",
            "message": "Export successful"
        }
        
    Raises:
        ToolError: If export fails
    """
    try:
        # Step 1: Get version
        try:
            if version is None:
                data_version = get_latest_version(session_id)
            else:
                data_version = get_version(session_id, version)
            
            data = data_version["content"]
            version_num = data_version["version"]
            
        except (SessionNotFoundError, VersionNotFoundError) as e:
            raise ToolError(str(e))
        
        # Step 2: Validate schema
        try:
            validate_domain_pack(data)
        except Exception as e:
            raise ToolError(f"Data validation failed: {str(e)}")
        
        # Step 3: Serialize
        try:
            content = serialize_content(data, file_type)
        except Exception as e:
            raise ToolError(f"Serialization failed: {str(e)}")
        
        return {
            "success": True,
            "session_id": session_id,
            "version": version_num,
            "file_type": file_type,
            "content": content,
            "message": "Export successful"
        }
        
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")


def get_session_info_tool(session_id: str) -> Dict[str, Any]:
    """
    Get session information and version history.
    
    Args:
        session_id: Session UUID
        
    Returns:
        {
            "success": true,
            "session": {...},
            "current_version": 5,
            "versions": [...]
        }
        
    Raises:
        ToolError: If retrieval fails
    """
    try:
        session = get_session(session_id)
        versions = list_versions(session_id)
        
        return {
            "success": True,
            "session": session,
            "current_version": session["current_version"],
            "versions": versions
        }
        
    except SessionNotFoundError:
        raise ToolError(f"Session not found: {session_id}")
    except Exception as e:
        raise ToolError(f"Failed to get session info: {str(e)}")
