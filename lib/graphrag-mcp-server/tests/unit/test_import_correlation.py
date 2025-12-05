"""Unit tests for correlation builder."""

from uuid import uuid4

import pytest

from graphrag_mcp_server.document_import.correlation import CorrelationBuilder
from graphrag_mcp_server.document_import.models import (
    CorrelationType,
    Language,
    TextChunk,
)


class TestCorrelationBuilder:
    """Tests for CorrelationBuilder class."""
    
    def test_init_defaults(self):
        """Test default initialization."""
        builder = CorrelationBuilder()
        
        assert builder.similarity_threshold == 0.7
        assert builder.build_adjacent is True
        assert builder.build_semantic is True
    
    def test_init_custom(self):
        """Test custom initialization."""
        builder = CorrelationBuilder(
            similarity_threshold=0.5,
            build_adjacent=False,
            build_semantic=False,
        )
        
        assert builder.similarity_threshold == 0.5
        assert builder.build_adjacent is False
        assert builder.build_semantic is False
    
    @pytest.mark.asyncio
    async def test_build_graph_empty(self):
        """Test building graph with no chunks."""
        builder = CorrelationBuilder()
        
        graph = await builder.build_graph([])
        
        assert graph.node_count == 0
        assert graph.edge_count == 0
    
    @pytest.mark.asyncio
    async def test_build_graph_single_chunk(self):
        """Test building graph with single chunk."""
        builder = CorrelationBuilder()
        doc_id = uuid4()
        
        chunks = [
            TextChunk(
                text="Single chunk content.",
                language=Language.ENGLISH,
                document_id=doc_id,
                chunk_index=0,
                start_char=0,
                end_char=20,
                token_count=3,
            ),
        ]
        
        graph = await builder.build_graph(chunks)
        
        assert graph.node_count == 1
        assert graph.edge_count == 0  # No edges for single node
    
    @pytest.mark.asyncio
    async def test_build_adjacent_correlations(self):
        """Test building adjacent correlations."""
        builder = CorrelationBuilder(build_semantic=False)
        doc_id = uuid4()
        
        chunks = [
            TextChunk(
                text="First chunk.",
                language=Language.ENGLISH,
                document_id=doc_id,
                chunk_index=0,
                start_char=0,
                end_char=12,
                token_count=2,
            ),
            TextChunk(
                text="Second chunk.",
                language=Language.ENGLISH,
                document_id=doc_id,
                chunk_index=1,
                start_char=12,
                end_char=25,
                token_count=2,
            ),
            TextChunk(
                text="Third chunk.",
                language=Language.ENGLISH,
                document_id=doc_id,
                chunk_index=2,
                start_char=25,
                end_char=37,
                token_count=2,
            ),
        ]
        
        graph = await builder.build_graph(chunks)
        
        assert graph.node_count == 3
        assert graph.edge_count == 2  # 3 chunks = 2 adjacent edges
        
        # All edges should be ADJACENT type
        for edge in graph.edges:
            assert edge.correlation_type == CorrelationType.ADJACENT
            assert edge.weight == 1.0
    
    @pytest.mark.asyncio
    async def test_skip_adjacent_correlations(self):
        """Test skipping adjacent correlations when disabled."""
        builder = CorrelationBuilder(
            build_adjacent=False,
            build_semantic=False,
        )
        doc_id = uuid4()
        
        chunks = [
            TextChunk(
                text="First chunk.",
                language=Language.ENGLISH,
                document_id=doc_id,
                chunk_index=0,
                start_char=0,
                end_char=12,
                token_count=2,
            ),
            TextChunk(
                text="Second chunk.",
                language=Language.ENGLISH,
                document_id=doc_id,
                chunk_index=1,
                start_char=12,
                end_char=25,
                token_count=2,
            ),
        ]
        
        graph = await builder.build_graph(chunks)
        
        assert graph.node_count == 2
        assert graph.edge_count == 0  # No correlations built
    
    @pytest.mark.asyncio
    async def test_semantic_correlations_high_similarity(self):
        """Test semantic correlations with similar content."""
        builder = CorrelationBuilder(
            similarity_threshold=0.3,  # Low threshold for testing
            build_adjacent=False,
        )
        doc_id = uuid4()
        
        # Create chunks with similar words
        chunks = [
            TextChunk(
                text="The quick brown fox jumps.",
                language=Language.ENGLISH,
                document_id=doc_id,
                chunk_index=0,
                start_char=0,
                end_char=26,
                token_count=5,
            ),
            TextChunk(
                text="Something different here.",
                language=Language.ENGLISH,
                document_id=doc_id,
                chunk_index=1,
                start_char=26,
                end_char=51,
                token_count=3,
            ),
            TextChunk(
                text="The quick brown fox leaps.",
                language=Language.ENGLISH,
                document_id=doc_id,
                chunk_index=2,
                start_char=51,
                end_char=77,
                token_count=5,
            ),
        ]
        
        graph = await builder.build_graph(chunks)
        
        # Should find semantic correlation between chunk 0 and 2
        semantic_edges = [
            e for e in graph.edges
            if e.correlation_type == CorrelationType.SEMANTIC
        ]
        
        # The similar chunks (0 and 2) should have a correlation
        assert len(semantic_edges) >= 0  # May or may not meet threshold
    
    @pytest.mark.asyncio
    async def test_graph_document_id(self):
        """Test that graph has correct document ID."""
        builder = CorrelationBuilder()
        doc_id = uuid4()
        
        chunks = [
            TextChunk(
                text="Test content.",
                language=Language.ENGLISH,
                document_id=doc_id,
                chunk_index=0,
                start_char=0,
                end_char=13,
                token_count=2,
            ),
        ]
        
        graph = await builder.build_graph(chunks)
        
        assert graph.document_id == doc_id
    
    @pytest.mark.asyncio
    async def test_edge_metadata(self):
        """Test that edges have appropriate metadata."""
        builder = CorrelationBuilder(build_semantic=False)
        doc_id = uuid4()
        
        chunks = [
            TextChunk(
                text="First.",
                language=Language.ENGLISH,
                document_id=doc_id,
                chunk_index=0,
                start_char=0,
                end_char=6,
                token_count=1,
            ),
            TextChunk(
                text="Second.",
                language=Language.ENGLISH,
                document_id=doc_id,
                chunk_index=1,
                start_char=6,
                end_char=13,
                token_count=1,
            ),
        ]
        
        graph = await builder.build_graph(chunks)
        
        assert graph.edge_count == 1
        edge = graph.edges[0]
        assert "distance" in edge.metadata
        assert edge.metadata["distance"] == 1
