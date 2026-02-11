"""Authentication service for user management."""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.utils.security import get_password_hash, verify_password, create_access_token
from typing import Optional


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            db: Database session
            user_data: User creation data
            
        Returns:
            Created user
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if user exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            password_hash=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, user_data: UserLogin) -> Optional[User]:
        """
        Authenticate a user with email and password.
        
        Args:
            db: Database session
            user_data: Login credentials
            
        Returns:
            User if authenticated, None otherwise
        """
        user = db.query(User).filter(User.email == user_data.email).first()
        if not user:
            return None
        if not verify_password(user_data.password, user.password_hash):
            return None
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_token_for_user(user: User) -> str:
        """
        Create JWT token for user.
        
        Args:
            user: User object
            
        Returns:
            JWT token string
        """
        token_data = {
            "sub": str(user.id),
            "email": user.email
        }
        return create_access_token(token_data)
