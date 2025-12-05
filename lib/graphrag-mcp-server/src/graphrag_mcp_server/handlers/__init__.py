"""Handlers module for GraphRAG MCP Server."""

from graphrag_mcp_server.handlers.search import (
    SearchResult,
    handle_basic_search,
    handle_drift_search,
    handle_global_search,
    handle_local_search,
)
from graphrag_mcp_server.handlers.index import (
    IndexBuildResult,
    IndexStatistics,
    handle_build_index,
    handle_get_statistics,
)
from graphrag_mcp_server.handlers.streaming import (
    StreamChunk,
    StreamingSearchHandler,
    stream_global_search,
    stream_local_search,
    stream_drift_search,
    collect_stream,
)
from graphrag_mcp_server.handlers.formatters import (
    OutputFormat,
    FormattedResponse,
    ResponseFormatter,
    format_search_result,
    format_statistics,
)
from graphrag_mcp_server.handlers.cache import (
    CacheEntry,
    CacheStats,
    SearchCache,
    get_search_cache,
    cached_search,
)

__all__ = [
    # Search
    "SearchResult",
    "handle_basic_search",
    "handle_drift_search",
    "handle_global_search",
    "handle_local_search",
    # Index
    "IndexBuildResult",
    "IndexStatistics",
    "handle_build_index",
    "handle_get_statistics",
    # Streaming
    "StreamChunk",
    "StreamingSearchHandler",
    "stream_global_search",
    "stream_local_search",
    "stream_drift_search",
    "collect_stream",
    # Formatters
    "OutputFormat",
    "FormattedResponse",
    "ResponseFormatter",
    "format_search_result",
    "format_statistics",
    # Cache
    "CacheEntry",
    "CacheStats",
    "SearchCache",
    "get_search_cache",
    "cached_search",
]
