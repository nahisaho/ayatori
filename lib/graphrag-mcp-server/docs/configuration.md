# Configuration Guide

Complete guide to configuring GraphRAG MCP Server.

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GRAPHRAG_INDEX_PATH` | Path to the GraphRAG index | `/path/to/index` |
| `OPENAI_API_KEY` | OpenAI API key (if using OpenAI) | `sk-...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GRAPHRAG_LLM_PROVIDER` | LLM provider to use | `openai` |
| `GRAPHRAG_EMBEDDING_MODEL` | Embedding model name | `text-embedding-3-small` |
| `GRAPHRAG_LLM_MODEL` | LLM model name | `gpt-4o` |
| `GRAPHRAG_VECTOR_STORE` | Vector store type | `lancedb` |
| `GRAPHRAG_LOG_LEVEL` | Logging level | `INFO` |
| `GRAPHRAG_SSE_PORT` | SSE server port | `8080` |

## LLM Provider Configuration

### OpenAI

```bash
export GRAPHRAG_LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-your-api-key
export GRAPHRAG_LLM_MODEL=gpt-4o
export GRAPHRAG_EMBEDDING_MODEL=text-embedding-3-small
```

### Azure OpenAI

```bash
export GRAPHRAG_LLM_PROVIDER=azure_openai
export AZURE_OPENAI_API_KEY=your-azure-key
export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
export AZURE_OPENAI_DEPLOYMENT=your-deployment-name
export AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### Anthropic

```bash
export GRAPHRAG_LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY=your-anthropic-key
export GRAPHRAG_LLM_MODEL=claude-sonnet-4-20250514
```

### Ollama (Local)

```bash
export GRAPHRAG_LLM_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434
export GRAPHRAG_LLM_MODEL=llama3.2
export GRAPHRAG_EMBEDDING_MODEL=nomic-embed-text
```

## Vector Store Configuration

### LanceDB (Default)

```bash
export GRAPHRAG_VECTOR_STORE=lancedb
export GRAPHRAG_LANCEDB_URI=/path/to/lancedb
```

### Azure AI Search

```bash
export GRAPHRAG_VECTOR_STORE=azure_ai_search
export AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
export AZURE_SEARCH_KEY=your-search-key
export AZURE_SEARCH_INDEX_NAME=graphrag-index
```

## Configuration File

You can also use a `graphrag.yaml` configuration file:

```yaml
# graphrag.yaml
llm:
  provider: openai
  model: gpt-4o
  temperature: 0.0
  max_tokens: 4096

embeddings:
  provider: openai
  model: text-embedding-3-small
  batch_size: 16

vector_store:
  type: lancedb
  uri: ./data/lancedb

index:
  path: ./data/index
  chunk_size: 1200
  chunk_overlap: 100

search:
  default_community_level: 2
  default_top_k: 10

server:
  transport: stdio
  sse_port: 8080
  log_level: INFO
```

## Transport Configuration

### stdio Transport (Default)

For local integrations with VS Code or Claude Desktop:

```json
{
  "mcpServers": {
    "graphrag": {
      "command": "graphrag-mcp",
      "args": ["serve", "--transport", "stdio"],
      "env": {
        "GRAPHRAG_INDEX_PATH": "/path/to/index"
      }
    }
  }
}
```

### SSE Transport

For network access or multi-client scenarios:

```json
{
  "mcpServers": {
    "graphrag": {
      "command": "graphrag-mcp",
      "args": ["serve", "--transport", "sse", "--port", "8080"],
      "env": {
        "GRAPHRAG_INDEX_PATH": "/path/to/index"
      }
    }
  }
}
```

Connect clients to: `http://localhost:8080/sse`

## Performance Tuning

### Memory Optimization

```bash
# Limit embedding batch size for low-memory systems
export GRAPHRAG_EMBEDDING_BATCH_SIZE=8

# Use disk-based vector store
export GRAPHRAG_LANCEDB_URI=/path/to/disk/lancedb
```

### Concurrency Settings

```bash
# Limit concurrent requests
export GRAPHRAG_MAX_CONCURRENT_REQUESTS=5

# Request timeout (seconds)
export GRAPHRAG_REQUEST_TIMEOUT=120
```

### Caching

```bash
# Enable response caching
export GRAPHRAG_CACHE_ENABLED=true
export GRAPHRAG_CACHE_TTL=3600

# Cache directory
export GRAPHRAG_CACHE_DIR=/path/to/cache
```

## Security Configuration

### API Key Security

Never commit API keys to version control. Use environment variables or secure secret management:

```bash
# Using direnv
echo 'export OPENAI_API_KEY=sk-...' >> .envrc
direnv allow

# Using VS Code settings (not recommended for shared repos)
# Use workspace settings with ${env:VAR} syntax
```

### Rate Limiting

```bash
# Enable rate limiting
export GRAPHRAG_RATE_LIMIT_ENABLED=true
export GRAPHRAG_RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

## Debugging

### Enable Debug Logging

```bash
export GRAPHRAG_LOG_LEVEL=DEBUG
export GRAPHRAG_LOG_FILE=/path/to/debug.log
```

### Trace Requests

```bash
export GRAPHRAG_TRACE_ENABLED=true
export GRAPHRAG_TRACE_FILE=/path/to/trace.json
```

## Validation

Validate your configuration:

```bash
# Check configuration
graphrag-mcp config validate

# Test LLM connection
graphrag-mcp config test-llm

# Test vector store connection
graphrag-mcp config test-vector-store
```
