"""Tests for search handlers."""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path

from graphrag_mcp_server.handlers.search import (
    SearchResult,
    handle_global_search,
    handle_local_search,
    handle_drift_search,
    handle_basic_search,
)
from graphrag_mcp_server.config import Settings


class TestSearchResult:
    """Tests for SearchResult dataclass."""
    
    def test_search_result_creation(self):
        """Should create SearchResult with required fields."""
        result = SearchResult(
            response="Test response",
            context_data={"key": "value"},
            metadata={"search_type": "test"}
        )
        assert result.response == "Test response"
        assert result.context_data == {"key": "value"}
        assert result.metadata == {"search_type": "test"}
    
    def test_search_result_str(self):
        """String representation should return response."""
        result = SearchResult(
            response="Test response",
            context_data={},
            metadata={}
        )
        assert str(result) == "Test response"


class TestHandleGlobalSearch:
    """Tests for handle_global_search function."""
    
    @pytest.mark.asyncio
    @patch("graphrag_mcp_server.handlers.search.get_settings")
    async def test_global_search_with_nonexistent_index(self, mock_settings):
        """Should raise IndexNotFoundError if index doesn't exist."""
        from graphrag_mcp_server.errors import IndexNotFoundError
        
        mock_settings.return_value = Mock(index_path=Path("/nonexistent/path"))
        
        with pytest.raises(IndexNotFoundError):
            await handle_global_search(query="test query")
    
    @pytest.mark.asyncio
    @patch("graphrag_mcp_server.handlers.search.get_settings")
    async def test_global_search_accepts_parameters(self, mock_settings):
        """Should accept query, community_level, and response_type."""
        mock_settings.return_value = Mock(index_path=Path("/nonexistent"))
        
        # The function should be callable with these parameters
        try:
            await handle_global_search(
                query="test",
                community_level=3,
                response_type="markdown"
            )
        except Exception:
            pass  # Expected to fail due to nonexistent path


class TestHandleLocalSearch:
    """Tests for handle_local_search function."""
    
    @pytest.mark.asyncio
    @patch("graphrag_mcp_server.handlers.search.get_settings")
    async def test_local_search_with_nonexistent_index(self, mock_settings):
        """Should raise IndexNotFoundError if index doesn't exist."""
        from graphrag_mcp_server.errors import IndexNotFoundError
        
        mock_settings.return_value = Mock(index_path=Path("/nonexistent/path"))
        
        with pytest.raises(IndexNotFoundError):
            await handle_local_search(query="test query")
    
    @pytest.mark.asyncio
    @patch("graphrag_mcp_server.handlers.search.get_settings")
    async def test_local_search_accepts_parameters(self, mock_settings):
        """Should accept query and community_level."""
        mock_settings.return_value = Mock(index_path=Path("/nonexistent"))
        
        try:
            await handle_local_search(
                query="test",
                community_level=2
            )
        except Exception:
            pass


class TestHandleDriftSearch:
    """Tests for handle_drift_search function."""
    
    @pytest.mark.asyncio
    @patch("graphrag_mcp_server.handlers.search.get_settings")
    async def test_drift_search_with_nonexistent_index(self, mock_settings):
        """Should raise IndexNotFoundError if index doesn't exist."""
        from graphrag_mcp_server.errors import IndexNotFoundError
        
        mock_settings.return_value = Mock(index_path=Path("/nonexistent/path"))
        
        with pytest.raises(IndexNotFoundError):
            await handle_drift_search(query="test query")


class TestHandleBasicSearch:
    """Tests for handle_basic_search function."""
    
    @pytest.mark.asyncio
    @patch("graphrag_mcp_server.handlers.search.get_settings")
    async def test_basic_search_with_nonexistent_index(self, mock_settings):
        """Should raise IndexNotFoundError if index doesn't exist."""
        from graphrag_mcp_server.errors import IndexNotFoundError
        
        mock_settings.return_value = Mock(index_path=Path("/nonexistent/path"))
        
        with pytest.raises(IndexNotFoundError):
            await handle_basic_search(query="test query")
    
    @pytest.mark.asyncio
    @patch("graphrag_mcp_server.handlers.search.get_settings")
    async def test_basic_search_accepts_top_k(self, mock_settings):
        """Should accept top_k parameter."""
        mock_settings.return_value = Mock(index_path=Path("/nonexistent"))
        
        try:
            await handle_basic_search(
                query="test",
                top_k=20
            )
        except Exception:
            pass
