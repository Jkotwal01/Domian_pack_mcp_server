"""
Base classes for API endpoints using OOP principles.
Reduces code duplication and provides consistent error handling.
"""

from fastapi import HTTPException, status
from typing import Callable, Any, Dict
import logging
from functools import wraps

from app.core import db


class BaseEndpoint:
    """Base class for all API endpoints with common error handling."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def handle_db_errors(self, func: Callable) -> Callable:
        """
        Decorator for consistent database error handling.
        """
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except db.SessionNotFoundError as e:
                self.logger.error(f"Session not found: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found"
                )
            except db.VersionNotFoundError as e:
                self.logger.error(f"Version not found: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=str(e)
                )
            except db.DatabaseError as e:
                self.logger.error(f"Database error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database operation failed"
                )
            except ValueError as e:
                self.logger.error(f"Validation error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
            except Exception as e:
                self.logger.error(f"Unexpected error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e)
                )
        return wrapper


class SessionEndpoint(BaseEndpoint):
    """Handles session-related operations."""
    
    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get session information with error handling."""
        return db.get_session(session_id)
    
    async def create_new_session(
        self,
        content: Dict[str, Any],
        file_type: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Create a new session with error handling."""
        return db.create_session(content, file_type, metadata)
    
    async def remove_session(self, session_id: str) -> None:
        """Delete a session with error handling."""
        db.delete_session(session_id)


class VersionEndpoint(BaseEndpoint):
    """Handles version-related operations."""
    
    async def get_version_list(self, session_id: str, limit: int = 50) -> list:
        """Get list of versions for a session."""
        return db.list_versions(session_id, limit=limit)
    
    async def get_version_data(self, session_id: str, version: int) -> Dict[str, Any]:
        """Get specific version data."""
        return db.get_version(session_id, version)
    
    async def get_latest_version(self, session_id: str) -> Dict[str, Any]:
        """Get latest version for a session."""
        return db.get_latest_version(session_id)

    async def remove_version(self, session_id: str, version: int) -> None:
        """Delete a specific version with error handling."""
        db.delete_version(session_id, version)


class DashboardEndpoint(BaseEndpoint):
    """Handles dashboard-related operations."""
    
    async def get_all_sessions(self) -> list:
        """Get all sessions with metadata."""
        return db.list_all_sessions()
    
    async def get_all_versions(self) -> list:
        """Get all latest versions across sessions."""
        return db.get_all_latest_versions()
    
    async def get_session_with_versions(self, session_id: str) -> Dict[str, Any]:
        """Get session with all its versions."""
        return db.get_session_with_versions(session_id)


def extract_domain_name(content: Dict[str, Any]) -> str:
    """
    Extract domain name from content.
    Centralized helper function to avoid duplication.
    """
    if isinstance(content, dict):
        return content.get("name", "Unknown")
    return "Unknown"


def extract_semantic_version(content: Dict[str, Any]) -> str:
    """
    Extract semantic version from content.
    Centralized helper function to avoid duplication.
    """
    if isinstance(content, dict):
        return content.get("version", "0.0.0")
    return "0.0.0"
