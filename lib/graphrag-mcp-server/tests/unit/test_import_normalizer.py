"""Unit tests for element normalizer."""

from unittest.mock import MagicMock

import pytest

from graphrag_mcp_server.document_import.models import ElementType, Language
from graphrag_mcp_server.document_import.normalizer import ElementNormalizer


class TestElementNormalizer:
    """Tests for ElementNormalizer class."""
    
    def test_init_defaults(self):
        """Test default initialization."""
        normalizer = ElementNormalizer()
        
        assert normalizer.detect_language is True
        assert normalizer.default_language == Language.UNKNOWN
        assert normalizer.min_text_length == 1
    
    def test_init_custom(self):
        """Test custom initialization."""
        normalizer = ElementNormalizer(
            detect_language=False,
            default_language=Language.JAPANESE,
            min_text_length=10,
        )
        
        assert normalizer.detect_language is False
        assert normalizer.default_language == Language.JAPANESE
        assert normalizer.min_text_length == 10
    
    def test_element_type_mapping(self):
        """Test element type mapping from Unstructured categories."""
        normalizer = ElementNormalizer()
        
        # Create mock elements with different categories
        mock_title = MagicMock()
        mock_title.category = "Title"
        mock_title.__str__ = MagicMock(return_value="Test Title")
        
        mock_text = MagicMock()
        mock_text.category = "NarrativeText"
        mock_text.__str__ = MagicMock(return_value="Test paragraph text")
        
        result_title = normalizer.normalize(mock_title, 0)
        result_text = normalizer.normalize(mock_text, 1)
        
        assert result_title.element_type == ElementType.TITLE
        assert result_text.element_type == ElementType.NARRATIVE_TEXT
    
    def test_normalize_skips_empty_text(self):
        """Test that empty text elements are skipped."""
        normalizer = ElementNormalizer(min_text_length=1)
        
        mock_elem = MagicMock()
        mock_elem.category = "NarrativeText"
        mock_elem.__str__ = MagicMock(return_value="")
        
        result = normalizer.normalize(mock_elem, 0)
        
        assert result is None
    
    def test_normalize_respects_min_length(self):
        """Test that short text is filtered based on min_text_length."""
        normalizer = ElementNormalizer(min_text_length=10)
        
        mock_elem = MagicMock()
        mock_elem.category = "NarrativeText"
        mock_elem.__str__ = MagicMock(return_value="Short")
        
        result = normalizer.normalize(mock_elem, 0)
        
        assert result is None
    
    def test_normalize_preserves_position(self):
        """Test that position is correctly assigned."""
        normalizer = ElementNormalizer()
        
        mock_elem = MagicMock()
        mock_elem.category = "NarrativeText"
        mock_elem.__str__ = MagicMock(return_value="Test text")
        mock_elem.metadata = MagicMock()
        mock_elem.metadata.page_number = None
        mock_elem.metadata.parent_id = None
        
        result = normalizer.normalize(mock_elem, 42)
        
        assert result.position == 42
    
    def test_normalize_extracts_page_number(self):
        """Test extraction of page number from metadata."""
        normalizer = ElementNormalizer()
        
        mock_elem = MagicMock()
        mock_elem.category = "NarrativeText"
        mock_elem.__str__ = MagicMock(return_value="Test text")
        mock_elem.metadata = MagicMock()
        mock_elem.metadata.page_number = 5
        mock_elem.metadata.parent_id = None
        
        result = normalizer.normalize(mock_elem, 0)
        
        assert result.page_number == 5
    
    def test_normalize_all(self):
        """Test normalizing multiple elements."""
        normalizer = ElementNormalizer(detect_language=False)
        
        elements = []
        for i in range(3):
            mock = MagicMock()
            mock.category = "NarrativeText"
            mock.__str__ = MagicMock(return_value=f"Paragraph {i}")
            mock.metadata = MagicMock()
            mock.metadata.page_number = None
            mock.metadata.parent_id = None
            elements.append(mock)
        
        results = normalizer.normalize_all(elements)
        
        assert len(results) == 3
        assert all(r.element_type == ElementType.NARRATIVE_TEXT for r in results)
        assert [r.position for r in results] == [0, 1, 2]
    
    def test_normalize_all_filters_empty(self):
        """Test that normalize_all filters out empty elements."""
        normalizer = ElementNormalizer(detect_language=False)
        
        mock_valid = MagicMock()
        mock_valid.category = "NarrativeText"
        mock_valid.__str__ = MagicMock(return_value="Valid text")
        mock_valid.metadata = MagicMock()
        mock_valid.metadata.page_number = None
        mock_valid.metadata.parent_id = None
        
        mock_empty = MagicMock()
        mock_empty.category = "NarrativeText"
        mock_empty.__str__ = MagicMock(return_value="")
        
        results = normalizer.normalize_all([mock_valid, mock_empty, mock_valid])
        
        # Should only get 2 results (empty one filtered)
        assert len(results) == 2
    
    def test_detect_document_language_empty(self):
        """Test document language detection with empty list."""
        normalizer = ElementNormalizer(default_language=Language.ENGLISH)
        
        result = normalizer.detect_document_language([])
        
        assert result == Language.ENGLISH
    
    def test_unknown_category_maps_to_uncategorized(self):
        """Test that unknown categories map to UNCATEGORIZED."""
        normalizer = ElementNormalizer(detect_language=False)
        
        mock_elem = MagicMock()
        mock_elem.category = "SomeUnknownCategory"
        mock_elem.__str__ = MagicMock(return_value="Test text")
        mock_elem.metadata = MagicMock()
        mock_elem.metadata.page_number = None
        mock_elem.metadata.parent_id = None
        
        result = normalizer.normalize(mock_elem, 0)
        
        assert result.element_type == ElementType.UNCATEGORIZED
    
    def test_title_gets_heading_level(self):
        """Test that title elements get a heading level."""
        normalizer = ElementNormalizer(detect_language=False)
        
        mock_elem = MagicMock()
        mock_elem.category = "Title"
        mock_elem.__str__ = MagicMock(return_value="Chapter Title")
        mock_elem.metadata = MagicMock()
        mock_elem.metadata.page_number = None
        mock_elem.metadata.parent_id = None
        
        result = normalizer.normalize(mock_elem, 0)
        
        assert result.element_type == ElementType.TITLE
        assert result.heading_level is not None
