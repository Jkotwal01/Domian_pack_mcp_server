"""
MCP Client Wrapper
Interfaces with the YAML MCP server for deterministic operations
"""
from typing import List, Dict, Any, Optional
import asyncio
import json
import logging
import os
import yaml
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.schemas import Operation, MCPOperationResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class MCPClient:
    """Wrapper for MCP YAML server operations"""
    
    def __init__(self):
        # Determine command based on file extension
        server_path = settings.MCP_YAML_SERVER_PATH
        server_dir = os.path.dirname(server_path)
        
        command = "node"
        if server_path.endswith(".py"):
            command = "python"
            # Try to find a virtual environment in the server's directory
            # Common patterns for Windows (.venv\Scripts\python.exe) and Unix (.venv/bin/python)
            venv_patterns = [
                os.path.join(server_dir, ".venv", "Scripts", "python.exe"),
                os.path.join(server_dir, "venv", "Scripts", "python.exe"),
                os.path.join(server_dir, ".venv", "bin", "python"),
                os.path.join(server_dir, "venv", "bin", "python"),
            ]
            for venv_path in venv_patterns:
                if os.path.exists(venv_path):
                    command = venv_path
                    logger.info(f"Using MCP server virtual environment: {command}")
                    break
        
        # Prepare environment variables to silence FastMCP startup noise and ensure UTF-8
        env = os.environ.copy()
        env["FASTMCP_NO_BANNER"] = "1"
        env["FASTMCP_QUIET"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUNBUFFERED"] = "1"
        
        self.server_params = StdioServerParameters(
            command=command,
            args=[server_path],
            env=env
        )
        self.session: Optional[ClientSession] = None
        self.stdio_context = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Establish connection to MCP server"""
        try:
            logger.info(f"Starting MCP server process: {self.server_params.command} with args {self.server_params.args}")
            # stdio_client is an async context manager
            self.stdio_context = stdio_client(self.server_params)
            # Manually enter the context
            logger.info("Entering stdio context...")
            read, write = await self.stdio_context.__aenter__()
            logger.info("Stdio transport established")
            
            # Create session with the transport pair
            self.session = ClientSession(read, write)
            
            # IMPORTANT: ClientSession is ALSO an async context manager.
            # We MUST enter it to start the background read loop!
            logger.info("Entering MCP session context...")
            await self.session.__aenter__()
            
            logger.info("Initializing MCP session (timeout=20s)...")
            # Add timeout to initialization
            try:
                await asyncio.wait_for(self.session.initialize(), timeout=20.0)
                logger.info(f"Connected to MCP YAML server ({self.server_params.command})")
            except asyncio.TimeoutError:
                logger.error("Timeout during MCP session initialization")
                raise RuntimeError("MCP server timed out during initialization")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            if self.session:
                try:
                    await self.session.__aexit__(None, None, None)
                except: pass
                self.session = None
            if self.stdio_context:
                await self.stdio_context.__aexit__(None, None, None)
                self.stdio_context = None
            raise
    
    async def disconnect(self):
        """Close connection to MCP server"""
        if self.session:
            try:
                await self.session.__aexit__(None, None, None)
                self.session = None
            except Exception as e:
                logger.error(f"Error exiting MCP session: {e}")
                
        if self.stdio_context:
            try:
                await self.stdio_context.__aexit__(None, None, None)
                self.stdio_context = None
                logger.info("Disconnected from MCP YAML server")
            except Exception as e:
                logger.error(f"Error disconnecting from MCP server: {e}")
    
    async def apply_operations(
        self,
        current_yaml: Dict[str, Any],
        operations: List[Operation]
    ) -> MCPOperationResponse:
        """
        Apply structured operations to YAML via MCP server
        
        Args:
            current_yaml: Current YAML content as dict
            operations: List of structured operations
        
        Returns:
            MCPOperationResponse with updated YAML, diff, and errors
        """
        if not self.session:
            raise RuntimeError("MCP client not connected")
        
        try:
            # Serialize current state to YAML
            document_str = yaml.dump(current_yaml, sort_keys=False)
            
            # Map op_type to action (server expects "add", "remove", "replace", etc.)
            # Our backend uses "add_field", "remove_field", etc.
            # The server's operations.py seems to handle a variety of actions.
            # Looking at mcp_server/main.py, it takes operations directly.
            
            # Convert operations to MCP format
            mcp_operations = []
            for op in operations:
                action = op.op_type
                if action.endswith("_field"):
                    action = action.replace("_field", "")
                
                mcp_op = {
                    "action": action,
                    "path": op.target_path if isinstance(op.target_path, list) else op.target_path.split("."),
                    "value": op.payload
                }
                mcp_operations.append(mcp_op)
            
            logger.info(f"Calling MCP transform_document with {len(mcp_operations)} operations")
            # For debugging, log the first operation
            if mcp_operations:
                logger.debug(f"First operation: {json.dumps(mcp_operations[0])}")
            
            # Call MCP server tool: transform_document
            result = await self.session.call_tool(
                "transform_document",
                arguments={
                    "document": document_str,
                    "format": "yaml",
                    "operations": mcp_operations
                }
            )
            
            # Parse response
            if result.isError:
                logger.error(f"MCP operation failed: {result.content}")
                return MCPOperationResponse(
                    success=False,
                    errors=[str(result.content)]
                )
            
            # Extract result content
            response_data = result.content[0].text if result.content else "{}"
            if isinstance(response_data, str):
                try:
                    response_data = json.loads(response_data)
                except json.JSONDecodeError:
                    # If it's not JSON, might be raw text or something else
                    logger.warning(f"Could not parse MCP response as JSON: {response_data}")
                    response_data = {"success": True, "document": response_data}
            
            return MCPOperationResponse(
                success=response_data.get("success", True),
                updated_yaml=response_data.get("document"),
                diff=response_data.get("diff"),
                errors=[e["message"] for e in response_data.get("errors", [])] if response_data.get("errors") else [],
                warnings=[w["message"] for w in response_data.get("warnings", [])] if response_data.get("warnings") else []
            )
        
        except Exception as e:
            logger.error(f"Error applying MCP operations: {e}")
            return MCPOperationResponse(
                success=False,
                errors=[f"MCP client error: {str(e)}"]
            )
    
    async def validate_operations(
        self,
        operations: List[Operation]
    ) -> Dict[str, Any]:
        """
        Validate operations without applying them
        
        Returns:
            Validation result with any errors or warnings
        """
        if not self.session:
            raise RuntimeError("MCP client not connected")
        
        try:
            # Call MCP server tool: validate_document
            result = await self.session.call_tool(
                "validate_document",
                arguments={
                    "document": yaml.dump(operations[0].payload) if operations else "", 
                    "format": "yaml"
                }
            )
            
            if result.isError:
                return {
                    "valid": False,
                    "errors": [str(result.content)]
                }
            
            response_data = json.loads(result.content[0].text) if result.content else {}
            return response_data
        
        except Exception as e:
            logger.error(f"Error validating operations: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"]
            }


# Singleton instance
_mcp_client: Optional[MCPClient] = None


async def get_mcp_client() -> MCPClient:
    """Get or create MCP client instance"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
        await _mcp_client.connect()
    return _mcp_client


async def close_mcp_client():
    """Close MCP client connection"""
    global _mcp_client
    if _mcp_client:
        await _mcp_client.disconnect()
        _mcp_client = None
