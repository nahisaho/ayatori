# Architecture

This document describes the architecture and design decisions for GraphRAG MCP Server.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Clients                              │
│  (VS Code, Claude Desktop, Other IDE Integrations)              │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
              ┌─────▼─────┐           ┌─────▼─────┐
              │   stdio   │           │    SSE    │
              │ Transport │           │ Transport │
              └─────┬─────┘           └─────┬─────┘
                    │                       │
                    └───────────┬───────────┘
                                │
              ┌─────────────────▼─────────────────┐
              │         MCP Server Core           │
              │  (mcp.server.FastMCP wrapper)     │
              ├───────────────────────────────────┤
              │  • Tool Registration              │
              │  • Prompt Registration            │
              │  • Request Routing                │
              └─────────────────┬─────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
  ┌─────▼─────┐           ┌─────▼─────┐           ┌─────▼─────┐
  │  Search   │           │   Index   │           │  Prompts  │
  │ Handlers  │           │ Handlers  │           │ Handlers  │
  └─────┬─────┘           └─────┬─────┘           └───────────┘
        │                       │
        └───────────┬───────────┘
                    │
      ┌─────────────▼─────────────┐
      │     GraphRAG API          │
      │  (Direct API Calls)       │
      ├───────────────────────────┤
      │  • global_search()        │
      │  • local_search()         │
      │  • drift_search()         │
      │  • build_index()          │
      └─────────────┬─────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
  ┌─────▼─────┐           ┌─────▼─────┐
  │  Vector   │           │    LLM    │
  │   Store   │           │ Provider  │
  │ (LanceDB/ │           │ (OpenAI/  │
  │  Azure)   │           │ Anthropic/│
  └───────────┘           │  Ollama)  │
                          └───────────┘
```

## Design Principles

### Article VIII Compliance

The server follows MUSUBI Constitutional Article VIII (Simplicity & Transparency) by:

1. **No Custom Abstraction Layers**: GraphRAG API is called directly without intermediate abstractions
2. **Transparent Error Handling**: Errors from GraphRAG are propagated with full context
3. **Minimal Dependencies**: Only essential dependencies are included

### Component Responsibilities

#### Transport Layer

- **stdio Transport**: Default transport for local integrations (VS Code, Claude Desktop)
- **SSE Transport**: HTTP-based Server-Sent Events for network access

#### Server Core

- Manages MCP protocol lifecycle
- Routes tool calls to appropriate handlers
- Handles authentication and rate limiting

#### Handlers

- **Search Handlers**: Execute GraphRAG search operations
- **Index Handlers**: Manage knowledge graph indexing
- **Prompt Handlers**: Provide prompt templates

### LLM Provider Integration

The server uses the Esperanto library for unified LLM access:

```python
from esperanto import EsperantoOpenAI, EsperantoAnthropic

# Provider selection via configuration
provider = get_llm_provider(settings.llm_provider)
```

Supported providers:
- OpenAI (GPT-4, GPT-4o)
- Azure OpenAI
- Anthropic (Claude)
- Ollama (local models)

### Vector Store Options

| Store | Use Case |
|-------|----------|
| LanceDB | Local development, single-user |
| Azure AI Search | Production, multi-tenant |

## Data Flow

### Search Query Flow

```
1. Client sends tool call request
2. Server validates parameters
3. Handler loads index data
4. GraphRAG API executes search
5. LLM generates response
6. Handler formats result
7. Server returns response to client
```

### Index Build Flow

```
1. Client sends build_index tool call
2. Handler validates input path
3. GraphRAG API processes documents
4. Embeddings generated via LLM provider
5. Knowledge graph stored in vector store
6. Statistics updated
7. Build result returned to client
```

## Configuration

See [Configuration Guide](configuration.md) for detailed configuration options.

## Error Handling

Errors are categorized as:

| Error Type | HTTP Code | Retryable |
|------------|-----------|-----------|
| `IndexNotFoundError` | 404 | No |
| `ConfigurationError` | 400 | No |
| `LLMProviderError` | 502 | Yes |
| `RateLimitError` | 429 | Yes |

## Security Considerations

1. **API Key Management**: Keys stored in environment variables only
2. **Input Validation**: All inputs validated before processing
3. **Sandboxed Execution**: No arbitrary code execution
4. **Rate Limiting**: Configurable rate limits per client
