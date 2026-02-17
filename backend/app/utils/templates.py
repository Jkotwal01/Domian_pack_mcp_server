"""Base domain configuration template."""
from typing import Dict, Any
from openai import AsyncOpenAI
import json
import os
import asyncio
import logging
import traceback
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger("uvicorn.error")
llm_call_count = 0

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# JSON Schema strictly following your template
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
                    "required": ["name", "type", "description", "attributes", "synonyms"],
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
                                "required": ["name", "description", "examples"],
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "examples": {
                                        "type": "array",
                                        "minItems": 1,
                                        "items": {"type": "string"}
                                    }
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
                    "required": ["name", "from", "to", "description", "attributes"],
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
                                "required": ["name", "description", "examples"],
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "examples": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
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

async def generate_domain_template(domain_name: str, description: str) -> Dict[str, Any]:
    """
    Generate a domain template using OpenAI with strict schema enforcement.
    Falls back to a hardcoded base template on error.
    """
    global llm_call_count
    llm_call_count += 1
    
    try:
        # Use beta.chat.completions.parse for structured output
        response = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            temperature=0.2,
            response_format={
                "type": "json_schema",
                "json_schema": DOMAIN_SCHEMA    
            },
            messages=[
                {
                    "role": "system",
                    "content": "You are a domain modeling assistant. "
                               "Generate a structured domain configuration strictly following the schema."
                },
                {
                    "role": "user",
                    "content": f"""
                        Domain Name: {domain_name}
                        Description: {description}

                        Requirements:
                        - At least 2–3 entities
                        - At least 1 relationship between entities
                        - At least 2 regex-based extraction patterns
                        - At least 3 key terms
                        - For each entity/relationship attribute, provide 2-3 realistic 'examples' as a list of strings
                        - Use realistic entity types (DOCUMENT, PERSON, ORGANIZATION, EVENT, LOCATION, SYSTEM)
                        - For entity 'name' use capitalized words (e.g., 'Numeric Value')
                        - For entity 'type' use uppercase with underscores (e.g., 'NUMERIC_VALUE')
                        """
                }
            ]
        )
        # for Tokens Analysis
        logger.info(f"Token Usage: Input={response.usage.prompt_tokens}, "
            f"Output={response.usage.completion_tokens}, "
            f"Total={response.usage.total_tokens}")
        # Access the structured output via .parsed
        logger.info(f"OpenAI API - \"POST /v1/chat/completions HTTP/1.1\" 200 OK (Call count: {llm_call_count})")
        
        if response.choices[0].message.refusal:
            logger.warning(f"Model refused to generate: {response.choices[0].message.refusal}")
            return get_base_template(domain_name, description)
            
        parsed_data = response.choices[0].message.parsed
        if parsed_data is None:
            raw_content = response.choices[0].message.content
            logger.warning("Model returned successful response but parsed data is None (validation failed)")
            logger.warning(f"Raw content: {raw_content}")
            
            # Fallback to manual parsing if possible
            if raw_content:
                try:
                    # Clean the content if it contains markdown markers
                    cleaned_content = raw_content
                    if "```json" in cleaned_content:
                        cleaned_content = cleaned_content.split("```json")[1].split("```")[0].strip()
                    elif "```" in cleaned_content:
                        cleaned_content = cleaned_content.split("```")[1].split("```")[0].strip()
                    
                    parsed_data = json.loads(cleaned_content)
                    logger.info("Successfully recovered data via manual JSON parsing")
                    return parsed_data
                except Exception as parse_err:
                    logger.error(f"Manual parsing also failed: {str(parse_err)}")
            
            return get_base_template(domain_name, description)
            
        return parsed_data
    except Exception as e:
        logger.error(f"AI Template Generation Error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.info(f"OpenAI API - \"POST /v1/chat/completions HTTP/1.1\" 500 Internal Server Error (Fallback to base template)")
        return get_base_template(domain_name, description)

def get_base_template(name: str = "New Domain", description: str = "") -> Dict[str, Any]:
    """
    Returns the base template for a new domain configuration.
    This template includes universal entities, relationships, and patterns.
    """
    return {
        "name": name,
        "description": description or "A new domain configuration",
        "version": "1.0.0",
        "entities": [
            {
                "name": "Document",
                "type": "DOCUMENT",
                "description": "A document or file in the domain",
                        "attributes": [
                    {
                        "name": "title",
                        "description": "The title or name of the document",
                        "examples": ["2023 Annual Report", "Technical Specification V1"]
                    },
                    {
                        "name": "date",
                        "description": "The date associated with the document",
                        "examples": ["2023-10-25", "January 15, 2024"]
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
                        "description": "Full name of the person",
                        "examples": ["John Smith", "Alice Johnson"]
                    },
                    {
                        "name": "role",
                        "description": "Role or position of the person",
                        "examples": ["Manager", "Lead Engineer"]
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
                        "description": "Name of the organization",
                        "examples": ["Acme Corp", "HealthLink Systems"]
                    },
                    {
                        "name": "type",
                        "description": "Type of organization",
                        "examples": ["Private Company", "Non-profit Organization"]
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
                        "description": "When the document was created",
                        "examples": ["2023-11-01", "Yesterday"]
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
                        "description": "Job title or position",
                        "examples": ["Software Engineer", "Project Coordinator"]
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


