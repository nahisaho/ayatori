"""Streaming handlers for GraphRAG MCP Server.

Provides async streaming support for search operations,
enabling real-time response delivery to clients.
"""

import asyncio
import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class StreamChunk:
    """A chunk of streaming response data."""

    content: str
    chunk_type: str = "content"  # content, context, metadata, done
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "content": self.content,
            "type": self.chunk_type,
            "metadata": self.metadata or {},
        }


class StreamingSearchHandler:
    """Handler for streaming search responses.

    Wraps search operations to provide chunked streaming output,
    enabling progressive response delivery.
    """

    def __init__(self, chunk_size: int = 100):
        """Initialize streaming handler.

        Args:
            chunk_size: Approximate size of content chunks in characters.
        """
        self.chunk_size = chunk_size

    async def stream_response(
        self, response: str, context_data: dict[str, Any] | None = None
    ) -> AsyncGenerator[StreamChunk, None]:
        """Stream a response in chunks.

        Args:
            response: The full response text to stream.
            context_data: Optional context data to include at the end.

        Yields:
            StreamChunk objects containing response fragments.
        """
        if not response:
            yield StreamChunk(content="", chunk_type="done")
            return

        # Split response into paragraphs for natural chunking
        paragraphs = response.split("\n\n")
        
        for i, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                continue
                
            # For long paragraphs, split into smaller chunks
            if len(paragraph) > self.chunk_size:
                for chunk in self._chunk_text(paragraph):
                    yield StreamChunk(content=chunk, chunk_type="content")
                    await asyncio.sleep(0)  # Allow other tasks to run
            else:
                yield StreamChunk(
                    content=paragraph + ("\n\n" if i < len(paragraphs) - 1 else ""),
                    chunk_type="content",
                )
                await asyncio.sleep(0)

        # Send context data if available
        if context_data:
            yield StreamChunk(
                content="",
                chunk_type="context",
                metadata={"context_data": context_data},
            )

        # Signal completion
        yield StreamChunk(content="", chunk_type="done")

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into chunks at word boundaries.

        Args:
            text: Text to split into chunks.

        Returns:
            List of text chunks.
        """
        chunks = []
        words = text.split(" ")
        current_chunk = []
        current_length = 0

        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > self.chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk) + " ")
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += word_length

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks


async def stream_global_search(
    query: str,
    community_level: int = 2,
    response_type: str = "Multiple Paragraphs",
) -> AsyncGenerator[StreamChunk, None]:
    """Stream global search results.

    Args:
        query: Search query.
        community_level: Community hierarchy level.
        response_type: Desired response format.

    Yields:
        StreamChunk objects with search results.
    """
    from graphrag_mcp_server.config import get_settings
    from graphrag_mcp_server.errors import IndexNotFoundError

    settings = get_settings()
    index_path = settings.index_path

    if not index_path.exists():
        raise IndexNotFoundError(str(index_path))

    handler = StreamingSearchHandler()

    try:
        # Import and call GraphRAG API
        from graphrag.api import global_search

        result = await global_search(
            root_dir=str(index_path),
            community_level=community_level,
            response_type=response_type,
            query=query,
        )

        response_text = result.response if hasattr(result, "response") else str(result)
        context_data = result.context_data if hasattr(result, "context_data") else {}

        async for chunk in handler.stream_response(response_text, context_data):
            yield chunk

    except ImportError:
        # Fallback for development
        logger.warning("GraphRAG not available, using mock response")
        mock_response = f"[Mock Global Search]\nQuery: {query}\nCommunity Level: {community_level}"
        async for chunk in handler.stream_response(mock_response):
            yield chunk


async def stream_local_search(
    query: str,
    community_level: int = 2,
) -> AsyncGenerator[StreamChunk, None]:
    """Stream local search results.

    Args:
        query: Search query.
        community_level: Community hierarchy level.

    Yields:
        StreamChunk objects with search results.
    """
    from graphrag_mcp_server.config import get_settings
    from graphrag_mcp_server.errors import IndexNotFoundError

    settings = get_settings()
    index_path = settings.index_path

    if not index_path.exists():
        raise IndexNotFoundError(str(index_path))

    handler = StreamingSearchHandler()

    try:
        from graphrag.api import local_search

        result = await local_search(
            root_dir=str(index_path),
            community_level=community_level,
            query=query,
        )

        response_text = result.response if hasattr(result, "response") else str(result)
        context_data = result.context_data if hasattr(result, "context_data") else {}

        async for chunk in handler.stream_response(response_text, context_data):
            yield chunk

    except ImportError:
        logger.warning("GraphRAG not available, using mock response")
        mock_response = f"[Mock Local Search]\nQuery: {query}"
        async for chunk in handler.stream_response(mock_response):
            yield chunk


async def stream_drift_search(
    query: str,
    community_level: int = 2,
) -> AsyncGenerator[StreamChunk, None]:
    """Stream DRIFT search results.

    Args:
        query: Search query.
        community_level: Community hierarchy level.

    Yields:
        StreamChunk objects with search results.
    """
    from graphrag_mcp_server.config import get_settings
    from graphrag_mcp_server.errors import IndexNotFoundError

    settings = get_settings()
    index_path = settings.index_path

    if not index_path.exists():
        raise IndexNotFoundError(str(index_path))

    handler = StreamingSearchHandler()

    try:
        from graphrag.api import drift_search

        result = await drift_search(
            root_dir=str(index_path),
            community_level=community_level,
            query=query,
        )

        response_text = result.response if hasattr(result, "response") else str(result)
        context_data = result.context_data if hasattr(result, "context_data") else {}

        async for chunk in handler.stream_response(response_text, context_data):
            yield chunk

    except ImportError:
        logger.warning("GraphRAG not available, using mock response")
        mock_response = f"[Mock DRIFT Search]\nQuery: {query}"
        async for chunk in handler.stream_response(mock_response):
            yield chunk


async def collect_stream(
    stream: AsyncGenerator[StreamChunk, None]
) -> tuple[str, dict[str, Any]]:
    """Collect all chunks from a stream into a complete response.

    Utility function for non-streaming clients.

    Args:
        stream: Async generator of StreamChunk objects.

    Returns:
        Tuple of (complete_response, context_data).
    """
    content_parts = []
    context_data = {}

    async for chunk in stream:
        if chunk.chunk_type == "content":
            content_parts.append(chunk.content)
        elif chunk.chunk_type == "context":
            context_data = chunk.metadata.get("context_data", {}) if chunk.metadata else {}
        elif chunk.chunk_type == "done":
            break

    return "".join(content_parts), context_data
