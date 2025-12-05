"""Data models for document import functionality.

This module defines the core data structures used throughout the import
pipeline, from raw document elements to chunked text with correlations.

All models use Pydantic for validation and serialization.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ElementType(str, Enum):
    """Types of document elements extracted by Unstructured."""
    
    TITLE = "Title"
    NARRATIVE_TEXT = "NarrativeText"
    LIST_ITEM = "ListItem"
    TABLE = "Table"
    IMAGE = "Image"
    HEADER = "Header"
    FOOTER = "Footer"
    PAGE_BREAK = "PageBreak"
    FORMULA = "Formula"
    CODE = "Code"
    UNCATEGORIZED = "UncategorizedText"


class Language(str, Enum):
    """Supported languages for chunking."""
    
    JAPANESE = "ja"
    ENGLISH = "en"
    CHINESE = "zh"
    KOREAN = "ko"
    UNKNOWN = "unknown"


class CorrelationType(str, Enum):
    """Types of relationships between chunks."""
    
    ADJACENT = "adjacent"          # Sequential chunks in document
    SEMANTIC = "semantic"          # Semantically similar content
    REFERENCE = "reference"        # Cross-references
    HIERARCHICAL = "hierarchical"  # Parent-child (heading-content)
    COOCCURRENCE = "cooccurrence"  # Shared entities/terms


class DocumentMetadata(BaseModel):
    """Metadata about the source document."""
    
    source_path: Path = Field(..., description="Path to source document")
    file_name: str = Field(..., description="Original file name")
    file_type: str = Field(..., description="File extension/type")
    file_size: int = Field(..., description="File size in bytes")
    page_count: int | None = Field(None, description="Number of pages if applicable")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    language: Language = Field(default=Language.UNKNOWN)
    custom_metadata: dict[str, Any] = Field(default_factory=dict)


class NormalizedElement(BaseModel):
    """A normalized document element extracted from parsing.
    
    This represents a single structural element from the document
    (e.g., paragraph, heading, list item) in a normalized format
    suitable for chunking.
    """
    
    id: UUID = Field(default_factory=uuid4)
    element_type: ElementType
    text: str = Field(..., description="The text content of the element")
    language: Language = Field(default=Language.UNKNOWN)
    page_number: int | None = Field(None, description="Source page number")
    position: int = Field(..., description="Position in document (0-indexed)")
    
    # Structural metadata
    parent_id: UUID | None = Field(None, description="Parent element ID for hierarchy")
    heading_level: int | None = Field(None, description="Heading level (1-6) if applicable")
    
    # Raw element data for reference
    raw_metadata: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        frozen = True


class TextChunk(BaseModel):
    """A chunk of text ready for GraphRAG indexing.
    
    Chunks are created from normalized elements using language-aware
    chunking strategies. Each chunk maintains traceability to its
    source elements.
    """
    
    id: UUID = Field(default_factory=uuid4)
    text: str = Field(..., description="The chunk text content")
    language: Language
    
    # Source tracking
    source_elements: list[UUID] = Field(
        default_factory=list,
        description="IDs of source NormalizedElements"
    )
    document_id: UUID = Field(..., description="Parent document ID")
    
    # Position information
    chunk_index: int = Field(..., description="Index within document")
    start_char: int = Field(..., description="Start character position in original text")
    end_char: int = Field(..., description="End character position in original text")
    
    # Token information
    token_count: int = Field(..., description="Number of tokens in chunk")
    
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        frozen = True


class ChunkCorrelation(BaseModel):
    """A correlation (edge) between two chunks.
    
    Correlations form the edges of the chunk correlation graph,
    enabling understanding of relationships between text chunks.
    """
    
    id: UUID = Field(default_factory=uuid4)
    source_chunk_id: UUID
    target_chunk_id: UUID
    correlation_type: CorrelationType
    weight: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Correlation strength (0-1)"
    )
    
    # Optional metadata about the correlation
    metadata: dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        frozen = True


class CorrelationGraph(BaseModel):
    """A graph of chunk correlations.
    
    This represents the correlation structure between all chunks
    in a document, enabling graph-based analysis and navigation.
    """
    
    document_id: UUID
    nodes: list[UUID] = Field(default_factory=list, description="Chunk IDs as nodes")
    edges: list[ChunkCorrelation] = Field(default_factory=list)
    
    # Graph statistics
    node_count: int = Field(default=0)
    edge_count: int = Field(default=0)
    density: float = Field(default=0.0, description="Graph density (edges/max_edges)")
    
    def add_correlation(self, correlation: ChunkCorrelation) -> None:
        """Add a correlation to the graph."""
        self.edges.append(correlation)
        self.edge_count = len(self.edges)
        self._update_density()
    
    def _update_density(self) -> None:
        """Update graph density metric."""
        if self.node_count > 1:
            max_edges = self.node_count * (self.node_count - 1) / 2
            self.density = self.edge_count / max_edges if max_edges > 0 else 0.0


class ImportConfig(BaseModel):
    """Configuration for document import process."""
    
    # Chunking settings
    chunk_size: int = Field(
        default=1000,
        ge=100,
        le=10000,
        description="Target chunk size in characters"
    )
    chunk_overlap: int = Field(
        default=100,
        ge=0,
        description="Overlap between chunks in characters"
    )
    
    # Language settings
    auto_detect_language: bool = Field(
        default=True,
        description="Automatically detect document language"
    )
    default_language: Language = Field(
        default=Language.ENGLISH,
        description="Default language if detection fails"
    )
    
    # Correlation settings
    build_correlation_graph: bool = Field(
        default=True,
        description="Build chunk correlation graph"
    )
    semantic_similarity_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Threshold for semantic correlations"
    )
    
    # Output settings
    output_format: str = Field(
        default="graphrag",
        description="Output format (graphrag, json, csv)"
    )


class ImportResult(BaseModel):
    """Result of a document import operation.
    
    Contains all the artifacts produced by importing a document:
    chunks, correlations, and metadata for traceability.
    """
    
    id: UUID = Field(default_factory=uuid4)
    status: str = Field(default="success")
    
    # Source document
    document_metadata: DocumentMetadata
    
    # Extracted elements
    elements: list[NormalizedElement] = Field(default_factory=list)
    element_count: int = Field(default=0)
    
    # Generated chunks
    chunks: list[TextChunk] = Field(default_factory=list)
    chunk_count: int = Field(default=0)
    
    # Correlation graph
    correlation_graph: CorrelationGraph | None = None
    
    # Processing statistics
    processing_time_seconds: float = Field(default=0.0)
    total_tokens: int = Field(default=0)
    
    # Errors/warnings
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    
    def add_chunk(self, chunk: TextChunk) -> None:
        """Add a chunk to the result."""
        self.chunks.append(chunk)
        self.chunk_count = len(self.chunks)
        self.total_tokens += chunk.token_count
