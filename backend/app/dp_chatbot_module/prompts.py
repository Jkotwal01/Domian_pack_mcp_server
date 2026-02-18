"""Prompt templates for LLM nodes in the chatbot workflow."""

INTENT_CLASSIFICATION_PROMPT = """You are analyzing a user request related to a domain configuration.

Current Domain Context:
{context}

User Request:
{user_message}

Classify the intent as ONE of these operations:
- update_domain_name, update_domain_description, update_domain_version
- add_entity, update_entity_name, update_entity_type, update_entity_description, delete_entity
- add_entity_attribute, update_entity_attribute_name, update_entity_attribute_description, delete_entity_attribute
- add_entity_attribute_example, update_entity_attribute_example, delete_entity_attribute_example
- add_entity_synonym, update_entity_synonym, delete_entity_synonym
- add_relationship, update_relationship_name, update_relationship_from, update_relationship_to, update_relationship_description, delete_relationship
- add_relationship_attribute, update_relationship_attribute_name, update_relationship_attribute_description, delete_relationship_attribute
- add_relationship_attribute_example, update_relationship_attribute_example, delete_relationship_attribute_example
- add_extraction_pattern, update_extraction_pattern_pattern, update_extraction_pattern_entity_type, update_extraction_pattern_attribute, update_extraction_pattern_extract_full_match, update_extraction_pattern_confidence, delete_extraction_pattern
- add_key_term, update_key_term, delete_key_term
- info_query (for specific questions ABOUT the current configuration: "what entities do I have?", "list my attributes", "show extraction patterns")
- general_query (for general knowledge about domain packs, how the system works, best practices for schema design, or suggestions for new domains/concepts)

CRITICAL RULES FOR NAMING CONFLICTS:
1. If the user asks to ADD an element (Entity, Relationship) that ALREADY EXISTS in the 'Current Domain Context' below, DO NOT use an 'add_' operation.
2. Instead, if they are providing new details, classify it as the corresponding 'update_' operation.
3. If they are just stating it exists or asking about it, classify it as 'info_query'.
4. This avoids 'duplicate name' errors during validation.

Examples:
- "list all entities" -> info_query
- "show me attributes for Case" -> info_query
- "what is a domain pack?" -> general_query
- "how should I structure extraction patterns?" -> general_query
- "suggest some medical entities for a new clinic domain" -> general_query

Respond with ONLY the operation name, nothing else."""


PATCH_GENERATION_PROMPT = """Generate PatchList (array of PatchOperations) for:
Intent: {intent}
Context: {context}
Request: {user_message}

RULES:
- REASONING: Provide 1-2 concise sentences explaining your plan.
- Entities/Relationships MUST have 'type' and 'description'.
- Attributes: {{"name": str, "description": str, "examples": []}}
- Extraction Patterns: valid Python REGEX.
- CONFLICTS: If ADDING something that EXISTS in Context, use 'update' instead.

PatchOperation Schema:
- type: e.g. 'add_entity', 'update_entity_name'
- target_name, parent_name, attribute_name, old_value, new_value, payload (as needed)

Example (Multiple actions):
{{
  "reasoning": "Plan to add a new 'dosage' key term and create the 'Dx' entity.",
  "patches": [
    {{ "type": "add_key_term", "new_value": "dosage" }},
    {{ "type": "add_entity", "payload": {{"name": "Dx", "type": "DX", "description": "...", "attributes": []}} }}
  ]
}}"""


ERROR_EXPLANATION_PROMPT = """The following error occurred while trying to apply a change to the domain configuration:

Error: {error_message}

User's original request: {user_message}

Explain the error to the user in a friendly, helpful way and suggest how they can fix it.
Keep it concise and actionable."""


INFO_QUERY_PROMPT = """You are a helpful domain configuration assistant.
The user is asking a question about the current domain configuration.

Current Domain Configuration:
{context}

User Question: {user_message}

Answer the user's question accurately based ONLY on the provided configuration.
- If they ask to list entities, list them clearly with their descriptions.
- If they ask for suggestions (entities, attributes, relationships), provide creative and relevant ideas based on the existing domain context.
- If they ask about relationships, explain how entities are connected.
- If they ask for general information, be helpful and concise.
- If you don't know the answer or it's not in the config, say so politely.

Your response should be friendly and formatted in markdown."""


GENERAL_KNOWLEDGE_PROMPT = """You are an expert in Domain Pack configuration and data modeling.
The user has a general question about domain packs, system functionality, or broad data modeling concepts.

Documentation Context:
{context}

User Question: {user_message}

Answer the user's question comprehensively.
- Explain core concepts like Entities, Relationships, Extraction Patterns, and Key Terms if relevant.
- provide best practices for domain pack design.
- If suggesting new concepts, be creative and align with the user's apparent goal.
- Maintain a helpful, assistant-like persona: "Domain Pack AI Assistant".

Your response should be professional, formatted in markdown, and very clear."""