
import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.services.mcp_client import MCPClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("verify_mcp")

async def test_mcp():
    print("=== MCP Verification Tool ===")
    client = MCPClient()
    
    try:
        print(f"Server Path: {os.environ.get('MCP_YAML_SERVER_PATH')}")
        print("Connecting...")
        await client.connect()
        print("✅ Connection successful!")
        
        print("Testing tool: list_tools...")
        tools = await client.session.list_tools()
        print(f"Available tools: {[t.name for t in tools.tools]}")
        
        print("Disconnecting...")
        await client.disconnect()
        print("✅ Cleanup successful!")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp())
