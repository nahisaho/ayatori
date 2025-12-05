# GraphRAG MCP Server

MCP (Model Context Protocol) Server for Microsoft GraphRAG - Enables AI assistants to query knowledge graphs.

## Features

- **Global Search**: Map-reduce style search across community summaries
- **Local Search**: Entity-based search with relationship traversal
- **DRIFT Search**: Dynamic reasoning combining global and local methods
- **Basic Search**: Vector similarity search on text units
- **Index Management**: Build and update GraphRAG indexes

## Installation

```bash
pip install graphrag-mcp-server
```

## Quick Start

### 1. Set Environment Variables

```bash
export GRAPHRAG_INDEX_PATH="./graphrag_index"
export GRAPHRAG_LLM_PROVIDER="openai"
export GRAPHRAG_LLM_API_KEY="your-api-key"
```

### 2. Start the Server

```bash
# stdio mode (for VS Code, Cursor, etc.)
graphrag-mcp serve --transport stdio

# SSE mode (for web clients)
graphrag-mcp serve --transport sse --port 8080
```

### 3. VS Code Configuration

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "graphrag": {
      "command": "graphrag-mcp",
      "args": ["serve", "--transport", "stdio"],
      "env": {
        "GRAPHRAG_INDEX_PATH": "${workspaceFolder}/graphrag_index"
      }
    }
  }
}
```

## CLI Commands

```bash
# Start MCP server
graphrag-mcp serve [--transport stdio|sse] [--port PORT]

# Build/update index
graphrag-mcp index [--mode full|incremental] DATA_PATH

# Query (for debugging)
graphrag-mcp query [--type global|local|drift|basic] "your query"

# Show index statistics
graphrag-mcp stats [--format text|json]

# Show version
graphrag-mcp --version
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `global_search` | Search across community summaries |
| `local_search` | Entity-based search |
| `drift_search` | DRIFT search combining methods |
| `basic_search` | Vector similarity search |
| `build_index` | Build GraphRAG index |
| `get_statistics` | Get index statistics |

## MCP Resources

| Resource | Description |
|----------|-------------|
| `graphrag://entities` | List of entities |
| `graphrag://communities` | List of communities |
| `graphrag://relationships` | List of relationships |
| `graphrag://statistics` | Index statistics |

## MCP Prompts

| Prompt | Description |
|--------|-------------|
| `analyze_topic` | Analyze a topic using the knowledge graph |
| `explore_entity` | Explore an entity and its relationships |
| `summarize_community` | Get a summary of a community |
| `compare_entities` | Compare two or more entities |

## Supported LLM Providers

| Provider | Environment Variables |
|----------|----------------------|
| OpenAI | `GRAPHRAG_LLM_API_KEY` |
| Azure OpenAI | `GRAPHRAG_AZURE_OPENAI_ENDPOINT`, `GRAPHRAG_LLM_API_KEY` |
| Anthropic | `GRAPHRAG_LLM_API_KEY` |
| Ollama | `GRAPHRAG_OLLAMA_BASE_URL` (default: `http://localhost:11434`) |

## Configuration

All settings can be configured via environment variables with the `GRAPHRAG_` prefix:

| Variable | Description | Default |
|----------|-------------|---------|
| `GRAPHRAG_INDEX_PATH` | Path to GraphRAG index | `./graphrag_index` |
| `GRAPHRAG_LLM_PROVIDER` | LLM provider | `openai` |
| `GRAPHRAG_LLM_MODEL` | LLM model name | `gpt-4o` |
| `GRAPHRAG_LLM_API_KEY` | LLM API key | - |
| `GRAPHRAG_EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `GRAPHRAG_VECTOR_STORE` | Vector store type | `lancedb` |

## Requirements

- Python 3.11+
- GraphRAG 2.0+
- MCP SDK 1.0+

## Development

```bash
# Clone the repository
git clone https://github.com/your-org/graphrag-mcp-server.git
cd graphrag-mcp-server

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=graphrag_mcp_server
```

## License

MIT License
