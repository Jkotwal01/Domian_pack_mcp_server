"""Base domain configuration template."""
from typing import Dict, Any


def get_base_template() -> Dict[str, Any]:
    """
    Returns the base template for a new domain configuration.
    This template includes universal entities, relationships, and patterns.
    """
    return {
        "name": "New Domain",
        "description": "A new domain configuration",
        "version": "1.0.0",
        "entities": [
            {
                "name": "Document",
                "type": "DOCUMENT",
                "description": "A document or file in the domain",
                "attributes": [
                    {
                        "name": "title",
                        "description": "The title or name of the document"
                    },
                    {
                        "name": "date",
                        "description": "The date associated with the document"
                    }
                ],
                "synonyms": ["File", "Record"]
            },
            {
                "name": "Person",
                "type": "PERSON",
                "description": "An individual person",
                "attributes": [
                    {
                        "name": "name",
                        "description": "Full name of the person"
                    },
                    {
                        "name": "role",
                        "description": "Role or position of the person"
                    }
                ],
                "synonyms": ["Individual", "User"]
            },
            {
                "name": "Organization",
                "type": "ORGANIZATION",
                "description": "A company, institution, or organization",
                "attributes": [
                    {
                        "name": "name",
                        "description": "Name of the organization"
                    },
                    {
                        "name": "type",
                        "description": "Type of organization"
                    }
                ],
                "synonyms": ["Company", "Institution"]
            }
        ],
        "relationships": [
            {
                "name": "CREATED_BY",
                "from": "DOCUMENT",
                "to": "PERSON",
                "description": "Indicates that a document was created by a person",
                "attributes": [
                    {
                        "name": "date",
                        "description": "When the document was created"
                    }
                ]
            },
            {
                "name": "WORKS_FOR",
                "from": "PERSON",
                "to": "ORGANIZATION",
                "description": "Indicates that a person works for an organization",
                "attributes": [
                    {
                        "name": "position",
                        "description": "Job title or position"
                    }
                ]
            }
        ],
        "extraction_patterns": [
            {
                "pattern": r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",
                "entity_type": "PERSON",
                "attribute": "name",
                "extract_full_match": True,
                "confidence": 0.8
            },
            {
                "pattern": r"\b\d{4}-\d{2}-\d{2}\b",
                "entity_type": "DOCUMENT",
                "attribute": "date",
                "extract_full_match": True,
                "confidence": 0.95
            }
        ],
        "key_terms": [
            "document",
            "person",
            "organization",
            "created",
            "works for"
        ]
    }


def create_custom_template(name: str, description: str, version: str = "1.0.0") -> Dict[str, Any]:
    """
    Create a custom domain template with specified metadata.
    
    Args:
        name: Domain name
        description: Domain description
        version: Version string
        
    Returns:
        Domain configuration dictionary
    """
    template = get_base_template()
    template["name"] = name
    template["description"] = description
    template["version"] = version
    return template
