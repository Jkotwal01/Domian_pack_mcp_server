"""
Domain Pack JSON Schema Definition and Validation

This module defines the complete JSON Schema for Domain Pack validation.
It enforces strict validation for all 14 top-level sections:
1. name, description, version (metadata)
2. entities
3. key_terms
4. entity_aliases
5. extraction_patterns
6. business_context
7. relationship_types
8. relationships
9. business_patterns
10. reasoning_templates
11. multihop_questions
12. question_templates
13. business_rules
14. validation_rules
"""

import jsonschema
from typing import Dict, Any


# Complete JSON Schema for Domain Pack
DOMAIN_PACK_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["name", "description", "version"],
    "additionalProperties": False,
    "properties": {
        # Section 1-3: Metadata
        "name": {
            "type": "string",
            "minLength": 1,
            "description": "Domain pack name"
        },
        "description": {
            "type": "string",
            "minLength": 1,
            "description": "Domain pack description"
        },
        "version": {
            "type": "string",
            "pattern": r"^\d+\.\d+\.\d+$",
            "description": "Semantic version (e.g., 3.0.0)"
        },
        
        # Section 2: Entities
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "type", "attributes"],
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "type": {"type": "string", "minLength": 1},
                    "attributes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1
                    },
                    "synonyms": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        },
        
        # Section 3: Key Terms
        "key_terms": {
            "type": "array",
            "items": {"type": "string", "minLength": 1}
        },
        
        # Section 4: Entity Aliases
        "entity_aliases": {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        
        # Section 5: Extraction Patterns
        "extraction_patterns": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["pattern", "entity_type", "attribute", "confidence"],
                "additionalProperties": False,
                "properties": {
                    "pattern": {"type": "string", "minLength": 1},
                    "entity_type": {"type": "string", "minLength": 1},
                    "attribute": {"type": "string", "minLength": 1},
                    "confidence": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                }
            }
        },
        
        # Section 6: Business Context
        "business_context": {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        
        # Section 7: Relationship Types
        "relationship_types": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type", "business_context"],
                "additionalProperties": False,
                "properties": {
                    "type": {"type": "string", "minLength": 1},
                    "business_context": {
                        "type": "object",
                        "additionalProperties": {"type": "boolean"}
                    }
                }
            }
        },
        
        # Section 8: Relationships
        "relationships": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "from", "to", "attributes","synonyms"],
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "from": {"type": "string", "minLength": 1},
                    "to": {"type": "string", "minLength": 1},
                    "attributes": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "synonyms": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        },
        
        # Section 9: Business Patterns
        "business_patterns": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "description", "stages"],
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "description": {"type": "string", "minLength": 1},
                    "stages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1
                    },
                    "triggers": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "entities_involved": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "decision_points": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        },
        
        # Section 10: Reasoning Templates
        "reasoning_templates": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "steps", "triggers", "confidence_threshold"],
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "steps": {
                        "type": "object",
                        "additionalProperties": {"type": "string"}
                    },
                    "triggers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                }
            }
        },
        
        # Section 11: Multihop Questions
        "multihop_questions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["template", "examples", "priority", "reasoning_type"],
                "additionalProperties": False,
                "properties": {
                    "template": {"type": "string", "minLength": 1},
                    "examples": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"]
                    },
                    "reasoning_type": {"type": "string", "minLength": 1}
                }
            }
        },
        
        # Section 12: Question Templates
        "question_templates": {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["template", "priority", "expected_answer_type"],
                    "properties": {
                        "template": {"type": "string", "minLength": 1},
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "critical"]
                        },
                        "expected_answer_type": {"type": "string", "minLength": 1},
                        "entity_types": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "attributes": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "entity_pairs": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {"type": "string"} 
                            }
                        },
                        "process_types": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "financial_types": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            }
        },
        
        # Section 13: Business Rules
        "business_rules": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "description", "rules"],
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "description": {"type": "string", "minLength": 1},
                    "rules": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1
                    }
                }
            }
        },
        
        # Section 14: Validation Rules
        "validation_rules": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "additionalProperties": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
    }
}


class DomainPackValidator:
    """
    Validates Domain Pack data against the strict JSON schema.
    Ensures all structural and business rules are enforced.
    """
    
    def __init__(self):
        self.validator = jsonschema.Draft7Validator(DOMAIN_PACK_SCHEMA)
    
    def validate(self, data: Dict[str, Any]) -> None:
        """
        Validate domain pack data against schema.
        Args:
            data: Domain pack data as dictionary
        Raises:
            jsonschema.ValidationError: If validation fails
            ValueError: If data is None or not a dict
        """
        if data is None:
            raise ValueError("Domain pack data cannot be None")
        
        if not isinstance(data, dict):
            raise ValueError(f"Domain pack data must be a dictionary, got {type(data).__name__}")
        
        # Validate against JSON schema
        try:
            self.validator.validate(data)
        except jsonschema.ValidationError as e:
            # Enhance error message with path information
            path = " -> ".join(str(p) for p in e.path) if e.path else "root"
            raise jsonschema.ValidationError(
                f"Validation failed at {path}: {e.message}"
            )
    
    def is_valid(self, data: Dict[str, Any]) -> bool:
        """
        Check if domain pack data is valid without raising exception.
        Args:
            data: Domain pack data as dictionary
        Returns:
            True if valid, False otherwise
        """
        try:
            self.validate(data)
            return True
        except (jsonschema.ValidationError, ValueError):
            return False
    
    def get_errors(self, data: Dict[str, Any]) -> list:
        """
        Get all validation errors for the data.
        Args:
            data: Domain pack data as dictionary
        Returns:
            List of error messages
        """
        errors = []
        
        if data is None:
            return ["Domain pack data cannot be None"]
        
        if not isinstance(data, dict):
            return [f"Domain pack data must be a dictionary, got {type(data).__name__}"]
        
        for error in self.validator.iter_errors(data):
            path = " -> ".join(str(p) for p in error.path) if error.path else "root"
            errors.append(f"{path}: {error.message}")
        
        return errors


# Global validator instance
validator = DomainPackValidator()


def validate_domain_pack(data: Dict[str, Any]) -> None:
    """
    Convenience function to validate domain pack data.
    
    Args:
        data: Domain pack data as dictionary
    Raises:
        jsonschema.ValidationError: If validation fails
        ValueError: If data is invalid
    """
    validator.validate(data)
