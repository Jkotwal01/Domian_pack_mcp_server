# Complete System Setup - Backend + Frontend

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                          │
│                   (React Frontend)                           │
│              http://localhost:5173                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP/WebSocket
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   FASTAPI BACKEND                            │
│              http://localhost:8000                           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Layer (REST)                        │   │
│  │  • /auth     - Authentication                        │   │
│  │  • /chat     - Sessions & Messages                   │   │
│  │  • /proposals - Proposal Management                  │   │
│  │  • /versions  - Version Control                      │   │
│  └────────────────┬─────────────────────────────────────┘   │
│                   │                                          │
│  ┌────────────────▼─────────────────────────────────────┐   │
│  │           LangGraph Workflow                         │   │
│  │  Intent → Context → Proposal → HITL → MCP → Commit  │   │
│  └────────────────┬─────────────────────────────────────┘   │
│                   │                                          │
│  ┌────────────────▼─────────────────────────────────────┐   │
│  │              Service Layer                           │   │
│  │  • ProposalManager  • VersionManager                 │   │
│  │  • MemoryStore      • SessionManager                 │   │
│  │  • AuthService      • MCPClient                      │   │
│  └────────────────┬─────────────────────────────────────┘   │
│                   │                                          │
│  ┌────────────────▼─────────────────────────────────────┐   │
│  │          Database Layer (SQLAlchemy)                 │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐      ┌────────▼────────┐
│   PostgreSQL   │      │   Redis Cache   │
│   Database     │      │   (Optional)    │
└────────────────┘      └─────────────────┘
```

## Complete Setup Checklist

### Backend Setup

- [ ] **Install Prerequisites**
  - [ ] Python 3.11+
  - [ ] PostgreSQL 14+
  - [ ] Redis 7+ (optional)

- [ ] **Database Setup**
  - [ ] Start PostgreSQL service
  - [ ] Create database: `domain_pack_mcp`
  - [ ] Note your PostgreSQL password

- [ ] **Backend Installation**
  ```bash
  cd backend
  python -m venv .venv
  .venv\Scripts\activate
  pip install -r requirements.txt
  ```

- [ ] **Environment Configuration**
  ```bash
  cp .env.example .env
  # Edit .env with your settings
  ```
  
  Required settings:
  - [ ] `DB_PASSWORD` - Your PostgreSQL password
  - [ ] `GROQ_API_KEY` - Get from https://console.groq.com/
  - [ ] `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

- [ ] **Initialize Database**
  ```bash
  python scripts/init_db.py
  ```

- [ ] **Start Backend**
  ```bash
  uvicorn app.main:app --reload
  ```

- [ ] **Verify Backend**
  - [ ] Visit http://localhost:8000/health
  - [ ] Visit http://localhost:8000/api/v1/docs

### Frontend Setup

- [ ] **Install Prerequisites**
  - [ ] Node.js 18+
  - [ ] npm or yarn

- [ ] **Frontend Installation**
  ```bash
  cd frontend
  npm install
  ```

- [ ] **Environment Configuration**
  - [ ] `.env` already configured with:
    - `VITE_API_URL=http://localhost:8000/api/v1`

- [ ] **Start Frontend**
  ```bash
  npm run dev
  ```

- [ ] **Verify Frontend**
  - [ ] Visit http://localhost:5173
  - [ ] See login page

### Test the System

- [ ] **Login**
  - Email: `admin@example.com`
  - Password: `admin123`

- [ ] **Navigate Dashboard**
  - [ ] See stats cards
  - [ ] Create new session

- [ ] **Test API**
  - [ ] Check http://localhost:8000/api/v1/docs
  - [ ] Try authentication endpoints

## Default Credentials

**Admin User:**
- Email: `admin@example.com`
- Password: `admin123`

⚠️ **IMPORTANT:** Change this password in production!

## URLs Reference

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | React application |
| Backend API | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/api/v1/docs | Swagger UI |
| Health Check | http://localhost:8000/health | Server health |

## Common Commands

### Backend

```bash
# Activate virtual environment
.venv\Scripts\activate

# Start server
uvicorn app.main:app --reload

# Initialize database
python scripts/init_db.py

# Run cleanup
python scripts/cleanup_legacy.py
```

### Frontend

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| Database connection error | Check PostgreSQL is running: `pg_isready` |
| Module not found | Activate venv: `.venv\Scripts\activate` |
| Port already in use | Use different port: `--port 8001` |
| LLM API error | Verify API key in `.env` |
| Frontend won't start | Run `npm install` again |

## File Structure

```
domain-pack-mcp/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Config, logging
│   │   ├── db/              # Database models
│   │   ├── langgraph/       # LangGraph workflow
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── main.py          # FastAPI app
│   ├── scripts/
│   │   ├── init_db.py       # Database setup
│   │   └── cleanup_legacy.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── SETUP_GUIDE.md       # Detailed setup
│   └── QUICKSTART.md        # Quick setup
│
└── frontend/
    ├── src/
    │   ├── api/             # Backend integration
    │   ├── components/      # React components
    │   ├── pages/           # Page components
    │   ├── stores/          # Zustand stores
    │   ├── App.jsx
    │   └── main.jsx
    ├── package.json
    ├── .env
    └── README.md
```

## Next Steps

1. ✅ Complete backend setup
2. ✅ Complete frontend setup
3. ✅ Test login functionality
4. 🔄 Implement Chat page
5. 🔄 Implement Proposals page
6. 🔄 Implement Versions page
7. 🔄 Add WebSocket support
8. 🔄 Write tests

## Support Documentation

- **Backend Setup**: `backend/SETUP_GUIDE.md`
- **Backend Quick Start**: `backend/QUICKSTART.md`
- **Backend README**: `backend/README.md`
- **Frontend README**: `frontend/README.md`
- **Implementation Plan**: See artifacts
- **Walkthroughs**: See artifacts

---

**🎉 You're all set! Happy coding!**
