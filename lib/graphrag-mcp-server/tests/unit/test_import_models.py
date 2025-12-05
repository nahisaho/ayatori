"""Unit tests for import module models."""

from uuid import UUID

import pytest

from graphrag_mcp_server.document_import.models import (
    ChunkCorrelation,
    CorrelationGraph,
    CorrelationType,
    DocumentMetadata,
    ElementType,
    ImportConfig,
    ImportResult,
    Language,
    NormalizedElement,
    TextChunk,
)


class TestElementType:
    """Tests for ElementType enum."""
    
    def test_element_types_exist(self):
        """Test that all expected element types exist."""
        assert ElementType.TITLE == "Title"
        assert ElementType.NARRATIVE_TEXT == "NarrativeText"
        assert ElementType.LIST_ITEM == "ListItem"
        assert ElementType.TABLE == "Table"
        assert ElementType.CODE == "Code"


class TestLanguage:
    """Tests for Language enum."""
    
    def test_language_codes(self):
        """Test language code values."""
        assert Language.JAPANESE == "ja"
        assert Language.ENGLISH == "en"
        assert Language.CHINESE == "zh"
        assert Language.KOREAN == "ko"
        assert Language.UNKNOWN == "unknown"


class TestCorrelationType:
    """Tests for CorrelationType enum."""
    
    def test_correlation_types(self):
        """Test correlation type values."""
        assert CorrelationType.ADJACENT == "adjacent"
        assert CorrelationType.SEMANTIC == "semantic"
        assert CorrelationType.HIERARCHICAL == "hierarchical"


class TestNormalizedElement:
    """Tests for NormalizedElement model."""
    
    def test_create_element(self):
        """Test creating a normalized element."""
        elem = NormalizedElement(
            element_type=ElementType.NARRATIVE_TEXT,
            text="This is a test paragraph.",
            position=0,
        )
        
        assert isinstance(elem.id, UUID)
        assert elem.element_type == ElementType.NARRATIVE_TEXT
        assert elem.text == "This is a test paragraph."
        assert elem.position == 0
        assert elem.language == Language.UNKNOWN
    
    def test_element_with_metadata(self):
        """Test element with additional metadata."""
        elem = NormalizedElement(
            element_type=ElementType.TITLE,
            text="Chapter 1",
            position=0,
            page_number=1,
            heading_level=1,
            language=Language.ENGLISH,
        )
        
        assert elem.page_number == 1
        assert elem.heading_level == 1
        assert elem.language == Language.ENGLISH
    
    def test_element_immutable(self):
        """Test that elements are immutable (frozen)."""
        elem = NormalizedElement(
            element_type=ElementType.NARRATIVE_TEXT,
            text="Test",
            position=0,
        )
        
        with pytest.raises(Exception):  # ValidationError or TypeError
            elem.text = "Modified"


class TestTextChunk:
    """Tests for TextChunk model."""
    
    def test_create_chunk(self):
        """Test creating a text chunk."""
        from uuid import uuid4
        doc_id = uuid4()
        
        chunk = TextChunk(
            text="This is chunk content.",
            language=Language.ENGLISH,
            document_id=doc_id,
            chunk_index=0,
            start_char=0,
            end_char=22,
            token_count=4,
        )
        
        assert isinstance(chunk.id, UUID)
        assert chunk.text == "This is chunk content."
        assert chunk.language == Language.ENGLISH
        assert chunk.document_id == doc_id
        assert chunk.chunk_index == 0
        assert chunk.token_count == 4
    
    def test_chunk_with_sources(self):
        """Test chunk with source element tracking."""
        from uuid import uuid4
        doc_id = uuid4()
        source_ids = [uuid4(), uuid4()]
        
        chunk = TextChunk(
            text="Combined text from elements.",
            language=Language.JAPANESE,
            source_elements=source_ids,
            document_id=doc_id,
            chunk_index=0,
            start_char=0,
            end_char=28,
            token_count=5,
        )
        
        assert len(chunk.source_elements) == 2
        assert chunk.source_elements == source_ids


class TestChunkCorrelation:
    """Tests for ChunkCorrelation model."""
    
    def test_create_correlation(self):
        """Test creating a correlation."""
        from uuid import uuid4
        source_id = uuid4()
        target_id = uuid4()
        
        correlation = ChunkCorrelation(
            source_chunk_id=source_id,
            target_chunk_id=target_id,
            correlation_type=CorrelationType.ADJACENT,
            weight=1.0,
        )
        
        assert correlation.source_chunk_id == source_id
        assert correlation.target_chunk_id == target_id
        assert correlation.correlation_type == CorrelationType.ADJACENT
        assert correlation.weight == 1.0
    
    def test_correlation_weight_bounds(self):
        """Test that correlation weight is bounded 0-1."""
        from uuid import uuid4
        
        # Valid weight
        correlation = ChunkCorrelation(
            source_chunk_id=uuid4(),
            target_chunk_id=uuid4(),
            correlation_type=CorrelationType.SEMANTIC,
            weight=0.5,
        )
        assert correlation.weight == 0.5
        
        # Weight should be validated
        with pytest.raises(ValueError):
            ChunkCorrelation(
                source_chunk_id=uuid4(),
                target_chunk_id=uuid4(),
                correlation_type=CorrelationType.SEMANTIC,
                weight=1.5,  # Out of bounds
            )


class TestCorrelationGraph:
    """Tests for CorrelationGraph model."""
    
    def test_create_graph(self):
        """Test creating a correlation graph."""
        from uuid import uuid4
        doc_id = uuid4()
        
        graph = CorrelationGraph(
            document_id=doc_id,
            node_count=3,
        )
        
        assert graph.document_id == doc_id
        assert graph.node_count == 3
        assert graph.edge_count == 0
        assert graph.density == 0.0
    
    def test_add_correlation(self):
        """Test adding correlations to graph."""
        from uuid import uuid4
        doc_id = uuid4()
        node1, node2 = uuid4(), uuid4()
        
        graph = CorrelationGraph(
            document_id=doc_id,
            nodes=[node1, node2],
            node_count=2,
        )
        
        correlation = ChunkCorrelation(
            source_chunk_id=node1,
            target_chunk_id=node2,
            correlation_type=CorrelationType.ADJACENT,
        )
        
        graph.add_correlation(correlation)
        
        assert graph.edge_count == 1
        assert len(graph.edges) == 1


class TestImportConfig:
    """Tests for ImportConfig model."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ImportConfig()
        
        assert config.chunk_size == 1000
        assert config.chunk_overlap == 100
        assert config.auto_detect_language is True
        assert config.default_language == Language.ENGLISH
        assert config.build_correlation_graph is True
        assert config.semantic_similarity_threshold == 0.7
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = ImportConfig(
            chunk_size=500,
            chunk_overlap=50,
            default_language=Language.JAPANESE,
            build_correlation_graph=False,
        )
        
        assert config.chunk_size == 500
        assert config.chunk_overlap == 50
        assert config.default_language == Language.JAPANESE
        assert config.build_correlation_graph is False
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Chunk size too small
        with pytest.raises(ValueError):
            ImportConfig(chunk_size=50)  # Min is 100
        
        # Negative overlap
        with pytest.raises(ValueError):
            ImportConfig(chunk_overlap=-10)


class TestImportResult:
    """Tests for ImportResult model."""
    
    def test_create_result(self, tmp_path):
        """Test creating an import result."""
        from pathlib import Path
        
        metadata = DocumentMetadata(
            source_path=tmp_path / "test.pdf",
            file_name="test.pdf",
            file_type=".pdf",
            file_size=1024,
        )
        
        result = ImportResult(
            document_metadata=metadata,
        )
        
        assert result.status == "success"
        assert result.element_count == 0
        assert result.chunk_count == 0
        assert result.total_tokens == 0
    
    def test_add_chunk(self, tmp_path):
        """Test adding chunks to result."""
        from uuid import uuid4
        
        metadata = DocumentMetadata(
            source_path=tmp_path / "test.pdf",
            file_name="test.pdf",
            file_type=".pdf",
            file_size=1024,
        )
        
        result = ImportResult(document_metadata=metadata)
        
        chunk = TextChunk(
            text="Test chunk",
            language=Language.ENGLISH,
            document_id=uuid4(),
            chunk_index=0,
            start_char=0,
            end_char=10,
            token_count=2,
        )
        
        result.add_chunk(chunk)
        
        assert result.chunk_count == 1
        assert result.total_tokens == 2
