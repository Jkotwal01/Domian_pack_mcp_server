# FastAPI-First Domain Pack Backend

## 🎯 Architecture Overview

This backend implements a **FastAPI-first architecture** with embedded core logic from the MCP server. The LLM is used **ONLY** for intent extraction (natural language → structured operations), while the backend remains fully deterministic and authoritative.

### Key Principles

✅ **FastAPI is the only backend** - No MCP server, no MCP tools exposed to LLM  
✅ **Reuse ALL core logic** - Schema validation, operations, versioning, diff calculation  
✅ **LLM for intent ONLY** - Translates user intent to structured operations  
✅ **Backend is deterministic** - All operations are pure, validated, and versioned  
✅ **PostgreSQL for versioning** - Immutable version storage with rollback support  
✅ **Real-time streaming** - Server-Sent Events (SSE) for progress updates

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   │
│   ├── api/v1/
│   │   ├── router.py              # API router aggregator
│   │   └── endpoints/
│   │       ├── sessions.py        # Session management
│   │       ├── chat.py            # Natural language interface
│   │       ├── operations.py      # Direct operations
│   │       ├── versions.py        # Version management
│   │       ├── rollback.py        # Rollback functionality
│   │       └── export.py          # Export functionality
│   │
│   ├── core/                      # MCP CORE (unchanged)
│   │   ├── db.py                  # PostgreSQL versioning
│   │   ├── schema.py              # JSON Schema validation
│   │   ├── operations.py          # Pure operations
│   │   ├── utils.py               # Parse/serialize
│   │   └── version_manager.py     # Version bumping
│   │
│   ├── services/
│   │   ├── llm_intent.py          # LLM intent extraction
│   │   ├── intent_guard.py        # Confirmation logic
│   │   └── streaming.py           # SSE streaming service
│   │
│   └── models/
│       └── api_models.py          # Pydantic DTOs
│
├── scripts/
│   └── init_db.py                 # Database initialization
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 3. Initialize Database

Make sure PostgreSQL is running, then:

```bash
python scripts/init_db.py
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

---

## 🔄 Execution Flow

### 1. Upload → Create Session

```
User uploads YAML/JSON
  ↓
Backend: detect type → parse → validate → store version 1
  ↓
Return: session_id + tools list
```

### 2. Natural Language → Intent

```
User: "Add Attorney entity"
  ↓
Backend: load schema → send to LLM with context
  ↓
LLM: returns structured operation
  ↓
Backend: store pending intent
  ↓
Return: intent summary + proposed operation
```

### 3. Confirm → Apply

```
User: confirms operation
  ↓
Backend: load version → parse → validate → apply operation → bump version → validate → diff → store
  ↓
Return: new version + diff
```

### 4. Direct Operation

```
User: sends operation directly
  ↓
Backend: same pipeline as confirm (skip LLM)
  ↓
Return: new version + diff
```

All operations are:
- ✅ Deterministic
- ✅ Validated (pre and post)
- ✅ Versioned (immutable)
- ✅ Diffed (auditable)
- ✅ Rollbackable (creates new version)

---

## 📡 API Endpoints

### Sessions

- `POST /api/v1/sessions` - Create session from uploaded file
- `GET /api/v1/sessions/{id}` - Get session info
- `DELETE /api/v1/sessions/{id}` - Delete session

### Chat (Natural Language)

- `POST /api/v1/chat/intent` - Extract intent from natural language
- `GET /api/v1/chat/intent/stream/{session_id}` - SSE stream for intent progress
- `POST /api/v1/chat/confirm` - Confirm and apply operation

### Operations (Direct)

- `POST /api/v1/operations/apply` - Apply operation directly
- `GET /api/v1/operations/stream/{operation_id}` - SSE stream for operation progress
- `POST /api/v1/operations/batch` - Apply batch operations
- `GET /api/v1/operations/tools` - List available tools

### Versions

- `GET /api/v1/versions/{session_id}` - List all versions
- `GET /api/v1/versions/{session_id}/{version}` - Get specific version

### Rollback

- `POST /api/v1/rollback` - Rollback to previous version

### Export

- `GET /api/v1/export/{session_id}?format=yaml|json` - Export domain pack
- `GET /api/v1/export/{session_id}/download?format=yaml|json` - Download as file

---

## 🌊 Streaming Progress Updates

The backend supports real-time progress updates via Server-Sent Events (SSE):

### Event Types

- `status` - General status updates
- `validation` - Validation steps
- `llm_chunk` - LLM response tokens (streamed)
- `diff` - Diff calculation results
- `complete` - Operation completed
- `error` - Error occurred

### Example Usage

```javascript
// Connect to SSE stream
const eventSource = new EventSource('/api/v1/chat/intent/stream/session-id');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`[${data.type}] ${data.message} (${data.progress_percent}%)`);
};

// Then send the request
fetch('/api/v1/chat/intent', {
  method: 'POST',
  body: JSON.stringify({ session_id: 'session-id', message: 'Add Attorney entity' })
});
```

---

## 🔧 Available Operations

1. **add** - Add a value to a path (for dicts: adds new key, for arrays: appends)
2. **replace** - Replace value at path
3. **delete** - Delete value at path
4. **update** - Update multiple fields in an object
5. **merge** - Merge objects or arrays
6. **add_unique** - Add value only if it doesn't exist
7. **assert** - Assert a condition (validation)

---

## 🗄️ Database Schema

### sessions table

- `id` (UUID, primary key)
- `file_type` (varchar)
- `current_version` (integer)
- `metadata` (jsonb)
- `created_at` (timestamp)

### versions table

- `id` (serial, primary key)
- `session_id` (UUID, foreign key)
- `version` (integer)
- `content` (jsonb)
- `diff` (jsonb)
- `reason` (text)
- `created_at` (timestamp)

---

## 🔐 Environment Variables

See `.env.example` for all required configuration:

- **Database**: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- **LLM**: `OPENAI_API_KEY`, `OPENAI_MODEL`
- **Intent Guard**: `INTENT_TIMEOUT_SECONDS`

---

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# Test with sample file
curl -X POST http://localhost:8000/api/v1/sessions \
  -F "file=@../mcp_server/sample.yaml"
```

---

## 📝 License

MIT
