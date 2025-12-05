"""Document importer orchestrating the full import pipeline.

This module provides the main DocumentImporter class that coordinates
parsing, normalization, chunking, and correlation building.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

from graphrag_mcp_server.document_import.models import (
    DocumentMetadata,
    ImportConfig,
    ImportResult,
    Language,
)
from graphrag_mcp_server.document_import.normalizer import ElementNormalizer
from graphrag_mcp_server.document_import.parser import DocumentParser

if TYPE_CHECKING:
    from graphrag_mcp_server.document_import.chunker.base import BaseChunker


class DocumentImporter:
    """Main class for importing documents into GraphRAG.
    
    Orchestrates the full import pipeline:
    1. Parse document to extract elements
    2. Normalize elements to consistent format
    3. Chunk text with language-aware strategies
    4. Build correlation graph between chunks
    5. Return GraphRAG-ready output
    
    Example:
        >>> importer = DocumentImporter()
        >>> result = await importer.import_document(
        ...     Path("document.pdf"),
        ...     config=ImportConfig(chunk_size=1000)
        ... )
        >>> print(f"Created {result.chunk_count} chunks")
    """
    
    def __init__(
        self,
        *,
        parser: DocumentParser | None = None,
        normalizer: ElementNormalizer | None = None,
        config: ImportConfig | None = None,
    ):
        """Initialize the document importer.
        
        Args:
            parser: Custom document parser (or use default).
            normalizer: Custom element normalizer (or use default).
            config: Import configuration (or use defaults).
        """
        self.parser = parser or DocumentParser()
        self.normalizer = normalizer or ElementNormalizer()
        self.config = config or ImportConfig()
        self._chunkers: dict[Language, BaseChunker] = {}
    
    def _get_chunker(self, language: Language) -> BaseChunker:
        """Get the appropriate chunker for a language.
        
        Args:
            language: Target language.
            
        Returns:
            Chunker instance for the language.
        """
        if language not in self._chunkers:
            from graphrag_mcp_server.document_import.chunker import get_chunker
            self._chunkers[language] = get_chunker(
                language,
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap,
            )
        return self._chunkers[language]
    
    def _create_document_metadata(
        self,
        file_path: Path,
        language: Language,
    ) -> DocumentMetadata:
        """Create document metadata from file.
        
        Args:
            file_path: Path to the document.
            language: Detected document language.
            
        Returns:
            DocumentMetadata instance.
        """
        stat = file_path.stat()
        
        return DocumentMetadata(
            source_path=file_path,
            file_name=file_path.name,
            file_type=file_path.suffix.lower(),
            file_size=stat.st_size,
            language=language,
        )
    
    async def import_document(
        self,
        file_path: Path,
        *,
        config: ImportConfig | None = None,
    ) -> ImportResult:
        """Import a document and produce GraphRAG-ready output.
        
        Args:
            file_path: Path to the document to import.
            config: Override configuration for this import.
            
        Returns:
            ImportResult with chunks and correlations.
        """
        start_time = time.time()
        cfg = config or self.config
        
        # Initialize result
        result = ImportResult(
            id=uuid4(),
            document_metadata=self._create_document_metadata(
                file_path, Language.UNKNOWN
            ),
        )
        
        try:
            # Step 1: Parse document
            raw_elements = await self.parser.parse_async(file_path)
            
            # Step 2: Normalize elements
            elements = self.normalizer.normalize_all(raw_elements)
            result.elements = elements
            result.element_count = len(elements)
            
            # Step 3: Detect document language
            language = self.normalizer.detect_document_language(elements)
            if cfg.auto_detect_language:
                result.document_metadata.language = language
            else:
                language = cfg.default_language
                result.document_metadata.language = language
            
            # Step 4: Chunk text
            chunker = self._get_chunker(language)
            chunks = await chunker.chunk_elements(elements, result.id)
            result.chunks = chunks
            result.chunk_count = len(chunks)
            result.total_tokens = sum(c.token_count for c in chunks)
            
            # Step 5: Build correlation graph (if enabled)
            if cfg.build_correlation_graph:
                from graphrag_mcp_server.document_import.correlation import (
                    CorrelationBuilder,
                )
                builder = CorrelationBuilder(
                    similarity_threshold=cfg.semantic_similarity_threshold
                )
                result.correlation_graph = await builder.build_graph(chunks)
            
            result.status = "success"
            
        except Exception as e:
            result.status = "error"
            result.errors.append(str(e))
        
        result.processing_time_seconds = time.time() - start_time
        return result
    
    def import_document_sync(
        self,
        file_path: Path,
        *,
        config: ImportConfig | None = None,
    ) -> ImportResult:
        """Synchronous version of import_document.
        
        Args:
            file_path: Path to the document to import.
            config: Override configuration for this import.
            
        Returns:
            ImportResult with chunks and correlations.
        """
        import asyncio
        return asyncio.run(self.import_document(file_path, config=config))

    async def import_directory(
        self,
        directory: Path,
        *,
        extensions: list[str] | None = None,
        recursive: bool = True,
        config: ImportConfig | None = None,
    ) -> list[ImportResult]:
        """Import all documents from a directory.
        
        Args:
            directory: Path to directory containing documents.
            extensions: File extensions to include (e.g., [".pdf", ".docx"]).
                If None, uses all supported formats.
            recursive: Whether to search subdirectories.
            config: Override configuration for all imports.
            
        Returns:
            List of ImportResult for successfully processed files.
        """
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")
        
        # Default to all supported extensions
        allowed_exts = set(extensions) if extensions else self.parser.SUPPORTED_FORMATS
        
        # Find all matching files
        pattern = "**/*" if recursive else "*"
        files = [
            f for f in directory.glob(pattern)
            if f.is_file() and f.suffix.lower() in allowed_exts
        ]
        
        results = []
        for file_path in files:
            try:
                result = await self.import_document(file_path, config=config)
                results.append(result)
            except Exception:
                # Skip files that fail to process
                continue
        
        return results
