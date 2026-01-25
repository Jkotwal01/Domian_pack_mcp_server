"""
LLM Intent Extraction Service

Uses LLM to translate natural language into structured operations.
LLM is used ONLY for intent extraction, NOT for file manipulation.
"""

import json
import os
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from app.models.api_models import OperationSpec


# System prompt for LLM
SYSTEM_PROMPT = """You translate user intent into structured operations for a domain pack editor.

RULES:
- NEVER edit files directly
- NEVER assume schema structure
- ONLY output operations from this list: add, replace, delete, update, merge, add_unique, assert
- ALWAYS wait for confirmation
- If uncertain, ask a clarifying question

OUTPUT SCHEMA:
{
  "intent_summary": "string - human-readable description of what will be done",
  "operation": {
    "action": "add | replace | delete | update | merge | add_unique | assert",
    "path": ["string"],  // path in domain pack structure
    "value": {}  // depends on action
  }
}

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
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
    
    async def extract_intent(
        self,
        user_message: str,
        schema_definition: Dict[str, Any],
        stream_callback: Optional[callable] = None
    ) -> tuple[str, OperationSpec]:
        """
        Extract structured operation from natural language.
        
        Args:
            user_message: Natural language message from user
            schema_definition: Current domain pack schema for context
            stream_callback: Optional callback for streaming LLM chunks
            
        Returns:
            Tuple of (intent_summary, operation_spec)
            
        Raises:
            ValueError: If LLM response is invalid
            RuntimeError: If LLM API call fails
        """
        if not self.client:
            raise RuntimeError("OpenAI API key not configured")
        
        # Build prompt with schema context
        prompt = SYSTEM_PROMPT.format(
            schema_definition=json.dumps(schema_definition, indent=2),
            user_message=user_message
        )
        
        try:
            # Call LLM with streaming if callback provided
            if stream_callback:
                response_text = await self._stream_completion(prompt, stream_callback)
            else:
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
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": prompt}],
            temperature=0.1,  # Low temperature for more deterministic output
            response_format={"type": "json_object"}  # Ensure JSON response
        )
        
        return response.choices[0].message.content
    
    async def _stream_completion(self, prompt: str, callback: callable) -> str:
        """
        Get completion from LLM with streaming.
        
        Args:
            prompt: System prompt
            callback: Async callback function for each chunk
            
        Returns:
            Complete LLM response text
        """
        full_response = ""
        
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                await callback(content)  # Stream chunk to callback
        
        return full_response
    
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
