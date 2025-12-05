"""Unit tests for DocumentImporter."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from graphrag_mcp_server.document_import.importer import DocumentImporter
from graphrag_mcp_server.document_import.models import (
    ElementType,
    ImportConfig,
    Language,
    NormalizedElement,
    TextChunk,
)


class TestDocumentImporter:
    """Tests for DocumentImporter class."""
    
    def test_init_defaults(self):
        """Test default initialization."""
        importer = DocumentImporter()
        
        assert importer.config.chunk_size == 1000
        assert importer.config.chunk_overlap == 100
        assert importer.config.default_language == Language.ENGLISH
        assert importer.parser is not None
        assert importer.normalizer is not None
    
    def test_init_custom_config(self):
        """Test custom initialization with config."""
        config = ImportConfig(
            chunk_size=1024,
            chunk_overlap=100,
            default_language=Language.JAPANESE,
        )
        importer = DocumentImporter(config=config)
        
        assert importer.config.chunk_size == 1024
        assert importer.config.chunk_overlap == 100
        assert importer.config.default_language == Language.JAPANESE
    
    @pytest.mark.asyncio
    async def test_import_document_not_found(self):
        """Test importing non-existent file."""
        importer = DocumentImporter()
        
        with pytest.raises(FileNotFoundError):
            await importer.import_document(Path("/nonexistent/file.txt"))
    
    @pytest.mark.asyncio
    async def test_import_document_success(self, tmp_path):
        """Test successful document import."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("This is a test document. It has multiple sentences.")
        
        importer = DocumentImporter()
        
        # Mock the internal components with correct field names
        mock_elements = [
            NormalizedElement(
                text="This is a test document.",
                element_type=ElementType.NARRATIVE_TEXT,
                language=Language.ENGLISH,
                position=0,
            ),
            NormalizedElement(
                text="It has multiple sentences.",
                element_type=ElementType.NARRATIVE_TEXT,
                language=Language.ENGLISH,
                position=1,
            ),
        ]
        
        mock_chunks = [
            TextChunk(
                text="This is a test document.",
                language=Language.ENGLISH,
                document_id=uuid4(),
                chunk_index=0,
                start_char=0,
                end_char=24,
                token_count=5,
            ),
        ]
        
        # Mock raw unstructured elements
        mock_raw_element = MagicMock()
        mock_raw_element.text = "Test content"
        mock_raw_element.category = "NarrativeText"
        mock_raw_element.metadata = MagicMock()
        
        # Mock async methods
        mock_chunker = MagicMock()
        mock_chunker.chunk_elements = AsyncMock(return_value=mock_chunks)
        
        with patch.object(importer.parser, "parse_async", new=AsyncMock(return_value=[mock_raw_element])):
            with patch.object(importer.normalizer, "normalize_all", return_value=mock_elements):
                with patch.object(importer, "_get_chunker", return_value=mock_chunker):
                    result = await importer.import_document(test_file)
        
        assert result is not None
        assert result.id is not None
        assert result.document_metadata.source_path == test_file
    
    @pytest.mark.asyncio
    async def test_import_document_with_japanese(self, tmp_path):
        """Test import with Japanese content."""
        test_file = tmp_path / "japanese.txt"
        test_file.write_text("これはテストドキュメントです。日本語の文章が含まれています。")
        
        importer = DocumentImporter()
        
        # Create mock element with detected Japanese
        mock_element = NormalizedElement(
            text="これはテストドキュメントです。",
            element_type=ElementType.NARRATIVE_TEXT,
            language=Language.JAPANESE,
            position=0,
        )
        
        mock_chunk = TextChunk(
            text="これはテストドキュメントです。",
            language=Language.JAPANESE,
            document_id=uuid4(),
            chunk_index=0,
            start_char=0,
            end_char=15,
            token_count=10,
        )
        
        mock_raw = MagicMock()
        mock_raw.text = "テスト"
        mock_raw.category = "NarrativeText"
        mock_raw.metadata = MagicMock()
        
        mock_chunker = MagicMock()
        mock_chunker.chunk_elements = AsyncMock(return_value=[mock_chunk])
        
        with patch.object(importer.parser, "parse_async", new=AsyncMock(return_value=[mock_raw])):
            with patch.object(importer.normalizer, "normalize_all", return_value=[mock_element]):
                with patch.object(importer, "_get_chunker", return_value=mock_chunker):
                    result = await importer.import_document(test_file)
        
        assert result is not None
        assert result.status == "success"
    
    @pytest.mark.asyncio
    async def test_import_directory_empty(self, tmp_path):
        """Test importing empty directory."""
        importer = DocumentImporter()
        
        results = await importer.import_directory(tmp_path)
        
        assert results == []
    
    @pytest.mark.asyncio
    async def test_import_directory_with_files(self, tmp_path):
        """Test importing directory with files."""
        # Create test files
        (tmp_path / "doc1.txt").write_text("First document.")
        (tmp_path / "doc2.txt").write_text("Second document.")
        
        importer = DocumentImporter()
        
        mock_result = MagicMock()
        mock_result.source_path = tmp_path / "doc1.txt"
        
        with patch.object(importer, "import_document", new=AsyncMock(return_value=mock_result)):
            results = await importer.import_directory(tmp_path, extensions=[".txt"])
        
        assert len(results) == 2
    
    @pytest.mark.asyncio
    async def test_import_directory_with_extension_filter(self, tmp_path):
        """Test importing directory with extension filter."""
        # Create different file types
        (tmp_path / "doc.txt").write_text("Text document.")
        (tmp_path / "doc.md").write_text("# Markdown document")
        (tmp_path / "doc.pdf").write_bytes(b"fake pdf content")
        
        importer = DocumentImporter()
        
        mock_result = MagicMock()
        
        with patch.object(importer, "import_document", new=AsyncMock(return_value=mock_result)):
            results = await importer.import_directory(tmp_path, extensions=[".txt", ".md"])
        
        assert len(results) == 2
    
    @pytest.mark.asyncio
    async def test_import_directory_recursive(self, tmp_path):
        """Test importing directory recursively."""
        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        (tmp_path / "root.txt").write_text("Root document.")
        (subdir / "nested.txt").write_text("Nested document.")
        
        importer = DocumentImporter()
        
        mock_result = MagicMock()
        
        with patch.object(importer, "import_document", new=AsyncMock(return_value=mock_result)):
            results = await importer.import_directory(tmp_path, recursive=True, extensions=[".txt"])
        
        assert len(results) == 2
    
    @pytest.mark.asyncio
    async def test_import_directory_non_recursive(self, tmp_path):
        """Test importing directory non-recursively."""
        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        (tmp_path / "root.txt").write_text("Root document.")
        (subdir / "nested.txt").write_text("Nested document.")
        
        importer = DocumentImporter()
        
        mock_result = MagicMock()
        
        with patch.object(importer, "import_document", new=AsyncMock(return_value=mock_result)):
            results = await importer.import_directory(tmp_path, recursive=False, extensions=[".txt"])
        
        assert len(results) == 1  # Only root.txt
    
    @pytest.mark.asyncio
    async def test_import_directory_handles_errors(self, tmp_path):
        """Test that directory import handles individual file errors gracefully."""
        (tmp_path / "good.txt").write_text("Good document.")
        (tmp_path / "bad.txt").write_text("Bad document.")
        
        importer = DocumentImporter()
        
        mock_result = MagicMock()
        
        async def mock_import(path, **kwargs):
            if "bad" in str(path):
                raise ValueError("Parse error")
            return mock_result
        
        with patch.object(importer, "import_document", new=AsyncMock(side_effect=mock_import)):
            # Should not raise, just skip the bad file
            results = await importer.import_directory(tmp_path, extensions=[".txt"])
        
        assert len(results) == 1  # Only good.txt processed
    
    def test_get_chunker_for_language(self):
        """Test getting appropriate chunker for language."""
        importer = DocumentImporter()
        
        english_chunker = importer._get_chunker(Language.ENGLISH)
        japanese_chunker = importer._get_chunker(Language.JAPANESE)
        
        # Should return different chunkers for different languages
        assert english_chunker is not None
        assert japanese_chunker is not None
        
        # Verify caching works
        english_chunker2 = importer._get_chunker(Language.ENGLISH)
        assert english_chunker is english_chunker2


class TestDocumentImporterIntegration:
    """Integration-style tests for DocumentImporter."""
    
    @pytest.mark.asyncio
    async def test_full_pipeline_mock(self, tmp_path):
        """Test full import pipeline with mocked components."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content for pipeline.")
        
        importer = DocumentImporter()
        
        # Mock all components
        mock_raw_element = MagicMock()
        mock_raw_element.text = "Test content for pipeline."
        mock_raw_element.category = "NarrativeText"
        mock_raw_element.metadata = MagicMock(
            filename="test.txt",
            page_number=1,
            coordinates=None,
        )
        
        mock_normalized = NormalizedElement(
            text="Test content for pipeline.",
            element_type=ElementType.NARRATIVE_TEXT,
            language=Language.ENGLISH,
            position=0,
        )
        
        mock_chunk = TextChunk(
            text="Test content for pipeline.",
            language=Language.ENGLISH,
            document_id=uuid4(),
            chunk_index=0,
            start_char=0,
            end_char=26,
            token_count=4,
        )
        
        mock_chunker = MagicMock()
        mock_chunker.chunk_elements = AsyncMock(return_value=[mock_chunk])
        
        with patch.object(importer.parser, "parse_async", new=AsyncMock(return_value=[mock_raw_element])):
            with patch.object(importer.normalizer, "normalize_all", return_value=[mock_normalized]):
                with patch.object(importer, "_get_chunker", return_value=mock_chunker):
                    result = await importer.import_document(test_file)
        
        assert result is not None
        assert result.document_metadata.source_path == test_file
        assert result.chunk_count >= 0
