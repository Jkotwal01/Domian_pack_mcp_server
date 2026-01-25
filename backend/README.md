
# Domain Pack Generator Backend

FastAPI backend for Domain Pack Generator, migrating logic from the original MCP server.

## Features
- **Session Management**: Create, retrive, delete sessions.
- **Versioning**: Immutable version history with diffs.
- **Deterministic Operations**: Add, update, delete, merge logic.
- **Strict Validation**: JSON Schema validation for domain packs.
- **Utilities**: YAML/JSON parsing and conversion.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file in `backend/app` or root:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=domain_pack_mcp
   DB_USER=postgres
   DB_PASSWORD=postgres
   ```

3. **Run Server**:
   You can run the server using `uvicorn` directly from the `backend` directory:
   ```bash
   # Make sure you are in the 'backend' directory
   cd backend
   
   # Run the server with hot-reload enabled
   python -m uvicorn app.main:app --reload
   ```
   
   The server will start at `http://localhost:8000`.

## API Documentation
- **Interactive Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Logs
- Application logs are output to the console (stdout).
- Logs are also persisted to `backend/app.log`.
- Log level is set to `INFO` by default.
