# Quick Start Guide - Domain Pack MCP Server

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.8+
- PostgreSQL 12+

### Step 1: Install Dependencies (1 min)

```bash
pip install fastmcp jsonschema ruamel.yaml deepdiff psycopg2-binary
```

### Step 2: Setup Database (1 min)

```bash
# Create database
createdb domain_pack_mcp

# Configure environment (optional - uses defaults if not set)
export DB_NAME=domain_pack_mcp
export DB_USER=postgres
export DB_PASSWORD=postgres
```

### Step 3: Run Tests (1 min)

```bash
python test_server.py
```

Expected output:
```
============================================================
Domain Pack MCP Server - Test Suite
============================================================

=== Testing Schema Validation ===
✓ Valid minimal domain pack accepted
✓ Invalid data rejected
✓ Invalid version format rejected

=== Testing Operations ===
✓ ADD operation works
✓ REPLACE operation works
✓ DELETE operation works
✓ ASSERT operation works
✓ BATCH operation works

=== Testing YAML Parsing ===
✓ YAML parsing works
✓ YAML serialization works

=== Testing Diff Calculation ===
✓ Diff calculation works

=== Testing Full Workflow ===
✓ Parsed sample.yaml
✓ Validated schema
✓ Applied operation
✓ Validated result
✓ Calculated diff
✓ Serialized result

============================================================
Test suite completed
============================================================
```

### Step 4: Start Server (30 sec)

```bash
python main.py
```

Expected output:
```
Initializing database...
Database initialized successfully
Starting Domain Pack MCP Server...
```

### Step 5: Use the Server (1 min)

```python
from tools import create_session_tool, apply_change_tool, export_domain_pack_tool

# Create session
result = create_session_tool("""
name: Legal
description: Legal domain
version: 1.0.0
entities:
  - name: Client
    type: CLIENT
    attributes: [name, email]
""", "yaml")

session_id = result["session_id"]

# Add entity
apply_change_tool(
    session_id,
    {
        "action": "add",
        "path": ["entities"],
        "value": {
            "name": "Attorney",
            "type": "ATTORNEY",
            "attributes": ["name", "bar_number"]
        }
    },
    "Added Attorney entity"
)

# Export
result = export_domain_pack_tool(session_id, "yaml")
print(result["content"])
```

## 📖 Common Operations

### Add to Array
```python
{
    "action": "add",
    "path": ["entities"],
    "value": {"name": "Document", "type": "DOCUMENT", "attributes": ["title"]}
}
```

### Update Field
```python
{
    "action": "replace",
    "path": ["version"],
    "value": "2.0.0"
}
```

### Merge Arrays
```python
{
    "action": "merge",
    "path": ["key_terms"],
    "value": ["contract", "litigation"]
}
```

### Batch Operations
```python
{
    "operations": [
        {"action": "replace", "path": ["version"], "value": "3.0.0"},
        {"action": "add", "path": ["key_terms"], "value": "arbitration"}
    ]
}
```

### Rollback
```python
rollback_tool(session_id, target_version=2)
```

## 🔧 Troubleshooting

### Database Connection Error
```
Error: Failed to connect to database
```
**Solution**: Check PostgreSQL is running and credentials are correct

### Schema Validation Error
```
Error: Validation failed at root: 'version' is a required property
```
**Solution**: Ensure all required fields (name, description, version) are present

### Operation Error
```
Error: Key 'entities' already exists at root and is not an array
```
**Solution**: Use correct operation type (add for arrays, replace for values)

## 📚 Next Steps

1. Read [README.md](README.md) for full documentation
2. Check [examples.py](examples.py) for more usage examples
3. Review [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for architecture details

## 🎯 Key Concepts

- **Sessions**: Each domain pack editing session has a unique ID
- **Versions**: Every change creates a new immutable version
- **Operations**: Structured transformations (no direct YAML editing)
- **Validation**: Schema checked before and after every operation
- **Rollback**: Creates new version with old content (never deletes)

## ✅ Success Checklist

- [ ] PostgreSQL installed and running
- [ ] Dependencies installed
- [ ] Database created
- [ ] Tests passing
- [ ] Server starts without errors
- [ ] Can create session
- [ ] Can apply operations
- [ ] Can export domain pack

---

**You're ready to go! 🎉**

For questions or issues, refer to the comprehensive [README.md](README.md).
