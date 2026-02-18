# Domain Pack System Knowledge Base

## Core Concepts
- **Entity**: A primary object in the domain (e.g., Case, Patient, Invoice).
- **Attribute**: A property of an entity (e.g., entity 'Case' has attribute 'case_number').
- **Relationship**: A connection between two entities (e.g., 'Case' is 'located_in' 'Court').
- **Extraction Pattern**: A regular expression used to identify and extract data from text into specific attributes.
- **Key Term**: A list of words or phrases that are highly relevant to the domain.

## Best Practices
- **Naming**: Use PascalCase for entities (e.g., `LegalMatter`) and snake_case for attributes (e.g., `filing_date`).
- **Descriptions**: Provide clear, concise descriptions for all elements to help the system understand the context.
- **Patterns**: Ensure regex patterns are robust and use capture groups where necessary.
- **Relationships**: Clearly define the source (from) and target (to) entities for all relationships.

## System Functionality
- The Domain Pack Generator allows users to create, update, and manage domain-specific data schemas.
- It uses LLMs to assist in generating these schemas from natural language requests.
- Validations ensure that the configuration remains consistent and error-free (e.g., no duplicate entities, valid references).
