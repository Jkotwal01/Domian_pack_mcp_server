# Domain Pack MCP Server

A production-ready MCP (Model Context Protocol) server for managing Domain Packs with strict schema validation, versioning, and deterministic operations.

## 🎯 Overview

This MCP server enables LLMs to safely modify Domain Pack YAML/JSON files through structured, deterministic operations. It prevents hallucinated YAML by converting natural language requests into validated operations.

### Key Features

- ✅ **Strict Schema Validation** - Enforces 14-section Domain Pack schema
- ✅ **Deterministic Operations** - Path-based transformations, no LLM YAML editing
- ✅ **Immutable Versioning** - PostgreSQL-backed version history with diffs
- ✅ **Atomic Rollback** - Rollback creates new versions, never deletes history
- ✅ **Format Preservation** - YAML formatting preserved using ruamel.yaml
- ✅ **Safety Guarantees** - Validation before and after every operation

## 📁 Architecture

```
domain-pack-mcp/
├── main.py          # FastMCP server entry point
├── db.py            # PostgreSQL connection & version storage
├── schema.py        # JSON Schema validation for Domain Packs
├── operations.py    # Pure, deterministic operations (add, replace, delete, etc.)
├── tools.py         # MCP tool orchestration layer
├── utils.py         # YAML/JSON parsing, serialization, diff calculation
└── README.md        # This file
```

## 🔄 System Flow

```
User (Natural Language) + Upload Base YAML/JSON
   ↓
LLM (Intent → Structured Operation)
   ↓
MCP Tool (tools.py)
   ↓
Parse → Validate → Apply → Validate → Diff
   ↓
PostgreSQL (New Immutable Version)
```

**Rollback** creates a new version, never deletes history.

## 🛠️ Supported Operations

All operations are **path-based** and **deterministic**:

| Operation | Description | Example |
|-----------|-------------|---------|
| `add` | Add value to path | Add new entity to `entities` array |
| `replace` | Replace value at path | Update `version` field |
| `delete` | Delete value at path | Remove entity from `entities` |
| `update` | Update object fields | Update multiple entity attributes |
| `merge` | Merge objects/arrays | Merge new key_terms into existing |
| `add_unique` | Add if not exists | Add unique synonym |
| `batch` | Atomic multi-op | Execute multiple operations together |
| `assert` | Validate condition | Assert version equals "3.0.0" |

## 📋 Domain Pack Schema

The server validates all 14 top-level sections:

1. **Metadata**: `name`, `description`, `version`
2. **entities**: Entity definitions with attributes and synonyms
3. **key_terms**: Domain-specific terminology
4. **entity_aliases**: Alternative names for entities
5. **extraction_patterns**: Regex patterns for entity extraction
6. **business_context**: Business rules and contexts
7. **relationship_types**: Types of relationships between entities
8. **relationships**: Actual relationship definitions
9. **business_patterns**: Business process patterns
10. **reasoning_templates**: Templates for reasoning workflows
11. **multihop_questions**: Complex multi-step questions
12. **question_templates**: Question generation templates
13. **business_rules**: Business validation rules
14. **validation_rules**: Field validation requirements

## 🚀 Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+

### Setup

1. **Install dependencies**:
```bash
pip install fastmcp jsonschema ruamel.yaml deepdiff psycopg2-binary
```

2. **Configure PostgreSQL**:

Set environment variables (or use defaults):
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=domain_pack_mcp
export DB_USER=postgres
export DB_PASSWORD=postgres
```

3. **Create database**:
```bash
createdb domain_pack_mcp
```

4. **Run server**:
```bash
python main.py
```

The server will automatically initialize database tables on first run.

## 📖 Usage Examples

### 1. Create Session

```python
create_session(
    initial_content="""
name: Legal
description: Legal and compliance domain
version: 3.0.0
entities:
  - name: Client
    type: CLIENT
    attributes: [name, contact_info]
""",
    file_type="yaml"
)
# Returns: {"success": true, "session_id": "uuid", "version": 1}
```

### 2. Add Entity

```python
apply_change(
    session_id="uuid-here",
    operation={
        "action": "add",
        "path": ["entities"],
        "value": {
            "name": "Attorney",
            "type": "ATTORNEY",
            "attributes": ["name", "bar_number"],
            "synonyms": ["lawyer", "counsel"]
        }
    },
    reason="Added Attorney entity for legal representation"
)
# Returns: {"success": true, "version": 2, "diff": {...}}
```

### 3. Update Version

```python
apply_change(
    session_id="uuid-here",
    operation={
        "action": "replace",
        "path": ["version"],
        "value": "3.1.0"
    },
    reason="Incremented version for new features"
)
```

### 4. Batch Operations

```python
apply_batch(
    session_id="uuid-here",
    operations=[
        {"action": "replace", "path": ["version"], "value": "4.0.0"},
        {"action": "add", "path": ["key_terms"], "value": "arbitration"},
        {"action": "add", "path": ["key_terms"], "value": "mediation"}
    ],
    reason="Major version update with new key terms"
)
```

### 5. Rollback

```python
rollback(
    session_id="uuid-here",
    target_version=3
)
# Returns: {"success": true, "version": 5, "rolled_back_to": 3}
# Note: Creates version 5 with content from version 3
```

### 6. Export

```python
export_domain_pack(
    session_id="uuid-here",
    file_type="yaml"
)
# Returns: {"success": true, "content": "name: Legal\n..."}
```

## 🔒 Safety Guarantees

### Validation Flow

Every change follows this strict flow:

1. **Parse** - Convert YAML/JSON to dict
2. **Validate Schema** - Check current version is valid
3. **Apply Operation** - Execute deterministic transformation
4. **Validate Result** - Ensure result matches schema
5. **Calculate Diff** - Compute changes from previous version
6. **Store Version** - Save to PostgreSQL

**If ANY step fails, the entire operation is aborted.**

### Operation Safety

- **Pure Functions**: Operations have no side effects
- **No DB Access**: Operations never touch the database
- **No Schema Validation**: Operations don't validate (tools.py does)
- **Deterministic**: Same input always produces same output
- **Atomic Batches**: All operations succeed or all fail

### LLM Interaction Guidelines

**DO:**
- Convert user intent to structured operations
- Use `assert` to validate assumptions
- Use `batch` for related changes
- Provide clear `reason` messages

**DON'T:**
- Generate YAML/JSON directly
- Skip validation
- Assume schema structure
- Make partial updates

## 🗄️ Database Schema

### Sessions Table
```sql
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    current_version INTEGER NOT NULL DEFAULT 1,
    file_type VARCHAR(10) NOT NULL,
    metadata JSONB
);
```

### Versions Table
```sql
CREATE TABLE versions (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(session_id),
    version INTEGER NOT NULL,
    content JSONB NOT NULL,
    diff JSONB,
    reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(session_id, version)
);
```

## 🧪 Testing

Test the server with sample operations:

```python
# Load sample domain pack
with open('sample.yaml', 'r') as f:
    content = f.read()

# Create session
result = create_session(content, "yaml")
session_id = result["session_id"]

# Test operations
apply_change(session_id, {
    "action": "add",
    "path": ["key_terms"],
    "value": "contract"
}, "Added contract term")

# Verify
info = get_session_info(session_id)
print(f"Current version: {info['current_version']}")
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | localhost | PostgreSQL host |
| `DB_PORT` | 5432 | PostgreSQL port |
| `DB_NAME` | domain_pack_mcp | Database name |
| `DB_USER` | postgres | Database user |
| `DB_PASSWORD` | postgres | Database password |

## 📊 Operation DSL Reference

### Add Operation
```json
{
  "action": "add",
  "path": ["entities"],
  "value": {"name": "Document", "type": "DOCUMENT", "attributes": ["title"]}
}
```

### Replace Operation
```json
{
  "action": "replace",
  "path": ["version"],
  "value": "3.2.0"
}
```

### Delete Operation
```json
{
  "action": "delete",
  "path": ["entities", "0"]
}
```

### Update Operation
```json
{
  "action": "update",
  "path": ["entities", "0"],
  "updates": {"name": "UpdatedName"}
}
```

### Merge Operation
```json
{
  "action": "merge",
  "path": ["key_terms"],
  "value": ["new_term1", "new_term2"]
}
```

### Assert Operation
```json
{
  "action": "assert",
  "path": ["version"],
  "equals": "3.0.0"
}
```

## 🚫 What NOT to Do

❌ **Don't add extra operations** - Only use the 8 defined operations  
❌ **Don't add authentication** - Out of scope for this version  
❌ **Don't add UI** - This is a backend MCP server  
❌ **Don't use async** - Unless required by FastMCP  
❌ **Don't invent schema fields** - Follow the 14-section structure  
❌ **Don't over-engineer** - Keep it minimal and extensible  

## 🎯 Success Criteria

This MCP server is successful if it:

1. ✅ Prevents LLMs from hallucinating YAML
2. ✅ Enforces strict schema validation
3. ✅ Provides complete version history
4. ✅ Supports safe rollback
5. ✅ Maintains deterministic behavior
6. ✅ Serves as foundation for future scaling

## 📝 License

This is foundational infrastructure designed for production use.

## 🤝 Contributing

This is a minimal, complete implementation. Extensions should:
- Maintain deterministic behavior
- Preserve safety guarantees
- Follow the existing architecture
- Add comprehensive tests

---

**Built with FastMCP for safe LLM interaction with Domain Packs**
