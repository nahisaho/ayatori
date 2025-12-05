"""Document Import Module for GraphRAG MCP Server.

This module provides functionality for importing documents into GraphRAG,
with support for multiple formats and Japanese-aware semantic chunking.

Key Features:
- Multi-format document parsing (PDF, DOCX, HTML, Markdown)
- Japanese-aware semantic chunking with fugashi
- Chunk correlation graph construction
- GraphRAG-ready output format

Example:
    >>> from graphrag_mcp_server.document_import import DocumentImporter
    >>> importer = DocumentImporter()
    >>> result = await importer.import_document("document.pdf")
    >>> print(f"Imported {len(result.chunks)} chunks")
"""

from graphrag_mcp_server.document_import.models import (
    ChunkCorrelation,
    CorrelationGraph,
    DocumentMetadata,
    ImportConfig,
    ImportResult,
    NormalizedElement,
    TextChunk,
)
from graphrag_mcp_server.document_import.parser import DocumentParser
from graphrag_mcp_server.document_import.normalizer import ElementNormalizer
from graphrag_mcp_server.document_import.importer import DocumentImporter

__all__ = [
    # Core classes
    "DocumentImporter",
    "DocumentParser",
    "ElementNormalizer",
    # Data models
    "NormalizedElement",
    "TextChunk",
    "ChunkCorrelation",
    "CorrelationGraph",
    "ImportResult",
    "ImportConfig",
    "DocumentMetadata",
]
