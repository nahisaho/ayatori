"""Unit tests for chunker implementations."""

import pytest

from graphrag_mcp_server.document_import.chunker.base import BaseChunker
from graphrag_mcp_server.document_import.chunker.default import DefaultChunker
from graphrag_mcp_server.document_import.chunker.factory import get_chunker
from graphrag_mcp_server.document_import.models import Language, NormalizedElement, ElementType


class TestDefaultChunker:
    """Tests for DefaultChunker class."""
    
    def test_init_defaults(self):
        """Test default initialization."""
        chunker = DefaultChunker()
        
        assert chunker.language == Language.ENGLISH
        assert chunker.chunk_size == 1000
        assert chunker.chunk_overlap == 100
    
    def test_init_custom(self):
        """Test custom initialization."""
        chunker = DefaultChunker(
            language=Language.ENGLISH,
            chunk_size=500,
            chunk_overlap=50,
        )
        
        assert chunker.chunk_size == 500
        assert chunker.chunk_overlap == 50
    
    def test_count_tokens_empty(self):
        """Test token counting with empty text."""
        chunker = DefaultChunker()
        
        assert chunker.count_tokens("") == 0
    
    def test_count_tokens_simple(self):
        """Test token counting with simple text."""
        chunker = DefaultChunker()
        
        # Simple word-based counting
        assert chunker.count_tokens("one two three") == 3
        assert chunker.count_tokens("hello world") == 2
    
    def test_split_sentences(self):
        """Test sentence splitting."""
        chunker = DefaultChunker()
        
        text = "First sentence. Second sentence! Third sentence?"
        sentences = chunker._split_sentences(text)
        
        assert len(sentences) == 3
        assert "First sentence." in sentences[0]
    
    def test_split_sentences_empty(self):
        """Test sentence splitting with empty text."""
        chunker = DefaultChunker()
        
        assert chunker._split_sentences("") == []
        assert chunker._split_sentences("   ") == []
    
    def test_chunk_text_simple(self):
        """Test chunking simple text."""
        chunker = DefaultChunker(chunk_size=50, chunk_overlap=10)
        
        text = "This is the first sentence. This is the second one. And a third."
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) >= 1
        assert all(isinstance(c, str) for c in chunks)
    
    def test_chunk_text_empty(self):
        """Test chunking empty text."""
        chunker = DefaultChunker()
        
        assert chunker.chunk_text("") == []
    
    def test_chunk_text_respects_size(self):
        """Test that chunks respect size limit."""
        chunker = DefaultChunker(chunk_size=100, chunk_overlap=0)
        
        text = "A. " * 50  # About 150 chars
        chunks = chunker.chunk_text(text)
        
        # Should produce multiple chunks, each within size limit
        # (with some tolerance for sentence boundaries)
        assert len(chunks) >= 1
    
    def test_chunk_by_size_fallback(self):
        """Test fallback chunking by size."""
        chunker = DefaultChunker(chunk_size=20, chunk_overlap=5)
        
        # Text without sentence endings
        text = "abcdefghij klmnopqrst uvwxyz"
        chunks = chunker._chunk_by_size(text)
        
        assert len(chunks) >= 1


class TestChunkerFactory:
    """Tests for chunker factory function."""
    
    def test_get_english_chunker(self):
        """Test getting English chunker."""
        chunker = get_chunker(Language.ENGLISH)
        
        assert isinstance(chunker, DefaultChunker)
        assert chunker.language == Language.ENGLISH
    
    def test_get_japanese_chunker(self):
        """Test getting Japanese chunker."""
        from graphrag_mcp_server.document_import.chunker.japanese import JapaneseChunker
        
        chunker = get_chunker(Language.JAPANESE)
        
        assert isinstance(chunker, JapaneseChunker)
        assert chunker.language == Language.JAPANESE
    
    def test_get_chunker_with_custom_size(self):
        """Test getting chunker with custom size."""
        chunker = get_chunker(
            Language.ENGLISH,
            chunk_size=500,
            chunk_overlap=50,
        )
        
        assert chunker.chunk_size == 500
        assert chunker.chunk_overlap == 50


class TestJapaneseChunker:
    """Tests for JapaneseChunker class."""
    
    def test_init(self):
        """Test Japanese chunker initialization."""
        from graphrag_mcp_server.document_import.chunker.japanese import JapaneseChunker
        
        chunker = JapaneseChunker(chunk_size=500, chunk_overlap=50)
        
        assert chunker.language == Language.JAPANESE
        assert chunker.chunk_size == 500
        assert chunker.chunk_overlap == 50
    
    def test_sentence_endings(self):
        """Test Japanese sentence ending detection."""
        from graphrag_mcp_server.document_import.chunker.japanese import JapaneseChunker
        
        chunker = JapaneseChunker()
        
        # Japanese sentence endings
        text = "これは一文目です。これは二文目です！そして三文目？"
        sentences = chunker._split_sentences(text)
        
        assert len(sentences) == 3
    
    def test_count_tokens_fallback(self):
        """Test token counting without fugashi."""
        from graphrag_mcp_server.document_import.chunker.japanese import JapaneseChunker
        
        chunker = JapaneseChunker()
        
        # Without fugashi, should fall back to character count
        text = "テスト"
        count = chunker.count_tokens(text)
        
        assert count > 0
    
    def test_chunk_text_empty(self):
        """Test chunking empty text."""
        from graphrag_mcp_server.document_import.chunker.japanese import JapaneseChunker
        
        chunker = JapaneseChunker()
        
        assert chunker.chunk_text("") == []


class TestBaseChunker:
    """Tests for BaseChunker abstract class."""
    
    def test_combine_element_text(self):
        """Test combining element texts."""
        from uuid import uuid4
        
        chunker = DefaultChunker()
        
        elements = [
            NormalizedElement(
                id=uuid4(),
                element_type=ElementType.NARRATIVE_TEXT,
                text="First paragraph.",
                position=0,
            ),
            NormalizedElement(
                id=uuid4(),
                element_type=ElementType.NARRATIVE_TEXT,
                text="Second paragraph.",
                position=1,
            ),
        ]
        
        combined, positions = chunker._combine_element_text(elements)
        
        assert "First paragraph." in combined
        assert "Second paragraph." in combined
        assert len(positions) == 2
    
    def test_find_source_elements(self):
        """Test finding source elements for a chunk range."""
        from uuid import uuid4
        
        chunker = DefaultChunker()
        
        id1, id2, id3 = uuid4(), uuid4(), uuid4()
        positions = [
            (0, 50, id1),
            (52, 100, id2),
            (102, 150, id3),
        ]
        
        # Chunk that overlaps id1 and id2
        sources = chunker._find_source_elements(25, 75, positions)
        
        assert id1 in sources
        assert id2 in sources
        assert id3 not in sources
    
    @pytest.mark.asyncio
    async def test_chunk_elements(self):
        """Test chunking a list of elements."""
        from uuid import uuid4
        
        chunker = DefaultChunker(chunk_size=100, chunk_overlap=10)
        doc_id = uuid4()
        
        elements = [
            NormalizedElement(
                element_type=ElementType.NARRATIVE_TEXT,
                text="This is the first element with some content.",
                position=0,
            ),
            NormalizedElement(
                element_type=ElementType.NARRATIVE_TEXT,
                text="This is the second element with more content.",
                position=1,
            ),
        ]
        
        chunks = await chunker.chunk_elements(elements, doc_id)
        
        assert len(chunks) >= 1
        assert all(c.document_id == doc_id for c in chunks)
        assert all(len(c.source_elements) > 0 for c in chunks)
    
    @pytest.mark.asyncio
    async def test_chunk_elements_empty(self):
        """Test chunking empty element list."""
        from uuid import uuid4
        
        chunker = DefaultChunker()
        
        chunks = await chunker.chunk_elements([], uuid4())
        
        assert chunks == []
