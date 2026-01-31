"""
Start the ArmorIQ MCP server.

Default port: 8010
POST /mcp expects JSON-RPC requests and responds with SSE (text/event-stream)
"""
import os
import sys
import uvicorn

if __name__ == "__main__":
    try:
        from ports_config import PORTS
        default_port = PORTS.get("MCP", 8011)
    except ImportError:
        default_port = 8011
        
    port = int(os.getenv("MCP_PORT", str(default_port)))
    uvicorn.run("armoriq_mcp_server:app", host="0.0.0.0", port=port, reload=False)

