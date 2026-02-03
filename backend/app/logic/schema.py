"""
Domain Pack JSON Schema Definition and Validation

This module defines the complete JSON Schema for Domain Pack validation.
It enforces strict validation for all 14 top-level sections.
"""

import jsonschema
from jsonschema import Draft7Validator
from typing import Dict, Any, List

DOMAIN_PACK_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["name", "description", "version"],
    "additionalProperties": False,

    "properties": {
        # ─────────────────────────────
        # 1. Metadata
        # ─────────────────────────────
        "name": {
            "type": "string",
            "minLength": 1
        },
        "description": {
            "type": "string",
            "minLength": 1
        },
        "version": {
            "type": "string",
            "pattern": "^\\d+\\.\\d+\\.\\d+$"
        },

        # ─────────────────────────────
        # 2. Entities
        # ─────────────────────────────
        "entities": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["name", "type", "attributes"],
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "type": {"type": "string", "minLength": 1},
                    "attributes": {
                        "type": "array",
                        "minItems": 1,
                        "items": {"type": "string", "minLength": 1}
                    },
                    "synonyms": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1}
                    }
                }
            }
        },

        # ─────────────────────────────
        # 3. Extraction Patterns
        # ─────────────────────────────
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

        # ─────────────────────────────
        # 4. Key Terms
        # ─────────────────────────────
        "key_terms": {
            "type": "array",
            "items": {"type": "string", "minLength": 1}
        },

        # ─────────────────────────────
        # 5. Reasoning Templates
        # ─────────────────────────────
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
                        "minProperties": 1,
                        "additionalProperties": {"type": "string"}
                    },
                    "triggers": {
                        "type": "array",
                        "minItems": 1,
                        "items": {"type": "string"}
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                }
            }
        },

        # ─────────────────────────────
        # 6. Relationship Types
        # ─────────────────────────────
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
                        "minProperties": 1,
                        "additionalProperties": {"type": "boolean"}
                    }
                }
            }
        },

        # ─────────────────────────────
        # 7. Entity Aliases
        # ─────────────────────────────
        "entity_aliases": {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": {"type": "string", "minLength": 1}
            }
        },

        # ─────────────────────────────
        # 8. Business Context
        # ─────────────────────────────
        "business_context": {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": {"type": "string", "minLength": 1}
            }
        },

        # ─────────────────────────────
        # 9. Relationships
        # ─────────────────────────────
        "relationships": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "from", "to", "attributes"],
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "from": {"type": "string", "minLength": 1},
                    "to": {"type": "string", "minLength": 1},
                    "attributes": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1}
                    },
                    "synonyms": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1}
                    }
                }
            }
        },

        # ─────────────────────────────
        # 10. Business Patterns
        # ─────────────────────────────
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
                        "minItems": 1,
                        "items": {"type": "string"}
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

        # ─────────────────────────────
        # 11. Question Templates
        # ─────────────────────────────
        "question_templates": {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["template", "priority", "expected_answer_type"],
                    "additionalProperties": False,
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
                                "minItems": 2,
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

        # ─────────────────────────────
        # 12. Multihop Questions
        # ─────────────────────────────
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
                        "minItems": 1,
                        "items": {"type": "string"}
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"]
                    },
                    "reasoning_type": {"type": "string", "minLength": 1}
                }
            }
        },

        # ─────────────────────────────
        # 13. Business Rules
        # ─────────────────────────────
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
                        "minItems": 1,
                        "items": {"type": "string"}
                    }
                }
            }
        },

        # ─────────────────────────────
        # 14. Validation Rules
        # ─────────────────────────────
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
    Validates Domain Pack data against the strict JSON Schema.
    Structural validation only (no business logic, no mutation).
    """

    def __init__(self, schema: Dict[str, Any]):
        if not isinstance(schema, dict):
            raise ValueError("Schema must be a dictionary")

        # Pre-compile validator for performance & determinism
        self.schema = schema
        self.validator = Draft7Validator(schema)

    def validate(self, data: Dict[str, Any]) -> None:
        """
        Validate domain pack data against schema.

        Args:
            data: Domain pack data as dictionary

        Raises:
            ValueError: If input is invalid
            jsonschema.ValidationError: If schema validation fails
        """
        if data is None:
            raise ValueError("Domain pack data cannot be None")

        if not isinstance(data, dict):
            raise ValueError(
                f"Domain pack data must be a dictionary, got {type(data).__name__}"
            )

        errors = sorted(
            self.validator.iter_errors(data),
            key=lambda e: list(e.path)
        )

        if errors:
            error = errors[0]
            path = self._format_path(error.path)
            raise jsonschema.ValidationError(
                f"Validation failed at {path}: {error.message}"
            )

    def is_valid(self, data: Dict[str, Any]) -> bool:
        """
        Check validity without raising.

        Args:
            data: Domain pack data

        Returns:
            True if valid, False otherwise
        """
        try:
            self.validate(data)
            return True
        except (ValueError, jsonschema.ValidationError):
            return False

    def get_errors(self, data: Dict[str, Any]) -> List[str]:
        """
        Return all validation errors (non-throwing).

        Args:
            data: Domain pack data

        Returns:
            List of human-readable error messages
        """
        if data is None:
            return ["Domain pack data cannot be None"]

        if not isinstance(data, dict):
            return [
                f"Domain pack data must be a dictionary, got {type(data).__name__}"
            ]

        errors = []

        for error in sorted(
            self.validator.iter_errors(data),
            key=lambda e: list(e.path)
        ):
            path = self._format_path(error.path)
            errors.append(f"{path}: {error.message}")

        return errors

    @staticmethod
    def _format_path(path) -> str:
        """
        Format jsonschema error path consistently.
        """
        if not path:
            return "root"

        return " -> ".join(str(p) for p in path)


# ─────────────────────────────────────────────
# Global validator instance (canonical)
# ─────────────────────────────────────────────

validator = DomainPackValidator(DOMAIN_PACK_SCHEMA)


def validate_domain_pack(data: Dict[str, Any]) -> None:
    """
    Convenience wrapper for domain pack validation.
    """
    validator.validate(data)
