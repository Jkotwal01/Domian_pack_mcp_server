"""Base domain configuration template."""
import json
import os
import asyncio
import logging
import traceback
import re
import ast
from typing import Dict, Any, List, Optional, Any
from dotenv import load_dotenv
from app.config import settings
from pydantic import BaseModel, Field
from typing import List, Optional, Any

# Set up logging
logger = logging.getLogger("uvicorn.error")
llm_call_count = 0

# Load environment variables
load_dotenv()
class Attribute(BaseModel):
    name: str = Field(..., description="Attribute name (e.g. 'title')")
    description: str = Field(..., description="Description")
    examples: List[str] = Field(default_factory=list, description="Examples")

class Entity(BaseModel):
    name: str = Field(..., description="PascalCase name")
    type: str = Field(..., description="UPPERCASE_SNAKE_CASE type")
    description: str = Field(..., description="Description")
    attributes: List[Attribute] = Field(default_factory=list)
    synonyms: List[str] = Field(default_factory=list)

class RelationshipAttribute(BaseModel):
    name: str = Field(..., description="Attribute name")
    description: str = Field(..., description="Description")
    examples: List[str] = Field(default_factory=list)

class Relationship(BaseModel):
    name: str = Field(..., description="UPPERCASE_SNAKE_CASE name")
    from_entity: str = Field(..., alias="from", description="Source entity")
    to: str = Field(..., description="Target entity")
    description: str = Field(..., description="Description")
    attributes: List[RelationshipAttribute] = Field(default_factory=list)

class ExtractionPattern(BaseModel):
    pattern: str = Field(..., description="Regex")
    entity_type: str = Field(..., description="Target entity name")
    attribute: str = Field(..., description="Attribute name")
    extract_full_match: bool = Field(default=True)
    confidence: float = Field(default=0.8)

class DomainConfig(BaseModel):
    """Structured domain configuration."""
    name: str = Field(..., description="Domain name")
    description: str = Field(..., description="Description")
    version: str = Field(default="1.0.0")
    entities: List[Entity] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    extraction_patterns: List[ExtractionPattern] = Field(default_factory=list)
    key_terms: List[str] = Field(default_factory=list)

async def generate_domain_template(
    domain_name: str, 
    description: str, 
    retriever: Any = None
) -> Dict[str, Any]:
    """
    Generate a domain template using the configured LLM with structured output.
    Falls back to a hardcoded base template on error.
    
    If a retriever is provided, it uses RAG to augment the context.
    """
    from app.utils.llm_factory import get_llm
    global llm_call_count
    llm_call_count += 1
    
    # Augment description with RAG if retriever is available
    rag_context = ""
    if retriever:
        try:
            # Query the retriever for entities, relationships and patterns
            docs = retriever.invoke(f"entities, relationships, and extraction patterns for {domain_name} in the context of {description}")
            rag_context = "\n".join([doc.page_content for doc in docs])
            logger.info(f"Retrieved {len(docs)} documents for RAG context")
        except Exception as rag_err:
            logger.error(f"RAG retrieval failed: {str(rag_err)}")
            rag_context = ""

    try:
        prompt_content = f"""
                        Domain Name: {domain_name}
                        User Description: {description}
                        """
        
        if rag_context:
            prompt_content += f"\n\nContext from associated PDF:\n{rag_context}"

        prompt_content += """
                        Requirements:
                        - Entity 'name' must be in PascalCase (e.g., 'MedicalRecord').
                        - Entity 'type' must be in UPPERCASE_SNAKE_CASE (e.g., 'MEDICAL_RECORD').
                        - Generate at least 2 entities and 1 relationship.
                        - Use realistic entity categories: DOCUMENT, PERSON, ORGANIZATION, EVENT, LOCATION, SYSTEM.
                        """

        # Get configured LLM
        llm = get_llm(temperature=0.1)
        is_groq = settings.LLM_PROVIDER.lower() == "groq"
        
        if is_groq:
            # For Groq, manual JSON mode is often more robust for complex schemas
            system_msg = (
                "You are a domain modeling assistant. Generate a structured domain configuration as a single JSON object. "
                "STRICT NAMING REQUIREMENTS: Entity 'name' = PascalCase, Entity 'type' = UPPERCASE_SNAKE_CASE. "
                "Output MUST be ONLY the valid JSON object matching the provided structure."
            )
            
            # Use the base template as a clear schema indicator in the prompt
            schema_json = json.dumps(get_base_template("DomainName", "Description"), indent=2)
            user_msg = f"{prompt_content}\n\nOutput MUST strictly follow this JSON structure:\n{schema_json}"
            
            messages = [("system", system_msg), ("user", user_msg)]
            logger.info(f"Generating template using {settings.LLM_PROVIDER} with manual JSON recovery mode")
            
            response = await llm.ainvoke(messages)
            content = response.content if hasattr(response, "content") else str(response)
            
            # Extract JSON from potential markdown blocks or text
            json_match = re.search(r'(\{.*\})', content, re.DOTALL)
            if json_match:
                try:
                    parsed_data = json.loads(json_match.group(1))
                    logger.info("✅ Successfully generated domain template using Groq (manual JSON mode)")
                    return parsed_data
                except Exception as parse_err:
                    logger.error(f"Failed to parse JSON from Groq response: {str(parse_err)}")
            
            logger.warning("Could not find or parse JSON in Groq response - falling back")
            return get_base_template(domain_name, description)

        else:
            # Use LangChain's structured output for OpenAI
            structured_llm = llm.with_structured_output(DomainConfig)
            messages = [
                (
                    "system", 
                    "You are a domain modeling assistant. Generate a structured domain configuration strictly following the schema. "
                    "STRICT NAMING REQUIREMENTS: Entity 'name' = PascalCase, Entity 'type' = UPPERCASE_SNAKE_CASE."
                ),
                ("user", prompt_content)
            ]
            
            logger.info(f"Generating template using {settings.LLM_PROVIDER} with structured output")
            parsed_data = await structured_llm.ainvoke(messages)
            
            if not parsed_data:
                return get_base_template(domain_name, description)
                
            logger.info(f"Successfully generated domain template using {settings.LLM_PROVIDER}")
            return parsed_data.model_dump(by_alias=True) if hasattr(parsed_data, "model_dump") else parsed_data

    except Exception as e:
        logger.error(f"AI Template Generation Error: {str(e)}")
        logger.info("Falling back to hardcoded base template due to error")
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


