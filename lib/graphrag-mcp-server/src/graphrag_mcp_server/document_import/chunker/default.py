"""Default chunker for non-Japanese languages.

This module provides a sentence-based chunker suitable for
English and other Western languages.
"""

from __future__ import annotations

import re

from graphrag_mcp_server.document_import.chunker.base import BaseChunker
from graphrag_mcp_server.document_import.models import Language


class DefaultChunker(BaseChunker):
    """Default chunker using sentence-based splitting.
    
    This chunker splits text at sentence boundaries and combines
    sentences to meet the target chunk size. Suitable for English
    and other languages with clear sentence delimiters.
    
    Example:
        >>> chunker = DefaultChunker(Language.ENGLISH, chunk_size=500)
        >>> chunks = chunker.chunk_text("This is a long document...")
    """
    
    # Sentence ending patterns
    SENTENCE_ENDINGS = re.compile(r'(?<=[.!?])\s+')
    
    def __init__(
        self,
        language: Language = Language.ENGLISH,
        *,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
    ):
        """Initialize the default chunker.
        
        Args:
            language: Target language for chunking.
            chunk_size: Target chunk size in characters.
            chunk_overlap: Overlap between chunks in characters.
        """
        super().__init__(
            language=language,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using simple word splitting.
        
        For English and similar languages, words are a reasonable
        approximation of tokens.
        
        Args:
            text: Text to count tokens in.
            
        Returns:
            Approximate number of tokens.
        """
        if not text:
            return 0
        
        # Simple word count as token approximation
        words = text.split()
        return len(words)
    
    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences.
        
        Args:
            text: Text to split.
            
        Returns:
            List of sentences.
        """
        if not text:
            return []
        
        # Split on sentence endings
        sentences = self.SENTENCE_ENDINGS.split(text)
        
        # Clean up and filter empty strings
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def chunk_text(self, text: str) -> list[str]:
        """Chunk text into segments at sentence boundaries.
        
        Args:
            text: Text to chunk.
            
        Returns:
            List of text chunks.
        """
        if not text:
            return []
        
        sentences = self._split_sentences(text)
        
        if not sentences:
            # If no sentences found, chunk by size
            return self._chunk_by_size(text)
        
        chunks: list[str] = []
        current_chunk: list[str] = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence exceeds chunk size
            if current_length + sentence_length > self.chunk_size:
                if current_chunk:
                    # Save current chunk
                    chunks.append(" ".join(current_chunk))
                    
                    # Handle overlap
                    if self.chunk_overlap > 0:
                        # Keep sentences for overlap
                        overlap_length = 0
                        overlap_sentences: list[str] = []
                        for s in reversed(current_chunk):
                            if overlap_length + len(s) <= self.chunk_overlap:
                                overlap_sentences.insert(0, s)
                                overlap_length += len(s)
                            else:
                                break
                        current_chunk = overlap_sentences
                        current_length = overlap_length
                    else:
                        current_chunk = []
                        current_length = 0
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _chunk_by_size(self, text: str) -> list[str]:
        """Fallback chunking by character size.
        
        Used when sentence splitting fails or produces no results.
        
        Args:
            text: Text to chunk.
            
        Returns:
            List of text chunks.
        """
        chunks: list[str] = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at word boundary
            if end < len(text):
                # Look for space to break at
                break_pos = text.rfind(" ", start, end)
                if break_pos > start:
                    end = break_pos
            
            chunks.append(text[start:end].strip())
            
            # Apply overlap
            start = end - self.chunk_overlap
            if start <= 0:
                start = end
        
        return chunks
