"""Tests for streaming handlers."""

import pytest
from unittest.mock import patch, AsyncMock

from graphrag_mcp_server.handlers.streaming import (
    StreamChunk,
    StreamingSearchHandler,
    stream_global_search,
    stream_local_search,
    stream_drift_search,
    collect_stream,
)


class TestStreamChunk:
    """Tests for StreamChunk dataclass."""

    def test_chunk_creation(self):
        """Should create chunk with default type."""
        chunk = StreamChunk(content="test")
        assert chunk.content == "test"
        assert chunk.chunk_type == "content"
        assert chunk.metadata is None

    def test_chunk_with_type(self):
        """Should accept custom type."""
        chunk = StreamChunk(content="", chunk_type="done")
        assert chunk.chunk_type == "done"

    def test_chunk_to_dict(self):
        """Should convert to dictionary."""
        chunk = StreamChunk(
            content="test",
            chunk_type="context",
            metadata={"key": "value"},
        )
        d = chunk.to_dict()
        assert d["content"] == "test"
        assert d["type"] == "context"
        assert d["metadata"] == {"key": "value"}


class TestStreamingSearchHandler:
    """Tests for StreamingSearchHandler."""

    def test_handler_creation(self):
        """Should create handler with default chunk size."""
        handler = StreamingSearchHandler()
        assert handler.chunk_size == 100

    def test_handler_custom_chunk_size(self):
        """Should accept custom chunk size."""
        handler = StreamingSearchHandler(chunk_size=50)
        assert handler.chunk_size == 50

    @pytest.mark.asyncio
    async def test_stream_empty_response(self):
        """Should yield done chunk for empty response."""
        handler = StreamingSearchHandler()
        chunks = []
        async for chunk in handler.stream_response(""):
            chunks.append(chunk)
        
        assert len(chunks) == 1
        assert chunks[0].chunk_type == "done"

    @pytest.mark.asyncio
    async def test_stream_short_response(self):
        """Should yield content then done."""
        handler = StreamingSearchHandler()
        chunks = []
        async for chunk in handler.stream_response("Hello world"):
            chunks.append(chunk)
        
        assert len(chunks) >= 2
        assert chunks[0].chunk_type == "content"
        assert chunks[-1].chunk_type == "done"

    @pytest.mark.asyncio
    async def test_stream_with_context(self):
        """Should include context chunk."""
        handler = StreamingSearchHandler()
        chunks = []
        async for chunk in handler.stream_response("Response", {"key": "value"}):
            chunks.append(chunk)
        
        context_chunks = [c for c in chunks if c.chunk_type == "context"]
        assert len(context_chunks) == 1

    @pytest.mark.asyncio
    async def test_stream_multiline_response(self):
        """Should handle multi-paragraph responses."""
        handler = StreamingSearchHandler()
        response = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
        chunks = []
        async for chunk in handler.stream_response(response):
            chunks.append(chunk)
        
        content_chunks = [c for c in chunks if c.chunk_type == "content"]
        assert len(content_chunks) >= 1


class TestCollectStream:
    """Tests for collect_stream utility."""

    @pytest.mark.asyncio
    async def test_collect_simple_stream(self):
        """Should collect all content chunks."""
        handler = StreamingSearchHandler()
        stream = handler.stream_response("Hello world")
        content, context = await collect_stream(stream)
        
        assert "Hello world" in content

    @pytest.mark.asyncio
    async def test_collect_stream_with_context(self):
        """Should return context data."""
        handler = StreamingSearchHandler()
        stream = handler.stream_response("Response", {"entities": [1, 2, 3]})
        content, context = await collect_stream(stream)
        
        assert context.get("entities") == [1, 2, 3]


class TestStreamGlobalSearch:
    """Tests for stream_global_search function."""

    @pytest.mark.asyncio
    @patch("graphrag_mcp_server.config.get_settings")
    async def test_raises_for_nonexistent_index(self, mock_settings):
        """Should raise IndexNotFoundError."""
        from pathlib import Path
        from unittest.mock import Mock
        from graphrag_mcp_server.errors import IndexNotFoundError

        mock_settings.return_value = Mock(index_path=Path("/nonexistent"))
        
        with pytest.raises(IndexNotFoundError):
            async for _ in stream_global_search("test query"):
                pass


class TestStreamLocalSearch:
    """Tests for stream_local_search function."""

    @pytest.mark.asyncio
    @patch("graphrag_mcp_server.config.get_settings")
    async def test_raises_for_nonexistent_index(self, mock_settings):
        """Should raise IndexNotFoundError."""
        from pathlib import Path
        from unittest.mock import Mock
        from graphrag_mcp_server.errors import IndexNotFoundError

        mock_settings.return_value = Mock(index_path=Path("/nonexistent"))
        
        with pytest.raises(IndexNotFoundError):
            async for _ in stream_local_search("test query"):
                pass


class TestStreamDriftSearch:
    """Tests for stream_drift_search function."""

    @pytest.mark.asyncio
    @patch("graphrag_mcp_server.config.get_settings")
    async def test_raises_for_nonexistent_index(self, mock_settings):
        """Should raise IndexNotFoundError."""
        from pathlib import Path
        from unittest.mock import Mock
        from graphrag_mcp_server.errors import IndexNotFoundError

        mock_settings.return_value = Mock(index_path=Path("/nonexistent"))
        
        with pytest.raises(IndexNotFoundError):
            async for _ in stream_drift_search("test query"):
                pass
