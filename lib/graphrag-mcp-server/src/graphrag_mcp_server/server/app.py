"""MCP Server application for GraphRAG."""

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    Resource,
    TextContent,
    Tool,
)

from graphrag_mcp_server.config import Settings, get_settings

logger = logging.getLogger(__name__)

# Create the MCP server instance
server = Server("graphrag-mcp-server")


@dataclass
class GraphRAGContext:
    """Context for GraphRAG MCP server operations."""

    settings: Settings
    index_path: Path | None = None


def create_server() -> tuple[Server, GraphRAGContext]:
    """Create and configure the MCP server.

    Returns:
        Tuple of (server, context) for GraphRAG MCP operations.
    """
    settings = get_settings()
    context = GraphRAGContext(settings=settings)
    return server, context


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools.

    Returns:
        List of available tools for GraphRAG operations.
    """
    return [
        Tool(
            name="global_search",
            description="Execute a global search across the entire dataset using community summaries. Best for high-level questions about the overall themes and topics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
                    "community_level": {
                        "type": "integer",
                        "description": "Community hierarchy level (0=most detailed, higher=more summarized)",
                        "default": 2,
                    },
                    "response_type": {
                        "type": "string",
                        "description": "Desired response format",
                        "default": "Multiple Paragraphs",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="local_search",
            description="Execute an entity-based local search. Best for specific questions about particular entities, relationships, or detailed information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
                    "entity_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by entity types (e.g., ['PERSON', 'ORGANIZATION'])",
                    },
                    "response_type": {
                        "type": "string",
                        "default": "Multiple Paragraphs",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="drift_search",
            description="Execute DRIFT search combining global and local methods with dynamic follow-up questions. Best for complex, multi-faceted queries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
                    "follow_up_depth": {
                        "type": "integer",
                        "description": "Depth of follow-up questions",
                        "default": 2,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="basic_search",
            description="Execute basic vector similarity search on text units. Fastest search method for simple queries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="build_index",
            description="Build or update the GraphRAG index from source documents.",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_path": {
                        "type": "string",
                        "description": "Path to the data directory containing documents",
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["full", "incremental"],
                        "description": "Index mode: full (rebuild) or incremental (update)",
                        "default": "incremental",
                    },
                },
                "required": ["data_path"],
            },
        ),
        Tool(
            name="get_statistics",
            description="Get statistics about the current GraphRAG index.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="import_document",
            description="Import a document into GraphRAG for indexing. Supports PDF, DOCX, PPTX, HTML, MD, and TXT formats.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the document file to import",
                    },
                    "chunk_size": {
                        "type": "integer",
                        "description": "Target chunk size in characters",
                        "default": 1000,
                    },
                    "chunk_overlap": {
                        "type": "integer",
                        "description": "Overlap between chunks in characters",
                        "default": 100,
                    },
                    "auto_detect_language": {
                        "type": "boolean",
                        "description": "Automatically detect document language",
                        "default": True,
                    },
                    "build_correlation_graph": {
                        "type": "boolean",
                        "description": "Build correlation graph between chunks",
                        "default": True,
                    },
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="import_directory",
            description="Import all documents from a directory into GraphRAG.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Path to the directory containing documents",
                    },
                    "extensions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "File extensions to include (e.g., ['.pdf', '.docx'])",
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Whether to search subdirectories",
                        "default": True,
                    },
                    "chunk_size": {
                        "type": "integer",
                        "description": "Target chunk size in characters",
                        "default": 1000,
                    },
                    "chunk_overlap": {
                        "type": "integer",
                        "description": "Overlap between chunks in characters",
                        "default": 100,
                    },
                },
                "required": ["directory_path"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls.

    Args:
        name: Name of the tool to call
        arguments: Tool arguments

    Returns:
        List of text content with results.
    """
    from graphrag_mcp_server.handlers.search import (
        handle_basic_search,
        handle_drift_search,
        handle_global_search,
        handle_local_search,
    )
    from graphrag_mcp_server.handlers.index import (
        handle_build_index,
        handle_get_statistics,
    )
    from graphrag_mcp_server.handlers.import_handler import (
        handle_import_document,
        handle_import_directory,
    )

    try:
        if name == "global_search":
            result = await handle_global_search(
                query=arguments["query"],
                community_level=arguments.get("community_level", 2),
                response_type=arguments.get("response_type", "Multiple Paragraphs"),
            )
        elif name == "local_search":
            result = await handle_local_search(
                query=arguments["query"],
                entity_types=arguments.get("entity_types"),
                response_type=arguments.get("response_type", "Multiple Paragraphs"),
            )
        elif name == "drift_search":
            result = await handle_drift_search(
                query=arguments["query"],
                follow_up_depth=arguments.get("follow_up_depth", 2),
            )
        elif name == "basic_search":
            result = await handle_basic_search(
                query=arguments["query"],
                top_k=arguments.get("top_k", 10),
            )
        elif name == "build_index":
            result = await handle_build_index(
                data_path=arguments["data_path"],
                mode=arguments.get("mode", "incremental"),
            )
        elif name == "get_statistics":
            result = await handle_get_statistics()
        elif name == "import_document":
            result = await handle_import_document(
                file_path=arguments["file_path"],
                chunk_size=arguments.get("chunk_size", 1000),
                chunk_overlap=arguments.get("chunk_overlap", 100),
                auto_detect_language=arguments.get("auto_detect_language", True),
                build_correlation_graph=arguments.get("build_correlation_graph", True),
            )
        elif name == "import_directory":
            result = await handle_import_directory(
                directory_path=arguments["directory_path"],
                extensions=arguments.get("extensions"),
                recursive=arguments.get("recursive", True),
                chunk_size=arguments.get("chunk_size", 1000),
                chunk_overlap=arguments.get("chunk_overlap", 100),
            )
        else:
            result = f"Unknown tool: {name}"

        return [TextContent(type="text", text=str(result))]

    except Exception as e:
        logger.exception(f"Error calling tool {name}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available MCP resources.

    Returns:
        List of available resources for GraphRAG data access.
    """
    return [
        Resource(
            uri="graphrag://entities",
            name="Entities",
            description="List of entities in the knowledge graph",
            mimeType="application/json",
        ),
        Resource(
            uri="graphrag://communities",
            name="Communities",
            description="List of communities (entity clusters) in the graph",
            mimeType="application/json",
        ),
        Resource(
            uri="graphrag://relationships",
            name="Relationships",
            description="List of relationships between entities",
            mimeType="application/json",
        ),
        Resource(
            uri="graphrag://statistics",
            name="Index Statistics",
            description="Statistics about the GraphRAG index",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource by URI.

    Args:
        uri: Resource URI

    Returns:
        Resource content as string.
    """
    import json
    from graphrag_mcp_server.handlers.resources import (
        get_entities,
        get_communities,
        get_relationships,
        get_statistics,
    )

    try:
        if uri == "graphrag://entities":
            data = await get_entities()
        elif uri == "graphrag://communities":
            data = await get_communities()
        elif uri == "graphrag://relationships":
            data = await get_relationships()
        elif uri == "graphrag://statistics":
            data = await get_statistics()
        else:
            data = {"error": f"Unknown resource: {uri}"}

        return json.dumps(data, indent=2, default=str)

    except Exception as e:
        logger.exception(f"Error reading resource {uri}")
        return json.dumps({"error": str(e)})


@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List available MCP prompts.

    Returns:
        List of available prompts for GraphRAG operations.
    """
    return [
        Prompt(
            name="analyze_topic",
            description="Analyze a topic using the knowledge graph",
            arguments=[
                PromptArgument(
                    name="topic",
                    description="The topic to analyze",
                    required=True,
                ),
                PromptArgument(
                    name="depth",
                    description="Analysis depth: brief, moderate, or comprehensive",
                    required=False,
                ),
            ],
        ),
        Prompt(
            name="explore_entity",
            description="Explore an entity and its relationships",
            arguments=[
                PromptArgument(
                    name="entity_name",
                    description="Name of the entity to explore",
                    required=True,
                ),
            ],
        ),
        Prompt(
            name="summarize_community",
            description="Get a summary of a community in the graph",
            arguments=[
                PromptArgument(
                    name="community_id",
                    description="ID of the community to summarize",
                    required=True,
                ),
            ],
        ),
        Prompt(
            name="compare_entities",
            description="Compare two or more entities",
            arguments=[
                PromptArgument(
                    name="entities",
                    description="Comma-separated list of entity names to compare",
                    required=True,
                ),
            ],
        ),
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    """Get a prompt by name.

    Args:
        name: Prompt name
        arguments: Prompt arguments

    Returns:
        Prompt result with messages.
    """
    arguments = arguments or {}

    if name == "analyze_topic":
        topic = arguments.get("topic", "")
        depth = arguments.get("depth", "moderate")
        return GetPromptResult(
            description=f"Analyze topic: {topic}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Analyze the following topic using the knowledge graph data:

Topic: {topic}
Analysis Depth: {depth}

Please use the global_search tool to find high-level themes, then use local_search to explore specific entities mentioned. Provide a {depth} analysis covering:
1. Main concepts and entities related to this topic
2. Key relationships and connections
3. Important themes and patterns
4. Relevant insights from the data""",
                    ),
                )
            ],
        )

    elif name == "explore_entity":
        entity_name = arguments.get("entity_name", "")
        return GetPromptResult(
            description=f"Explore entity: {entity_name}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Explore the entity "{entity_name}" in the knowledge graph.

Use local_search to find information about this entity, including:
1. Description and key attributes
2. Related entities and their relationships
3. Communities this entity belongs to
4. Relevant context from source documents""",
                    ),
                )
            ],
        )

    elif name == "summarize_community":
        community_id = arguments.get("community_id", "")
        return GetPromptResult(
            description=f"Summarize community: {community_id}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Summarize the community with ID "{community_id}" from the knowledge graph.

Include:
1. Main theme or topic of this community
2. Key entities in this community
3. Important relationships within the community
4. Connections to other communities""",
                    ),
                )
            ],
        )

    elif name == "compare_entities":
        entities = arguments.get("entities", "")
        return GetPromptResult(
            description=f"Compare entities: {entities}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Compare the following entities from the knowledge graph: {entities}

Use local_search to find information about each entity, then compare:
1. Key attributes and descriptions
2. Shared relationships and connections
3. Common communities or themes
4. Differences and unique characteristics""",
                    ),
                )
            ],
        )

    else:
        return GetPromptResult(
            description=f"Unknown prompt: {name}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Unknown prompt: {name}",
                    ),
                )
            ],
        )


async def run_stdio_server() -> None:
    """Run the MCP server with stdio transport."""
    logger.info("Starting GraphRAG MCP Server (stdio transport)")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    """Main entry point for the server."""
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_stdio_server())


if __name__ == "__main__":
    main()
