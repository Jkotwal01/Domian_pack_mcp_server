"""
MySQL Database Layer for Domain Pack MCP Server

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
import json
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List
from datetime import datetime

import mysql.connector
from mysql.connector import Error

load_dotenv()


# =========================
# Custom Exceptions
# =========================

class DatabaseError(Exception):
    """Raised when database operations fail"""
    pass


class SessionNotFoundError(DatabaseError):
    """Raised when session doesn't exist"""
    pass


class VersionNotFoundError(DatabaseError):
    """Raised when version doesn't exist"""
    pass


# =========================
# Connection Management
# =========================

def create_connection():
    """
    Create a new MySQL database connection.

    Environment variables:
    - DB_HOST (default: localhost)
    - DB_PORT (default: 3306)
    - DB_NAME (default: domain_pack)
    - DB_USER (default: root)
    - DB_PASSWORD (default: "")

    Returns:
        mysql.connector connection
    """
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            database=os.getenv("DB_NAME", "domain_pack"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
        )
    except Error as e:
        raise DatabaseError(f"Failed to connect to database: {e}")


# =========================
# Schema Initialization
# =========================

def init_database():
    """
    Initialize MySQL database schema.
    Creates tables and indexes if they don't exist.
    """
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id CHAR(36) PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP,
                current_version INT NOT NULL DEFAULT 1,
                file_type VARCHAR(10) NOT NULL,
                metadata JSON
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS versions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id CHAR(36) NOT NULL,
                version INT NOT NULL,
                content JSON NOT NULL,
                diff JSON,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uniq_session_version (session_id, version),
                FOREIGN KEY (session_id)
                    REFERENCES sessions(session_id)
                    ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE INDEX idx_versions_session_id
            ON versions(session_id)
        """)

        cursor.execute("""
            CREATE INDEX idx_versions_session_version
            ON versions(session_id, version DESC)
        """)

        conn.commit()

    except Error as e:
        if conn:
            conn.rollback()
        raise DatabaseError(f"Failed to initialize database: {e}")
    finally:
        if conn:
            conn.close()


# =========================
# Session Management
# =========================

def create_session(
    initial_content: Dict[str, Any],
    file_type: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a new domain pack session with initial content.
    """
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()

        session_id = str(uuid.uuid4())

        cursor.execute(
            """
            INSERT INTO sessions (session_id, file_type, metadata)
            VALUES (%s, %s, %s)
            """,
            (session_id, file_type, json.dumps(metadata) if metadata else None)
        )

        cursor.execute(
            """
            INSERT INTO versions (session_id, version, content, reason)
            VALUES (%s, %s, %s, %s)
            """,
            (session_id, 1, json.dumps(initial_content), "Initial version")
        )

        conn.commit()
        return session_id

    except Error as e:
        if conn:
            conn.rollback()
        raise DatabaseError(f"Failed to create session: {e}")
    finally:
        if conn:
            conn.close()


def get_session(session_id: str) -> Dict[str, Any]:
    """
    Retrieve session metadata.
    """
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT session_id, created_at, updated_at,
                   current_version, file_type, metadata
            FROM sessions
            WHERE session_id = %s
            """,
            (session_id,)
        )

        result = cursor.fetchone()
        if not result:
            raise SessionNotFoundError(f"Session not found: {session_id}")

        return result

    except Error as e:
        raise DatabaseError(f"Failed to get session: {e}")
    finally:
        if conn:
            conn.close()


# =========================
# Version Retrieval
# =========================

def get_latest_version(session_id: str) -> Dict[str, Any]:
    """
    Get the latest version of a domain pack.
    """
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)

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

        return result

    except Error as e:
        raise DatabaseError(f"Failed to get latest version: {e}")
    finally:
        if conn:
            conn.close()


def get_version(session_id: str, version: int) -> Dict[str, Any]:
    """
    Retrieve a specific version.
    """
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)

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
            raise VersionNotFoundError(
                f"Version {version} not found for session {session_id}"
            )

        return result

    except Error as e:
        raise DatabaseError(f"Failed to get version: {e}")
    finally:
        if conn:
            conn.close()


# =========================
# Version Mutation
# =========================

def insert_version(
    session_id: str,
    content: Dict[str, Any],
    diff: Dict[str, Any],
    reason: str
) -> int:
    """
    Insert a new immutable version for a session.
    """
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT current_version FROM sessions WHERE session_id = %s",
            (session_id,)
        )

        row = cursor.fetchone()
        if not row:
            raise SessionNotFoundError(f"Session not found: {session_id}")

        new_version = row[0] + 1

        cursor.execute(
            """
            INSERT INTO versions (session_id, version, content, diff, reason)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                session_id,
                new_version,
                json.dumps(content),
                json.dumps(diff),
                reason
            )
        )

        cursor.execute(
            """
            UPDATE sessions
            SET current_version = %s
            WHERE session_id = %s
            """,
            (new_version, session_id)
        )

        conn.commit()
        return new_version

    except Error as e:
        if conn:
            conn.rollback()
        raise DatabaseError(f"Failed to insert version: {e}")
    finally:
        if conn:
            conn.close()


# =========================
# Version Listing
# =========================

def list_versions(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    List version history (metadata only).
    """
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT version, reason, created_at,
                   JSON_KEYS(diff) AS change_keys
            FROM versions
            WHERE session_id = %s
            ORDER BY version DESC
            LIMIT %s
            """,
            (session_id, limit)
        )

        return cursor.fetchall()

    except Error as e:
        raise DatabaseError(f"Failed to list versions: {e}")
    finally:
        if conn:
            conn.close()


# =========================
# Deletion
# =========================

def delete_session(session_id: str):
    """
    Delete a session and all associated versions.
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

    except Error as e:
        if conn:
            conn.rollback()
        raise DatabaseError(f"Failed to delete session: {e}")
    finally:
        if conn:
            conn.close()
