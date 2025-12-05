"""Chunker package for text chunking strategies.

This package provides language-aware text chunking with support
for Japanese semantic chunking using morphological analysis.
"""

from graphrag_mcp_server.document_import.chunker.base import BaseChunker
from graphrag_mcp_server.document_import.chunker.factory import get_chunker
from graphrag_mcp_server.document_import.models import Language

__all__ = [
    "BaseChunker",
    "get_chunker",
    "Language",
]
