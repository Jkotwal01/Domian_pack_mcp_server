# MCP Client with Groq

A simple MCP (Model Context Protocol) client that uses **Groq** for ultra-fast LLM responses.

## Features

- ✅ **Groq Integration** - 10-100x faster than GPT-4
- ✅ **MCP Tool Calling** - Full support for domain pack operations
- ✅ **Interactive Chat** - Command-line interface
- ✅ **uv Package Manager** - Fast dependency management

## Setup

### 1. Install Dependencies

All dependencies are managed by `uv`:

```bash
uv add groq python-dotenv mcp
```

### 2. Configure Environment

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run the Client

```bash
uv run main.py ../domain-pack-mcp/main.py
```

## Usage

Once started, you can chat with the MCP server:

```
MCP Client with Groq Started!
Type your queries or 'quit' to exit.

Query: Create a Legal domain pack with version 1.0.0

[Called create_session]
✅ Created Legal domain pack successfully!
Session ID: abc-123-def-456
Version: 1

Query: Add an Attorney entity

Do you want to proceed? (yes/no)

Query: yes

[Called apply_change]
✅ Added Attorney entity!
New version: 2

Query: quit
```

## How It Works

1. **Connect to MCP Server** - Starts the domain-pack-mcp server via stdio
2. **List Available Tools** - Gets all MCP tools (create_session, apply_change, etc.)
3. **Chat with Groq** - Sends user query to Groq with tool schemas
4. **Execute Tools** - Groq decides which tools to call
5. **Call MCP Tools** - Executes tools via MCP session
6. **Return Results** - Groq formats the final response

## Model

Using **llama-3.3-70b-versatile**:
- ⚡ Ultra-fast responses (0.5-2 seconds)
- 🧠 Excellent reasoning
- 🔧 Full tool calling support
- 💰 Very affordable

## Commands

**Start client:**
```bash
uv run main.py <path_to_mcp_server>
```

**Example:**
```bash
uv run main.py ../domain-pack-mcp/main.py
```

## Architecture

```
User Input
    ↓
Groq LLM (llama-3.3-70b-versatile)
    ↓
Tool Calls
    ↓
MCP Client Session (stdio)
    ↓
Domain Pack MCP Server
    ↓
Tool Execution (PostgreSQL)
    ↓
Results back to Groq
    ↓
Formatted Response
```

## Dependencies

Automatically installed via `uv`:

- `groq` - Groq API client
- `python-dotenv` - Environment variable management
- `mcp` - Model Context Protocol SDK
- `jsonschema` - Schema validation
- `httpx` - HTTP client

## Comparison

| Feature | This Client | Previous Backend |
|---------|-------------|------------------|
| LLM | Groq | Groq/OpenAI/Anthropic |
| Speed | ⚡ 0.5-2s | ⚡ 0.5-2s |
| Interface | CLI | REST API |
| Dependencies | uv | pip + venv |
| Use Case | Testing | Production API |

## Tips

- Type `quit` to exit
- Groq is 10-100x faster than GPT-4
- All MCP operations are versioned and immutable
- Session IDs persist across versions

## Troubleshooting

**Error: "No module named 'groq'"**
```bash
uv add groq
```

**Error: "GROQ_API_KEY not found"**
- Create `.env` file with your Groq API key
- Get key from: https://console.groq.com

**Error: "Server script must be .py or .js"**
- Make sure you're pointing to the MCP server's main.py

## Next Steps

- Add web interface (FastAPI)
- Stream responses
- Save conversation history
- Add more MCP servers

---

**Ready to chat with your domain packs via Groq!** 🚀
