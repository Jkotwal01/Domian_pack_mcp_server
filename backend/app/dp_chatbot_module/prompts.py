"""Prompts for LangGraph nodes."""

INTENT_DETECTION_PROMPT = """You are an AI assistant helping users configure a domain knowledge graph.

Current Domain: {domain_name}
Description: {domain_description}

Existing Entities: {entity_list}
Existing Relationships: {relationship_list}

User Message: {user_message}

Recent Conversation:
{chat_history}

Analyze the user's intent and classify it into ONE of the following categories:

1. **add_entity** - User wants to add a new entity type
2. **edit_entity** - User wants to modify an existing entity
3. **delete_entity** - User wants to remove an entity
4. **add_relationship** - User wants to add a new relationship between entities
5. **edit_relationship** - User wants to modify an existing relationship
6. **delete_relationship** - User wants to remove a relationship
7. **add_pattern** - User wants to add an extraction pattern
8. **edit_pattern** - User wants to modify an extraction pattern
9. **delete_pattern** - User wants to remove an extraction pattern
10. **add_term** - User wants to add a key term
11. **delete_term** - User wants to remove a key term
12. **general_query** - User is asking a question about the domain or needs clarification
13. **confirmation_yes** - User is confirming a proposed change
14. **confirmation_no** - User is rejecting a proposed change

Respond with ONLY the intent category name (e.g., "add_entity").
"""

PATCH_GENERATION_PROMPT = """You are generating a JSONPatch to modify a domain configuration.

Intent: {intent}
User Message: {user_message}

Current Domain Configuration:
{domain_config}

Based on the user's request, generate a JSONPatch operation to make the requested change.

For adding an entity, use:
[{{"op": "add", "path": "/entities/-", "value": {{"name": "...", "type": "...", "description": "...", "attributes": [], "synonyms": []}}}}]

For editing an entity, use:
[{{"op": "replace", "path": "/entities/0/description", "value": "new description"}}]

For adding a relationship, use:
[{{"op": "add", "path": "/relationships/-", "value": {{"name": "...", "from": "...", "to": "...", "description": "...", "attributes": []}}}}]

For adding a pattern, use:
[{{"op": "add", "path": "/extraction_patterns/-", "value": {{"pattern": "...", "entity_type": "...", "attribute": "...", "extract_full_match": true, "confidence": 0.9}}}}]

For adding a key term, use:
[{{"op": "add", "path": "/key_terms/-", "value": "term"}}]

Respond with ONLY the JSONPatch array in valid JSON format.
"""

CONFIRMATION_PROMPT = """You are explaining a proposed change to the user.

Intent: {intent}
Proposed Changes: {proposed_patch}

Generate a clear, concise message asking the user to confirm this change.
Be specific about what will be added, modified, or deleted.

Example: "I'll add a new entity called 'Contract' with attributes for title, date, and parties. Should I proceed?"

Your confirmation message:
"""

RESPONSE_GENERATION_PROMPT = """You are a helpful AI assistant for domain configuration.

Intent: {intent}
User Message: {user_message}

Context:
{context}

Generate a natural, helpful response to the user.

If changes were applied, confirm what was done.
If this is a query, provide a clear answer based on the domain configuration.
If there was an error, explain it clearly and suggest how to fix it.

Your response:
"""

GENERAL_QUERY_PROMPT = """You are answering a question about a domain configuration.

Domain: {domain_name}
Description: {domain_description}

Entities: {entity_list}
Relationships: {relationship_list}
Extraction Patterns: {pattern_count}
Key Terms: {term_count}

User Question: {user_message}

Provide a clear, helpful answer based on the current domain configuration.
If the user is asking how to do something, guide them step by step.

Your answer:
"""
