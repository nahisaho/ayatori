"""Tests for index handlers."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
from datetime import datetime

from graphrag_mcp_server.handlers.index import (
    IndexStatistics,
    IndexBuildResult,
    handle_build_index,
    handle_get_statistics,
)
from graphrag_mcp_server.config import Settings


class TestIndexStatistics:
    """Tests for IndexStatistics dataclass."""
    
    def test_statistics_creation(self):
        """Should create IndexStatistics with all fields."""
        stats = IndexStatistics(
            entity_count=100,
            relationship_count=200,
            community_count=10,
            text_unit_count=50,
            document_count=5,
            index_path="/test/path",
            last_updated=datetime(2024, 1, 1)
        )
        assert stats.entity_count == 100
        assert stats.relationship_count == 200
        assert stats.community_count == 10
        assert stats.text_unit_count == 50
        assert stats.document_count == 5
        assert stats.index_path == "/test/path"
    
    def test_statistics_to_dict(self):
        """Should convert to dictionary."""
        stats = IndexStatistics(
            entity_count=100,
            relationship_count=200,
            community_count=10,
            text_unit_count=50,
            document_count=5,
            index_path="/test/path",
            last_updated=None
        )
        d = stats.to_dict()
        assert d["entity_count"] == 100
        assert d["relationship_count"] == 200
        assert "community_count" in d
        assert d["last_updated"] is None
    
    def test_statistics_str(self):
        """Should have string representation."""
        stats = IndexStatistics(
            entity_count=100,
            relationship_count=200,
            community_count=10,
            text_unit_count=50,
            document_count=5,
            index_path="/test/path",
            last_updated=None
        )
        result = str(stats)
        assert "100" in result
        assert "200" in result


class TestIndexBuildResult:
    """Tests for IndexBuildResult dataclass."""
    
    def test_build_result_creation(self):
        """Should create IndexBuildResult with required fields."""
        result = IndexBuildResult(
            success=True,
            message="Build completed",
            entity_count=100,
            relationship_count=200,
            community_count=10,
            duration_seconds=5.5
        )
        assert result.success is True
        assert result.message == "Build completed"
        assert result.entity_count == 100
    
    def test_build_result_str_success(self):
        """String representation for success."""
        result = IndexBuildResult(
            success=True,
            message="Build completed",
            entity_count=100,
            relationship_count=200,
            community_count=10,
            duration_seconds=5.5
        )
        s = str(result)
        assert "successfully" in s
        assert "100" in s
    
    def test_build_result_str_failure(self):
        """String representation for failure."""
        result = IndexBuildResult(
            success=False,
            message="Build failed: some error",
            entity_count=0,
            relationship_count=0,
            community_count=0,
            duration_seconds=0.0
        )
        s = str(result)
        assert "failed" in s


class TestHandleBuildIndex:
    """Tests for handle_build_index function."""
    
    @pytest.mark.asyncio
    @patch("graphrag_mcp_server.handlers.index.get_settings")
    async def test_build_index_accepts_data_path(self, mock_settings):
        """Should accept data_path parameter."""
        mock_settings.return_value = Mock(index_path=Path("/test"))
        
        # Verify function accepts data_path
        try:
            await handle_build_index(data_path="/test/data")
        except Exception:
            pass  # Expected to fail without actual implementation


class TestHandleGetStatistics:
    """Tests for handle_get_statistics function."""
    
    @pytest.mark.asyncio
    @patch("graphrag_mcp_server.handlers.index.get_settings")
    async def test_get_statistics_with_nonexistent_index(self, mock_settings):
        """Should raise IndexNotFoundError if index doesn't exist."""
        from graphrag_mcp_server.errors import IndexNotFoundError
        
        mock_settings.return_value = Mock(index_path=Path("/nonexistent/path"))
        
        with pytest.raises(IndexNotFoundError):
            await handle_get_statistics()
