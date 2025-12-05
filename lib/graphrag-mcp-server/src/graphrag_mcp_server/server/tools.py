"""MCP Tools definitions for GraphRAG MCP Server.

This module defines all MCP tools exposed by the server.
Each tool corresponds to a GraphRAG API operation.
"""

from typing import Any

# MCP Tool definitions as dictionaries for registration
# These follow the MCP 1.0 specification

GLOBAL_SEARCH_TOOL = {
    "name": "global_search",
    "description": """Perform a global search across the entire knowledge graph.

Global search uses map-reduce pattern over community reports to answer
high-level questions about the entire corpus. Best for:
- Questions about overall themes and patterns
- Summarization across multiple topics
- Corpus-wide analysis

Parameters:
- query: The search query string
- community_level: Optional community level (0=highest, default=2)
- response_type: Optional response format (default="markdown")
""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to execute"
            },
            "community_level": {
                "type": "integer",
                "description": "Community level for search (0=highest level, higher=more granular)",
                "default": 2
            },
            "response_type": {
                "type": "string",
                "description": "Response format type",
                "enum": ["markdown", "text", "json"],
                "default": "markdown"
            }
        },
        "required": ["query"]
    }
}

LOCAL_SEARCH_TOOL = {
    "name": "local_search",
    "description": """Perform a local search on specific entities in the knowledge graph.

Local search retrieves relevant entities and relationships, then uses
context from the subgraph for focused Q&A. Best for:
- Questions about specific entities or topics
- Detailed information retrieval
- Relationship exploration

Parameters:
- query: The search query string
- community_level: Optional community level (default=2)
- response_type: Optional response format (default="markdown")
""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to execute"
            },
            "community_level": {
                "type": "integer",
                "description": "Community level for context building",
                "default": 2
            },
            "response_type": {
                "type": "string",
                "description": "Response format type",
                "enum": ["markdown", "text", "json"],
                "default": "markdown"
            }
        },
        "required": ["query"]
    }
}

DRIFT_SEARCH_TOOL = {
    "name": "drift_search",
    "description": """Perform a DRIFT (Dynamic Reasoning and Inference with Flexible Traversal) search.

DRIFT search dynamically expands context through follow-up queries,
allowing for deeper exploration. Best for:
- Complex multi-hop questions
- Questions requiring inference chains
- Exploratory analysis

Parameters:
- query: The search query string
- community_level: Optional community level (default=2)
- response_type: Optional response format (default="markdown")
""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to execute"
            },
            "community_level": {
                "type": "integer",
                "description": "Community level for context building",
                "default": 2
            },
            "response_type": {
                "type": "string",
                "description": "Response format type",
                "enum": ["markdown", "text", "json"],
                "default": "markdown"
            }
        },
        "required": ["query"]
    }
}

BASIC_SEARCH_TOOL = {
    "name": "basic_search",
    "description": """Perform a basic RAG search without graph augmentation.

Basic search uses traditional vector similarity search without
leveraging the knowledge graph structure. Best for:
- Simple factual queries
- Direct text matching
- Baseline comparison

Parameters:
- query: The search query string
- top_k: Number of results to return (default=10)
""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to execute"
            },
            "top_k": {
                "type": "integer",
                "description": "Number of results to return",
                "default": 10,
                "minimum": 1,
                "maximum": 100
            }
        },
        "required": ["query"]
    }
}

BUILD_INDEX_TOOL = {
    "name": "build_index",
    "description": """Build or rebuild the GraphRAG index.

Creates the knowledge graph index from input documents. This includes:
- Entity and relationship extraction
- Community detection and hierarchy building
- Embedding generation
- Summary generation

Parameters:
- input_path: Path to input documents (optional, uses config default)
- resume: Whether to resume from previous run (default=false)
""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "input_path": {
                "type": "string",
                "description": "Path to input documents directory"
            },
            "resume": {
                "type": "boolean",
                "description": "Resume from previous indexing run",
                "default": False
            }
        },
        "required": []
    }
}

GET_STATISTICS_TOOL = {
    "name": "get_statistics",
    "description": """Get statistics about the current index.

Returns information about:
- Number of entities and relationships
- Number of communities at each level
- Number of text units
- Index build time and status

Parameters: None
""",
    "inputSchema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

IMPORT_DOCUMENT_TOOL = {
    "name": "import_document",
    "description": """Import a document into GraphRAG for indexing.

Parses and chunks a document, preparing it for GraphRAG indexing.
Supports multiple formats:
- PDF (.pdf)
- Microsoft Word (.docx)
- Microsoft PowerPoint (.pptx)
- HTML (.html, .htm)
- Markdown (.md)
- Plain text (.txt)

The import process:
1. Parses document to extract structured elements
2. Normalizes elements to consistent format
3. Chunks text with language-aware strategies (auto-detects Japanese)
4. Builds correlation graph between chunks
5. Returns import result with chunks ready for indexing

Parameters:
- file_path: Path to the document file to import
- chunk_size: Target chunk size in characters (default=1000)
- chunk_overlap: Overlap between chunks (default=100)
- auto_detect_language: Whether to auto-detect language (default=true)
- build_correlation_graph: Whether to build chunk correlations (default=true)
""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the document file to import"
            },
            "chunk_size": {
                "type": "integer",
                "description": "Target chunk size in characters",
                "default": 1000,
                "minimum": 100,
                "maximum": 10000
            },
            "chunk_overlap": {
                "type": "integer",
                "description": "Overlap between chunks in characters",
                "default": 100,
                "minimum": 0
            },
            "auto_detect_language": {
                "type": "boolean",
                "description": "Automatically detect document language",
                "default": True
            },
            "build_correlation_graph": {
                "type": "boolean",
                "description": "Build correlation graph between chunks",
                "default": True
            }
        },
        "required": ["file_path"]
    }
}

IMPORT_DIRECTORY_TOOL = {
    "name": "import_directory",
    "description": """Import all documents from a directory into GraphRAG.

Recursively processes all supported documents in a directory.
Same processing as import_document but for multiple files.

Parameters:
- directory_path: Path to the directory containing documents
- extensions: File extensions to include (default: all supported)
- recursive: Whether to search subdirectories (default=true)
- chunk_size: Target chunk size in characters (default=1000)
- chunk_overlap: Overlap between chunks (default=100)
""",
    "inputSchema": {
        "type": "object",
        "properties": {
            "directory_path": {
                "type": "string",
                "description": "Path to the directory containing documents"
            },
            "extensions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "File extensions to include (e.g., ['.pdf', '.docx'])"
            },
            "recursive": {
                "type": "boolean",
                "description": "Whether to search subdirectories",
                "default": True
            },
            "chunk_size": {
                "type": "integer",
                "description": "Target chunk size in characters",
                "default": 1000,
                "minimum": 100,
                "maximum": 10000
            },
            "chunk_overlap": {
                "type": "integer",
                "description": "Overlap between chunks in characters",
                "default": 100,
                "minimum": 0
            }
        },
        "required": ["directory_path"]
    }
}


# All available tools
ALL_TOOLS = [
    GLOBAL_SEARCH_TOOL,
    LOCAL_SEARCH_TOOL,
    DRIFT_SEARCH_TOOL,
    BASIC_SEARCH_TOOL,
    BUILD_INDEX_TOOL,
    GET_STATISTICS_TOOL,
    IMPORT_DOCUMENT_TOOL,
    IMPORT_DIRECTORY_TOOL,
]


def get_tool_by_name(name: str) -> dict[str, Any] | None:
    """Get a tool definition by name.
    
    Args:
        name: The tool name to look up
        
    Returns:
        Tool definition dictionary or None if not found
    """
    for tool in ALL_TOOLS:
        if tool["name"] == name:
            return tool
    return None


def list_tool_names() -> list[str]:
    """Get list of all available tool names.
    
    Returns:
        List of tool name strings
    """
    return [tool["name"] for tool in ALL_TOOLS]
