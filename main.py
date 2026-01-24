"""
Domain Pack MCP Server - Main Entry Point.
"""

import sys
from fastmcp import FastMCP
from typing import Dict, Any, List
import os

# Import tools
from tools import (
    create_session_tool,
    apply_change_tool,
    apply_batch_tool,
    rollback_tool,
    export_domain_pack_tool,
    get_session_info_tool,
    ToolError
)

# Import database initialization
from db import init_database, DatabaseError


# Create FastMCP instance
mcp = FastMCP("Domain Pack MCP Server")


@mcp.tool()
def create_session(initial_content: str, file_type: str) -> Dict[str, Any]:
    """
    Create a new domain pack session with initial content.
    
    IMPORTANT USAGE RULES:
    1. 'initial_content' must be a VALID YAML or JSON string, NOT a placeholder.
    2. 'file_type' must be "yaml" or "json".
    
    Args:
        initial_content: The complete initial content of the domain pack.
                        MUST be a valid dictionary string (e.g. YAML or JSON).
                        DO NOT send "template goes here". Send the ACTUAL template.
        file_type: "yaml" or "json"
        
    Returns:
        Session information including session_id
        
    Example:
        create_session(
            initial_content=\"\"\"
name: Legal
description: Legal domain
version: 1.0.0
entities: []
\"\"\",
            file_type="yaml"
        )
    """
    try:
        return create_session_tool(initial_content, file_type)
    except ToolError as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create session"
        }

@mcp.tool()
def apply_change(session_id: str, operation: Dict[str, Any], reason: str) -> Dict[str, Any]:
    """
    Apply a single operation to a domain pack.
    
    Args:
        session_id: Session UUID from create_session
        operation: Operation dictionary containing:
                  - action: "add", "replace", "remove", "move", "copy", "test"
                  - path: List of keys/indices to target (e.g. ["entities", 0, "name"])
                  - value: New value (for add/replace/test)
        reason: Human-readable reason for the change
        
    Returns:
        Result including new version number and diff
        
    Example:
        apply_change(
            session_id="uuid-here",
            operation={
                "action": "add",
                "path": ["entities"],
                "value": {"name": "NewEntity", "type": "TEST"}
            },
            reason="Adding new entity"
        )
    """
    try:
        return apply_change_tool(session_id, operation, reason)
    except ToolError as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to apply change"
        }


@mcp.tool()
def apply_batch(session_id: str, operations: List[Dict[str, Any]], reason: str) -> Dict[str, Any]:
    """
    Apply multiple operations atomically to a domain pack.
    
    Args:
        session_id: Session UUID from create_session
        operations: List of operation dictionaries (see apply_change for format)
        reason: Human-readable reason for the changes
        
    Returns:
        Result including new version number and diff
        
    Example:
        apply_batch(
            session_id="uuid-here",
            operations=[
                {"action": "replace", "path": ["version"], "value": "1.1.0"},
                {"action": "add", "path": ["key_terms"], "value": "compliance"}
            ],
            reason="Bumping version and adding term"
        )
    """
    try:
        return apply_batch_tool(session_id, operations, reason)
    except ToolError as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to apply batch"
        }


@mcp.tool()
def rollback(session_id: str, target_version: int) -> Dict[str, Any]:
    """
    Rollback to a previous version.
    Creates a new version with content from target_version.
    Never deletes history - rollback is a new version.
    Args:
        session_id: Session UUID from create_session
        target_version: Version number to rollback to
        
    Returns:
        Result including new version number
        
    Example:
        rollback(
            session_id="uuid-here",
            target_version=3
        )
    """
    try:
        return rollback_tool(session_id, target_version)
    except ToolError as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to rollback"
        }


@mcp.tool()
def export_domain_pack(session_id: str, file_type: str, version: int = None) -> Dict[str, Any]:
    """
    Export domain pack as YAML or JSON.
    Args:
        session_id: Session UUID from create_session
        file_type: Output format - "yaml" or "json"
        version: Optional version number (default: latest)
    Returns:
        Domain pack content as string
        
    Example:
        export_domain_pack(
            session_id="uuid-here",
            file_type="yaml"
        )
    """
    try:
        return export_domain_pack_tool(session_id, file_type, version)
    except ToolError as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to export"
        }


@mcp.tool()
def get_session_info(session_id: str) -> Dict[str, Any]:
    """
    Get session information and version history.
    Args:
        session_id: Session UUID from create_session
        
    Returns:
        Session metadata and version list
        
    Example:
        get_session_info(session_id="uuid-here")
    """
    try:
        return get_session_info_tool(session_id)
    except ToolError as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get session info"
        }


def main():
    """
    Main entry point.
    Initializes database and runs the MCP server.
    """
    try:
        print("DB: Initializing database.", file=sys.stderr)
        init_database()
        print("DB: Database initialized successfully.", file=sys.stderr)

        print("SERVER: Starting Domain Pack MCP Server", file=sys.stderr)
        mcp.run()

    except DatabaseError as e:
        print(f"Database initialization failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Server failed to start: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
