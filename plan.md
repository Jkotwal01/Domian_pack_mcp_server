# Backend Guide – Domain Customisation Platform

## 1. Understand the Requirements (Before Writing Code)

### Core Product Goal

Enable users to create, view, edit, and customize domain packs (JSON/YAML) via:

- UI-based configuration
- Chatbot-driven CRUD (context-aware, session-based)

### Functional Requirements Breakdown

#### A. Domain Initialization

User has two entry paths:

**New Domain**

- Inputs:
  - name
  - description
  - version
- System initializes a base domain pack structure.

**Existing Domain**

- User selects an existing domain.
- System loads the full domain pack into the UI.

#### B. Domain Pack Processing

Backend must:

- Parse domain pack (JSON / YAML)
- Extract:
  - Entities
  - Attributes
  - Relationships
  - Extraction patterns
  - Key terms

This extracted structure becomes:

- UI-editable
- Chatbot-context-aware

#### C. UI Editing

User can:

- View entire domain pack
- Edit any key-value
- Save changes → new version stored
- Backend validates structure before saving

#### D. Chatbot Interaction

Chatbot can:

- Create new entities/attributes/relationships
- Update existing ones
- Delete existing ones

Must:

- Maintain session context
- Be aware of current domain structure
- Apply changes deterministically to domain pack
- No version history required here

### Non-Functional Requirements

- Session-based interactions
- Safe editing (no invalid schema writes)
- Extensible for future domain types
- Clean separation of responsibilities

## 2. Choose the Right Architecture

### Recommended Choice: Modular Monolith

**Why?**

- You are early-stage
- Heavy shared domain logic
- Fast iteration required
- Microservices would add artificial complexity
- You can always split later once boundaries stabilize

### High-Level Architecture

```
Client (UI / Chatbot)
        |
     API Layer
        |
Application / Service Layer
        |
Domain Logic Layer
        |
Persistence Layer (PostgreSQL)
```

### Key Architectural Principles Applied

**Separation of Concerns**

- API ≠ Business logic
- Chatbot logic ≠ CRUD logic
- Parsing ≠ Storage

**Loose Coupling**

- Chatbot talks to domain via commands
- UI talks via contracts (DTOs)

**High Cohesion**

- All domain-pack logic lives in one bounded context

### Logical Modules

```
/domain
  ├── domain_pack/
  ├── entity/
  ├── relationship/
  ├── extraction_pattern/
  ├── key_terms/

/application
  ├── domain_service/
  ├── chatbot_service/
  ├── validation_service/

/api
  ├── domain_routes/
  ├── chatbot_routes/

/infrastructure
  ├── db/
  ├── auth/
  ├── logging/
```

## 3. API Design (The Contract)

### API Style: REST

**Why?**

- CRUD-heavy
- UI + chatbot friendly
- Easy to version

### Versioning Strategy

```
/api/v1/...
```

### Core API Groups

#### Domain Management

```
POST   /domains               → create new domain
GET    /domains               → list domains
GET    /domains/{id}          → fetch full domain pack
PUT    /domains/{id}          → update domain pack
```

#### Domain Pack Editing

```
PUT /domains/{id}/entities
PUT /domains/{id}/relationships
PUT /domains/{id}/patterns
PUT /domains/{id}/key-terms
```

These endpoints are schema-aware, not raw JSON dumps.

#### Chatbot Interaction

```
POST /chat/session/start
POST /chat/session/{id}/message
POST /chat/session/{id}/apply
```

Chat returns:

- Parsed intent
- Proposed domain mutations
- Apply endpoint commits changes

### API Design Rules

- Use correct HTTP verbs
- Never expose internal DB models
- Always return structured errors
- Always validate before persist

### Error Response Standard

```json
{
  "error": {
    "code": "INVALID_DOMAIN_SCHEMA",
    "message": "Entity type 'CourtX' does not exist",
    "details": {}
  }
}
```

## 4. Database Design (PostgreSQL)

### Why PostgreSQL

- Strong schema support
- JSONB for flexible structures
- Transactions for safe edits
- Mature ecosystem

### Storage Strategy (Hybrid)

| Data            | Storage            |
| --------------- | ------------------ |
| Domain metadata | Relational columns |
| Domain pack     | JSONB              |
| Chat sessions   | Relational         |
| Chat context    | JSONB              |

### Core Tables

#### domains

- `id`
- `name`
- `description`
- `version`
- `domain_pack` (JSONB)
- `created_at`
- `updated_at`

#### chat_sessions

- `id`
- `domain_id`
- `user_id`
- `context_snapshot` (JSONB)
- `created_at`
- `last_active_at`

### Indexing Strategy

- domain name (unique)
- JSONB GIN index on entities/relationships
- session_id for chatbot speed

### Data Integrity

- JSON Schema validation before insert
- Foreign key constraints
- Transactions on updates

### Migrations

- Versioned schema migrations
- JSON schema evolution tracked separately

## 5. Authentication & Authorization

### Authentication

- JWT-based
- Access token + refresh token
- Secure password hashing

### Security Practices

- HTTPS only
- Token expiration
- Audit logs for edits
- No trust in client input

## 6. Error Handling & Logging

### Error Handling Strategy

- Central error handler
- Domain-specific exceptions
- User-safe error messages

### Logging

**Structured logs (JSON)**

Levels:

- `INFO` – domain saved
- `WARN` – invalid input
- `ERROR` – system failure

### Observability

- Request ID per call
- Chat session traceability
- Alerts for DB failures

### Graceful Failure

- Partial failures don't corrupt domain pack
- Rollback on invalid updates
- Chatbot proposals never auto-commit

## 7. Testing Strategy

### Unit Tests

- Domain validation logic
- Chatbot intent parsing
- JSON/YAML transformations

### Integration Tests

- API ↔ DB
- Chat session lifecycle
- Domain save/update flows

### Edge Cases to Test

- Circular relationships
- Duplicate entity types
- Invalid regex patterns
- Concurrent edits
- Chat session timeout

## 8. Final Mental Model

**Domain Pack is the source of truth**

UI and chatbot are just two ways of mutating it safely.

## 9. Technology Stack

### Backend

- **Framework:** Python FastAPI
- **Database:** PostgreSQL
- **API Testing:** FastAPI /docs or POSTMAN

### Frontend

- **Framework:** Vite + React.js (or Next.js)

### Chatbot

- **Framework:** LangGraph
- **Concepts:**
  - Create new, update, and delete existing domain pack keys and values
  - Context-aware based on extracted entities, attributes, and relationships
  - Enable users to add/edit to create more customized templates
  - No versioning required
  - Chain of thought reasoning
  - Session-based
  - LLM provides operation spec to core Python for editing after user confirmation

### JSON/YAML Mutation

- All mutations done through core Python logic

### Development Focus

- **Phase 1:** Core backend and domain logic
- **Phase 2:** Chatbot integration

## 10. Backend Folder Structure

Production-grade backend folder structure tailored for:

- FastAPI
- PostgreSQL
- Domain Pack CRUD + validation
- Future LangGraph chatbot (isolated, not mixed)
- Pure Python mutation engine for JSON/YAML
- Clear separation of concerns

### High-Level Backend Folder Structure

```
backend/
├── app/
│   ├── main.py
│   ├── config/
│   ├── api/
│   ├── core/
│   ├── domain/
│   ├── services/
│   ├── persistence/
│   ├── schemas/
│   ├── utils/
│   ├── chatbot/               # Scaffold only (future focus)
│   └── tests/
│
├── alembic/
├── alembic.ini
├── requirements.txt
├── README.md
└── .env
```

### 10.1 app/main.py

**Application entry point**

Responsibilities:

- Create FastAPI app
- Register routers
- Load middleware
- Startup/shutdown events

### 10.2 Configuration Layer: app/config/

```
app/config/
├── settings.py
├── database.py
├── logging.py
└── security.py
```

**Purpose:** Centralized configuration

- DB connection
- JWT settings
- Environment variables
- Logging formats

_Note: Nothing domain-specific lives here_

### 10.3 API Layer (HTTP Contract): app/api/

```
app/api/
├── __init__.py
├── v1/
│   ├── __init__.py
│   ├── domain_routes.py
│   ├── domain_pack_routes.py
│   ├── health_routes.py
│   └── chat_routes.py        # Minimal placeholder (future)
```

**Responsibilities:**

- Request/response handling
- Validation via schemas
- Call application services
- **NO business logic**

**Example responsibility split:**

- `domain_routes.py` → create/select domain
- `domain_pack_routes.py` → edit entities, relationships, patterns

### 10.4 Core Logic (MOST IMPORTANT): app/core/

```
app/core/
├── domain_pack/
│   ├── loader.py
│   ├── serializer.py
│   ├── validator.py
│   ├── normalizer.py
│   └── diff.py
│
├── mutation/
│   ├── base.py
│   ├── entity_ops.py
│   ├── relationship_ops.py
│   ├── pattern_ops.py
│   ├── key_term_ops.py
│   └── dispatcher.py
│
├── parsing/
│   ├── json_parser.py
│   ├── yaml_parser.py
│   └── extractor.py
│
└── errors/
    ├── domain_errors.py
    └── validation_errors.py
```

**Why this matters:**

- ALL JSON/YAML mutations happen here
- Chatbot never edits files directly
- UI never edits files directly
- This layer validates schema, applies mutations deterministically, prevents corruption

### 10.5 Domain Models (Pure Business Objects): app/domain/

```
app/domain/
├── domain_pack.py
├── entity.py
├── attribute.py
├── relationship.py
├── extraction_pattern.py
└── key_term.py
```

**Purpose:**

- Represent domain concepts
- No FastAPI, no DB, no HTTP
- Used by core mutation engine, chatbot context, validation layer

### 10.6 Application Services (Use Cases): app/services/

```
app/services/
├── domain_service.py
├── domain_pack_service.py
├── import_export_service.py
├── validation_service.py
└── chat_context_service.py
```

**Responsibilities:**

- Orchestrate workflows
- Call core logic
- Handle transactions
- Enforce business rules

**Example:** "Update entity → validate → mutate → persist"

### 10.7 Persistence Layer (PostgreSQL): app/persistence/

```
app/persistence/
├── models/
│   ├── domain.py
│   ├── chat_session.py
│   └── user.py
│
├── repositories/
│   ├── domain_repository.py
│   ├── chat_session_repository.py
│   └── base.py
│
└── session.py
```

**Responsibilities:**

- ORM models
- DB access only
- No business logic
- JSONB storage for domain packs

### 10.8 Schemas (API Contracts): app/schemas/

```
app/schemas/
├── domain/
│   ├── create_domain.py
│   ├── update_domain.py
│   └── domain_response.py
│
├── domain_pack/
│   ├── entity_schema.py
│   ├── relationship_schema.py
│   ├── extraction_pattern_schema.py
│   └── full_domain_pack.py
│
├── chat/
│   ├── chat_request.py
│   ├── chat_response.py
│   └── operation_spec.py
│
└── common/
    ├── error.py
    └── pagination.py
```

**Purpose:**

- Strict request/response contracts
- UI safety
- Chatbot operation specs

### 10.9 Utilities: app/utils/

```
app/utils/
├── id_generator.py
├── time.py
├── file_helpers.py
└── schema_loader.py
```

Pure helpers. No logic.

### 10.10 Chatbot Module (Scaffold Only – NOT FOCUS NOW): app/chatbot/

```
app/chatbot/
├── graph/
│   ├── state.py
│   ├── nodes/
│   │   ├── intent_node.py
│   │   ├── context_node.py
│   │   ├── propose_mutation_node.py
│   │   └── confirmation_node.py
│   └── graph_builder.py
│
├── llm/
│   ├── client.py
│   └── prompts.py
│
├── operations/
│   ├── operation_schema.py
│   └── translator.py
│
└── session/
    ├── session_manager.py
    └── context_store.py
```

**Chatbot does NOT:**

- Mutate domain packs
- Access DB directly

**It only:** Emits operation specs → core mutation engine

### 10.11 Tests: app/tests/

```
app/tests/
├── unit/
│   ├── core/
│   ├── mutation/
│   └── validation/
│
├── integration/
│   ├── api/
│   └── database/
│
└── fixtures/
```

### 10.12 Migrations (Alembic): alembic/

```
alembic/
├── versions/
└── env.py
```

### 10.13 Frontend (Reference Only): frontend/

```
frontend/
├── src/
│   ├── pages/
│   ├── components/
│   ├── services/
│   └── types/
└── api/
```

## 11. Key Mental Model

- **Domain Pack** = single source of truth
- **Core Python logic** = only mutation authority
- **API** = orchestration
- **Chatbot** = decision maker, not executor
