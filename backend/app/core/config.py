from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Domain Pack Authoring API"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "domain_pack_mcp"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # LLM Provider Configuration
    LLM_PROVIDER: str = "openai"  # Options: openai, groq
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    
    # Embedding Model
    EMBEDDING_PROVIDER: str = "openai"
    EMBEDDING_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Backward compatibility
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # LangSmith
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: str = "domain-pack-authoring"
    LANGSMITH_TRACING: bool = False
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    
    # MCP Configuration
    MCP_YAML_SERVER_PATH: str = "D:\My Code\Enable\domain_pack_Gen\domain-pack-mcp\mcp_server\main.py"
    MCP_SEARCH_SERVER_ENABLED: bool = False
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    PROPOSAL_LIMIT_PER_HOUR: int = 10
    
    # Proposal Configuration
    PROPOSAL_EXPIRY_HOURS: int = 24
    AUTO_APPROVE_CONFIDENCE_THRESHOLD: float = 0.95
    HIGH_RISK_FIELD_THRESHOLD: int = 5
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def ASYNC_SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def get_llm_api_key(self) -> Optional[str]:
        """Get LLM API key with backward compatibility"""
        return self.LLM_API_KEY or self.OPENAI_API_KEY
    
    @property
    def get_llm_model(self) -> str:
        """Get LLM model with backward compatibility"""
        if self.LLM_MODEL:
            return self.LLM_MODEL
        
        # Default models per provider
        if self.LLM_PROVIDER == "groq":
            return "llama-3.3-70b-versatile"
        else:  # openai
            return self.OPENAI_MODEL
            
    @property
    def get_llm_base_url(self) -> Optional[str]:
        """Get LLM base URL based on provider"""
        if self.LLM_BASE_URL:
            return self.LLM_BASE_URL
            
        if self.LLM_PROVIDER == "groq":
            return "https://api.groq.com/openai/v1"
        
        return None  # Default OpenAI
    
    @property
    def get_embedding_api_key(self) -> Optional[str]:
        """Get embedding API key"""
        return self.EMBEDDING_API_KEY or self.OPENAI_API_KEY
    
    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse CORS allowed origins"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
