"""Integration tests for search handlers."""

import sys
import pytest
from unittest.mock import MagicMock, patch

from graphrag_mcp_server.handlers.search import (
    handle_global_search,
    handle_local_search,
    handle_drift_search,
    handle_basic_search,
    SearchResult,
)
from graphrag_mcp_server.errors import IndexNotFoundError, LLMProviderError


# Helper to create mock settings
def create_mock_settings(index_exists: bool = True):
    """Create mock settings for testing."""
    mock_settings = MagicMock()
    mock_settings.index_path = MagicMock()
    mock_settings.index_path.exists.return_value = index_exists
    mock_settings.index_path.__str__ = lambda x: "/mock/index/path"
    mock_settings.llm_provider.value = "openai"
    return mock_settings


@pytest.fixture
def mock_graphrag_api():
    """Fixture to disable graphrag.api imports, forcing mock response fallback."""
    # Remove graphrag.api from sys.modules to force ImportError in handlers
    original_modules = {}
    api_modules = [k for k in sys.modules.keys() if k.startswith("graphrag.api")]
    for mod in api_modules:
        original_modules[mod] = sys.modules.pop(mod)
    
    # Also block future imports
    with patch.dict(sys.modules, {"graphrag.api": None}):
        yield
    
    # Restore original modules
    sys.modules.update(original_modules)


class TestGlobalSearchHandler:
    """Integration tests for global search handler."""

    @pytest.mark.asyncio
    async def test_global_search_with_valid_index(self, mock_graphrag_api):
        """Test global search with a valid mock index."""
        with patch("graphrag_mcp_server.handlers.search.get_settings") as mock_get_settings:
            mock_get_settings.return_value = create_mock_settings(index_exists=True)
            
            result = await handle_global_search(
                query="What are the main themes?",
                community_level=2,
            )

            assert isinstance(result, SearchResult)
            assert result.metadata["search_type"] == "global"
            assert result.metadata.get("mock") is True  # Should be mock response

    @pytest.mark.asyncio
    async def test_global_search_with_missing_index(self):
        """Test global search raises error when index is missing."""
        with patch("graphrag_mcp_server.handlers.search.get_settings") as mock_get_settings:
            mock_get_settings.return_value = create_mock_settings(index_exists=False)

            with pytest.raises(IndexNotFoundError):
                await handle_global_search(query="test query")

    @pytest.mark.asyncio
    async def test_global_search_with_custom_response_type(self, mock_graphrag_api):
        """Test global search with custom response type."""
        with patch("graphrag_mcp_server.handlers.search.get_settings") as mock_get_settings:
            mock_get_settings.return_value = create_mock_settings(index_exists=True)
            
            result = await handle_global_search(
                query="Summarize the key points",
                response_type="Single Paragraph",
            )

            assert isinstance(result, SearchResult)


class TestLocalSearchHandler:
    """Integration tests for local search handler."""

    @pytest.mark.asyncio
    async def test_local_search_with_valid_index(self, mock_graphrag_api):
        """Test local search with a valid mock index."""
        with patch("graphrag_mcp_server.handlers.search.get_settings") as mock_get_settings:
            mock_get_settings.return_value = create_mock_settings(index_exists=True)

            result = await handle_local_search(
                query="Tell me about Microsoft",
                entity_types=["ORGANIZATION"],
            )

            assert isinstance(result, SearchResult)
            assert result.metadata["search_type"] == "local"
            assert result.metadata.get("mock") is True

    @pytest.mark.asyncio
    async def test_local_search_without_entity_filter(self, mock_graphrag_api):
        """Test local search without entity type filter."""
        with patch("graphrag_mcp_server.handlers.search.get_settings") as mock_get_settings:
            mock_get_settings.return_value = create_mock_settings(index_exists=True)

            result = await handle_local_search(query="Find related entities")

            assert isinstance(result, SearchResult)

    @pytest.mark.asyncio
    async def test_local_search_with_missing_index(self):
        """Test local search raises error when index is missing."""
        with patch("graphrag_mcp_server.handlers.search.get_settings") as mock_get_settings:
            mock_get_settings.return_value = create_mock_settings(index_exists=False)

            with pytest.raises(IndexNotFoundError):
                await handle_local_search(query="test query")


class TestDriftSearchHandler:
    """Integration tests for DRIFT search handler."""

    @pytest.mark.asyncio
    async def test_drift_search_with_valid_index(self, mock_graphrag_api):
        """Test DRIFT search with a valid mock index."""
        with patch("graphrag_mcp_server.handlers.search.get_settings") as mock_get_settings:
            mock_get_settings.return_value = create_mock_settings(index_exists=True)

            result = await handle_drift_search(
                query="Complex multi-faceted question",
                follow_up_depth=3,
            )

            assert isinstance(result, SearchResult)
            assert result.metadata["search_type"] == "drift"
            assert result.metadata.get("mock") is True

    @pytest.mark.asyncio
    async def test_drift_search_default_depth(self, mock_graphrag_api):
        """Test DRIFT search with default follow-up depth."""
        with patch("graphrag_mcp_server.handlers.search.get_settings") as mock_get_settings:
            mock_get_settings.return_value = create_mock_settings(index_exists=True)

            result = await handle_drift_search(query="Another query")

            assert isinstance(result, SearchResult)
            assert result.metadata["search_type"] == "drift"

    @pytest.mark.asyncio
    async def test_drift_search_with_missing_index(self):
        """Test DRIFT search raises error when index is missing."""
        with patch("graphrag_mcp_server.handlers.search.get_settings") as mock_get_settings:
            mock_get_settings.return_value = create_mock_settings(index_exists=False)

            with pytest.raises(IndexNotFoundError):
                await handle_drift_search(query="test query")


class TestBasicSearchHandler:
    """Integration tests for basic search handler."""

    @pytest.mark.asyncio
    async def test_basic_search_with_valid_index(self, mock_graphrag_api):
        """Test basic search with a valid mock index."""
        with patch("graphrag_mcp_server.handlers.search.get_settings") as mock_get_settings:
            mock_get_settings.return_value = create_mock_settings(index_exists=True)

            result = await handle_basic_search(
                query="Simple vector search",
                top_k=5,
            )

            assert isinstance(result, SearchResult)
            assert result.metadata["search_type"] == "basic"
            assert result.metadata.get("mock") is True

    @pytest.mark.asyncio
    async def test_basic_search_default_top_k(self, mock_graphrag_api):
        """Test basic search with default top_k."""
        with patch("graphrag_mcp_server.handlers.search.get_settings") as mock_get_settings:
            mock_get_settings.return_value = create_mock_settings(index_exists=True)

            result = await handle_basic_search(query="Another query")

            assert isinstance(result, SearchResult)
            assert result.metadata["search_type"] == "basic"

    @pytest.mark.asyncio
    async def test_basic_search_with_missing_index(self):
        """Test basic search raises error when index is missing."""
        with patch("graphrag_mcp_server.handlers.search.get_settings") as mock_get_settings:
            mock_get_settings.return_value = create_mock_settings(index_exists=False)

            with pytest.raises(IndexNotFoundError):
                await handle_basic_search(query="test query")


class TestSearchResultFormat:
    """Tests for SearchResult format and serialization."""

    def test_search_result_str(self):
        """Test SearchResult string representation."""
        result = SearchResult(
            response="This is a test response",
            context_data={"key": "value"},
            metadata={"search_type": "global"},
        )

        assert str(result) == "This is a test response"

    def test_search_result_with_empty_context(self):
        """Test SearchResult with empty context."""
        result = SearchResult(
            response="Response without context",
            context_data={},
            metadata={"search_type": "local"},
        )

        assert result.context_data == {}
        assert result.response == "Response without context"


class TestSearchWorkflows:
    """End-to-end workflow tests for search operations."""

    @pytest.mark.asyncio
    async def test_multiple_search_types_sequence(self, mock_graphrag_api):
        """Test executing multiple search types in sequence."""
        with patch("graphrag_mcp_server.handlers.search.get_settings") as mock_get_settings:
            mock_get_settings.return_value = create_mock_settings(index_exists=True)

            global_result = await handle_global_search(query="Overview question")
            local_result = await handle_local_search(query="Specific entity question")
            basic_result = await handle_basic_search(query="Simple search")

            # All should return valid results
            assert global_result.metadata["search_type"] == "global"
            assert local_result.metadata["search_type"] == "local"
            assert basic_result.metadata["search_type"] == "basic"

    @pytest.mark.asyncio
    async def test_search_with_different_community_levels(self, mock_graphrag_api):
        """Test global search with different community levels."""
        with patch("graphrag_mcp_server.handlers.search.get_settings") as mock_get_settings:
            mock_get_settings.return_value = create_mock_settings(index_exists=True)

            results = []
            for level in [0, 1, 2, 3]:
                result = await handle_global_search(
                    query="Test query",
                    community_level=level,
                )
                results.append(result)

            # All should be mock responses
            for result in results:
                assert result.metadata["search_type"] == "global"
                assert result.metadata.get("mock") is True
