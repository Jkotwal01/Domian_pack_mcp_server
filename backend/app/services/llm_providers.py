"""
LLM Provider Abstraction Layer

Provides a unified interface for different LLM providers (OpenAI, Groq, etc.)
Allows dynamic provider selection through configuration.
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable
from openai import AsyncOpenAI
from groq import AsyncGroq


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
    
    @abstractmethod
    async def complete(
        self,
        prompt: str,
        temperature: float = 0.1,
        response_format: Optional[dict] = None
    ) -> str:
        """
        Get completion from LLM without streaming.
        
        Args:
            prompt: System prompt
            temperature: Temperature for generation
            response_format: Response format specification
            
        Returns:
            LLM response text
        """
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider implementation"""
    
    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None):
        super().__init__(api_key, model, base_url)
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    async def complete(
        self,
        prompt: str,
        temperature: float = 0.1,
        response_format: Optional[dict] = None
    ) -> str:
        """Get completion from OpenAI without streaming"""
        kwargs = {
            "model": self.model,
            "messages": [{"role": "system", "content": prompt}],
            "temperature": temperature
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = await self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content


class GroqProvider(BaseLLMProvider):
    """Groq LLM provider implementation"""
    
    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None):
        super().__init__(api_key, model, base_url)
        # Groq uses OpenAI-compatible API
        kwargs = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        self.client = AsyncGroq(**kwargs)
    
    async def complete(
        self,
        prompt: str,
        temperature: float = 0.1,
        response_format: Optional[dict] = None
    ) -> str:
        """Get completion from Groq without streaming"""
        kwargs = {
            "model": self.model,
            "messages": [{"role": "system", "content": prompt}],
            "temperature": temperature
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = await self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content


def get_llm_provider(
    provider_name: str,
    api_key: str,
    model: str,
    base_url: Optional[str] = None
) -> BaseLLMProvider:
    """
    Factory function to get the appropriate LLM provider.
    
    Args:
        provider_name: Name of the provider (openai, groq)
        api_key: API key for the provider
        model: Model name to use
        base_url: Optional custom base URL
        
    Returns:
        LLM provider instance
        
    Raises:
        ValueError: If provider is not supported
    """
    provider_name = provider_name.lower()
    
    if provider_name == "openai":
        return OpenAIProvider(api_key, model, base_url)
    elif provider_name == "groq":
        return GroqProvider(api_key, model, base_url)
    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider_name}. "
            f"Supported providers: openai, groq"
        )
