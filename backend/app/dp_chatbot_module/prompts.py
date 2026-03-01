"""Prompt templates for LLM nodes in the chatbot workflow."""

INTENT_CLASSIFICATION_PROMPT = """You are an intent classifier for a domain configuration assistant.

## Context
{context}

## User Request
{user_message}

## Intents
| Intent | Use when |
|--------|----------|
| domain_operation | Changing domain name, description, or version |
| entity_operation | Add/edit/delete an entity OR its attributes, synonyms, or examples |
| relationship_operation | Add/edit/delete a relationship OR its attributes |
| extraction_pattern_operation | Add/edit/delete extraction patterns |
| key_term_operation | Add/edit/delete key terms |
| info_query | READ-ONLY — list, show, does X exist, how many |
| general_query | Advice, suggestions, explanations unrelated to config changes |

## Examples
"List all entities" → info_query
"Does the STUDENT entity exist?" → info_query
"Add a new entity called COURSE" → entity_operation
"Add synonym 'pupil' to STUDENT" → entity_operation
"Add attribute 'grade' to STUDENT" → entity_operation
"Rename COURSE to MODULE" → entity_operation
"Delete the ENROLLED_IN relationship" → relationship_operation
"Change the domain description to 'Education'" → domain_operation
"Add extraction pattern for detecting dates" → extraction_pattern_operation
"Add 'machine learning' as a key term" → key_term_operation
"What entities should I add?" → general_query
"Explain what a domain pack is" → general_query

Respond with ONLY the exact category name — no punctuation, no explanation.
"""


PATCH_GENERATION_PROMPT = """Generate a PatchList to fulfill the user's request.
Intent: {intent}
Context: {context}
Request: {user_message}

RULES:
1. Entities and Relationships MUST have 'type' and 'description'.
2. Relationships MUST use entity 'type' for 'from' and 'to' fields (e.g., STUDENT, not Student).
3. If ADDING something that ALREADY EXISTS, use 'update' operations instead to avoid conflicts.
4. Extraction Patterns MUST be valid Python REGEX.
5. ARRAY ADDITIONS (synonyms, examples, key_terms): Set 'parent_name' to the entity/relationship name and put the string value directly in 'new_value'. Do NOT use 'payload' or 'target_name' for these.
6. ATTRIBUTE ADDITIONS (add_entity_attribute, add_relationship_attribute): ALWAYS use 'payload' with at minimum {{ "name": "<attr_name>", "description": "<desc>", "examples": [] }}. Do NOT use 'new_value' for these.
7. CRITICAL — parent_name vs target_name: Use 'parent_name' for nested operations (synonyms, attributes, examples). Only use 'target_name' for TOP-LEVEL operations (update_entity_name, update_entity_description, delete_entity, etc.).

SYNONYM EXAMPLE (correct):
  {{ "type": "add_entity_synonym", "parent_name": "Policy Renewal", "new_value": "Policy Extension" }}
  NOT: {{ "type": "add_entity_synonym", "target_name": "Policy Renewal", "new_value": "Policy Extension" }}
"""


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


GENERAL_KNOWLEDGE_PROMPT = """You are a concise expert in Domain Pack configuration and data modeling.
The user has a general question. Answer directly and briefly.

Documentation Context:
{context}

User Question: {user_message}

Rules:
- Start immediately with the answer. No "Based on...", "Sure!", or "As an AI...".
- Use short, impactful bullet points for lists or suggestions.
- Do NOT explain basic concepts unless explicitly asked.
- End immediately after the final piece of info. No "Conclusion" or "I hope this helps".
- Markdown only."""