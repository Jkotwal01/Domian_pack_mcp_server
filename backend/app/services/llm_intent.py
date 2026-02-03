"""
LLM Intent Extraction Service

Uses LLM to translate natural language into structured operations.
LLM is used ONLY for intent extraction, NOT for file manipulation.
"""

import json
import os
from typing import Dict, Any, List, Optional
from app.models.api_models import OperationSpec
from app.services.llm_providers import BaseLLMProvider, get_llm_provider
from app.core.config import settings


# System prompt for LLM - CRUD Operations
SYSTEM_PROMPT = """You translate user intent into structured CRUD operations for a domain pack editor.

RULES:
- NEVER edit files directly
- NEVER assume schema structure
- ONLY use the 4 CRUD operations: CREATE, READ, UPDATE, DELETE
- ALWAYS wait for confirmation before applying changes
- If uncertain, ask a clarifying question
- Use exact operation names (uppercase)

OUTPUT SCHEMA:
{{
  "type": "suggestion | operation",
  "message": "string - conversational response for 'suggestion', or summary for 'operation'",
  "operations": [  // ONLY required if type is 'operation'
    {{
      "op": "CREATE | READ | UPDATE | DELETE",
      "path": ["key1", "key2", ...],  // List of strings for navigation
      "value": {{}}  // Only for CREATE and UPDATE
    }}
  ]
}}

GUIDELINES:
1. If user is asking for ideas, enhancements, or "what should I do", set type="suggestion" and provide helpful natural language response in detail as per user request. Leave "operations" empty or null.
2. If user is requesting a specific change, set type="operation", provide brief summary in "message", and define the "operations" list with appropriate CRUD operations.

AVAILABLE OPERATIONS (4 primitives):

1. CREATE - Create a new key in dict or insert/append to list
   - For dicts: Creates new key (fails if exists)
   - For lists: Use "-" as final path element to append, or integer index to insert
   - Requires: path, value
   - Example: {{"op": "CREATE", "path": ["entities", "-"], "value": {{"name": "User", "fields": []}}}}
   - Example: {{"op": "CREATE", "path": ["entities", "0", "fields", "-"], "value": "id"}}

2. READ - Fetch value at path (for validation/debug)
   - Returns value without modification
   - Requires: path
   - Example: {{"op": "READ", "path": ["entities", "0", "name"]}}

3. UPDATE - Replace value at existing path
   - Path MUST exist (fails if not)
   - Requires: path, value
   - Example: {{"op": "UPDATE", "path": ["version"], "value": "2.0.0"}}
   - Example: {{"op": "UPDATE", "path": ["entities", "0", "name"], "value": "UpdatedName"}}

4. DELETE - Remove key from dict or item from list
   - Path MUST exist (fails if not)
   - Requires: path
   - Example: {{"op": "DELETE", "path": ["entities", "0", "fields", "1"]}}

PATH FORMAT:
- Always use list of strings: ["key1", "key2", ...]
- For list indices, use string numbers: ["items", "0", "fields", "2"]
- To append to list, use "-": ["items", "-"]
- Empty path [] only valid for READ (returns entire data)

DOMAIN PACK STRUCTURE AND REQUIRED FIELDS:

Root level (REQUIRED fields):
- name: string (min 1 char)
- description: string (min 1 char)  
- version: string (semantic versioning: "1.0.0")

1. entities (array) - REQUIRED fields for each item:
   - name: string (min 1 char)
   - type: string (min 1 char)
   - attributes: array of strings (min 1 item, each min 1 char)
   - synonyms: array of strings (optional)
   Example: {{"name": "Student", "type": "STUDENT",  "attributes": ["id", "name", "email"], "synonyms": ["Learner"]}}

2. extraction_patterns (array) - REQUIRED fields for each item:
   - pattern: string (min 1 char)
   - entity_type: string (min 1 char)
   - attribute: string (min 1 char)
   - confidence: number (0.0 to 1.0)
   Example: {{"pattern": "student ID: (\\\\d+)", "entity_type": "Student", "attribute": "id", "confidence": 0.95}}

3. key_terms (array) - Simple strings:
   - Each item: string (min 1 char)
   Example: ["enrollment", "registration", "course"]

4. reasoning_templates (array) - REQUIRED fields for each item:
   - name: string (min 1 char)
   - steps: object with at least 1 property (keys and values are strings)
   - triggers: array of strings (min 1 item)
   - confidence_threshold: number (0.0 to 1.0)
   Example: {{"name": "Enrollment Check", "steps": {{"1": "Verify student", "2": "Check course"}}, "triggers": ["enroll"], "confidence_threshold": 0.8}}

5. relationship_types (array) - REQUIRED fields for each item:
   - type: string (min 1 char)
   - business_context: object with at least 1 property (values are booleans)
   Example: {{"type": "enrolls_in", "business_context": {{"academic": true, "financial": false}}}}

6. entity_aliases (object) - Key-value pairs:
   - Keys: entity names
   - Values: arrays of strings (aliases)
   Example: {{"Student": ["Learner", "Pupil"], "Course": ["Class", "Subject"]}}

7. business_context (object) - Key-value pairs:
   - Keys: context categories
   - Values: arrays of strings
   Example: {{"academic": ["grades", "credits"], "financial": ["tuition", "fees"]}}

8. relationships (array) - REQUIRED fields for each item:
   - name: string (min 1 char)
   - from: string (min 1 char) - source entity
   - to: string (min 1 char) - target entity
   - attributes: array of strings
   - synonyms: array of strings (optional)
   Example: {{"name": "enrolls_in", "from": "Student", "to": "Course", "attributes": ["enrollment_date", "status"], "synonyms": ["registers_for"]}}

9. business_patterns (array) - REQUIRED fields for each item:
   - name: string (min 1 char)
   - description: string (min 1 char)
   - stages: array of strings (min 1 item)
   - triggers: array of strings (optional)
   - entities_involved: array of strings (optional)
   - tags: array of strings (optional)
   - decision_points: array of strings (optional)
   Example: {{"name": "Course Registration", "description": "Student enrolls in course", "stages": ["select", "verify", "confirm"], "triggers": ["enroll_request"]}}

10. question_templates (object) - Categories with arrays:
    - Keys: category names (e.g., "Course", "Student")
    - Values: arrays of question objects
    - REQUIRED fields for each question object:
      * template: string (min 1 char)
      * priority: string - MUST be one of: "low", "medium", "high", "critical"
      * expected_answer_type: string (min 1 char)
      * entity_types: array of strings (optional)
      * attributes: array of strings (optional)
      * entity_pairs: array of arrays (optional)
      * process_types: array of strings (optional)
      * financial_types: array of strings (optional)
    Example: {{"Course": [{{"template": "What courses is {{student}} enrolled in?", "priority": "high", "expected_answer_type": "list"}}]}}

11. multihop_questions (array) - REQUIRED fields for each item:
    - template: string (min 1 char)
    - examples: array of strings (min 1 item)
    - priority: string - MUST be one of: "low", "medium", "high", "critical"
    - reasoning_type: string (min 1 char)
    Example: {{"template": "Which students are in courses taught by {{professor}}?", "examples": ["Which students are in courses taught by Dr. Smith?"], "priority": "medium", "reasoning_type": "multi-hop"}}

12. business_rules (array) - REQUIRED fields for each item:
    - name: string (min 1 char)
    - description: string (min 1 char)
    - rules: array of strings (min 1 item)
    Example: {{"name": "Enrollment Limit", "description": "Max students per course", "rules": ["max_students <= 30", "min_students >= 5"]}}

13. validation_rules (object) - Nested objects:
    - Keys: entity names
    - Values: objects with validation rules
      * Keys: field names
      * Values: arrays of strings (validation rules)
    Example: {{"Student": {{"email": ["required", "email_format"], "age": ["required", "min:18"]}}}}

CRITICAL VALIDATION RULES:
1. ALWAYS include ALL required fields when creating objects
2. priority field MUST be one of: "low", "medium", "high", "critical" (lowercase)
3. confidence values MUST be between 0.0 and 1.0
4. version MUST match pattern: "X.Y.Z" (e.g., "1.0.0")
5. Arrays marked as "min 1 item" MUST have at least one element
6. Strings marked as "min 1 char" MUST NOT be empty
7. When creating question_templates, ALWAYS include: template, priority, expected_answer_type
8. When creating multihop_questions, ALWAYS include: template, examples, priority, reasoning_type

COMMON PATTERNS:

Adding a new entity:
{{"op": "CREATE", "path": ["entities", "-"], "value": {{"name": "EntityName", "type": "core", "attributes": ["id"], "synonyms": []}}}}

Adding field to entity:
{{"op": "CREATE", "path": ["entities", "0", "attributes", "-"], "value": "fieldName"}}

Updating entity name:
{{"op": "UPDATE", "path": ["entities", "0", "name"], "value": "NewName"}}

Removing an entity:
{{"op": "DELETE", "path": ["entities", "0"]}}

CRITICAL RULES:
- Use CREATE with "-" to append to arrays
- Use CREATE with index to insert at specific position
- Use UPDATE only for existing paths
- Use DELETE to remove items
- Always provide complete object structure when creating new items
- Validate enum values like "priority": "high|medium|low|critical"
- Version must match semantic versioning (e.g., "1.0.0")

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
        schema_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured operation or suggestion from natural language.
        
        Args:
            user_message: Natural language message from user
            schema_definition: Current domain pack schema for context
            
        Returns:
            Dictionary matching ChatIntentResponse structure (without intent_id)
            
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
            
            # Extract basic fields
            resp_type = response_data.get("type", "suggestion")
            # fallback for old 'intent_summary' if LLM uses it
            message = response_data.get("message") or response_data.get("intent_summary", "")
            operations_data = response_data.get("operations", [])
            
            # Fallback for old single 'operation' format
            if not operations_data and "operation" in response_data:
                operations_data = [response_data["operation"]]
            
            # If it has operations, it's an operation
            if operations_data and resp_type == "suggestion":
                resp_type = "operation"
            
            result = {
                "type": resp_type,
                "message": message
            }
            
            if resp_type == "operation" and operations_data:
                # Normalize operations to match logic layer format
                normalized_ops = self._normalize_operations(operations_data, schema_definition)
                # Convert to list of OperationSpec to validate
                result["operations"] = [OperationSpec(**op) for op in normalized_ops]
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"LLM intent extraction failed: {str(e)}")
    
    def _normalize_operations(self, operations_data: List[Dict[str, Any]], schema_definition: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Normalize operations from LLM output to match logic layer format.
        Ensures all operations use correct action names and structure.
        Converts ADD_FIELD to UPDATE_FIELD/MERGE_OBJECT if field already exists.
        
        Args:
            operations_data: Raw operations from LLM
            schema_definition: Current schema to check for existing fields
            
        Returns:
            Normalized operations with correct structure
        """
        normalized = []
        schema_definition = schema_definition or {}
        
        for op in operations_data:
            if not isinstance(op, dict):
                continue
                
            action = op.get("action", "").upper()
            norm_op = {"action": action}
            
            # Copy path (required for all operations) - ensure all elements are strings
            if "path" in op:
                raw_path = op["path"] if isinstance(op["path"], list) else [op["path"]]
                # Convert all path elements to strings (LLM may return integers for array indices)
                norm_op["path"] = [str(p) for p in raw_path]
            
            # Validate operation against CRUD operations
            valid_ops = {"CREATE", "READ", "UPDATE", "DELETE"}
            
            # Check if LLM used "op" (new format) or "action" (old format)
            op_key = "op" if "op" in op else "action"
            operation = op.get(op_key, "").upper()
            
            if operation not in valid_ops:
                # Skip invalid operations or log warning
                continue
            
            # Normalize to CRUD format
            norm_op = {"op": operation}
            
            # Copy path (required for all operations except some edge cases)
            if "path" in op:
                raw_path = op["path"] if isinstance(op["path"], list) else [op["path"]]
                # Convert all path elements to strings
                norm_op["path"] = [str(p) for p in raw_path]
            
            # Copy value for CREATE and UPDATE
            if operation in ["CREATE", "UPDATE"] and "value" in op:
                norm_op["value"] = op["value"]
            
            normalized.append(norm_op)
        
        return normalized
    
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
