#!/usr/bin/env python3
"""
MCP Server for Text2SOQL MVP
Exposes sf.query and health tools for Salesforce integration
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import mcp.server
import mcp.server.stdio
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
)

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from salesforce.client import SalesforceClient
from utils.logging import setup_logging

# Setup logging
logger = setup_logging(__name__)

# Global Salesforce client
sf_client: Optional[SalesforceClient] = None


async def initialize_salesforce() -> None:
    """Initialize Salesforce client with environment variables."""
    global sf_client
    
    try:
        sf_client = SalesforceClient()
        await sf_client.connect()
        logger.info("Salesforce client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Salesforce client: {e}")
        sf_client = None


async def handle_list_tools() -> ListToolsResult:
    """Handle list tools request."""
    tools = [
        Tool(
            name="sf.query",
            description="Execute a SOQL query against Salesforce",
            inputSchema={
                "type": "object",
                "properties": {
                    "soql": {
                        "type": "string",
                        "description": "The SOQL query to execute"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Optional limit on number of records returned",
                        "default": 100
                    }
                },
                "required": ["soql"]
            }
        ),
        Tool(
            name="health",
            description="Check the health status of the MCP server and Salesforce connection",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        )
    ]
    
    return ListToolsResult(tools=tools)


async def handle_sf_query(soql: str, limit: Optional[int] = 100) -> Dict[str, Any]:
    """Execute a SOQL query against Salesforce."""
    if not sf_client:
        raise Exception("Salesforce client not initialized")
    
    try:
        # Validate SOQL query
        if not soql.strip().upper().startswith("SELECT"):
            raise ValueError("SOQL query must start with SELECT")
        
        # Add limit if not present and limit is specified
        if limit and "LIMIT" not in soql.upper():
            soql = f"{soql} LIMIT {limit}"
        
        logger.info(f"Executing SOQL query: {soql}")
        
        # Execute query
        result = await sf_client.query(soql)
        
        return {
            "success": True,
            "query": soql,
            "total_size": result.get("totalSize", 0),
            "done": result.get("done", True),
            "records": result.get("records", []),
            "message": f"Query executed successfully. Found {result.get('totalSize', 0)} records."
        }
        
    except Exception as e:
        logger.error(f"Error executing SOQL query: {e}")
        return {
            "success": False,
            "query": soql,
            "error": str(e),
            "message": f"Failed to execute query: {e}"
        }


async def handle_health() -> Dict[str, Any]:
    """Check health status of the MCP server and Salesforce connection."""
    try:
        # Check Salesforce connection
        sf_status = "connected" if sf_client and sf_client.is_connected() else "disconnected"
        
        # Check environment variables
        env_vars = {
            "SALESFORCE_USERNAME": bool(os.getenv("SALESFORCE_USERNAME")),
            "SALESFORCE_PASSWORD": bool(os.getenv("SALESFORCE_PASSWORD")),
            "SALESFORCE_SECURITY_TOKEN": bool(os.getenv("SALESFORCE_SECURITY_TOKEN")),
            "SALESFORCE_DOMAIN": bool(os.getenv("SALESFORCE_DOMAIN")),
        }
        
        all_env_set = all(env_vars.values())
        
        return {
            "status": "healthy" if sf_status == "connected" and all_env_set else "unhealthy",
            "salesforce": sf_status,
            "environment_variables": env_vars,
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": asyncio.get_event_loop().time()
        }


async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool call requests."""
    try:
        if name == "sf.query":
            soql = arguments.get("soql")
            limit = arguments.get("limit", 100)
            
            if not soql:
                raise ValueError("SOQL query is required")
            
            result = await handle_sf_query(soql, limit)
            content = [{"type": "text", "text": json.dumps(result, indent=2)}]
            
        elif name == "health":
            result = await handle_health()
            content = [{"type": "text", "text": json.dumps(result, indent=2)}]
            
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return CallToolResult(content=content)
        
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        error_content = [{"type": "text", "text": f"Error: {str(e)}"}]
        return CallToolResult(content=error_content)


async def main() -> None:
    """Main entry point for the MCP server."""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize Salesforce client
    await initialize_salesforce()
    
    # Create MCP server
    server = mcp.server.Server("text2soql-mvp")
    
    @server.list_tools()
    async def list_tools() -> ListToolsResult:
        return await handle_list_tools()
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
        return await handle_call_tool(name, arguments)
    
    # Run server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="text2soql-mvp",
                server_version="0.1.0",
                capabilities=mcp.server.ServerCapabilities(
                    tools=mcp.server.ToolsCapabilities(
                        listChanged=True,
                    ),
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
