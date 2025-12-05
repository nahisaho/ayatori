"""Server module for GraphRAG MCP Server."""

from graphrag_mcp_server.server.app import create_server, run_stdio_server, server
from graphrag_mcp_server.server.tools import (
    ALL_TOOLS,
    GLOBAL_SEARCH_TOOL,
    LOCAL_SEARCH_TOOL,
    DRIFT_SEARCH_TOOL,
    BASIC_SEARCH_TOOL,
    BUILD_INDEX_TOOL,
    GET_STATISTICS_TOOL,
    IMPORT_DOCUMENT_TOOL,
    IMPORT_DIRECTORY_TOOL,
    get_tool_by_name,
    list_tool_names,
)
from graphrag_mcp_server.server.resources import (
    STATIC_RESOURCES,
    RESOURCE_TEMPLATES,
    get_resource_by_uri,
    list_resource_uris,
    list_resource_templates,
)
from graphrag_mcp_server.server.prompts import (
    ALL_PROMPTS,
    get_prompt_by_name,
    list_prompt_names,
    get_prompt_template,
)

__all__ = [
    # App
    "create_server",
    "run_stdio_server",
    "server",
    # Tools
    "ALL_TOOLS",
    "GLOBAL_SEARCH_TOOL",
    "LOCAL_SEARCH_TOOL",
    "DRIFT_SEARCH_TOOL",
    "BASIC_SEARCH_TOOL",
    "BUILD_INDEX_TOOL",
    "GET_STATISTICS_TOOL",
    "get_tool_by_name",
    "list_tool_names",
    # Resources
    "STATIC_RESOURCES",
    "RESOURCE_TEMPLATES",
    "get_resource_by_uri",
    "list_resource_uris",
    "list_resource_templates",
    # Prompts
    "ALL_PROMPTS",
    "get_prompt_by_name",
    "list_prompt_names",
    "get_prompt_template",
]
