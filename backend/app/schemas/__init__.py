"""Schemas package initialization."""
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, TokenData
from app.schemas.domain import (
    DomainConfigCreate,
    DomainConfigUpdate,
    DomainConfigResponse,
    DomainConfigList,
    EntitySchema,
    RelationshipSchema,
    ExtractionPatternSchema
)
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatRequest,
    ChatResponse
)

__all__ = [
    "UserCreate", "UserLogin", "UserResponse", "Token", "TokenData",
    "DomainConfigCreate", "DomainConfigUpdate", "DomainConfigResponse", "DomainConfigList",
    "EntitySchema", "RelationshipSchema", "ExtractionPatternSchema",
    "ChatSessionCreate", "ChatSessionResponse", "ChatMessageCreate", "ChatMessageResponse",
    "ChatRequest", "ChatResponse"
]
