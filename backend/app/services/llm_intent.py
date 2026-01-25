"""
LLM Intent Extraction Service

Uses LLM to translate natural language into structured operations.
LLM is used ONLY for intent extraction, NOT for file manipulation.
"""

import json
import os
from typing import Dict, Any, Optional
from app.models.api_models import OperationSpec
from app.services.llm_providers import BaseLLMProvider, get_llm_provider
from app.core.config import settings


# System prompt for LLM
# System prompt for LLM
SYSTEM_PROMPT = """You translate user intent into structured operations for a domain pack editor.

RULES:
- NEVER edit files directly
- NEVER assume schema structure
- ONLY output operations from this list: add, replace, delete, update, merge, add_unique, assert
- ALWAYS wait for confirmation
- If uncertain, ask a clarifying question

OUTPUT SCHEMA:
{{
  "intent_summary": "string - human-readable description of what will be done",
  "operation": {{
    "action": "add | replace | delete | update | merge | add_unique | assert",
    "path": ["string"],  // path in domain pack structure
    "value": {{}}  // depends on action
  }}
}}

AVAILABLE OPERATIONS:
1. add - Add a value to a path (for dicts: adds new key, for arrays: appends)
2. replace - Replace value at path
3. delete - Delete value at path
4. update - Update multiple fields in an object
5. merge - Merge objects or arrays
6. add_unique - Add value only if it doesn't exist
7. assert - Assert a condition (validation)

CURRENT SCHEMA:
{schema_definition}

USER REQUEST:
{user_message}

Respond ONLY with valid JSON matching the OUTPUT SCHEMA above."""


class LLMIntentService:
    """
    Service for extracting structured operations from natural language.
    Supports multiple LLM providers (OpenAI, Groq, etc.) through configuration.
    """
    
    def __init__(
        self,
        provider: Optional[BaseLLMProvider] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        provider_name: Optional[str] = None
    ):
        """
        Initialize LLM Intent Service.
        
        Args:
            provider: Pre-configured provider instance (takes precedence)
            api_key: API key (falls back to config)
            model: Model name (falls back to config)
            provider_name: Provider name (falls back to config)
        """
        if provider:
            self.provider = provider
        else:
            # Get configuration from settings or parameters
            api_key = api_key or settings.get_llm_api_key
            model = model or settings.get_llm_model
            provider_name = provider_name or settings.LLM_PROVIDER
            
            if not api_key:
                raise RuntimeError(
                    f"LLM API key not configured. Set LLM_API_KEY or "
                    f"OPENAI_API_KEY in environment variables."
                )
            
            # Create provider using factory
            self.provider = get_llm_provider(
                provider_name=provider_name,
                api_key=api_key,
                model=model,
                base_url=settings.LLM_BASE_URL
            )
    
    async def extract_intent(
        self,
        user_message: str,
        schema_definition: Dict[str, Any]
    ) -> tuple[str, OperationSpec]:
        """
        Extract structured operation from natural language.
        
        Args:
            user_message: Natural language message from user
            schema_definition: Current domain pack schema for context
            
        Returns:
            Tuple of (intent_summary, operation_spec)
            
        Raises:
            ValueError: If LLM response is invalid
            RuntimeError: If LLM API call fails
        """
        if not self.provider:
            raise RuntimeError("LLM provider not configured")
        
        # Build prompt with schema context
        prompt = SYSTEM_PROMPT.format(
            schema_definition=json.dumps(schema_definition, indent=2),
            user_message=user_message
        )
        
        try:
            # Call LLM without streaming
            response_text = await self._complete(prompt)
            
            # Parse JSON response
            response_data = self._parse_llm_response(response_text)
            
            # Extract intent summary and operation
            intent_summary = response_data.get("intent_summary", "")
            operation_data = response_data.get("operation", {})
            
            if not intent_summary or not operation_data:
                raise ValueError("LLM response missing required fields")
            
            # Convert to OperationSpec
            operation = OperationSpec(**operation_data)
            
            return intent_summary, operation
            
        except Exception as e:
            raise RuntimeError(f"LLM intent extraction failed: {str(e)}")
    
    async def _complete(self, prompt: str) -> str:
        """
        Get completion from LLM without streaming.
        
        Args:
            prompt: System prompt
            
        Returns:
            LLM response text
        """
        return await self.provider.complete(
            prompt=prompt,
            temperature=0.1,  # Low temperature for more deterministic output
            response_format={"type": "json_object"}  # Ensure JSON response
        )
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse and validate LLM JSON response.
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            Parsed JSON data
            
        Raises:
            ValueError: If response is not valid JSON
        """
        try:
            # Try to parse as JSON
            data = json.loads(response_text)
            return data
        except json.JSONDecodeError as e:
            # Try to extract JSON from markdown code blocks
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            
            raise ValueError(f"LLM response is not valid JSON: {str(e)}")


# Global LLM service instance
llm_service = LLMIntentService()
