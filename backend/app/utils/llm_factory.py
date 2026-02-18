"""Factory for creating LLM instances based on configuration."""
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from app.config import settings

def get_llm(model: str = None, temperature: float = 0):
    """
    Get a configured LLM instance.
    
    Args:
        model: Optional model name to override the default for the provider
        temperature: Sampling temperature
        
    Returns:
        LLM instance (ChatOpenAI or ChatGroq)
    """
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "groq":
        model_name = model or settings.GROQ_MODEL
        return ChatGroq(
            model=model_name,
            temperature=temperature,
            groq_api_key=settings.GROQ_API_KEY
        )
    else:
        # Default to OpenAI
        model_name = model or settings.OPENAI_MODEL
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=settings.OPENAI_API_KEY
        )
