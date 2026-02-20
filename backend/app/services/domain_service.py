"""Domain configuration service."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Dict, Any
from uuid import UUID
from app.models.domain_config import DomainConfig
from app.models.user import User
from app.schemas.domain import DomainConfigCreate, DomainConfigUpdate
from app.utils.templates import generate_domain_template


class DomainService:
    """Service for domain configuration operations."""
    
    @staticmethod
    async def create_domain(
        db: Session, 
        domain_data: DomainConfigCreate, 
        user: User,
        pdf_file: bytes = None,
        filename: str = None
    ) -> DomainConfig:
        """
        Create a new domain configuration with AI-generated template (or fallback).
        
        Args:
            db: Database session
            domain_data: Domain creation data
            user: Owner user
            pdf_file: Optional PDF file bytes for context
            filename: Optional filename of the PDF
            
        Returns:
            Created domain configuration
        """
        from app.utils.rag_manager import ingest_pdf, _get_retriever
        import uuid
        
        # Temporary thread ID for generation session if not provided
        # In a real app, this might be linked to a chat session
        gen_thread_id = str(uuid.uuid4())
        
        retriever = None
        if pdf_file:
            try:
                ingest_pdf(pdf_file, gen_thread_id, filename)
                retriever = _get_retriever(gen_thread_id)
            except Exception as e:
                import logging
                logging.getLogger("uvicorn.error").error(f"Failed to ingest PDF for domain creation: {str(e)}")

        # Create domain config with AI template or fallback
        config_json = await generate_domain_template(
            domain_name=domain_data.name,
            description=domain_data.description or "",
            version=domain_data.version,
            retriever=retriever
        )
        
        db_domain = DomainConfig(
            owner_user_id=user.id,
            name=domain_data.name,
            description=domain_data.description,
            version=domain_data.version,
            config_json=config_json
        )
        
        # Update counts and metadata
        db_domain.sync_from_config()
        
        db.add(db_domain)
        db.commit()
        db.refresh(db_domain)
        
        return db_domain
    
    @staticmethod
    def get_user_domains(db: Session, user: User) -> List[DomainConfig]:
        """
        Get all domains owned by a user.
        
        Args:
            db: Database session
            user: Owner user
            
        Returns:
            List of domain configurations
        """
        return db.query(DomainConfig).filter(
            DomainConfig.owner_user_id == user.id
        ).order_by(DomainConfig.updated_at.desc()).all()
    
    @staticmethod
    def get_domain_by_id(db: Session, domain_id: UUID, user: User) -> DomainConfig:
        """
        Get a domain configuration by ID.
        
        Args:
            db: Database session
            domain_id: Domain UUID
            user: Current user
            
        Returns:
            Domain configuration
            
        Raises:
            HTTPException: If domain not found or access denied
        """
        domain = db.query(DomainConfig).filter(DomainConfig.id == domain_id).first()
        
        if not domain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain not found"
            )
        
        if domain.owner_user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return domain
    
    @staticmethod
    def update_domain(
        db: Session,
        domain_id: UUID,
        domain_data: DomainConfigUpdate,
        user: User
    ) -> DomainConfig:
        """
        Update a domain configuration.
        
        Args:
            db: Database session
            domain_id: Domain UUID
            domain_data: Update data
            user: Current user
            
        Returns:
            Updated domain configuration
        """
        domain = DomainService.get_domain_by_id(db, domain_id, user)
        
        # Update fields
        if domain_data.name is not None:
            domain.name = domain_data.name
        if domain_data.description is not None:
            domain.description = domain_data.description
        if domain_data.version is not None:
            domain.version = domain_data.version
        if domain_data.config_json is not None:
            domain.config_json = domain_data.config_json
            domain.sync_from_config()
        
        db.commit()
        db.refresh(domain)
        
        return domain
    
    @staticmethod
    def delete_domain(db: Session, domain_id: UUID, user: User) -> None:
        """
        Delete a domain configuration.
        
        Args:
            db: Database session
            domain_id: Domain UUID
            user: Current user
        """
        domain = DomainService.get_domain_by_id(db, domain_id, user)
        db.delete(domain)
        db.commit()
    
    @staticmethod
    def update_config_json(
        db: Session,
        domain_id: UUID,
        config_json: Dict[str, Any],
        user: User
    ) -> DomainConfig:
        """
        Update the config_json of a domain (used by chatbot).
        
        Args:
            db: Database session
            domain_id: Domain UUID
            config_json: New configuration JSON
            user: Current user
            
        Returns:
            Updated domain configuration
        """
        domain = DomainService.get_domain_by_id(db, domain_id, user)
        domain.config_json = config_json
        domain.sync_from_config()
        
        db.commit()
        db.refresh(domain)
        
        return domain
