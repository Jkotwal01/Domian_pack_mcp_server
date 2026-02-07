# Quick Start Guide - Backend

## TL;DR (5 Minutes Setup)

### 1. Install Prerequisites
- Python 3.11+
- PostgreSQL 14+

### 2. Setup Database
```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE domain_pack_mcp;
\q
```

### 3. Install Backend
```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example config
cp .env.example .env

# Edit .env and set:
# - DB_PASSWORD (your PostgreSQL password)
# - GROQ_API_KEY (get free key from https://console.groq.com/)
# - SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
```

### 5. Initialize Database
```bash
python scripts/init_db.py
```

### 6. Run Server
```bash
uvicorn app.main:app --reload
```

### 7. Test
Visit: http://localhost:8000/api/v1/docs

**Default Login:**
- Email: `admin@example.com`
- Password: `admin123`

---

## Detailed Setup

See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for complete instructions.

## Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready

# Verify credentials in .env match your PostgreSQL setup
```

### Module Not Found
```bash
# Make sure virtual environment is activated
.venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

## API Endpoints

Once running, access:
- **API Docs**: http://localhost:8000/api/v1/docs
- **Health Check**: http://localhost:8000/health
- **Root**: http://localhost:8000/

## Next Steps

1. Start frontend: `cd ../frontend && npm run dev`
2. Access app: http://localhost:5173
3. Login with admin credentials
