# API Reference

Complete reference for all GraphRAG MCP Server tools and prompts.

## Tools

### graphrag_global_search

Execute a global search across the knowledge graph using community-aware summarization.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `query` | string | Yes | - | The search query |
| `community_level` | integer | No | 2 | Community hierarchy level (0-4) |
| `response_type` | string | No | "Multiple Paragraphs" | Response format |

**Response Types:**
- `"Single Paragraph"` - Concise single paragraph
- `"Multiple Paragraphs"` - Detailed multiple paragraphs (default)
- `"Single Sentence"` - Brief one-sentence answer
- `"List of 3-7 Points"` - Bulleted list format

**Example:**

```json
{
  "name": "graphrag_global_search",
  "arguments": {
    "query": "What are the main themes in this document collection?",
    "community_level": 2,
    "response_type": "Multiple Paragraphs"
  }
}
```

**Response:**

```json
{
  "response": "The document collection covers several interconnected themes...",
  "context_data": {
    "communities": [...],
    "sources": [...]
  },
  "metadata": {
    "search_type": "global",
    "community_level": 2
  }
}
```

---

### graphrag_local_search

Execute a local search focused on specific entities and their relationships.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `query` | string | Yes | - | The search query |
| `entity_types` | array[string] | No | null | Filter by entity types |
| `response_type` | string | No | "Multiple Paragraphs" | Response format |

**Entity Types:**
- `"PERSON"` - People and individuals
- `"ORGANIZATION"` - Companies, institutions
- `"LOCATION"` - Places and geographic entities
- `"EVENT"` - Events and occurrences
- `"CONCEPT"` - Abstract concepts

**Example:**

```json
{
  "name": "graphrag_local_search",
  "arguments": {
    "query": "Tell me about Microsoft's partnerships",
    "entity_types": ["ORGANIZATION"]
  }
}
```

---

### graphrag_drift_search

Execute a DRIFT (Dynamic Reasoning with Iterative Follow-up Tracing) search for complex queries.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `query` | string | Yes | - | The search query |
| `follow_up_depth` | integer | No | 2 | Number of follow-up iterations |

**Example:**

```json
{
  "name": "graphrag_drift_search",
  "arguments": {
    "query": "How do climate change policies affect different economic sectors?",
    "follow_up_depth": 3
  }
}
```

---

### graphrag_basic_search

Execute a direct vector similarity search without graph enhancement.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `query` | string | Yes | - | The search query |
| `top_k` | integer | No | 10 | Number of results to return |

**Example:**

```json
{
  "name": "graphrag_basic_search",
  "arguments": {
    "query": "renewable energy technologies",
    "top_k": 5
  }
}
```

---

### graphrag_build_index

Build or update the knowledge graph index from source documents.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `data_path` | string | Yes | - | Path to source documents |
| `mode` | string | No | "incremental" | Build mode |

**Build Modes:**
- `"full"` - Complete rebuild of the index
- `"incremental"` - Update only changed documents

**Example:**

```json
{
  "name": "graphrag_build_index",
  "arguments": {
    "data_path": "/path/to/documents",
    "mode": "incremental"
  }
}
```

**Response:**

```json
{
  "success": true,
  "entities_indexed": 1500,
  "relationships_indexed": 4200,
  "communities_built": 25,
  "build_time_seconds": 120.5,
  "message": "Index built successfully"
}
```

---

### graphrag_get_statistics

Get statistics and health information about the current index.

**Parameters:**

None

**Example:**

```json
{
  "name": "graphrag_get_statistics",
  "arguments": {}
}
```

**Response:**

```json
{
  "index_path": "/path/to/index",
  "entity_count": 1500,
  "relationship_count": 4200,
  "community_count": 25,
  "document_count": 150,
  "last_updated": "2024-01-15T10:30:00Z",
  "index_size_mb": 256.5,
  "health_status": "healthy"
}
```

---

## Prompts

### graphrag_explore

Interactive prompt for exploratory knowledge graph analysis.

**Arguments:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `topic` | string | Yes | Topic to explore |

**Usage:**

```json
{
  "name": "graphrag_explore",
  "arguments": {
    "topic": "artificial intelligence trends"
  }
}
```

---

### graphrag_analyze

Deep analysis prompt for specific topics with multi-perspective examination.

**Arguments:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `topic` | string | Yes | Topic to analyze |
| `perspective` | string | No | Analysis perspective |

---

### graphrag_summarize

Summarization prompt for generating concise summaries of indexed content.

**Arguments:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `scope` | string | No | Scope of summarization |

---

## Error Responses

All tools may return error responses in the following format:

```json
{
  "error": {
    "code": "INDEX_NOT_FOUND",
    "message": "No index found at the specified path",
    "details": {
      "path": "/path/to/missing/index"
    }
  }
}
```

**Error Codes:**

| Code | Description |
|------|-------------|
| `INDEX_NOT_FOUND` | Index does not exist |
| `CONFIGURATION_ERROR` | Invalid configuration |
| `LLM_PROVIDER_ERROR` | LLM API error |
| `RATE_LIMIT_EXCEEDED` | Rate limit hit |
| `VALIDATION_ERROR` | Invalid parameters |
