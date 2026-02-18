"""Prompt templates for LLM nodes in the chatbot workflow."""

INTENT_CLASSIFICATION_PROMPT = """You are analyzing a user request to modify a domain configuration.

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

Respond with ONLY the operation name, nothing else."""


PATCH_GENERATION_PROMPT = """Generate a structured patch operation for the following request.

IMPORTANT: You MUST follow the strict domain template structure.
- Entities and Relationships MUST have a 'type' and 'description'.
- Attributes MUST be objects with 'name', 'description', and 'examples' (array).

Intent: {intent}
Relevant Context: {context}
User Request: {user_message}

Generate a PatchOperation with the appropriate fields based on the intent:
- type: the type of change (e.g., 'add_entity', 'add_relationship')
- target_name: name of the target element (for updates/deletes)
- parent_name: parent entity/relationship (for nested operations)
- attribute_name: attribute name (for attribute-level operations)
- old_value: current value (for array item updates)
- new_value: new value (for updates)
- payload: complete data object (for add operations)

Examples:
1. For "add entity Diagnosis":
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

2. For "add example 'admin@test.com' to email":
{{
  "type": "add_entity_attribute_example",
  "parent_name": "User",
  "attribute_name": "email",
  "new_value": "admin@test.com"
}}

3. For "add relationship OWNS from User to Product":
{{
  "type": "add_relationship",
  "payload": {{
    "name": "OWNS",
    "from": "User",
    "to": "Product",
    "description": "User owns a product",
    "attributes": []
  }}
}}

Generate the appropriate PatchOperation now."""


ERROR_EXPLANATION_PROMPT = """The following error occurred while trying to apply a change to the domain configuration:

Error: {error_message}

User's original request: {user_message}

Explain the error to the user in a friendly, helpful way and suggest how they can fix it.
Keep it concise and actionable."""