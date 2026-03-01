# Domain Pack Generator

> Build and manage **Knowledge Graph Domain Packs** through conversation. Describe what you want in plain English — the AI understands your intent and safely applies structured changes to your configuration.

## Documentation

| Document | Description |
|---|---|
| [backend/README.md](./backend/README.md) | Full backend architecture, chatbot node-by-node walkthrough, patch applier reference, and developer setup |
| [frontend/README.md](./frontend/README.md) | Frontend setup guide and project structure |

---

## What Is This?

**Domain Pack Generator** is a full-stack application for creating and editing **Domain Packs** — structured JSON/YAML configurations that define a knowledge graph's entities, relationships, extraction patterns, and vocabulary.

Instead of manually editing JSON, you **chat with an AI assistant** that translates your natural language into precise, validated configuration changes. The backend enforces safety, schema compliance, and versioning at every step.

---

## How It Works

```
You: "Add a Patient entity with name and age attributes."
         │
         ▼
   [AI understands intent]   ← GPT-4o-mini classifies your message
         │
         ▼
   [AI generates a patch]    ← Structured JSON patch plan is created
         │
         ▼
   [Python applies patch]    ← Pure deterministic code, no LLM involvement
         │
         ▼
   [Schema validates result] ← Pydantic checks the updated config
         │
         ▼
   [You confirm]             ← You review and approve the change
         │
         ▼
   [Config is saved]         ← Versioned and persisted to PostgreSQL
```

**The LLM never directly edits your data.** It only produces a plan. All mutations, validation, and storage are handled by deterministic Python backend logic.

---

## Key Features

| Feature | Description |
|---|---|
| 🤖 **AI Chat Interface** | Natural language domain pack editing — no JSON required |
| 🔒 **LLM-Safe Architecture** | LLM only classifies intent and generates patch plans; Python does all mutations |
| ✅ **Schema Validation** | Every change is validated against Pydantic schemas before being saved |
| 📊 **LLM Monitoring** | Per-node token usage and latency dashboard |
| 📁 **File Upload** | Upload existing YAML/JSON configs to seed the editor |
| 🔐 **Auth System** | JWT-based authentication; all data is user-scoped |

---

## Domain Pack Structure

A Domain Pack is a JSON document with four sections:

```json
{
  "name": "Healthcare Domain",
  "description": "Medical knowledge graph for clinical NLP",
  "version": "1.2.0",
  "entities": [
    {
      "name": "Patient",
      "type": "PATIENT",
      "description": "A person receiving medical care",
      "attributes": [
        { "name": "name", "description": "Patient full name", "examples": ["John Doe"] },
        { "name": "age",  "description": "Patient age in years", "examples": ["34"] }
      ],
      "synonyms": ["client", "individual"]
    }
  ],
  "relationships": [
    {
      "name": "TREATED_BY",
      "from": "PATIENT",
      "to": "DOCTOR",
      "description": "Links a patient to their treating physician",
      "attributes": []
    }
  ],
  "extraction_patterns": [
    {
      "pattern": "\\d{1,3} years? old",
      "entity_type": "PATIENT",
      "attribute": "age",
      "extract_full_match": true,
      "confidence": 0.95
    }
  ],
  "key_terms": ["diagnosis", "treatment", "prescription", "symptom"]
}
```

---

## Project Structure

```
domain-pack-mcp/
├── backend/        # FastAPI + LangGraph API server
│   └── README.md   # ← Full backend docs, chatbot deep-dive, setup guide
├── frontend/       # React + Vite SPA
│   └── README.md   # ← Full frontend docs, component reference, setup guide
└── templates/      # Pre-built domain pack YAML templates
```

---

## Quick Start

### 1. Start the Backend
```bash
cd backend
python -m venv .venv && .venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
# Configure .env with DATABASE_URL, SECRET_KEY, OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```
→ See [backend/README.md](./backend/README.md) for the full setup guide.

### 2. Start the Frontend
```bash
cd frontend
npm install
# Set VITE_API_BASE_URL=http://localhost:8000 in .env
npm run dev
```
→ See [frontend/README.md](./frontend/README.md) for the full setup guide.

### 3. Open the App
Visit [http://localhost:5173](http://localhost:5173), register an account, create a domain, and start chatting.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, React Router v6 |
| **Backend** | Python 3.11, FastAPI, LangGraph, LangChain |
| **AI** | OpenAI GPT-4o-mini (intent classification + patch generation) |
| **Database** | PostgreSQL 14+ with SQLAlchemy ORM + Alembic migrations |
| **Auth** | JWT (JSON Web Tokens) with bcrypt password hashing |


