"""Element normalizer for converting Unstructured elements.

This module normalizes raw Unstructured elements into a consistent
format suitable for chunking and further processing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from graphrag_mcp_server.document_import.models import (
    ElementType,
    Language,
    NormalizedElement,
)

if TYPE_CHECKING:
    from unstructured.documents.elements import Element


class ElementNormalizer:
    """Normalizes Unstructured elements into NormalizedElement objects.
    
    This class handles the conversion from Unstructured's element format
    to our internal NormalizedElement format, with support for language
    detection and metadata extraction.
    
    Example:
        >>> from unstructured.partition.auto import partition
        >>> elements = partition("document.pdf")
        >>> normalizer = ElementNormalizer(detect_language=True)
        >>> normalized = normalizer.normalize_all(elements)
    """
    
    # Mapping from Unstructured element categories to our ElementType
    ELEMENT_TYPE_MAP: dict[str, ElementType] = {
        "Title": ElementType.TITLE,
        "NarrativeText": ElementType.NARRATIVE_TEXT,
        "ListItem": ElementType.LIST_ITEM,
        "Table": ElementType.TABLE,
        "Image": ElementType.IMAGE,
        "Header": ElementType.HEADER,
        "Footer": ElementType.FOOTER,
        "PageBreak": ElementType.PAGE_BREAK,
        "Formula": ElementType.FORMULA,
        "FigureCaption": ElementType.NARRATIVE_TEXT,
        "Address": ElementType.NARRATIVE_TEXT,
        "EmailAddress": ElementType.NARRATIVE_TEXT,
        "CodeSnippet": ElementType.CODE,
    }
    
    def __init__(
        self,
        *,
        detect_language: bool = True,
        default_language: Language = Language.UNKNOWN,
        min_text_length: int = 1,
    ):
        """Initialize the element normalizer.
        
        Args:
            detect_language: Whether to detect language for each element.
            default_language: Default language if detection fails.
            min_text_length: Minimum text length to include element.
        """
        self.detect_language = detect_language
        self.default_language = default_language
        self.min_text_length = min_text_length
        self._langdetect_available: bool | None = None
    
    def _check_langdetect(self) -> bool:
        """Check if langdetect library is available."""
        if self._langdetect_available is None:
            try:
                import langdetect  # noqa: F401
                self._langdetect_available = True
            except ImportError:
                self._langdetect_available = False
        return self._langdetect_available
    
    def _detect_language(self, text: str) -> Language:
        """Detect the language of text.
        
        Args:
            text: Text to analyze.
            
        Returns:
            Detected language or default.
        """
        if not self.detect_language or not text or len(text) < 20:
            return self.default_language
        
        if not self._check_langdetect():
            return self.default_language
        
        try:
            from langdetect import detect, LangDetectException
            
            lang_code = detect(text)
            
            # Map to our Language enum
            lang_map = {
                "ja": Language.JAPANESE,
                "en": Language.ENGLISH,
                "zh-cn": Language.CHINESE,
                "zh-tw": Language.CHINESE,
                "ko": Language.KOREAN,
            }
            return lang_map.get(lang_code, Language.UNKNOWN)
            
        except LangDetectException:
            return self.default_language
    
    def _get_element_type(self, element: Element) -> ElementType:
        """Get the ElementType for an Unstructured element.
        
        Args:
            element: Unstructured element.
            
        Returns:
            Corresponding ElementType.
        """
        category = getattr(element, "category", None)
        if category:
            return self.ELEMENT_TYPE_MAP.get(category, ElementType.UNCATEGORIZED)
        return ElementType.UNCATEGORIZED
    
    def _extract_metadata(self, element: Element) -> dict[str, Any]:
        """Extract metadata from an Unstructured element.
        
        Args:
            element: Unstructured element.
            
        Returns:
            Dictionary of metadata.
        """
        metadata: dict[str, Any] = {}
        
        # Extract common metadata fields
        if hasattr(element, "metadata"):
            elem_meta = element.metadata
            if hasattr(elem_meta, "page_number"):
                metadata["page_number"] = elem_meta.page_number
            if hasattr(elem_meta, "filename"):
                metadata["filename"] = elem_meta.filename
            if hasattr(elem_meta, "coordinates"):
                metadata["coordinates"] = elem_meta.coordinates
            if hasattr(elem_meta, "parent_id"):
                metadata["parent_id"] = elem_meta.parent_id
            if hasattr(elem_meta, "languages"):
                metadata["languages"] = elem_meta.languages
        
        return metadata
    
    def _get_page_number(self, element: Element) -> int | None:
        """Extract page number from element metadata.
        
        Args:
            element: Unstructured element.
            
        Returns:
            Page number or None.
        """
        if hasattr(element, "metadata") and hasattr(element.metadata, "page_number"):
            return element.metadata.page_number
        return None
    
    def _get_parent_id(self, element: Element) -> UUID | None:
        """Extract parent ID from element metadata.
        
        Args:
            element: Unstructured element.
            
        Returns:
            Parent UUID or None.
        """
        if hasattr(element, "metadata") and hasattr(element.metadata, "parent_id"):
            parent_id = element.metadata.parent_id
            if parent_id:
                try:
                    return UUID(parent_id)
                except (ValueError, TypeError):
                    pass
        return None
    
    def normalize(
        self,
        element: Element,
        position: int,
    ) -> NormalizedElement | None:
        """Normalize a single Unstructured element.
        
        Args:
            element: Unstructured element to normalize.
            position: Position index in document.
            
        Returns:
            NormalizedElement or None if element should be skipped.
        """
        # Get text content
        text = str(element) if element else ""
        
        # Skip if text is too short
        if len(text.strip()) < self.min_text_length:
            return None
        
        # Get element type
        element_type = self._get_element_type(element)
        
        # Skip page breaks if they have no content
        if element_type == ElementType.PAGE_BREAK and not text.strip():
            return None
        
        # Detect language
        language = self._detect_language(text)
        
        # Extract metadata
        raw_metadata = self._extract_metadata(element)
        
        # Determine heading level for title elements
        heading_level = None
        if element_type == ElementType.TITLE:
            # Default to level 1, could be refined based on font size, etc.
            heading_level = raw_metadata.get("heading_level", 1)
        
        return NormalizedElement(
            element_type=element_type,
            text=text,
            language=language,
            page_number=self._get_page_number(element),
            position=position,
            parent_id=self._get_parent_id(element),
            heading_level=heading_level,
            raw_metadata=raw_metadata,
        )
    
    def normalize_all(
        self,
        elements: list[Element],
    ) -> list[NormalizedElement]:
        """Normalize a list of Unstructured elements.
        
        Args:
            elements: List of Unstructured elements.
            
        Returns:
            List of NormalizedElements (excluding skipped elements).
        """
        normalized: list[NormalizedElement] = []
        
        for position, element in enumerate(elements):
            norm = self.normalize(element, position)
            if norm is not None:
                normalized.append(norm)
        
        return normalized
    
    def detect_document_language(
        self,
        elements: list[NormalizedElement],
    ) -> Language:
        """Detect the primary language of a document.
        
        Analyzes all elements to determine the most common language
        in the document.
        
        Args:
            elements: List of normalized elements.
            
        Returns:
            Primary language of the document.
        """
        if not elements:
            return self.default_language
        
        # Count language occurrences weighted by text length
        lang_scores: dict[Language, int] = {}
        
        for elem in elements:
            if elem.language != Language.UNKNOWN:
                lang_scores[elem.language] = lang_scores.get(
                    elem.language, 0
                ) + len(elem.text)
        
        if not lang_scores:
            return self.default_language
        
        # Return language with highest score
        return max(lang_scores.items(), key=lambda x: x[1])[0]
