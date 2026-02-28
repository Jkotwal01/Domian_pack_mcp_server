# Domain Pack Generator - Backend User Guide

FastAPI + LangGraph backend for conversational domain pack configuration. This service provides robust API endpoints for authentication, domain management, and an AI-powered chatbot to help you build domain knowledge graphs.

## 📋 Prerequisites
- **Python**: 3.11 or higher
- **PostgreSQL**: 14 or higher
- **OpenAI API Key**: Required for LangGraph AI features

---

## 🚀 Quick Start (Recommended)

The easiest way to get started on Windows is using the automated setup script:

```powershell
cd backend
.\setup.ps1
```

**This script will:**
1. Create a virtual environment (`.venv`)
2. Install all required dependencies via `pip`
3. Create a `.env` file from the example template
4. Guide you through the database setup process

---

## 🛠️ Manual Installation

If you prefer to set up the environment manually:

### 1. Virtual Environment & Dependencies
```bash
# Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Environment Variables
Copy the example environment file and add your credentials:
```bash
cp .env.example .env
```
**Required fields in `.env`:**
- `DATABASE_URL`: Connection string (e.g., `postgresql://user:pass@localhost:5432/db`)
- `SECRET_KEY`: Security token (generate with `openssl rand -hex 32`)
- `OPENAI_API_KEY`: Your OpenAI API key

---

## 🗄️ Database Setup

### 1. Automated Setup
Run the database script to create the DB and all required tables/indexes:
```powershell
.\setup_database.ps1
```

### 2. Manual Setup
```bash
# Create PostgreSQL database
createdb domain_pack_db

# Run initialization script for tables and schemas
psql -d domain_pack_db -f init_db.sql

# Apply any pending migrations
alembic upgrade head
```

---

## 🏃 Running the Application

1. **Activate the Environment:**
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
2. **Start the Server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### 📚 API Documentation
Once the server is running, you can access interactive documentation at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## ⚒️ Common Commands

| Task | Command |
| :--- | :--- |
| **Activate Venv** | `.venv\Scripts\Activate.ps1` (Win) or `source .venv/bin/activate` (Unix) |
| **Start Server** | `uvicorn app.main:app --reload` |
| **Run Tests** | `pytest` |
| **New Migration** | `alembic revision --autogenerate -m "description"` |
| **Apply Migrations** | `alembic upgrade head` |
| **Format Code** | `black .` |
| **Lint Check** | `ruff check .` |

---

## 📂 Project Structure

```
backend/
├── app/
│   ├── api/          # API routes (Auth, Domains, Chat)
│   ├── models/       # SQLAlchemy database models
│   ├── schemas/      # Pydantic validation schemas
│   ├── services/     # Business logic & services
│   ├── langgraph/    # LangGraph AI state & nodes
│   └── utils/        # Security, templates & helpers
├── alembic/          # Database migration history
├── init_db.sql       # Raw SQL schema initialization
├── setup.ps1         # Automated environment setup
└── setup_database.ps1 # Automated database setup
```

---

## 🧪 Testing
Run the test suite using `pytest`:
```bash
pytest test_api.py
```

---

## 🛠️ API Raw JSON Payloads

Use these payloads for testing the API via Postman, cURL, or other tools. All protected routes require an `Authorization: Bearer <token>` header.

### 1. Authentication
**Signup (`POST /auth/signup`)**
```json
{
  "email": "user@example.com",
  "password": "strongpassword123"
}
```

**Login (`POST /auth/login`)**
```json
{
  "email": "user@example.com",
  "password": "strongpassword123"
}
```

### 2. Domain Management
**Create Domain (`POST /domains`)**
```json
{
  "name": "Healthcare Domain",
  "description": "Medical knowledge graph config",
  "version": "1.0.0"
}
```

**Update Domain (`PUT /domains/{id}`)**
*All fields are optional*
```json
{
  "name": "Updated Domain Name",
  "description": "Updated description",
  "version": "1.1.0",
  "config_json": {
    "entities": [],
    "relationships": [],
    "extraction_patterns": [],
    "key_terms": []
  }
}
```

### 3. Chat & AI Sessions
**Start/Get Active Session (`POST /chat/sessions`)**
```json
{
  "domain_config_id": "YOUR_DOMAIN_ID_HERE"
}
```

**Send Message to AI (`POST /chat/sessions/{id}/message`)**
```json
{
  "message": "Add an entity called 'Patient' with attributes 'name' and 'age'."
}
```

---

## 🏁 Next Steps
1. **Register**: Create a user account at `/auth/signup`.
2. **Login**: Authenticate at `/auth/login` to receive your JWT token.
3. **Configure**: Start managing your domain packs or use the chat interface to build one conversationally! 🚀

---

## 🚀 Future Optimization: Reducing LLM Token Overhead

**Goal**: Reduce the `generate_patch` node's input token usage (currently ~1,676 tokens) by roughly 40-50% by splitting the monolithic 59-operation schema into smaller, specialized models.

### Specialized Patch Schema Optimization Plan

#### 1. Refactor Schemas in `app/schemas/patch.py`
Break down `PatchOperation` into specialized sub-models:
- **DomainPatchOperation**: 3 top-level operations.
- **EntityPatchOperation**: Operations for entities, attributes, synonyms, and examples.
- **RelationshipPatchOperation**: Operations for relationships and their attributes.
- **ExtractionPatchOperation**: Operations for regex patterns.
- **KeyTermPatchOperation**: Operations for vocabulary.

#### 2. Update `generate_patch_node` in `app/dp_chatbot_module/nodes.py`
1. Read `state["intent"]`.
2. Map the intent to the corresponding specialized schema (e.g., `entity_operation` -> `EntityPatchList`).
3. Call `llm.with_structured_output(SelectedModel)`.
4. **Benefit**: The LLM receives a metadata schema for 3-15 operations instead of 59, saving hundreds of tokens per call.

#### 3. Verification
- **Token Count**: Compare `generate_patch` node tokens in the Monitoring dashboard before and after. Target: 500-700 tokens saved.
- **Functional Test**: Verify all operations (add/delete/edit) still function correctly across all categories.
