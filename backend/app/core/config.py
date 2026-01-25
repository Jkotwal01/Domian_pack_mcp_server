from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Domain Pack Generator API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "domain_pack_mcp"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    
    # LLM Provider Configuration
    LLM_PROVIDER: str = "openai"  # Options: openai, groq
    LLM_API_KEY: Optional[str] = None  # Generic API key
    LLM_MODEL: Optional[str] = None  # Generic model name
    LLM_BASE_URL: Optional[str] = None  # Custom base URL for provider
    
    # Backward compatibility - OpenAI specific (deprecated)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Intent Guard Configuration
    INTENT_TIMEOUT_SECONDS: int = 300
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
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

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
