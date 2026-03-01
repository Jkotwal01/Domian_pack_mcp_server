# Domain Pack Generator — Backend

> **FastAPI + LangGraph** backend for AI-assisted domain pack configuration. Conversational by design, deterministic by construction.

---

## 📋 Table of Contents

- [Developer Setup Guide](#developer-setup-guide)
- [Common Commands](#common-commands)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [AI Chatbot System (Deep Dive)](#ai-chatbot-system-deep-dive)
- [Patch Applier (Deep Dive)](#patch-applier-deep-dive)
- [API Reference](#api-reference)

---

## Developer Setup Guide

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.11 or higher |
| PostgreSQL | 14 or higher |
| OpenAI API Key | GPT-4o-mini access required |

---

### Step 1 — Clone & Navigate

```bash
git clone <repo-url>
cd domain-pack-mcp/backend
```

---

### Step 2 — Create Virtual Environment

```powershell
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
python -m venv .venv
source .venv/bin/activate
```

---

### Step 3 — Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt

# For development (pytest, black, ruff)
pip install -r requirements-dev.txt
```

---

### Step 4 — Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/domain_pack_db

# Security (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-here

# OpenAI
OPENAI_API_KEY=sk-...
```

---

### Step 5 — Set Up PostgreSQL Database

```bash
# Create the database
createdb domain_pack_db

# Initialize tables, indexes, and schemas
psql -d domain_pack_db -f init_db.sql

# Apply any pending ORM migrations
alembic upgrade head
```

---

### Step 6 — Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will be live at [http://localhost:8000](http://localhost:8000).

---

### Step 7 — Verify Setup

1. Visit [http://localhost:8000/docs](http://localhost:8000/docs) — Swagger UI should load.
2. `POST /auth/signup` with your credentials.
3. `POST /auth/login` to receive a JWT token.
4. Create a domain via `POST /domains`.
5. Start a chat session and send a message.

---

## Common Commands

| Task | Command |
|---|---|
| Activate venv (Win) | `.venv\Scripts\Activate.ps1` |
| Activate venv (Unix) | `source .venv/bin/activate` |
| Start server | `uvicorn app.main:app --reload` |
| New DB migration | `alembic revision --autogenerate -m "description"` |
| Apply migrations | `alembic upgrade head` |
| Rollback migration | `alembic downgrade -1` |
| Format code | `black .` |
| Lint check | `ruff check .` |
| Check token usage | View `/monitoring` page in frontend |

---

## Architecture Overview

The backend follows a strict **LLM-safe architecture**:

```
User Message
     │
     ▼
[LLM — Intent Classification]  ← Understands natural language
     │
     ▼
[LLM — Structured Patch Generation]  ← Produces a JSON patch plan
     │
     ▼
[Pure Python — Patch Applier]  ← Applies patch deterministically
     │
     ▼
[Pydantic — Schema Validation]  ← Validates the result
     │
     ▼
[PostgreSQL — Persistence]  ← Saves the final config
```

**Key Principle**: The LLM *never* writes to the database, edits YAML/JSON directly, or bypasses schema validation. Its only role is to understand intent and generate structured patch instructions. All mutations are handled by deterministic Python code.

---

## Project Structure

```
backend/
├── app/
│   ├── api/                    # FastAPI route handlers
│   │   ├── auth.py             #   Authentication (signup, login, JWT)
│   │   ├── chat.py             #   Chat sessions & AI messaging
│   │   └── domains.py          #   Domain CRUD operations
│   ├── dp_chatbot_module/      # LangGraph AI workflow
│   │   ├── graph.py            #   Graph topology & edge wiring
│   │   ├── nodes.py            #   All 7 LangGraph node functions
│   │   ├── prompts.py          #   LLM prompt templates
│   │   └── state.py            #   AgentState TypedDict schema
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic request/response schemas
│   │   └── patch.py            #   PatchOperation & PatchList schemas
│   ├── services/               # Business logic layer
│   │   ├── auth_service.py
│   │   ├── chat_service.py     #   Orchestrates LangGraph invocation
│   │   ├── domain_service.py
│   │   └── validation_service.py
│   └── utils/
│       ├── patch_applier.py    #   38+ pure Python patch handlers
│       ├── context_slicer.py   #   Reduces LLM token usage by 85–96%
│       ├── llm_factory.py      #   Centralized LLM client factory
│       ├── llm_monitor.py      #   Per-node token & latency tracking
│       ├── security.py         #   JWT + password hashing
│       └── templates.py        #   Domain config YAML templates
├── alembic/                    # DB migration history
├── init_db.sql                 # Raw SQL schema initialization
├── requirements.txt
└── requirements-dev.txt
```

---

## AI Chatbot System (Deep Dive)

The chatbot is a **7-node LangGraph state machine** located in `app/dp_chatbot_module/`. Each node is a pure Python function that receives and returns an `AgentState` dictionary.

### AgentState — The Shared State Schema

Defined in `state.py`, the `AgentState` TypedDict flows through every node:

| Field | Type | Description |
|---|---|---|
| `messages` | `List[BaseMessage]` | Full conversation history |
| `current_config` | `Dict` | The domain config being edited |
| `intent` | `str` | Classified intent label |
| `proposed_patch` | `Dict` | LLM-generated patch plan |
| `updated_config` | `Dict` | Config after patch is applied |
| `validation_result` | `Dict` | Pydantic schema check result |
| `needs_confirmation` | `bool` | Whether user must confirm changes |
| `reasoning` | `str` | LLM's reasoning for the patch |
| `assistant_response` | `str` | Final message returned to user |
| `node_call_logs` | `List[Dict]` | Per-node token count & latency |
| `error_message` | `str` | Error details if any node fails |

---

### LangGraph Workflow — Node by Node

#### Graph Topology

```
classify_intent
    │
    ├─── [info_query] ──────────────────────────► generate_response ──► END
    │
    ├─── [general_query] ────────────────────────► general_knowledge ──► END
    │
    └─── [any operation intent] ──► generate_patch ──► apply_patch ──► validate
                                                                             │
                                                        ┌────────────────────┤
                                                        │ [error]            │ [success]
                                                        ▼                    ▼
                                               generate_response    prepare_confirmation
                                                        │                    │
                                                        └────────────────────┘
                                                                 │
                                                        generate_response ──► END
```

---

#### Node 1 — `classify_intent_node`

**File**: `nodes.py` | **LLM**: GPT-4o-mini (temperature=0)

Determines *what the user wants to do* from their natural language message.

**How it works**:
1. Extracts full entity/relationship names + descriptions from the current config to build rich context (capped at 20 items for large configs).
2. Formats an intent classification prompt with this context.
3. Calls the LLM and normalizes the raw output against `VALID_INTENTS`.
4. Retries up to **3 times** with backoff on failure or invalid output.

**Valid Intent Labels**:

| Intent | Description |
|---|---|
| `domain_operation` | Edit domain name, description, or version |
| `entity_operation` | Add/edit/delete entities, attributes, synonyms |
| `relationship_operation` | Add/edit/delete relationships and their attributes |
| `extraction_pattern_operation` | Manage regex extraction patterns |
| `key_term_operation` | Manage vocabulary/key terms |
| `info_query` | User is asking a question about the config (no edit) |
| `general_query` | General knowledge question unrelated to the config |

---

#### Node 2 — `generate_patch_node`

**File**: `nodes.py` | **LLM**: GPT-4o-mini with **structured output** (temperature=0)

Translates the classified intent + user message into a structured **`PatchList`** — a list of `PatchOperation` objects.

**How it works**:
1. Calls `get_relevant_context()` to slice only the config section relevant to the intent (reduces token usage by 85–96%).
2. Takes the last 5 messages from history for conversation context.
3. Uses `llm.with_structured_output(PatchList)` — forces the LLM to return a Pydantic-validated patch plan, never raw text.
4. Retries up to **3 times** on failure.

**`PatchOperation` Schema** (defined in `schemas/patch.py`):

```python
class PatchOperation(BaseModel):
    operation: str        # e.g. "add_entity", "update_entity_description"
    target_name: str      # Name of the item to operate on
    parent_name: str      # For nested items (e.g. entity name for attribute ops)
    attribute_name: str   # For attribute-level operations
    old_value: Any        # For update/delete operations
    new_value: Any        # The new value to set
    payload: Dict         # For complex additions (e.g. new entity with all fields)
    reasoning: str        # LLM's explanation of the change
```

---

#### Node 3 — `apply_patch_node`

**File**: `nodes.py` → delegates to `utils/patch_applier.py` | **No LLM**

Applies the generated patch plan to `current_config` using **pure Python**.

**How it works**:
1. Deserializes the `proposed_patch` dict back into a `PatchList`.
2. Iterates over each `PatchOperation` and calls the central `apply_patch()` dispatcher.
3. Deep-copies the config before mutation to prevent side effects.
4. On `ValueError`, stores the error in state without crashing the graph.

---

#### Node 4 — `validate_patch_node`

**File**: `nodes.py` → delegates to `services/validation_service.py` | **No LLM**

Validates the updated config against the domain schema using **Pydantic**.

- If **valid**: Passes `validation_result` to state and continues.
- If **invalid**: Stores a descriptive error message and routes to `generate_response`.

---

#### Node 5 — `prepare_confirmation_node`

**File**: `nodes.py` | **No LLM**

Checks whether actual patches were generated. Sets `needs_confirmation = True` if there are patches to review, triggering the frontend's confirmation dialog.

---

#### Node 6 — `generate_response_node`

**File**: `nodes.py` | **LLM used only for error/info paths**

Generates the final assistant response for the user.

**Three paths**:
- **Error path**: Calls LLM with `ERROR_EXPLANATION_PROMPT` to turn technical errors into friendly messages.
- **Info query path**: Calls LLM with `INFO_QUERY_PROMPT` + relevant config slice to answer the user's question.
- **Success path**: Returns a deterministic confirmation string (no LLM call).

---

#### Node 7 — `general_knowledge_node`

**File**: `nodes.py` | **LLM**: GPT-4o-mini

Handles off-topic questions unrelated to the domain config (e.g., "What is a knowledge graph?"). Uses `GENERAL_KNOWLEDGE_PROMPT` to answer from the LLM's training knowledge.

---

### Context Slicer — Token Optimization

**File**: `utils/context_slicer.py`

Before calling the LLM for patch generation or info queries, only the *relevant slice* of the config is sent:

| Intent | Slice Sent to LLM |
|---|---|
| `entity_operation` | Only entities (+ target entity detail) |
| `relationship_operation` | Only relationships |
| `extraction_pattern_operation` | Only extraction_patterns |
| `key_term_operation` | Only key_terms |
| `domain_operation` | Only name, description, version |
| `info_query` | Keyword-routing to the appropriate slice |

This reduces token consumption by **85–96%** compared to sending the full config on every call.

---

## Patch Applier (Deep Dive)

**File**: `utils/patch_applier.py`

The patch applier is the backbone of all config mutations. It is a **pure Python, LLM-free, deterministic** module with **38 named operations**.

### How it Works

The entry point `apply_patch(config, patch)` deep-copies the config and dispatches to the correct handler via an operation map:

```python
operation_map = {
    "update_domain_name": update_domain_name,
    "add_entity": add_entity,
    "add_entity_attribute": add_entity_attribute,
    # ... 35 more
}
handler = operation_map.get(patch.operation)
return handler(config, patch)
```

### Complete Operation Reference

#### Domain-Level (3 operations)
| Operation | Description |
|---|---|
| `update_domain_name` | Sets `config["name"]` |
| `update_domain_description` | Sets `config["description"]` |
| `update_domain_version` | Sets `config["version"]` |

#### Entity Operations (5 operations)
| Operation | Key Behavior |
|---|---|
| `add_entity` | Requires `payload` with `name`, `type`, `description`. Guards against duplicate names. |
| `update_entity_name` | Renames entity display name. Does **not** cascade to relationships (relationships link by `type`). |
| `update_entity_type` | **Cascades** the old type to all relationship `from`/`to` fields. |
| `update_entity_description` | Simple field update. |
| `delete_entity` | Raises `ValueError` if the entity's `type` is still referenced in any relationship. |

#### Entity Attribute Operations (4 operations)
| Operation | Key Behavior |
|---|---|
| `add_entity_attribute` | Supports two LLM patterns: full `payload` object OR flat `new_value` + `attribute_name`. Guards against duplicates. |
| `update_entity_attribute_name` | Requires `parent_name` (entity) + `attribute_name`. |
| `update_entity_attribute_description` | Requires `parent_name` + `attribute_name`. |
| `delete_entity_attribute` | Filters out the attribute by name. |

#### Entity Attribute Examples (3 operations)
| Operation | Description |
|---|---|
| `add_entity_attribute_example` | Appends to `attr["examples"]` array. |
| `update_entity_attribute_example` | Replaces `old_value` with `new_value` in the examples array. |
| `delete_entity_attribute_example` | Filters out `old_value` from examples. |

#### Entity Synonyms (3 operations)
| Operation | Description |
|---|---|
| `add_entity_synonym` | Appends to `entity["synonyms"]`. Raises if duplicate. |
| `update_entity_synonym` | Replaces `old_value` with `new_value`. |
| `delete_entity_synonym` | Filters out `old_value`. |

#### Relationship Operations (6 operations)
| Operation | Key Behavior |
|---|---|
| `add_relationship` | Validates that `from` and `to` reference existing entity **types**. |
| `update_relationship_name` | Renames relationship label. |
| `update_relationship_from` | Validates new type exists before updating. |
| `update_relationship_to` | Validates new type exists before updating. |
| `update_relationship_description` | Simple field update. |
| `delete_relationship` | Removes by name. |

#### Relationship Attribute Operations (4 operations)
Same pattern as entity attribute operations but scoped to `relationships`.

#### Relationship Attribute Examples (3 operations)
Same pattern as entity attribute examples but scoped to relationship attributes.

#### Extraction Pattern Operations (6 operations)
| Operation | Key Behavior |
|---|---|
| `add_extraction_pattern` | Requires `payload` with `pattern`, `entity_type`, `attribute`. Defaults: `confidence=0.9`, `extract_full_match=True`. |
| `update_extraction_pattern_pattern` | Addressed by index (`target_name` must be a digit string). |
| `update_extraction_pattern_entity_type` | Addressed by index. |
| `update_extraction_pattern_attribute` | Addressed by index. |
| `update_extraction_pattern_extract_full_match` | Addressed by index. |
| `update_extraction_pattern_confidence` | Addressed by index. |
| `delete_extraction_pattern` | Removes by index. |

#### Key Term Operations (3 operations)
| Operation | Key Behavior |
|---|---|
| `add_key_term` | **Idempotent** — silently skips if term already exists (safe for bulk adds). |
| `update_key_term` | Replaces `old_value` term with `new_value`. |
| `delete_key_term` | Filters out `old_value`. |

---

## API Reference

All protected routes require: `Authorization: Bearer <token>`

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/signup` | Register a new user |
| `POST` | `/auth/login` | Login and receive JWT token |

**Signup / Login Payload:**
```json
{
  "email": "user@example.com",
  "password": "strongpassword123"
}
```

---

### Domain Management

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/domains` | List all domains for the current user |
| `POST` | `/domains` | Create a new domain pack |
| `GET` | `/domains/{id}` | Get a specific domain |
| `PUT` | `/domains/{id}` | Update a domain |
| `DELETE` | `/domains/{id}` | Delete a domain |

**Create Domain:**
```json
{
  "name": "Healthcare Domain",
  "description": "Medical knowledge graph configuration",
  "version": "1.0.0"
}
```

---

### Chat & AI Sessions

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat/sessions` | Create or retrieve active session |
| `GET` | `/chat/sessions/{id}` | Get session details |
| `GET` | `/chat/sessions/{id}/messages` | Get message history |
| `POST` | `/chat/sessions/{id}/message` | Send a message to the AI |
| `GET` | `/chat/sessions/{id}/node-calls` | Get per-node LLM call logs |
| `GET` | `/chat/sessions/{id}/stats` | Get session token usage stats |
| `POST` | `/chat/sessions/{id}/close` | Close a session |
| `DELETE` | `/chat/sessions/{id}` | Permanently delete a session |

**Send Message:**
```json
{
  "message": "Add an entity called 'Patient' with attributes 'name' and 'age'."
}
```

**Interactive API Docs** (auto-generated by FastAPI):
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---
<!-- 
## Future Improvements

### 1. Specialized Patch Schema Optimization (Token Reduction)

**Goal**: Reduce `generate_patch` node LLM input from ~1,676 tokens by 40–50%.

**Current Problem**: The monolithic `PatchList` schema exposes all 59 operations to the LLM regardless of the detected intent.

**Proposed Solution**:

Split `PatchOperation` in `schemas/patch.py` into specialized sub-models:

```python
class EntityPatchOperation(BaseModel):      # ~15 operations
class RelationshipPatchOperation(BaseModel): # ~14 operations
class ExtractionPatchOperation(BaseModel):   # ~6 operations
class KeyTermPatchOperation(BaseModel):      # ~3 operations
class DomainPatchOperation(BaseModel):       # ~3 operations
```

In `generate_patch_node`, map the classified intent to the appropriate schema before calling `llm.with_structured_output(SelectedModel)`. The LLM will receive a 3–15 operation schema instead of 59, saving **500–700 tokens per call**.

**Validation**: Compare token counts in the Monitoring dashboard before and after.

---

### 2. Streaming AI Responses

**Goal**: Improve perceived performance for long patch generation steps.

Stream LangGraph node outputs incrementally using FastAPI's `StreamingResponse` and `AsyncGenerator`. This allows the frontend to display partial responses and a live "thinking" indicator per node.

---

### 3. Smarter Conflict Detection

**Goal**: Warn users before destructive operations instead of hard-failing.

Add a pre-flight `conflict_check_node` that inspects the proposed patch for cascading effects (e.g., deleting an entity type that's referenced in relationships) and surfaces warnings to the user before applying.

---

### 4. Multi-Model LLM Support

**Goal**: Make the LLM provider configurable without code changes.

Extend `llm_factory.py` to support routing between OpenAI GPT-4o-mini, Anthropic Claude Haiku, and Google Gemini Flash based on a `.env` variable — enabling cost and latency optimization per intent type.

---

### 5. Automated Patch Testing Suite

**Goal**: Prevent regressions in the patch applier as operations are added.

Create a dedicated `tests/test_patch_applier.py` with parametrized test cases covering all 38 operations — including edge cases like duplicate detection, cascade updates, and index-based extraction pattern operations. -->
