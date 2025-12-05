"""Base chunker interface and common functionality.

This module defines the abstract base class for all chunker implementations,
providing a consistent interface for text chunking across languages.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from uuid import UUID

from graphrag_mcp_server.document_import.models import Language, NormalizedElement, TextChunk

if TYPE_CHECKING:
    pass


class BaseChunker(ABC):
    """Abstract base class for text chunkers.
    
    All chunker implementations must inherit from this class and
    implement the abstract methods for chunking text.
    
    Attributes:
        language: Target language for this chunker.
        chunk_size: Target chunk size in characters.
        chunk_overlap: Overlap between chunks in characters.
    """
    
    def __init__(
        self,
        language: Language,
        *,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
    ):
        """Initialize the chunker.
        
        Args:
            language: Target language for chunking.
            chunk_size: Target chunk size in characters.
            chunk_overlap: Overlap between chunks in characters.
        """
        self.language = language
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in text.
        
        Args:
            text: Text to count tokens in.
            
        Returns:
            Number of tokens.
        """
        pass
    
    @abstractmethod
    def chunk_text(self, text: str) -> list[str]:
        """Chunk text into segments.
        
        Args:
            text: Text to chunk.
            
        Returns:
            List of text chunks.
        """
        pass
    
    def _combine_element_text(
        self,
        elements: list[NormalizedElement],
    ) -> tuple[str, list[tuple[int, int, UUID]]]:
        """Combine element texts with position tracking.
        
        Args:
            elements: List of normalized elements.
            
        Returns:
            Tuple of (combined_text, list of (start, end, element_id)).
        """
        combined = ""
        positions: list[tuple[int, int, UUID]] = []
        
        for elem in elements:
            start = len(combined)
            combined += elem.text
            end = len(combined)
            positions.append((start, end, elem.id))
            combined += "\n\n"  # Separator between elements
        
        return combined.rstrip(), positions
    
    def _find_source_elements(
        self,
        chunk_start: int,
        chunk_end: int,
        positions: list[tuple[int, int, UUID]],
    ) -> list[UUID]:
        """Find source elements that overlap with a chunk.
        
        Args:
            chunk_start: Start position of chunk.
            chunk_end: End position of chunk.
            positions: List of (start, end, element_id) tuples.
            
        Returns:
            List of element IDs that overlap with the chunk.
        """
        sources: list[UUID] = []
        
        for start, end, elem_id in positions:
            # Check if ranges overlap
            if start < chunk_end and end > chunk_start:
                sources.append(elem_id)
        
        return sources
    
    async def chunk_elements(
        self,
        elements: list[NormalizedElement],
        document_id: UUID,
    ) -> list[TextChunk]:
        """Chunk a list of normalized elements.
        
        Args:
            elements: List of normalized elements to chunk.
            document_id: ID of the parent document.
            
        Returns:
            List of TextChunk objects.
        """
        if not elements:
            return []
        
        # Combine element texts
        combined_text, positions = self._combine_element_text(elements)
        
        # Chunk the combined text
        text_chunks = self.chunk_text(combined_text)
        
        # Create TextChunk objects with source tracking
        chunks: list[TextChunk] = []
        current_pos = 0
        
        for idx, chunk_text in enumerate(text_chunks):
            # Find position in combined text
            start_char = combined_text.find(chunk_text, current_pos)
            if start_char == -1:
                start_char = current_pos
            end_char = start_char + len(chunk_text)
            current_pos = start_char + 1  # Allow for overlap
            
            # Find source elements
            source_elements = self._find_source_elements(
                start_char, end_char, positions
            )
            
            chunk = TextChunk(
                text=chunk_text,
                language=self.language,
                source_elements=source_elements,
                document_id=document_id,
                chunk_index=idx,
                start_char=start_char,
                end_char=end_char,
                token_count=self.count_tokens(chunk_text),
            )
            chunks.append(chunk)
        
        return chunks
