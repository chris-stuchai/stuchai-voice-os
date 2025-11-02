"""
MCP (Model Context Protocol) Client module.

Handles integration with MCP servers for tool execution.
"""

import logging
from typing import Dict, List, Optional, Any
import httpx
import json

from shared.config import settings

logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP Client for executing tools and actions.
    
    Connects to MCP server and provides interface for tool execution.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize MCP client.
        
        Args:
            base_url: MCP server base URL
        """
        self.base_url = base_url or settings.MCP_SERVER_URL
        self.client = httpx.AsyncClient(timeout=30.0)
        self.enabled = settings.MCP_ENABLED
        self.tools: List[Dict] = []
    
    async def initialize(self) -> None:
        """Initialize MCP client and discover available tools."""
        if not self.enabled:
            logger.info("MCP is disabled")
            return
        
        try:
            # Discover available tools from MCP server
            response = await self.client.get(f"{self.base_url}/tools")
            response.raise_for_status()
            self.tools = response.json()
            logger.info(f"Discovered {len(self.tools)} MCP tools")
        
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            self.enabled = False
    
    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call an MCP tool.
        
        Args:
            tool_name: Name of the tool to call
            parameters: Tool parameters
            
        Returns:
            Dict: Tool execution result
        """
        if not self.enabled:
            raise RuntimeError("MCP is disabled")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/{tool_name}",
                json=parameters
            )
            response.raise_for_status()
            return response.json()
        
        except httpx.RequestError as e:
            logger.error(f"MCP tool call error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            raise
    
    async def list_tools(self) -> List[Dict]:
        """
        List available MCP tools.
        
        Returns:
            List[Dict]: Available tools
        """
        if not self.enabled:
            return []
        
        return self.tools
    
    async def close(self) -> None:
        """Close MCP client connection."""
        if self.client:
            await self.client.aclose()
            self.client = None


# Global MCP client instance
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """
    Get or create global MCP client instance.
    
    Returns:
        MCPClient: MCP client instance
    """
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
        # Note: initialize() should be called separately
    return _mcp_client

