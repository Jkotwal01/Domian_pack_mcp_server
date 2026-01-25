from mcp.server.fastmcp import FastMCP

mcp = FastMCP("smoke-test")

@mcp.tool()
def ping() -> str:
    return "pong"
