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
- info_query (for general questions, listing entities, suggestions for new entities/attributes, or clarifying the domain)

Examples:
- "suggest some entities" -> info_query
- "show me current entities" -> info_query
- "how are Case and Court related?" -> info_query
- "add a new entity Patient" -> add_entity
- "rename Case to LegalMatter" -> update_entity_name
- "remove key term tax" -> delete_key_term

Respond with ONLY the operation name, nothing else."""


PATCH_GENERATION_PROMPT = """Generate a sequence of structured patch operations for the following request.

IMPORTANT: You MUST return a PatchList containing an array of one or more patches.
- You MUST follow the strict domain template structure for each patch.
- Entities and Relationships MUST have a 'type' and 'description'.
- Attributes MUST be objects with 'name', 'description', and 'examples' (array).
- Extraction Patterns MUST use valid Python REGEX in the 'pattern' field.

Intent: {intent}
Relevant Context: {context}
User Request: {user_message}

Generate a PatchList with a list of PatchOperations. Each PatchOperation should have:
- type: the type of change (e.g., 'add_entity', 'add_extraction_pattern')
- target_name: name of the target element (for entity/relationship updates/deletes)
- parent_name: parent entity/relationship (for nested/attribute operations)
- attribute_name: attribute name (for attribute-level operations)
- old_value: the current value to be replaced or deleted (MANDATORY for delete_key_term, update_key_term, etc.)
- new_value: the new value (for updates or simple additions like add_key_term)
- payload: complete data object (MANDATORY for add_entity, add_relationship, add_extraction_pattern, etc.)

Examples:
1. For adding multiple key terms:
{{
  "patches": [
    {{ "type": "add_key_term", "new_value": "dosage" }},
    {{ "type": "add_key_term", "new_value": "allergy" }}
  ]
}}

2. For adding an Extraction Pattern:
{{
  "patches": [
    {{
      "type": "add_extraction_pattern",
      "payload": {{
        "pattern": "SPECIAL LEAVE PETITION NO\\\\.?\\\\s*(\\\\d+)\\\\s+OF\\\\s*(\\\\d{{4}})",
        "attribute": "case_number",
        "entity_type": "CASE",
        "confidence": 0.95,
        "extract_full_match": true,
        "full_match_template": "SPECIAL LEAVE PETITION NO. {{0}} OF {{1}}"
      }}
    }}
  ]
}}

3. For "add entity Diagnosis":
{{
  "patches": [
    {{
      "type": "add_entity",
      "payload": {{
        "name": "Diagnosis",
        "type": "DIAGNOSIS",
        "description": "Identification of a medical condition",
        "attributes": [
          {{
            "name": "code",
            "description": "ICD-10 clinical code",
            "examples": ["I10", "E11.9"]
          }}
        ],
        "synonyms": ["condition", "disease"]
      }}
    }}
  ]
}}

Generate the appropriate PatchList now."""


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