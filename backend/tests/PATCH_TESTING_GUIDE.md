# Domain Pack Patch Operations Testing Guide

This guide shows you how to test the domain pack CRUD operations using JSON Patch without the chatbot.

## 🎯 What Are Patch Operations?

JSON Patch (RFC 6902) is a format for describing changes to a JSON document. Instead of sending the entire updated configuration, you send only the changes.

## 📋 Available Operations

### 1. Add Operation
Adds a new value to an object or array.

```json
{
  "op": "add",
  "path": "/entities/-",
  "value": {
    "name": "Patient",
    "type": "PATIENT",
    "description": "A patient in the healthcare system",
    "attributes": [
      {"name": "name", "description": "Patient full name"},
      {"name": "age", "description": "Patient age"}
    ],
    "synonyms": ["Individual", "Person"]
  }
}
```

### 2. Remove Operation
Removes a value from an object or array.

```json
{
  "op": "remove",
  "path": "/entities/0"
}
```

### 3. Replace Operation
Replaces a value.

```json
{
  "op": "replace",
  "path": "/entities/0/description",
  "value": "Updated description"
}
```

### 4. Move Operation
Moves a value from one location to another.

```json
{
  "op": "move",
  "from": "/entities/0",
  "path": "/entities/1"
}
```

### 5. Copy Operation
Copies a value from one location to another.

```json
{
  "op": "copy",
  "from": "/entities/0",
  "path": "/entities/-"
}
```

### 6. Test Operation
Tests that a value at the target location is equal to a specified value.

```json
{
  "op": "test",
  "path": "/entities/0/name",
  "value": "Patient"
}
```

---

## 🧪 Testing Scenarios

### Scenario 1: Add a New Entity

**Initial Domain Config:**
```json
{
  "name": "Healthcare Domain",
  "description": "Medical domain",
  "version": "1.0.0",
  "entities": [],
  "relationships": [],
  "extraction_patterns": [],
  "key_terms": []
}
```

**Patch to Apply:**
```json
[
  {
    "op": "add",
    "path": "/entities/-",
    "value": {
      "name": "Patient",
      "type": "PATIENT",
      "description": "A patient in the healthcare system",
      "attributes": [
        {"name": "name", "description": "Patient full name"},
        {"name": "age", "description": "Patient age"}
      ],
      "synonyms": ["Individual"]
    }
  }
]
```

**Expected Result:**
```json
{
  "name": "Healthcare Domain",
  "description": "Medical domain",
  "version": "1.0.0",
  "entities": [
    {
      "name": "Patient",
      "type": "PATIENT",
      "description": "A patient in the healthcare system",
      "attributes": [
        {"name": "name", "description": "Patient full name"},
        {"name": "age", "description": "Patient age"}
      ],
      "synonyms": ["Individual"]
    }
  ],
  "relationships": [],
  "extraction_patterns": [],
  "key_terms": []
}
```

---

### Scenario 2: Add Multiple Entities at Once

**Patch:**
```json
[
  {
    "op": "add",
    "path": "/entities/-",
    "value": {
      "name": "Doctor",
      "type": "DOCTOR",
      "description": "A medical doctor",
      "attributes": [
        {"name": "name", "description": "Doctor name"},
        {"name": "specialization", "description": "Medical specialization"}
      ],
      "synonyms": ["Physician"]
    }
  },
  {
    "op": "add",
    "path": "/entities/-",
    "value": {
      "name": "Hospital",
      "type": "HOSPITAL",
      "description": "A medical facility",
      "attributes": [
        {"name": "name", "description": "Hospital name"},
        {"name": "location", "description": "Hospital address"}
      ],
      "synonyms": ["Medical Center"]
    }
  }
]
```

---

### Scenario 3: Add a Relationship

**Patch:**
```json
[
  {
    "op": "add",
    "path": "/relationships/-",
    "value": {
      "name": "TREATED_BY",
      "from": "PATIENT",
      "to": "DOCTOR",
      "description": "Patient is treated by a doctor",
      "attributes": [
        {"name": "date", "description": "Treatment date"}
      ]
    }
  }
]
```

---

### Scenario 4: Update Entity Description

**Patch:**
```json
[
  {
    "op": "replace",
    "path": "/entities/0/description",
    "value": "A person receiving medical care"
  }
]
```

---

### Scenario 5: Add Attribute to Existing Entity

**Patch:**
```json
[
  {
    "op": "add",
    "path": "/entities/0/attributes/-",
    "value": {
      "name": "blood_type",
      "description": "Patient blood type"
    }
  }
]
```

---

### Scenario 6: Remove an Entity

**Patch:**
```json
[
  {
    "op": "remove",
    "path": "/entities/1"
  }
]
```

---

### Scenario 7: Add Extraction Pattern

**Patch:**
```json
[
  {
    "op": "add",
    "path": "/extraction_patterns/-",
    "value": {
      "pattern": "\\bDr\\. [A-Z][a-z]+ [A-Z][a-z]+\\b",
      "entity_type": "DOCTOR",
      "attribute": "name",
      "extract_full_match": true,
      "confidence": 0.9
    }
  }
]
```

---

### Scenario 8: Add Key Terms

**Patch:**
```json
[
  {
    "op": "add",
    "path": "/key_terms",
    "value": ["patient", "doctor", "treatment", "diagnosis", "medication"]
  }
]
```

---

## 🚀 How to Test Using the API

### Step 1: Create a Domain
```bash
curl -X POST http://localhost:8000/domains \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Healthcare Domain",
    "description": "Medical domain for testing",
    "version": "1.0.0"
  }'
```

Save the returned `id` for the next steps.

### Step 2: Get Current Domain Config
```bash
curl -X GET http://localhost:8000/domains/YOUR_DOMAIN_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Step 3: Apply a Patch
```bash
curl -X PUT http://localhost:8000/domains/YOUR_DOMAIN_ID \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config_json": {
      "name": "Healthcare Domain",
      "description": "Medical domain",
      "version": "1.0.0",
      "entities": [
        {
          "name": "Patient",
          "type": "PATIENT",
          "description": "A patient",
          "attributes": [],
          "synonyms": []
        }
      ],
      "relationships": [],
      "extraction_patterns": [],
      "key_terms": []
    }
  }'
```

---

## 🧪 Python Test Script

Create a file `test_patches.py`:

```python
import requests
import json

API_BASE = "http://localhost:8000"
TOKEN = "YOUR_JWT_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 1. Create domain
domain_data = {
    "name": "Test Domain",
    "description": "Testing patch operations",
    "version": "1.0.0"
}
response = requests.post(f"{API_BASE}/domains", headers=headers, json=domain_data)
domain = response.json()
domain_id = domain["id"]
print(f"Created domain: {domain_id}")

# 2. Get initial config
response = requests.get(f"{API_BASE}/domains/{domain_id}", headers=headers)
config = response.json()["config_json"]
print(f"Initial config: {json.dumps(config, indent=2)}")

# 3. Add an entity
config["entities"].append({
    "name": "Patient",
    "type": "PATIENT",
    "description": "A patient",
    "attributes": [
        {"name": "name", "description": "Patient name"},
        {"name": "age", "description": "Patient age"}
    ],
    "synonyms": ["Individual"]
})

# 4. Update domain
update_data = {"config_json": config}
response = requests.put(f"{API_BASE}/domains/{domain_id}", headers=headers, json=update_data)
updated = response.json()
print(f"Updated config: {json.dumps(updated['config_json'], indent=2)}")

# 5. Verify entity count
print(f"Entity count: {updated['entity_count']}")
```

Run with:
```bash
python test_patches.py
```

---

## 📊 Validation Rules

The backend automatically validates:

1. **Entity Validation**:
   - Must have `name`, `type`, and `description`
   - `type` must be uppercase
   - `attributes` must be an array
   - `synonyms` must be an array

2. **Relationship Validation**:
   - Must have `name`, `from`, `to`, and `description`
   - `from` and `to` must reference existing entity types

3. **Pattern Validation**:
   - Must have `pattern`, `entity_type`, and `attribute`
   - `entity_type` must reference an existing entity

4. **Config Structure**:
   - Must have `entities`, `relationships`, `extraction_patterns`, and `key_terms` arrays

---

## 🎯 Quick Reference: Path Syntax

- `/entities/-` - Append to entities array
- `/entities/0` - First entity
- `/entities/0/attributes/-` - Append to first entity's attributes
- `/relationships/1/description` - Description of second relationship
- `/key_terms` - The key_terms array itself

---

## 💡 Tips

1. **Use `-` for array append**: `/entities/-` adds to the end
2. **Use index for specific items**: `/entities/0` targets first item
3. **Chain operations**: Multiple patches in one array
4. **Test before applying**: Use the `test` operation to verify state
5. **Validate after each change**: Check `entity_count`, `relationship_count`, etc.

---

## 🐛 Common Errors

### Error: "Patch removed entities array"
**Cause**: Trying to remove the entire entities array
**Fix**: Only remove individual entities, not the array itself

### Error: "Entity type PATIENT not found"
**Cause**: Relationship references non-existent entity
**Fix**: Add the entity first, then the relationship

### Error: "Invalid patch format"
**Cause**: Malformed JSON Patch
**Fix**: Ensure each operation has `op` and `path` fields

---

## 🎓 Next Steps

1. Test basic add/remove operations
2. Try complex multi-step patches
3. Validate error handling
4. Test with the Streamlit UI
5. Integrate with the chatbot (when OpenAI quota is available)
