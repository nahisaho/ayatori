"""Search handlers for GraphRAG MCP Server.

These handlers call GraphRAG API directly without custom abstraction
(Article VIII compliance).
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from graphrag_mcp_server.config import get_settings
from graphrag_mcp_server.errors import IndexNotFoundError, LLMProviderError

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result container."""

    response: str
    context_data: dict[str, Any]
    metadata: dict[str, Any]

    def __str__(self) -> str:
        """Return response as string."""
        return self.response


async def handle_global_search(
    query: str,
    community_level: int = 2,
    response_type: str = "Multiple Paragraphs",
) -> SearchResult:
    """Execute global search using GraphRAG API directly.

    Args:
        query: Search query
        community_level: Community hierarchy level
        response_type: Desired response format

    Returns:
        SearchResult with response and context data.

    Raises:
        IndexNotFoundError: If index is not found
        LLMProviderError: If LLM provider fails
    """
    settings = get_settings()
    index_path = settings.index_path

    if not index_path.exists():
        raise IndexNotFoundError(str(index_path))

    try:
        # Article VIII: Direct GraphRAG API call without wrapper
        from graphrag.api import global_search

        result = await global_search(
            root_dir=str(index_path),
            community_level=community_level,
            response_type=response_type,
            query=query,
        )

        return SearchResult(
            response=result.response,
            context_data=result.context_data if hasattr(result, "context_data") else {},
            metadata={
                "search_type": "global",
                "community_level": community_level,
            },
        )

    except ImportError:
        # Fallback for development/testing when graphrag is not fully configured
        logger.warning("GraphRAG API not available, returning mock response")
        return SearchResult(
            response=f"[Mock Global Search Response]\nQuery: {query}\nCommunity Level: {community_level}",
            context_data={},
            metadata={"search_type": "global", "mock": True},
        )
    except Exception as e:
        logger.exception("Global search failed")
        raise LLMProviderError(
            provider=settings.llm_provider.value,
            original_error=str(e),
            retryable=True,
        ) from e


async def handle_local_search(
    query: str,
    entity_types: Optional[list[str]] = None,
    response_type: str = "Multiple Paragraphs",
) -> SearchResult:
    """Execute local search using GraphRAG API directly.

    Args:
        query: Search query
        entity_types: Filter by entity types
        response_type: Desired response format

    Returns:
        SearchResult with response and context data.
    """
    settings = get_settings()
    index_path = settings.index_path

    if not index_path.exists():
        raise IndexNotFoundError(str(index_path))

    try:
        # Article VIII: Direct GraphRAG API call
        from graphrag.api import local_search

        result = await local_search(
            root_dir=str(index_path),
            query=query,
            response_type=response_type,
        )

        return SearchResult(
            response=result.response,
            context_data=result.context_data if hasattr(result, "context_data") else {},
            metadata={
                "search_type": "local",
                "entity_types": entity_types,
            },
        )

    except ImportError:
        logger.warning("GraphRAG API not available, returning mock response")
        return SearchResult(
            response=f"[Mock Local Search Response]\nQuery: {query}\nEntity Types: {entity_types}",
            context_data={},
            metadata={"search_type": "local", "mock": True},
        )
    except Exception as e:
        logger.exception("Local search failed")
        raise LLMProviderError(
            provider=settings.llm_provider.value,
            original_error=str(e),
            retryable=True,
        ) from e


async def handle_drift_search(
    query: str,
    follow_up_depth: int = 2,
) -> SearchResult:
    """Execute DRIFT search using GraphRAG API directly.

    Args:
        query: Search query
        follow_up_depth: Depth of follow-up questions

    Returns:
        SearchResult with response and context data.
    """
    settings = get_settings()
    index_path = settings.index_path

    if not index_path.exists():
        raise IndexNotFoundError(str(index_path))

    try:
        # Article VIII: Direct GraphRAG API call
        from graphrag.api import drift_search

        result = await drift_search(
            root_dir=str(index_path),
            query=query,
        )

        return SearchResult(
            response=result.response,
            context_data=result.context_data if hasattr(result, "context_data") else {},
            metadata={
                "search_type": "drift",
                "follow_up_depth": follow_up_depth,
            },
        )

    except ImportError:
        logger.warning("GraphRAG API not available, returning mock response")
        return SearchResult(
            response=f"[Mock DRIFT Search Response]\nQuery: {query}\nFollow-up Depth: {follow_up_depth}",
            context_data={},
            metadata={"search_type": "drift", "mock": True},
        )
    except Exception as e:
        logger.exception("DRIFT search failed")
        raise LLMProviderError(
            provider=settings.llm_provider.value,
            original_error=str(e),
            retryable=True,
        ) from e


async def handle_basic_search(
    query: str,
    top_k: int = 10,
) -> SearchResult:
    """Execute basic vector similarity search.

    Args:
        query: Search query
        top_k: Number of results to return

    Returns:
        SearchResult with response and context data.
    """
    settings = get_settings()
    index_path = settings.index_path

    if not index_path.exists():
        raise IndexNotFoundError(str(index_path))

    try:
        # Article VIII: Direct GraphRAG API call
        from graphrag.api import basic_search

        result = await basic_search(
            root_dir=str(index_path),
            query=query,
            top_k=top_k,
        )

        return SearchResult(
            response=result.response if hasattr(result, "response") else str(result),
            context_data=result.context_data if hasattr(result, "context_data") else {},
            metadata={
                "search_type": "basic",
                "top_k": top_k,
            },
        )

    except ImportError:
        logger.warning("GraphRAG API not available, returning mock response")
        return SearchResult(
            response=f"[Mock Basic Search Response]\nQuery: {query}\nTop-K: {top_k}",
            context_data={},
            metadata={"search_type": "basic", "mock": True},
        )
    except Exception as e:
        logger.exception("Basic search failed")
        raise LLMProviderError(
            provider=settings.llm_provider.value,
            original_error=str(e),
            retryable=True,
        ) from e
