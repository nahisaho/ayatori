# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-12-05

### Added

- Initial release of GraphRAG MCP Server
- **MCP Tools**:
  - `global_search`: Map-reduce style search across community summaries
  - `local_search`: Entity-based search with relationship traversal
  - `drift_search`: DRIFT search combining global and local methods
  - `basic_search`: Vector similarity search on text units
  - `build_index`: Build and update GraphRAG indexes
  - `get_statistics`: Get index statistics
- **MCP Resources**:
  - `graphrag://entities`: List of entities in the knowledge graph
  - `graphrag://communities`: List of communities (entity clusters)
  - `graphrag://relationships`: List of relationships between entities
  - `graphrag://statistics`: Index statistics
- **MCP Prompts**:
  - `analyze_topic`: Analyze a topic using the knowledge graph
  - `explore_entity`: Explore an entity and its relationships
  - `summarize_community`: Get a summary of a community
  - `compare_entities`: Compare two or more entities
- **Transport Support**:
  - stdio transport for VS Code, Cursor, and other MCP clients
  - SSE (Server-Sent Events) transport for web clients
- **LLM Provider Support**:
  - OpenAI
  - Azure OpenAI
  - Anthropic
  - Ollama (local LLM)
- **Vector Store Support**:
  - LanceDB (local)
  - Azure AI Search (cloud)
- CLI commands: `serve`, `index`, `query`, `stats`
- Comprehensive test suite (249+ unit tests, 13 integration tests)
- VS Code MCP configuration examples

### Dependencies

- Python 3.11+
- GraphRAG 2.0+
- MCP SDK 1.0+
- Esperanto (for unified LLM access)

[Unreleased]: https://github.com/your-org/graphrag-mcp-server/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/your-org/graphrag-mcp-server/releases/tag/v0.1.0
