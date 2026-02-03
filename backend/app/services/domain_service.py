import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import desc

from app.db.models import Session, Version
from app.core.db import SessionNotFoundError, VersionNotFoundError
from app.logic.schema import validate_domain_pack
from app.logic.operations import apply_batch, CRUDError
from app.logic.utils import calculate_diff
from app.models.api_models import SessionCreateRequest

class DomainService:
    def __init__(self, db: DBSession):
        self.db = db

    def create_session(self, request: CreateSessionRequest) -> Session:
        # Validate initial content
        validate_domain_pack(request.initial_content)
        
        session_id = uuid.uuid4()
        
        # Create Session
        db_session = Session(
            session_id=session_id,
            file_type=request.file_type,
            metadata_=request.metadata,
            current_version=1
        )
        self.db.add(db_session)
        
        # Create Initial Version
        db_version = Version(
            session_id=session_id,
            version=1,
            content=request.initial_content,
            diff=None,
            reason="Initial version"
        )
        self.db.add(db_version)
        
        self.db.commit()
        self.db.refresh(db_session)
        return db_session

    def get_session(self, session_id: uuid.UUID) -> Session:
        session = self.db.query(Session).filter(Session.session_id == session_id).first()
        if not session:
            raise SessionNotFoundError(f"Session not found: {session_id}")
        return session

    def get_latest_version(self, session_id: uuid.UUID) -> Version:
        version = self.db.query(Version).filter(
            Version.session_id == session_id
        ).order_by(desc(Version.version)).first()
        
        if not version:
             # Should not happen if session exists unless data corruption, but check anyway
             raise VersionNotFoundError(f"No versions found for session {session_id}")
        return version

    def get_version(self, session_id: uuid.UUID, version_num: int) -> Version:
        version = self.db.query(Version).filter(
            Version.session_id == session_id,
            Version.version == version_num
        ).first()
        if not version:
            raise VersionNotFoundError(f"Version {version_num} not found for session {session_id}")
        return version
    
    def list_versions(self, session_id: uuid.UUID, limit: int = 50) -> List[Version]:
        # Check if session exists first
        self.get_session(session_id)
        
        versions = self.db.query(Version).filter(
            Version.session_id == session_id
        ).order_by(desc(Version.version)).limit(limit).all()
        return versions

    def apply_operations(self, session_id: uuid.UUID, operations: List[Dict[str, Any]]) -> Version:
        # Get Session and Latest Version
        db_session = self.get_session(session_id)
        current_version_obj = self.get_latest_version(session_id)
        current_content = current_version_obj.content
        
        # Apply Operations (Pure)
        try:
            new_content = apply_batch(current_content, operations)
        except CRUDError as e:
            # Re-raise as ValueError for API to handle
            raise ValueError(f"Operation failed: {str(e)}")

        # Validate New Content (Schema)
        validate_domain_pack(new_content)
        
        # Calculate Diff
        diff = calculate_diff(current_content, new_content)
        
        # Create New Version
        new_version_num = current_version_obj.version + 1
        new_version = Version(
            session_id=session_id,
            version=new_version_num,
            content=new_content,
            diff=diff,
            reason=f"Applied {len(operations)} operations"
        )
        
        self.db.add(new_version)
        
        # Update Session
        db_session.current_version = new_version_num
        
        self.db.commit()
        self.db.refresh(new_version)
        return new_version

    def delete_session(self, session_id: uuid.UUID):
        session = self.get_session(session_id)
        self.db.delete(session)
        self.db.commit()
