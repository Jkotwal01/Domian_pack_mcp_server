# Domain Pack Authoring System - Backend

A comprehensive backend system for interactive, human-in-the-loop Domain Pack authoring using LangGraph, FastAPI, and PostgreSQL.

## Features

- 🤖 **LangGraph Orchestration**: Multi-node workflow with intent detection, context assembly, proposal generation, and HITL checkpoints
- 🔐 **Authentication & RBAC**: JWT-based auth with role-based access control (Editor, Reviewer, Admin)
- 📝 **Proposal System**: Human-in-the-loop workflow for all domain pack changes
- 📚 **Version Control**: Immutable version history with diffs and rollback support
- 🧠 **Memory Store**: Short-term and long-term memory with semantic search
- 🔌 **MCP Integration**: Deterministic YAML operations via Model Context Protocol
- 📊 **Audit Logging**: Complete audit trail for all significant events
- 🔍 **LangSmith Integration**: Full observability and tracing for LLM workflows

## Architecture

```
┌─────────────┐
│   Frontend  │
│   (React)   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│  ┌──────────────────────────────┐   │
│  │     API Layer (REST/WS)      │   │
│  └────────────┬─────────────────┘   │
│               ▼                     │
│  ┌──────────────────────────────┐   │
│  │   LangGraph Workflow         │   │
│  │  • Intent Detection          │   │
│  │  • Context Assembly          │   │
│  │  • Proposal Generation       │   │
│  │  • Human Checkpoint (HITL)   │   │
│  │  • MCP Router                │   │
│  │  • Commit Handler            │   │
│  └────────────┬─────────────────┘   │
│               ▼                     │
│  ┌──────────────────────────────┐   │
│  │   Service Layer              │   │
│  │  • ProposalManager           │   │
│  │  • VersionManager            │   │
│  │  • MemoryStore               │   │
│  │  • SessionManager            │   │
│  │  • AuthService               │   │
│  └────────────┬─────────────────┘   │
│               ▼                     │
│  ┌──────────────────────────────┐   │
│  │   Database (PostgreSQL)      │   │
│  │  • Users, Sessions           │   │
│  │  • Proposals, Versions       │   │
│  │  • Memory, Audit Logs        │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────┐
│   MCP Server    │
│  (YAML Ops)     │
└─────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+ (optional, for caching)
- Node.js 18+ (for MCP server)

### Installation

1. **Clone and navigate to backend**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**:
```bash
python scripts/init_db.py
```

6. **Run the server**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/api/v1/docs`
- OpenAPI Schema: `http://localhost:8000/api/v1/openapi.json`

## Configuration

Key environment variables in `.env`:

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=domain_pack_mcp
DB_USER=postgres
DB_PASSWORD=postgres

# LLM Provider
LLM_PROVIDER=groq  # or openai
LLM_API_KEY=your_api_key
LLM_MODEL=llama-3.3-70b-versatile

# Security
SECRET_KEY=your-secret-key-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=15

# LangSmith (optional)
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=domain-pack-authoring
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info

### Chat & Sessions
- `POST /api/v1/chat/sessions` - Create new conversation session
- `GET /api/v1/chat/sessions` - List active sessions
- `POST /api/v1/chat/sessions/{id}/messages` - Send message (triggers LangGraph)
- `WS /api/v1/chat/sessions/{id}/ws` - WebSocket for real-time updates

### Proposals
- `GET /api/v1/proposals/{id}` - Get proposal details
- `GET /api/v1/proposals/sessions/{id}/proposals` - List session proposals
- `POST /api/v1/proposals/{id}/confirm` - Confirm proposal (triggers commit)
- `POST /api/v1/proposals/{id}/reject` - Reject proposal

### Versions
- `GET /api/v1/versions/domain-packs/{id}/versions` - List all versions
- `GET /api/v1/versions/{id}` - Get version details
- `GET /api/v1/versions/{id}/diff` - Get version diff
- `POST /api/v1/versions/domain-packs/{id}/rollback` - Create rollback

## Development

### Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # Auth endpoints
│   │       ├── chat.py          # Chat endpoints
│   │       ├── proposals.py     # Proposal endpoints
│   │       ├── versions.py      # Version endpoints
│   │       └── router.py        # API router
│   ├── core/
│   │   ├── config.py            # Settings
│   │   └── logging.py           # Logging setup
│   ├── db/
│   │   ├── models.py            # SQLAlchemy models
│   │   └── session.py           # DB session management
│   ├── langgraph/
│   │   ├── state.py             # State definition
│   │   ├── nodes.py             # Workflow nodes
│   │   └── workflow.py          # Workflow assembly
│   ├── schemas/
│   │   └── __init__.py          # Pydantic schemas
│   ├── services/
│   │   ├── auth_service.py      # Authentication
│   │   ├── proposal_manager.py  # Proposal lifecycle
│   │   ├── version_manager.py   # Version control
│   │   ├── memory_store.py      # Memory management
│   │   ├── session_manager.py   # Session management
│   │   └── mcp_client.py        # MCP integration
│   └── main.py                  # FastAPI app
├── scripts/
│   └── init_db.py               # DB initialization
├── requirements.txt
└── .env.example
```

### Running Tests

```bash
pytest tests/ -v
```

### Database Migrations

Using Alembic:

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## LangGraph Workflow

The system uses a sophisticated LangGraph workflow:

1. **Intent Detection**: Analyzes user message to detect intent (add_field, remove_field, etc.)
2. **Context Assembly**: Gathers current snapshot, memories, and relevant context
3. **Proposal Generation**: LLM generates structured proposal with operations
4. **Human Checkpoint**: Pauses for user confirmation (HITL)
5. **MCP Router**: Routes operations to MCP server for deterministic execution
6. **Commit Handler**: Creates new version and updates database

## Security

- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- Password hashing with bcrypt
- CORS configuration
- Rate limiting (configurable)
- Audit logging for all significant events

## Observability

- Structured JSON logging
- LangSmith integration for LLM tracing
- Prometheus metrics (planned)
- Health check endpoints

## Production Deployment

### Using Docker

```bash
docker build -t domain-pack-backend .
docker run -p 8000:8000 --env-file .env domain-pack-backend
```

### Using Docker Compose

```bash
docker-compose up -d
```

### Environment Considerations

- Set `DEBUG=false` in production
- Use strong `SECRET_KEY`
- Configure proper CORS origins
- Enable HTTPS
- Set up database connection pooling
- Configure Redis for session storage
- Enable rate limiting
- Set up monitoring and alerting

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.
