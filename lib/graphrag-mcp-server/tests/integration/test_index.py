"""Integration tests for index handlers."""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

from graphrag_mcp_server.handlers.index import (
    handle_build_index,
    handle_get_statistics,
    IndexBuildResult,
    IndexStatistics,
)
from graphrag_mcp_server.errors import IndexNotFoundError


class TestIndexBuildHandler:
    """Integration tests for index build handler."""

    @pytest.mark.asyncio
    async def test_build_index_full_mode(self):
        """Test building index in full mode."""
        with patch("graphrag_mcp_server.handlers.index.get_settings") as mock_settings:
            mock_settings.return_value.index_path = MagicMock()
            
            result = await handle_build_index(
                data_path="/tmp/test_data",
                mode="full",
            )

            # With mock, should return success (mock response)
            assert isinstance(result, IndexBuildResult)

    @pytest.mark.asyncio
    async def test_build_index_incremental_mode(self):
        """Test building index in incremental mode."""
        with patch("graphrag_mcp_server.handlers.index.get_settings") as mock_settings:
            mock_settings.return_value.index_path = MagicMock()

            result = await handle_build_index(
                data_path="/tmp/test_data",
                mode="incremental",
            )

            assert isinstance(result, IndexBuildResult)

    @pytest.mark.asyncio
    async def test_build_index_with_missing_data_path(self):
        """Test build index fails when data path is missing."""
        with patch("graphrag_mcp_server.handlers.index.get_settings") as mock_settings:
            mock_settings.return_value.index_path = MagicMock()

            result = await handle_build_index(
                data_path="/nonexistent/path",
                mode="full",
            )

            # Should return failure result
            assert isinstance(result, IndexBuildResult)
            assert result.success is False
            assert "not found" in result.message.lower()

    @pytest.mark.asyncio
    async def test_build_index_default_mode(self):
        """Test build index uses incremental mode by default."""
        with patch("graphrag_mcp_server.handlers.index.get_settings") as mock_settings:
            mock_settings.return_value.index_path = MagicMock()

            result = await handle_build_index(data_path="/tmp/test_data")

            assert isinstance(result, IndexBuildResult)


class TestIndexStatisticsHandler:
    """Integration tests for index statistics handler."""

    @pytest.mark.asyncio
    async def test_get_statistics_with_valid_index(self):
        """Test getting statistics from a valid index."""
        with patch("graphrag_mcp_server.handlers.index.get_settings") as mock_settings:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path.__truediv__ = lambda self, other: MagicMock(exists=lambda: False)
            mock_settings.return_value.index_path = mock_path

            result = await handle_get_statistics()

            assert isinstance(result, IndexStatistics)
            assert result.index_path is not None

    @pytest.mark.asyncio
    async def test_get_statistics_with_missing_index(self):
        """Test get statistics raises error when index is missing."""
        with patch("graphrag_mcp_server.handlers.index.get_settings") as mock_settings:
            mock_settings.return_value.index_path = MagicMock()
            mock_settings.return_value.index_path.exists.return_value = False
            mock_settings.return_value.index_path.__str__ = lambda x: "/missing/path"

            with pytest.raises(IndexNotFoundError):
                await handle_get_statistics()


class TestIndexBuildResult:
    """Tests for IndexBuildResult dataclass."""

    def test_successful_result_str(self):
        """Test string representation of successful result."""
        result = IndexBuildResult(
            success=True,
            message="Index built successfully",
            entity_count=100,
            relationship_count=250,
            community_count=10,
            duration_seconds=5.5,
        )

        result_str = str(result)
        assert "successfully" in result_str
        assert "100" in result_str
        assert "250" in result_str
        assert "10" in result_str
        assert "5.50" in result_str

    def test_failed_result_str(self):
        """Test string representation of failed result."""
        result = IndexBuildResult(
            success=False,
            message="Connection failed",
            entity_count=0,
            relationship_count=0,
            community_count=0,
            duration_seconds=0.1,
        )

        result_str = str(result)
        assert "failed" in result_str
        assert "Connection failed" in result_str


class TestIndexStatistics:
    """Tests for IndexStatistics dataclass."""

    def test_statistics_str(self):
        """Test string representation of statistics."""
        stats = IndexStatistics(
            entity_count=500,
            relationship_count=1200,
            community_count=25,
            text_unit_count=300,
            document_count=50,
            index_path="/path/to/index",
            last_updated=datetime(2025, 12, 5, 10, 30, 0),
        )

        stats_str = str(stats)
        assert "500" in stats_str
        assert "1200" in stats_str
        assert "25" in stats_str
        assert "300" in stats_str
        assert "50" in stats_str
        assert "/path/to/index" in stats_str

    def test_statistics_to_dict(self):
        """Test statistics to_dict conversion."""
        stats = IndexStatistics(
            entity_count=100,
            relationship_count=200,
            community_count=10,
            text_unit_count=50,
            document_count=5,
            index_path="/path/to/index",
            last_updated=datetime(2025, 12, 5, 10, 30, 0),
        )

        result = stats.to_dict()

        assert result["entity_count"] == 100
        assert result["relationship_count"] == 200
        assert result["community_count"] == 10
        assert result["text_unit_count"] == 50
        assert result["document_count"] == 5
        assert result["index_path"] == "/path/to/index"
        assert result["last_updated"] == "2025-12-05T10:30:00"

    def test_statistics_to_dict_without_timestamp(self):
        """Test statistics to_dict with None timestamp."""
        stats = IndexStatistics(
            entity_count=100,
            relationship_count=200,
            community_count=10,
            text_unit_count=50,
            document_count=5,
            index_path="/path/to/index",
            last_updated=None,
        )

        result = stats.to_dict()

        assert result["last_updated"] is None


class TestIndexWorkflows:
    """End-to-end workflow tests for index operations."""

    @pytest.mark.asyncio
    async def test_build_and_stats_workflow(self):
        """Test building index then getting statistics."""
        with patch("graphrag_mcp_server.handlers.index.get_settings") as mock_settings:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path.__truediv__ = lambda self, other: MagicMock(exists=lambda: False)
            mock_settings.return_value.index_path = mock_path

            # Step 1: Build index
            build_result = await handle_build_index(
                data_path="/tmp/test_data",
                mode="full",
            )
            assert isinstance(build_result, IndexBuildResult)

            # Step 2: Get statistics
            stats = await handle_get_statistics()
            assert isinstance(stats, IndexStatistics)

    @pytest.mark.asyncio
    async def test_incremental_build_sequence(self):
        """Test multiple incremental builds in sequence."""
        with patch("graphrag_mcp_server.handlers.index.get_settings") as mock_settings:
            mock_settings.return_value.index_path = MagicMock()

            results = []
            for i in range(3):
                result = await handle_build_index(
                    data_path="/tmp/test_data",
                    mode="incremental",
                )
                results.append(result)

            # All should be valid results
            assert len(results) == 3
            for result in results:
                assert isinstance(result, IndexBuildResult)
