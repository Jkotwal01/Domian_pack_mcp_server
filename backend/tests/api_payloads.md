# API Test Payloads

Use these payloads to test the endpoints via Swagger UI (`/docs`).

## 1. Create Session
**Endpoint**: `POST /sessions`

**Description**: Creates a new session with initial Domain Pack content.

**Payload**:
```json
{
  "file_type": "json",
  "metadata": {
    "user": "test_user",
    "project": "legal_automation"
  },
  "initial_content": {
    "name": "Legal",
    "description": "Legal and compliance domain",
    "version": "3.0.0",
    "entities": [
      {
        "name": "Client",
        "type": "CLIENT",
        "attributes": ["name", "email", "phone"],
        "synonyms": ["customer"]
      }
    ],
    "key_terms": ["litigation", "compliance"],
    "entity_aliases": {},
    "extraction_patterns": [],
    "business_context": {},
    "relationship_types": [],
    "relationships": [],
    "business_patterns": [],
    "reasoning_templates": [],
    "multihop_questions": [],
    "question_templates": {},
    "business_rules": [],
    "validation_rules": {}
  }
}
```

## 2. Apply Operations
**Endpoint**: `POST /sessions/{session_id}/operations`

**Description**: Applies deterministic operations to modify the domain pack.

**Payload**:
```json
{
  "operations": [
    {
      "action": "add",
      "path": ["entities"],
      "value": {
        "name": "Judge",
        "type": "JUDGE",
        "attributes": ["name", "court", "tenure"],
        "synonyms": ["magistrate"]
      }
    },
    {
      "action": "update",
      "path": ["entities", "0"],
      "updates": {
        "attributes": ["name", "email", "phone", "address"]
      }
    }
  ]
}
```

## 3. Validate YAML
**Endpoint**: `POST /validate/yaml`

**Description**: Validates raw YAML content.

**Payload** (Send as raw body, NOT JSON):
```yaml
name: Legal Domain
description: Validated via API
version: 1.0.0
entities:
  - name: Lawyer
    type: PERSON
    attributes:
      - bar_number
      - practice_area
key_terms:
  - court
  - law
entity_aliases: {}
extraction_patterns: []
business_context: {}
relationship_types: []
relationships: []
business_patterns: []
reasoning_templates: []
multihop_questions: []
question_templates: {}
business_rules: []
validation_rules: {}
```
