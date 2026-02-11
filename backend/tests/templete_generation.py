"""Base domain configuration template."""
from dotenv import load_dotenv
from typing import Dict, Any
from openai import AsyncOpenAI
import json
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DOMAIN_SCHEMA = {
    "name": "domain_config",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "name",
            "description",
            "version",
            "entities",
            "relationships",
            "extraction_patterns",
            "key_terms"
        ],
        "properties": {
            "name": {"type": "string"},
            "description": {"type": "string"},
            "version": {"type": "string"},
            "entities": {
                "type": "array",
                "minItems": 2,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "name",
                        "type",
                        "description",
                        "attributes",
                        "synonyms"
                    ],
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "description": {"type": "string"},
                        "attributes": {
                            "type": "array",
                            "minItems": 1,
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "required": ["name", "description"],
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"}
                                }
                            }
                        },
                        "synonyms": {
                            "type": "array",
                            "minItems": 1,
                            "items": {"type": "string"}
                        }
                    }
                }
            },
            "relationships": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "name",
                        "from",
                        "to",
                        "description",
                        "attributes"
                    ],
                    "properties": {
                        "name": {"type": "string"},
                        "from": {"type": "string"},
                        "to": {"type": "string"},
                        "description": {"type": "string"},
                        "attributes": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "required": ["name", "description"],
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            "extraction_patterns": {
                "type": "array",
                "minItems": 2,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "pattern",
                        "entity_type",
                        "attribute",
                        "extract_full_match",
                        "confidence"
                    ],
                    "properties": {
                        "pattern": {"type": "string"},
                        "entity_type": {"type": "string"},
                        "attribute": {"type": "string"},
                        "extract_full_match": {"type": "boolean"},
                        "confidence": {"type": "number"}
                    }
                }
            },
            "key_terms": {
                "type": "array",
                "minItems": 3,
                "items": {"type": "string"}
            }
        }
    },
    "strict": True
}

async def generate_domain_template(domain_name: str, description: str) -> dict:
    response = await client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.2,
        response_format={
            "type": "json_schema",
            "json_schema": DOMAIN_SCHEMA
        },
        messages=[
            {
                "role": "system",
                "content": "You are a domain modeling assistant. "
                           "Generate a structured domain configuration."
            },
            {
                "role": "user",
                "content": f"""
                Domain Name: {domain_name}
                Description: {description}

                Requirements:
                - At least 2–3 entities
                - At least 1 relationship between those entities
                - At least 2 regex-based extraction patterns
                - At least 3 key terms
                - Use realistic entity types (DOCUMENT, PERSON, ORGANIZATION, EVENT, LOCATION, SYSTEM)
                """
            }
        ]
    )

    return response.choices[0].message.parsed


if __name__ == "__main__":
    ans = asyncio.run(
        generate_domain_template("Legal", "legal and compliance")
    )
    print(json.dumps(ans, indent=2))
