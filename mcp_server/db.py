"""
PostgreSQL Database Layer for Domain Pack MCP Server

Handles:
- Database connection management
- Session creation and retrieval
- Version storage and retrieval
- Rollback support

Schema:
- sessions table: tracks all domain pack sessions
- versions table: stores immutable version history with diffs

All versions are immutable. Rollback creates a new version.
"""

import os
import uuid
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

load_dotenv()

class DatabaseError(Exception):
    """Raised when database operations fail"""
    pass


class SessionNotFoundError(DatabaseError):
    """Raised when session doesn't exist"""
    pass


class VersionNotFoundError(DatabaseError):
    """Raised when version doesn't exist"""
    pass


def get_connection_string() -> str:
    """
    Get PostgreSQL connection string from environment or use defaults.
    
    Environment variables:
    - DB_HOST (default: localhost)
    - DB_PORT (default: 5432)
    - DB_NAME (default: domain_pack_mcp)
    - DB_USER (default: postgres)
    - DB_PASSWORD (default: postgres)
    
    Returns:
        Connection string
    """
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "domain_pack_mcp")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")
    
    return f"host={host} port={port} dbname={dbname} user={user} password={password}"


def create_connection():
    """
    Create a new database connection.
    
    Returns:
        psycopg2 connection object
        
    Raises:
        DatabaseError: If connection fails
    """
    try:
        conn = psycopg2.connect(get_connection_string())
        conn.autocommit = False
        return conn
    except psycopg2.Error as e:
        raise DatabaseError(f"Failed to connect to database: {str(e)}")


def init_database():
    """
    Initialize database schema.
    Creates tables if they don't exist.
    
    Raises:
        DatabaseError: If initialization fails
    """
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Create sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id UUID PRIMARY KEY,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                current_version INTEGER NOT NULL DEFAULT 1,
                file_type VARCHAR(10) NOT NULL,
                metadata JSONB
            )
        """)
        
        # Create versions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS versions (
                id SERIAL PRIMARY KEY,
                session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
                version INTEGER NOT NULL,
                content JSONB NOT NULL,
                diff JSONB,
                reason TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                UNIQUE(session_id, version)
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_versions_session_id 
            ON versions(session_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_versions_session_version 
            ON versions(session_id, version DESC)
        """)
        
        conn.commit()
        
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        raise DatabaseError(f"Failed to initialize database: {str(e)}")
    finally:
        if conn:
            conn.close()


def create_session(initial_content: Dict[str, Any], file_type: str, metadata: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a new domain pack session with initial content.
    
    Args:
        initial_content: Initial domain pack data
        file_type: "yaml" or "json"
        metadata: Optional metadata
        
    Returns:
        Session ID (UUID string)
        
    Raises:
        DatabaseError: If creation fails
    """
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor() # It creates a cursor object from an existing database connection
        
        session_id = str(uuid.uuid4())
        
        # Insert session
        cursor.execute(
            """
            INSERT INTO sessions (session_id, file_type, metadata)
            VALUES (%s, %s, %s)
            """,
            (session_id, file_type, json.dumps(metadata) if metadata else None)
        )
        
        # Insert initial version
        cursor.execute(
            """
            INSERT INTO versions (session_id, version, content, reason)
            VALUES (%s, %s, %s, %s)
            """,
            (session_id, 1, json.dumps(initial_content), "Initial version")
        )
        
        conn.commit()
        return session_id
        
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        raise DatabaseError(f"Failed to create session: {str(e)}")
    finally:
        if conn:
            conn.close()


def get_session(session_id: str) -> Dict[str, Any]:
    """
    Get session information.
    Args:
        session_id: Session UUID
    Returns:
        Session data including current_version and file_type
    Raises:
        SessionNotFoundError: If session doesn't exist
        DatabaseError: If retrieval fails
    """
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        """
        A cursor is used to:
        Execute SQL commands
        Fetch results from the database
        Iterate over query results
        """
        
        cursor.execute(
            """
            SELECT session_id, created_at, updated_at, current_version, file_type, metadata
            FROM sessions
            WHERE session_id = %s
            """,
            (session_id,)
        )
        
        result = cursor.fetchone() #fetchone() retrieves the next row of a query result set
        if not result:
            raise SessionNotFoundError(f"Session not found: {session_id}")
        
        return dict(result)
        
    except psycopg2.Error as e:
        raise DatabaseError(f"Failed to get session: {str(e)}")
    finally:
        if conn:
            conn.close()


def get_latest_version(session_id: str) -> Dict[str, Any]:
    """
    Get the latest version of a domain pack.
    Args:
        session_id: Session UUID
    Returns:
        Dictionary with version number and content
    Raises:
        SessionNotFoundError: If session doesn't exist
        DatabaseError: If retrieval fails
    """
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute(
            """
            SELECT version, content, diff, reason, created_at
            FROM versions
            WHERE session_id = %s
            ORDER BY version DESC
            LIMIT 1
            """,
            (session_id,)
        )
        
        result = cursor.fetchone()
        if not result:
            raise SessionNotFoundError(f"No versions found for session: {session_id}")
        
        return dict(result)
        
    except psycopg2.Error as e:
        raise DatabaseError(f"Failed to get latest version: {str(e)}")
    finally:
        if conn:
            conn.close()


def get_version(session_id: str, version: int) -> Dict[str, Any]:
    """
    Get a specific version of a domain pack.
    
    Args:
        session_id: Session UUID
        version: Version number
        
    Returns:
        Dictionary with version data
        
    Raises:
        VersionNotFoundError: If version doesn't exist
        DatabaseError: If retrieval fails
    """
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute(
            """
            SELECT version, content, diff, reason, created_at
            FROM versions
            WHERE session_id = %s AND version = %s
            """,
            (session_id, version)
        )
        result = cursor.fetchone()
        if not result:
            raise VersionNotFoundError(f"Version {version} not found for session {session_id}")
        
        return dict(result)
        
    except psycopg2.Error as e:
        raise DatabaseError(f"Failed to get version: {str(e)}")
    finally:
        if conn:
            conn.close()


def insert_version(session_id: str, content: Dict[str, Any], diff: Dict[str, Any], reason: str) -> int:
    """
    Insert a new version for a session.
    Args:
        session_id: Session UUID
        content: Domain pack content
        diff: Diff from previous version
        reason: Reason for the change
        
    Returns:
        New version number
    Raises:
        SessionNotFoundError: If session doesn't exist
        DatabaseError: If insertion fails
    """
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Get current version
        cursor.execute(
            "SELECT current_version FROM sessions WHERE session_id = %s",
            (session_id,)
        )
        result = cursor.fetchone()
        if not result:
            raise SessionNotFoundError(f"Session not found: {session_id}")
        
        current_version = result[0]
        new_version = current_version + 1
        
        # Insert new version
        cursor.execute(
            """
            INSERT INTO versions (session_id, version, content, diff, reason)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (session_id, new_version, json.dumps(content), json.dumps(diff), reason)
        )
        
        # Update session
        cursor.execute(
            """
            UPDATE sessions
            SET current_version = %s, updated_at = NOW()
            WHERE session_id = %s
            """,
            (new_version, session_id)
        )
        
        conn.commit()
        return new_version
        
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        raise DatabaseError(f"Failed to insert version: {str(e)}")
    finally:
        if conn:
            conn.close()


def list_versions(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    List all versions for a session.
    Args:
        session_id: Session UUID
        limit: Maximum number of versions to return
    Returns:
        List of version metadata (without full content)
        
    Raises:
        DatabaseError: If retrieval fails
    """
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute(
            """
            SELECT version, reason, created_at,
                   jsonb_object_keys(diff) as change_keys
            FROM versions
            WHERE session_id = %s
            ORDER BY version DESC
            LIMIT %s
            """,
            (session_id, limit)
        )
        
        results = cursor.fetchall()
        return [dict(r) for r in results]
        
    except psycopg2.Error as e:
        raise DatabaseError(f"Failed to list versions: {str(e)}")
    finally:
        if conn:
            conn.close()


def delete_session(session_id: str):
    """
    Delete a session and all its versions.
    
    Args:
        session_id: Session UUID
        
    Raises:
        DatabaseError: If deletion fails
    """
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM sessions WHERE session_id = %s",
            (session_id,)
        )
        
        conn.commit()
        
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        raise DatabaseError(f"Failed to delete session: {str(e)}")
    finally:
        if conn:
            conn.close()
