"""Unit tests for Vector Store providers module."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from graphrag_mcp_server.config import VectorStoreType
from graphrag_mcp_server.providers.vectorstore import (
    VectorStoreConfig,
    SearchResult,
    BaseVectorStoreAdapter,
    LanceDBAdapter,
    AzureAISearchAdapter,
    MockVectorStoreAdapter,
    create_vector_store_adapter,
    get_graphrag_vector_store_config,
)
from graphrag_mcp_server.errors import IndexNotFoundError


# ============================================================================
# VectorStoreConfig Tests
# ============================================================================

class TestVectorStoreConfig:
    """Tests for VectorStoreConfig dataclass."""

    def test_create_minimal_config(self):
        """Test creating config with minimal parameters."""
        config = VectorStoreConfig(
            store_type=VectorStoreType.LANCEDB,
        )
        
        assert config.store_type == VectorStoreType.LANCEDB
        assert config.connection_string is None
        assert config.index_name == "graphrag_index"
        assert config.embedding_dimension == 1536

    def test_create_full_config(self):
        """Test creating config with all parameters."""
        config = VectorStoreConfig(
            store_type=VectorStoreType.AZURE_SEARCH,
            connection_string="https://test.search.windows.net",
            api_key="test-key",
            index_name="custom-index",
            embedding_dimension=768,
        )
        
        assert config.store_type == VectorStoreType.AZURE_SEARCH
        assert config.connection_string == "https://test.search.windows.net"
        assert config.api_key == "test-key"
        assert config.index_name == "custom-index"
        assert config.embedding_dimension == 768

    def test_to_dict_minimal(self):
        """Test converting minimal config to dict."""
        config = VectorStoreConfig(
            store_type=VectorStoreType.LANCEDB,
        )
        
        result = config.to_dict()
        
        assert result["type"] == "lancedb"
        assert result["index_name"] == "graphrag_index"
        assert "connection_string" not in result

    def test_to_dict_full(self):
        """Test converting full config to dict."""
        config = VectorStoreConfig(
            store_type=VectorStoreType.AZURE_SEARCH,
            connection_string="https://test.search.windows.net",
            api_key="test-key",
        )
        
        result = config.to_dict()
        
        assert result["type"] == "azure_search"
        assert result["connection_string"] == "https://test.search.windows.net"
        assert result["api_key"] == "test-key"


# ============================================================================
# SearchResult Tests
# ============================================================================

class TestSearchResult:
    """Tests for SearchResult dataclass."""

    def test_create_search_result(self):
        """Test creating a search result."""
        result = SearchResult(
            id="doc-1",
            text="Test document",
            score=0.95,
            metadata={"source": "test"},
        )
        
        assert result.id == "doc-1"
        assert result.text == "Test document"
        assert result.score == 0.95
        assert result.metadata == {"source": "test"}

    def test_create_minimal_result(self):
        """Test creating result with empty metadata."""
        result = SearchResult(
            id="doc-1",
            text="Test",
            score=0.5,
            metadata={},
        )
        
        assert result.metadata == {}


# ============================================================================
# LanceDBAdapter Tests
# ============================================================================

class TestLanceDBAdapter:
    """Tests for LanceDB adapter."""

    @pytest.fixture
    def config(self):
        """Create LanceDB config."""
        return VectorStoreConfig(
            store_type=VectorStoreType.LANCEDB,
            index_name="test_index",
        )

    def test_validate_config_always_true(self, config):
        """Test LanceDB config always validates (minimal requirements)."""
        adapter = LanceDBAdapter(config)
        assert adapter.validate_config() is True

    def test_custom_db_path(self, config):
        """Test setting custom database path."""
        adapter = LanceDBAdapter(config, db_path=Path("/tmp/custom_db"))
        assert adapter.db_path == Path("/tmp/custom_db")

    def test_default_db_path(self, config):
        """Test default database path."""
        adapter = LanceDBAdapter(config)
        assert adapter.db_path == Path("./lancedb")


# ============================================================================
# AzureAISearchAdapter Tests
# ============================================================================

class TestAzureAISearchAdapter:
    """Tests for Azure AI Search adapter."""

    @pytest.fixture
    def valid_config(self):
        """Create valid Azure AI Search config."""
        return VectorStoreConfig(
            store_type=VectorStoreType.AZURE_SEARCH,
            connection_string="https://test.search.windows.net",
            api_key="test-key",
            index_name="test-index",
        )

    @pytest.fixture
    def invalid_config(self):
        """Create invalid Azure AI Search config."""
        return VectorStoreConfig(
            store_type=VectorStoreType.AZURE_SEARCH,
        )

    def test_validate_config_valid(self, valid_config):
        """Test config validation with valid config."""
        adapter = AzureAISearchAdapter(valid_config)
        assert adapter.validate_config() is True

    def test_validate_config_missing_connection(self, invalid_config):
        """Test config validation with missing connection string."""
        adapter = AzureAISearchAdapter(invalid_config)
        assert adapter.validate_config() is False

    @pytest.mark.asyncio
    async def test_search_invalid_config(self, invalid_config):
        """Test search with invalid config raises error."""
        adapter = AzureAISearchAdapter(invalid_config)
        
        with pytest.raises(IndexNotFoundError):
            await adapter.search([0.0] * 1536)

    @pytest.mark.asyncio
    async def test_upsert_invalid_config(self, invalid_config):
        """Test upsert with invalid config raises error."""
        adapter = AzureAISearchAdapter(invalid_config)
        
        with pytest.raises(IndexNotFoundError):
            await adapter.upsert("doc-1", [0.0] * 1536, "Test text")

    @pytest.mark.asyncio
    async def test_delete_invalid_config(self, invalid_config):
        """Test delete with invalid config returns False."""
        adapter = AzureAISearchAdapter(invalid_config)
        
        result = await adapter.delete("doc-1")
        assert result is False


# ============================================================================
# MockVectorStoreAdapter Tests
# ============================================================================

class TestMockVectorStoreAdapter:
    """Tests for mock vector store adapter."""

    @pytest.fixture
    def config(self):
        """Create mock config."""
        return VectorStoreConfig(
            store_type=VectorStoreType.LANCEDB,
        )

    def test_validate_config_always_true(self, config):
        """Test mock adapter always validates."""
        adapter = MockVectorStoreAdapter(config)
        assert adapter.validate_config() is True

    @pytest.mark.asyncio
    async def test_upsert_and_search(self, config):
        """Test upserting and searching."""
        adapter = MockVectorStoreAdapter(config)
        
        # Upsert some documents
        await adapter.upsert("doc-1", [0.0] * 10, "First document")
        await adapter.upsert("doc-2", [1.0] * 10, "Second document")
        
        # Search should return the documents
        results = await adapter.search([0.5] * 10, top_k=10)
        
        assert len(results) == 2
        assert all(isinstance(r, SearchResult) for r in results)

    @pytest.mark.asyncio
    async def test_delete_existing(self, config):
        """Test deleting existing document."""
        adapter = MockVectorStoreAdapter(config)
        
        await adapter.upsert("doc-1", [0.0] * 10, "Test document")
        result = await adapter.delete("doc-1")
        
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, config):
        """Test deleting nonexistent document."""
        adapter = MockVectorStoreAdapter(config)
        
        result = await adapter.delete("nonexistent")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_search_empty_store(self, config):
        """Test searching empty store."""
        adapter = MockVectorStoreAdapter(config)
        
        results = await adapter.search([0.0] * 10)
        
        assert results == []

    @pytest.mark.asyncio
    async def test_search_respects_top_k(self, config):
        """Test search respects top_k parameter."""
        adapter = MockVectorStoreAdapter(config)
        
        # Add multiple documents
        for i in range(10):
            await adapter.upsert(f"doc-{i}", [float(i)] * 10, f"Document {i}")
        
        results = await adapter.search([0.0] * 10, top_k=3)
        
        assert len(results) == 3


# ============================================================================
# Factory Function Tests
# ============================================================================

class TestCreateVectorStoreAdapter:
    """Tests for create_vector_store_adapter factory function."""

    def test_create_lancedb_adapter(self):
        """Test creating LanceDB adapter."""
        config = VectorStoreConfig(
            store_type=VectorStoreType.LANCEDB,
        )
        
        adapter = create_vector_store_adapter(config)
        
        assert isinstance(adapter, LanceDBAdapter)

    def test_create_azure_search_adapter(self):
        """Test creating Azure AI Search adapter."""
        config = VectorStoreConfig(
            store_type=VectorStoreType.AZURE_SEARCH,
            connection_string="https://test.search.windows.net",
            api_key="test-key",
        )
        
        adapter = create_vector_store_adapter(config)
        
        assert isinstance(adapter, AzureAISearchAdapter)

    def test_create_from_settings(self):
        """Test creating adapter from settings."""
        mock_settings = MagicMock()
        mock_settings.vector_store_type = VectorStoreType.LANCEDB
        mock_settings.vector_store_connection_string = None
        mock_settings.vector_store_api_key = None
        
        with patch(
            "graphrag_mcp_server.providers.vectorstore.get_settings",
            return_value=mock_settings,
        ):
            adapter = create_vector_store_adapter()
            assert isinstance(adapter, LanceDBAdapter)


class TestGetGraphRAGVectorStoreConfig:
    """Tests for get_graphrag_vector_store_config function."""

    def test_get_lancedb_config(self):
        """Test getting LanceDB config."""
        mock_settings = MagicMock()
        mock_settings.vector_store_type = VectorStoreType.LANCEDB
        mock_settings.vector_store_connection_string = None
        mock_settings.vector_store_api_key = None
        
        with patch(
            "graphrag_mcp_server.providers.vectorstore.get_settings",
            return_value=mock_settings,
        ):
            config = get_graphrag_vector_store_config()
            
            assert config["type"] == "lancedb"
            assert "connection_string" not in config

    def test_get_azure_search_config(self):
        """Test getting Azure AI Search config."""
        mock_settings = MagicMock()
        mock_settings.vector_store_type = VectorStoreType.AZURE_SEARCH
        mock_settings.vector_store_connection_string = "https://test.search.windows.net"
        mock_settings.vector_store_api_key = "test-key"
        
        with patch(
            "graphrag_mcp_server.providers.vectorstore.get_settings",
            return_value=mock_settings,
        ):
            config = get_graphrag_vector_store_config()
            
            assert config["type"] == "azure_search"
            assert config["connection_string"] == "https://test.search.windows.net"
            assert config["api_key"] == "test-key"


# ============================================================================
# Integration Tests
# ============================================================================

class TestVectorStoreIntegration:
    """Integration tests for vector store operations."""

    @pytest.mark.asyncio
    async def test_mock_store_full_workflow(self):
        """Test complete workflow with mock store."""
        config = VectorStoreConfig(
            store_type=VectorStoreType.LANCEDB,
            index_name="test",
        )
        adapter = MockVectorStoreAdapter(config)
        
        # Insert documents
        docs = [
            ("doc-1", [0.1] * 10, "First test document"),
            ("doc-2", [0.2] * 10, "Second test document"),
            ("doc-3", [0.3] * 10, "Third test document"),
        ]
        
        for doc_id, embedding, text in docs:
            await adapter.upsert(doc_id, embedding, text, {"source": "test"})
        
        # Search
        results = await adapter.search([0.15] * 10, top_k=2)
        assert len(results) == 2
        
        # Delete one
        deleted = await adapter.delete("doc-1")
        assert deleted is True
        
        # Search again
        results = await adapter.search([0.15] * 10, top_k=10)
        assert len(results) == 2
        assert "doc-1" not in [r.id for r in results]
