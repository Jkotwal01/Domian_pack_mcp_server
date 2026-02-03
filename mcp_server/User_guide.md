# Pure Deterministic MCP Server - README

## Overview

This is a **pure, deterministic document transformation engine** following the compiler model. It transforms YAML/JSON domain pack documents through structured operations with strict validation and all-or-nothing execution guarantees.

### Key Principles

✅ **Pure Function**: `(document, operations) → (updated_document, diff, errors)`  
✅ **No State**: No sessions, no version history, no database  
✅ **Deterministic**: Same input always produces identical output  
✅ **Atomic**: All-or-nothing execution  
✅ **Safe**: Multiple validation layers prevent invalid transformations  

---

## Architecture

```
Input: Document + Schema + Operations
  ↓
[1] Parse & Validate Input
  ↓
[2] Deep Copy Document
  ↓
[3] Schema Validation (Pre)
  ↓
[4] Safety Checks
  ↓
[5] Apply Operations
  ↓
[6] Schema Validation (Post)
  ↓
[7] Generate Diff
  ↓
[8] Serialize Output
  ↓
Output: Document + Diff + Errors
```

### Core Modules

| Module | Purpose | Lines |
|--------|---------|-------|
| `path_resolver.py` | Path parsing and resolution | ~350 |
| `safety_checks.py` | Pre-mutation safety validation | ~400 |
| `executor.py` | Atomic transformation pipeline | ~450 |
| `schema.py` | JSON Schema validation (enhanced) | ~500 |
| `operations.py` | Pure operation executors | ~570 |
| `utils.py` | Parsing, serialization, diff | ~400 |
| `main.py` | MCP interface layer | ~400 |

**Total: ~3,070 lines of pure transformation logic**

---

## Installation

```bash
# Install dependencies
pip install fastmcp jsonschema ruamel.yaml deepdiff pytest

# No database setup needed!
```

---

## Quick Start

### 1. Start the Server

```bash
python main.py
```

### 2. Use the MCP Tools

#### Transform Document

```python
transform_document(
    document='''
name: Legal
description: Legal domain
version: 1.0.0
entities: []
    ''',
    format="yaml",
    operations=[
        {
            "action": "add",
            "path": ["entities"],
            "value": {
                "name": "Attorney",
                "type": "ATTORNEY",
                "attributes": ["name", "bar_number"]
            }
        }
    ]
)
```

**Returns:**
```json
{
    "success": true,
    "document": { ... },
    "serialized": "...",
    "diff": { ... },
    "errors": [],
    "warnings": [],
    "affected_paths": ["entities"],
    "execution_metadata": {
        "operations_applied": 1,
        "duration_ms": 12.5,
        "validation_passed": true
    }
}
```

#### Validate Document

```python
validate_document(
    document='name: Legal\nversion: 1.0.0',
    format="yaml"
)
```

#### Preview Operations (Dry-Run)

```python
preview_operations(
    document='...',
    format="yaml",
    operations=[...]
)
```

---

## Supported Operations

| Operation | Description | Example |
|-----------|-------------|---------|
| `add` | Add value to path | `{"action": "add", "path": ["entities"], "value": {...}}` |
| `replace` | Replace value | `{"action": "replace", "path": ["version"], "value": "2.0.0"}` |
| `delete` | Delete value | `{"action": "delete", "path": ["key_terms"]}` |
| `update` | Update multiple fields | `{"action": "update", "path": [], "updates": {...}}` |
| `merge` | Merge objects/arrays | `{"action": "merge", "path": ["entities"], "value": [...]}` |
| `add_unique` | Add if not exists | `{"action": "add_unique", "path": ["key_terms"], "value": "legal"}` |
| `assert` | Validate condition | `{"action": "assert", "path": ["version"], "equals": "1.0.0"}` |

---

## Path Syntax

Supports flexible path notation:

- **Dot notation**: `entities.Attorney.name`
- **Array indexing**: `entities[0].name`
- **Mixed**: `entities[0].attributes[1]`

---

## Safety Guarantees

### Pre-Mutation Checks

✅ **Required field deletion** → Blocked  
✅ **Type mismatches** → Blocked  
✅ **Circular references** → Blocked  
✅ **Array out of bounds** → Blocked  
⚠️ **Bulk changes (>10 ops)** → Warning  
⚠️ **Key overwrites** → Warning  
⚠️ **Protected paths** → Warning  

### Execution Modes

**Strict Mode** (default): Warnings are blocking  
**Permissive Mode**: Warnings allowed, only errors block  

---

## Error Model

### Blocking Errors

```json
{
    "code": "SCHEMA_VALIDATION_FAILED_POST",
    "message": "Document invalid after transformation: ...",
    "phase": "post_validation",
    "path": "entities[0].name",
    "context": { ... }
}
```

### Non-Blocking Warnings

```json
{
    "code": "BULK_CHANGE_WARNING",
    "message": "Large number of operations (15) exceeds threshold (10)",
    "context": {
        "operation_count": 15,
        "threshold": 10
    }
}
```

---

## Execution Options

```python
{
    "strict_mode": True,           # Fail on warnings
    "auto_create_paths": False,    # Auto-create missing paths
    "preserve_formatting": True,   # Preserve YAML formatting
    "max_operations": 100,         # Maximum operations per batch
    "bulk_threshold": 10,          # Warning threshold
    "forbidden_paths": ["name"]    # Protected paths
}
```

---

## Testing

### Run All Tests

```bash
python -m pytest test_pure.py -v
```

**Results**: ✅ 37 tests passing

### Test Coverage

- ✅ Path resolution (8 tests)
- ✅ Safety checks (5 tests)
- ✅ Schema validation (4 tests)
- ✅ Operations (6 tests)
- ✅ Executor (4 tests)
- ✅ Utils (5 tests)
- ✅ Integration (2 tests)
- ✅ Idempotency (3 tests)

---

## Migration from Stateful Version

### Before (Stateful)

```python
# Create session
result = create_session(initial_content, "yaml")
session_id = result["session_id"]

# Apply changes
apply_change(session_id, operation1, "reason")
apply_change(session_id, operation2, "reason")

# Export
export_domain_pack(session_id, "yaml")
```

### After (Pure)

```python
# Single transformation
result = transform_document(
    document=initial_content,
    format="yaml",
    operations=[operation1, operation2]
)

# Output is in result["serialized"]
```

### Version History

If you need version history, implement it **outside** the MCP:
- Backend stores snapshots before/after transformations
- Backend manages version IDs and metadata
- MCP remains pure (no state)

---

## Performance

- **Typical transformation**: < 20ms
- **Complex batch (10 ops)**: < 50ms
- **Large document (10KB)**: < 100ms

All operations are O(n) where n is the number of operations.

---

## Comparison: Old vs New

| Feature | Old (Stateful) | New (Pure) |
|---------|---------------|------------|
| **Architecture** | Session-based | Stateless |
| **Database** | PostgreSQL required | None |
| **Version History** | Built-in | External (if needed) |
| **Rollback** | Built-in | N/A (use external) |
| **Complexity** | ~2,460 lines | ~3,070 lines |
| **Files** | 7 core + db | 7 core (no db) |
| **Determinism** | Partial | Complete |
| **Testability** | Moderate | Excellent |
| **Deployment** | Complex | Simple |

---

## API Reference

### `transform_document(document, format, operations, schema?, options?)`

Apply operations to document.

**Args:**
- `document` (str): YAML or JSON string
- `format` (str): "yaml" or "json"
- `operations` (List[Dict]): Operations to apply
- `schema` (Dict, optional): Custom schema
- `options` (Dict, optional): Execution options

**Returns:** `TransformationResult`

---

### `validate_document(document, format, schema?)`

Validate document against schema.

**Args:**
- `document` (str): YAML or JSON string
- `format` (str): "yaml" or "json"
- `schema` (Dict, optional): Custom schema

**Returns:** `ValidationResult`

---

### `preview_operations(document, format, operations, schema?, options?)`

Preview changes without applying (dry-run).

**Args:** Same as `transform_document`

**Returns:** `PreviewResult`

---

### `get_schema()`

Get the default domain pack schema.

**Returns:** `DOMAIN_PACK_SCHEMA`

---

## Examples

### Example 1: Version Bump

```python
result = transform_document(
    document='name: Legal\ndescription: Legal domain\nversion: 1.0.0',
    format="yaml",
    operations=[
        {"action": "replace", "path": ["version"], "value": "2.0.0"}
    ]
)
```

### Example 2: Add Entity

```python
result = transform_document(
    document=domain_pack_yaml,
    format="yaml",
    operations=[
        {
            "action": "add",
            "path": ["entities"],
            "value": {
                "name": "Contract",
                "type": "CONTRACT",
                "attributes": ["contract_id", "parties", "effective_date"]
            }
        }
    ]
)
```

### Example 3: Batch Update

```python
result = transform_document(
    document=domain_pack_yaml,
    format="yaml",
    operations=[
        {"action": "replace", "path": ["version"], "value": "2.0.0"},
        {"action": "add", "path": ["key_terms"], "value": "compliance"},
        {"action": "update", "path": ["entities", 0], "updates": {"type": "ATTORNEY_V2"}}
    ]
)
```

---

## Troubleshooting

### Error: "SCHEMA_VALIDATION_FAILED_PRE"

**Cause**: Input document doesn't match schema  
**Fix**: Validate document structure before transformation

### Error: "REQUIRED_FIELD_DELETION"

**Cause**: Attempting to delete required field (name, description, version)  
**Fix**: Don't delete required fields

### Error: "TYPE_MISMATCH"

**Cause**: Operation value type doesn't match schema  
**Fix**: Ensure value types match schema expectations

### Warning: "BULK_CHANGE_WARNING"

**Cause**: More than 10 operations in batch  
**Fix**: Either split into smaller batches or disable strict mode

---

## Contributing

This is a pure, deterministic system. When adding features:

1. **Maintain purity**: No side effects, no external state
2. **Add tests**: Every feature needs tests
3. **Document errors**: Clear error messages with context
4. **Preserve determinism**: Same input → same output

---

## License

[Your License Here]


