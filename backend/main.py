"""
FastAPI Backend with Groq + MCP Integration
Connects React frontend to MCP server using Groq LLM
"""
import os
import sys
import logging
import time
from collections import defaultdict
from contextlib import asynccontextmanager, AsyncExitStack
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backend_events.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Backend")

# Metrics
session_stats = defaultdict(lambda: {"count": 0})

# Configuration
GROQ_MODEL = "llama-3.3-70b-versatile"
MCP_SERVER_PATH = "../domain-pack-mcp/main.py"

# Global MCP session
mcp_session: ClientSession | None = None
exit_stack: AsyncExitStack | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global mcp_session, exit_stack
    
    # Startup: Connect to MCP server
    print("Starting MCP server connection...", file=sys.stderr)
    exit_stack = AsyncExitStack()
    
    try:
        path = Path(MCP_SERVER_PATH).resolve()
        server_params = StdioServerParameters(
            command="uv",
            args=["--directory", str(path.parent), "run", path.name],
            env=None,
        )
        
        stdio_transport = await exit_stack.__aenter__()
        stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        mcp_session = await exit_stack.enter_async_context(ClientSession(stdio, write))
        await mcp_session.initialize()
        
        # List tools
        response = await mcp_session.list_tools()
        tools = [tool.name for tool in response.tools]
        print(f"MCP server connected with tools: {tools}", file=sys.stderr)
        
    except Exception as e:
        print(f"Failed to start MCP server: {e}", file=sys.stderr)
        raise
    
    yield  # App runs
    
    # Shutdown
    print("Stopping MCP server...", file=sys.stderr)
    if exit_stack:
        await exit_stack.aclose()


# Initialize FastAPI
app = FastAPI(
    title="Groq + MCP Backend",
    description="Backend connecting React frontend to MCP server via Groq",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    files: Optional[List[Dict[str, Any]]] = None
    session_id: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    response: str
    session_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "provider": "groq",
        "model": GROQ_MODEL,
        "mcp_connected": mcp_session is not None
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint with Groq + MCP tool integration
    """
    if not mcp_session:
        raise HTTPException(status_code=503, detail="MCP server not connected")
    
    print(f"DEBUG: Received chat request. Message: {request.message}")
    print(f"DEBUG: Files received: {request.files}")
    if request.files:
        for i, f in enumerate(request.files):
            print(f"DEBUG: File {i} name: {f.get('name')}, content_preview: {str(f.get('content'))[:50]}")
    
    try:
        # OPTIMIZATION: Verify session or file presence before calling LLM
        # If no session is active and no file is uploaded, return immediate instructions
        # without invoking the LLM (saves tokens and latency).
        if not request.session_id and not request.files:
            print("DEBUG: No session and no file. Skipping LLM.")
            return ChatResponse(
                response="""# Welcome to the Domain Pack Manager

**Significance of this System:**
This application is designed for **safe, file-driven management** of your domain packs. Unlike standard chat assistants, it strictly enforces a verified workflow to prevent hallucinations and ensure data integrity. It acts as a bridge between your intent and your codebase, requiring explicit confirmation for every change.

**Complete Workflow:**
1.  📄 Upload: You MUST start by uploading a YAML or JSON domain pack file.
2.  🧠 Plan: The AI analyzes your file and proposes a plan.
3.  ✅ Confirm: You explicitly approve or reject the plan.
4.  🛠️ Execute: The AI uses specialized tools to apply changes safely.
5.  📜 Version: Every change is versioned, allowing for instant rollbacks.

**To Get Started:**
Please **upload your YAML or JSON file** now. I cannot create a session from empty text.""",
                session_id=None,
                tool_calls=[]
            )

        # Build messages
        messages = request.conversation_history or []
        
        # Add system message if not present
        if not messages or messages[0].get("role") != "system":
            system_msg = {
                "role": "system",
                "content": (
                    "You are a Domain Pack Management Assistant acting as an interface to an MCP Server.\n"
                    "Your specialized role is to translate natural language intents into structured MCP tool calls.\n\n"
                    "CRITICAL RULES:\n"
                    "1. SESSION CREATION RULE: You can ONLY create a session when the user UPLOADS a YAML or JSON file.\n"
                    "   - If user asks to create a session WITHOUT a file, REFUSE and ask them to upload a file first.\n"
                    "   - NEVER create a session from scratch or empty templates.\n"
                    "   - The 'initial_content' for create_session MUST come from the uploaded file content.\n"
                    "2. FILE EDITING RULE: NEVER edit the file content yourself. You MUST use the provided MCP tools.\n"
                    "3. STRICT WORKFLOW:\n"
                    "   a) User uploads file -> Call 'create_session' with file content.\n"
                    "      - After creating, SHOW the available tools list.\n"
                    "   b) User requests changes -> INTERPRET intent but DO NOT execute yet.\n"
                    "      - ASK: 'Do you want to proceed with these changes? (Proceed/Reject)'\n"
                    "   c) User confirms (Proceed) -> Execute using 'apply_change' or 'apply_batch'.\n"
                    "   d) User rejects -> Do nothing.\n"
                    "   e) Always offer 'rollback' if needed.\n\n"
                    "IMPORTANT: When calling create_session, the 'initial_content' MUST be a VERBATIM COPY of the raw string content provided in the 'UPLOADED FILES' section.\n"
                    "   - DO NOT summarize.\n"
                    "   - DO NOT fix syntax.\n"
                    "   - DO NOT reformat.\n"
                    "   - DO NOT hallucinate properties not present in the source.\n"
                    "   - If the file content is 'X', the 'initial_content' argument MUST be 'X'.\n\n"
                    "Always be transparent about which tool you are calling."
                )
            }
            messages.insert(0, system_msg)
        
        # Add user message
        # Add user message with strictly demarcated file content
        user_content = request.message
        if request.files:
            file_section = "\n\n--- START RAW FILE CONTENT (PASS VERBATIM) ---\n"
            for f in request.files:
                fname = f.get('name', 'unknown')
                fcontent = f.get('content', '')
                file_section += f"Filename: {fname}\nContent:\n{fcontent}\n\n"
            file_section += "--- END RAW FILE CONTENT ---\n"
            user_content += file_section

        user_msg = {"role": "user", "content": user_content}
        if request.session_id:
            user_msg["content"] += f"\n[Current session_id: {request.session_id}]"
        messages.append(user_msg)
        
        # Get MCP tools
        tools_response = await mcp_session.list_tools()
        available_tools = []
        for tool in tools_response.tools:
            available_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })
        
        # Call Groq
        logger.info(f"Sending request to LLM. Messages count: {len(messages)}, Tools count: {len(available_tools)}")
        start_time = time.time()
        try:
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                tools=available_tools,
                tool_choice="auto",
                max_tokens=512
            )
            
            # Metrics recording
            end_time = time.time()
            duration = end_time - start_time
            
            # Use provided session_id or fallback to 'pending'
            stats_key = request.session_id or "pending_session"
            session_stats[stats_key]["count"] += 1
            current_count = session_stats[stats_key]["count"]
            
            logger.info(f"Session {stats_key} | Call #{current_count} | Duration: {duration:.2f}s")
            logger.info("Received response from LLM")
        except Exception as llm_err:
            logger.error(f"LLM Call Failed: {llm_err}")
            raise
        
        message = response.choices[0].message
        tool_calls_made = []
        final_response = message.content or ""
        
        # Handle tool calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = eval(tool_call.function.arguments)
                
                # Execute via MCP
                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                try:
                    result = await mcp_session.call_tool(tool_name, tool_args)
                    logger.info(f"Tool {tool_name} execution completed")
                except Exception as tool_err:
                    logger.error(f"Tool {tool_name} failed: {tool_err}")
                    raise
                
                # Parse result
                result_data = {}
                for item in result.content:
                    if hasattr(item, 'text'):
                        import json
                        try:
                            result_data = json.loads(item.text)
                        except:
                            result_data = {"content": item.text}
                
                tool_calls_made.append({
                    "tool": tool_name,
                    "arguments": tool_args,
                    "result": result_data
                })
                
                # Add to conversation
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call.model_dump()]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result_data)
                })
            
            # Get final response
            final = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                max_tokens=2000
            )
            final_response = final.choices[0].message.content or "No response"
        
        # Extract session_id
        response_session_id = request.session_id
        for tc in tool_calls_made:
            if tc.get("result", {}).get("session_id"):
                response_session_id = tc["result"]["session_id"]
                break
        
        return ChatResponse(
            response=final_response,
            session_id=response_session_id,
            tool_calls=tool_calls_made if tool_calls_made else None
        )
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/call")
async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]):
    """Direct MCP tool calling (for testing)"""
    if not mcp_session:
        raise HTTPException(status_code=503, detail="MCP server not connected")
    
    try:
        result = await mcp_session.call_tool(tool_name, arguments)
        
        result_data = {}
        for item in result.content:
            if hasattr(item, 'text'):
                import json
                try:
                    result_data = json.loads(item.text)
                except:
                    result_data = {"content": item.text}
        
        return {"success": True, "result": result_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)