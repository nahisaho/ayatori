"""Chunker factory for language-specific chunker instantiation.

This module provides a factory function to get the appropriate
chunker implementation based on the target language.
"""

from __future__ import annotations

from graphrag_mcp_server.document_import.chunker.base import BaseChunker
from graphrag_mcp_server.document_import.models import Language


def get_chunker(
    language: Language,
    *,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
) -> BaseChunker:
    """Get a chunker for the specified language.
    
    Returns the appropriate chunker implementation based on the
    target language. Japanese uses morphological analysis,
    while other languages use simpler sentence-based splitting.
    
    Args:
        language: Target language for chunking.
        chunk_size: Target chunk size in characters.
        chunk_overlap: Overlap between chunks in characters.
        
    Returns:
        Chunker instance for the language.
    """
    if language == Language.JAPANESE:
        from graphrag_mcp_server.document_import.chunker.japanese import JapaneseChunker
        return JapaneseChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    else:
        from graphrag_mcp_server.document_import.chunker.default import DefaultChunker
        return DefaultChunker(
            language=language,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
