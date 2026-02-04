# Domain Pack Authoring System - Complete Backend Setup Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Database Setup](#database-setup)
4. [Environment Configuration](#environment-configuration)
5. [Running the Backend](#running-the-backend)
6. [API Documentation](#api-documentation)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

1. **Python 3.11+**
   - Download: https://www.python.org/downloads/
   - Verify installation:
     ```bash
     python --version
     # Should show: Python 3.11.x or higher
     ```

2. **PostgreSQL 14+**
   - **Windows**: Download from https://www.postgresql.org/download/windows/
   - **macOS**: `brew install postgresql@14`
   - **Linux**: `sudo apt-get install postgresql-14`
   
   - Verify installation:
     ```bash
     psql --version
     # Should show: psql (PostgreSQL) 14.x or higher
     ```

3. **Redis 7+ (Optional but Recommended)**
   - **Windows**: Download from https://github.com/microsoftarchive/redis/releases
   - **macOS**: `brew install redis`
   - **Linux**: `sudo apt-get install redis-server`
   
   - Verify installation:
     ```bash
     redis-cli --version
     # Should show: redis-cli 7.x or higher
     ```

4. **Git**
   - Download: https://git-scm.com/downloads
   - Verify: `git --version`

---

## Installation

### Step 1: Navigate to Backend Directory

```bash
cd d:\My Code\Enable\domain_pack_Gen\domain-pack-mcp\backend
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

### Step 3: Upgrade pip

```bash
python -m pip install --upgrade pip
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- SQLAlchemy (ORM)
- Alembic (database migrations)
- LangChain & LangGraph (LLM orchestration)
- PostgreSQL drivers
- Redis client
- And all other dependencies

**Expected output:** ~50+ packages installed

---

## Database Setup

### Step 1: Start PostgreSQL Service

**Windows:**
```bash
# Open Services (services.msc) and start "postgresql-x64-14"
# OR use pg_ctl
pg_ctl -D "C:\Program Files\PostgreSQL\14\data" start
```

**macOS:**
```bash
brew services start postgresql@14
```

**Linux:**
```bash
sudo systemctl start postgresql
```

### Step 2: Create Database

**Option A: Using psql (Recommended)**

```bash
# Login to PostgreSQL
psql -U postgres

# In psql prompt:
CREATE DATABASE domain_pack_mcp;
CREATE USER domain_pack_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE domain_pack_mcp TO domain_pack_user;
\q
```

**Option B: Using pgAdmin**

1. Open pgAdmin
2. Right-click "Databases" → "Create" → "Database"
3. Name: `domain_pack_mcp`
4. Owner: `postgres` (or create new user)
5. Click "Save"

### Step 3: Verify Database Connection

```bash
psql -U postgres -d domain_pack_mcp -c "SELECT version();"
```

Should display PostgreSQL version information.

---

## Environment Configuration

### Step 1: Create .env File

Copy the example environment file:

```bash
cp .env.example .env
```

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

### Step 2: Configure .env File

Open `.env` in your text editor and update the following:

```env
# ============================================
# DATABASE CONFIGURATION
# ============================================
DB_HOST=localhost
DB_PORT=5432
DB_NAME=domain_pack_mcp
DB_USER=postgres                    # Change to your PostgreSQL user
DB_PASSWORD=your_password_here      # Change to your PostgreSQL password

# ============================================
# LLM PROVIDER CONFIGURATION
# ============================================
# Choose ONE provider: openai or groq
LLM_PROVIDER=groq                   # or "openai"

# For Groq (Recommended - Free tier available)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# For OpenAI (Alternative)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# ============================================
# SECURITY CONFIGURATION
# ============================================
# Generate a secure secret key:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# ============================================
# REDIS CONFIGURATION (Optional)
# ============================================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=                     # Leave empty if no password

# ============================================
# LANGSMITH CONFIGURATION (Optional)
# ============================================
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_TRACING=false             # Set to "true" to enable
LANGSMITH_PROJECT=domain-pack-authoring

# ============================================
# APPLICATION CONFIGURATION
# ============================================
PROJECT_NAME=Domain Pack Authoring API
DEBUG=true                          # Set to "false" in production
API_V1_STR=/api/v1
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# ============================================
# RATE LIMITING (Optional)
# ============================================
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
```

### Step 3: Get API Keys

#### Groq API Key (Recommended - Free)

1. Visit: https://console.groq.com/
2. Sign up for free account
3. Navigate to "API Keys"
4. Click "Create API Key"
5. Copy the key and paste into `.env` as `GROQ_API_KEY`

#### OpenAI API Key (Alternative)

1. Visit: https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key and paste into `.env` as `OPENAI_API_KEY`

#### LangSmith API Key (Optional - For Tracing)

1. Visit: https://smith.langchain.com/
2. Sign up for account
3. Go to Settings → API Keys
4. Create new API key
5. Copy and paste into `.env` as `LANGSMITH_API_KEY`

### Step 4: Generate Secret Key

Run this command to generate a secure secret key:

**Windows (PowerShell):**
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**macOS/Linux:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste it as `SECRET_KEY` in `.env`

---

## Running the Backend

### Step 1: Initialize Database

Run the database initialization script:

```bash
python scripts/init_db.py
```

**Expected output:**
```
INFO - Starting database initialization...
INFO - Creating database tables...
INFO - Database tables created successfully
INFO - Admin user created: admin@example.com / admin123
INFO - Database initialization complete!
```

This creates:
- All database tables (Users, Sessions, DomainPacks, Versions, Proposals, MemoryEntries, AuditLogs)
- Default admin user

**Default Admin Credentials:**
- Email: `admin@example.com`
- Password: `admin123`
- **⚠️ IMPORTANT: Change this password in production!**

### Step 2: Start Redis (Optional)

If using Redis for caching:

**Windows:**
```bash
redis-server
```

**macOS:**
```bash
brew services start redis
```

**Linux:**
```bash
sudo systemctl start redis
```

### Step 3: Start the Backend Server

**Development Mode (with auto-reload):**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production Mode:**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Expected output:**
```
INFO:     Starting Domain Pack Authoring API...
INFO:     Database initialized
INFO:     LangSmith tracing enabled
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 4: Verify Backend is Running

Open your browser and visit:

1. **API Root**: http://localhost:8000/
   - Should show welcome message

2. **Health Check**: http://localhost:8000/health
   - Should return: `{"status": "healthy", "service": "domain-pack-authoring-api"}`

3. **API Documentation**: http://localhost:8000/api/v1/docs
   - Interactive Swagger UI with all endpoints

4. **OpenAPI Schema**: http://localhost:8000/api/v1/openapi.json
   - Raw OpenAPI specification

---

## API Documentation

### Available Endpoints

#### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get JWT token |
| GET | `/auth/me` | Get current user info |

#### Chat & Sessions (`/api/v1/chat`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat/sessions` | Create new session |
| GET | `/chat/sessions` | List all sessions |
| GET | `/chat/sessions/{id}` | Get session details |
| POST | `/chat/sessions/{id}/messages` | Send message (triggers LangGraph) |
| WS | `/chat/sessions/{id}/ws` | WebSocket connection |

#### Proposals (`/api/v1/proposals`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/proposals/{id}` | Get proposal details |
| GET | `/proposals/sessions/{id}/proposals` | List session proposals |
| POST | `/proposals/{id}/confirm` | Confirm proposal |
| POST | `/proposals/{id}/reject` | Reject proposal |

#### Versions (`/api/v1/versions`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/versions/domain-packs/{id}/versions` | List all versions |
| GET | `/versions/{id}` | Get version details |
| GET | `/versions/{id}/diff` | Get version diff |
| POST | `/versions/domain-packs/{id}/rollback` | Create rollback |

### Testing with cURL

#### Register User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "testpass123",
    "role": "EDITOR"
  }'
```

#### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### Get Current User
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Error

**Error:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions:**
- Verify PostgreSQL is running: `pg_isready`
- Check database credentials in `.env`
- Ensure database exists: `psql -U postgres -l`
- Check PostgreSQL logs

#### 2. Module Not Found Error

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solutions:**
- Activate virtual environment: `.venv\Scripts\activate`
- Reinstall dependencies: `pip install -r requirements.txt`
- Verify Python version: `python --version` (should be 3.11+)

#### 3. Port Already in Use

**Error:**
```
OSError: [Errno 98] Address already in use
```

**Solutions:**
- Change port: `uvicorn app.main:app --port 8001`
- Kill existing process:
  - Windows: `netstat -ano | findstr :8000` then `taskkill /PID <PID> /F`
  - Linux/Mac: `lsof -ti:8000 | xargs kill -9`

#### 4. LLM API Key Error

**Error:**
```
AuthenticationError: Invalid API key
```

**Solutions:**
- Verify API key in `.env` is correct
- Check LLM_PROVIDER matches your key (groq or openai)
- Ensure no extra spaces in `.env` file
- Regenerate API key if needed

#### 5. Redis Connection Error

**Error:**
```
redis.exceptions.ConnectionError
```

**Solutions:**
- Start Redis: `redis-server`
- Verify Redis is running: `redis-cli ping` (should return "PONG")
- Check REDIS_HOST and REDIS_PORT in `.env`
- Redis is optional - comment out Redis config if not using

### Logs

Check application logs:
```bash
# View app.log
cat app.log

# Tail logs in real-time
tail -f app.log
```

### Database Migrations

If you need to modify database schema:

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Production Deployment

### Environment Variables for Production

```env
DEBUG=false
SECRET_KEY=<strong-random-key>
ALLOWED_ORIGINS=https://yourdomain.com
LANGSMITH_TRACING=true
```

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t domain-pack-backend .
docker run -p 8000:8000 --env-file .env domain-pack-backend
```

### Using Gunicorn (Production WSGI)

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Next Steps

1. ✅ Backend is running
2. Start frontend: `cd ../frontend && npm run dev`
3. Access application: http://localhost:5173
4. Login with admin credentials
5. Explore the API documentation: http://localhost:8000/api/v1/docs

## Support

For issues or questions:
- Check logs: `app.log`
- Review API docs: http://localhost:8000/api/v1/docs
- Verify environment configuration: `.env`

---

**🎉 Congratulations! Your backend is now set up and running!**
