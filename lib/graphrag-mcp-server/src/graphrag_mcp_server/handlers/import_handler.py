"""Import handlers for MCP tools.

This module provides handlers for document import operations.
"""

import json
from pathlib import Path
from typing import Any

from graphrag_mcp_server.document_import import (
    DocumentImporter,
    ImportConfig,
    ImportResult,
)


async def handle_import_document(
    file_path: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
    auto_detect_language: bool = True,
    build_correlation_graph: bool = True,
) -> str:
    """Handle document import request.

    Args:
        file_path: Path to the document to import.
        chunk_size: Target size for text chunks (default: 1000).
        chunk_overlap: Overlap between chunks (default: 100).
        auto_detect_language: Whether to auto-detect language (default: True).
        build_correlation_graph: Whether to build chunk correlations (default: True).

    Returns:
        JSON string with import results.
    """
    # auto_detect_language=False means we need to specify language
    # For now, default to None to let the importer auto-detect
    language = None if auto_detect_language else "en"
    
    config = ImportConfig(
        language=language,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    importer = DocumentImporter(config=config)
    result = importer.import_document(Path(file_path))

    return _format_import_result(result)


async def handle_import_directory(
    directory_path: str,
    extensions: list[str] | None = None,
    recursive: bool = True,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
) -> str:
    """Handle directory import request.

    Args:
        directory_path: Path to the directory to import.
        extensions: File extensions to include (e.g., [".pdf", ".docx"]).
        recursive: Whether to search subdirectories (default: True).
        chunk_size: Target size for text chunks (default: 1000).
        chunk_overlap: Overlap between chunks (default: 100).

    Returns:
        JSON string with import results.
    """
    config = ImportConfig(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    importer = DocumentImporter(config=config)
    
    # Build pattern from extensions or use "*" for all files
    if extensions:
        # Import each extension pattern
        all_results = []
        for ext in extensions:
            pattern = f"*{ext}" if not ext.startswith("*") else ext
            results = importer.import_directory(
                Path(directory_path),
                pattern=pattern,
                recursive=recursive,
            )
            all_results.extend(results)
    else:
        all_results = importer.import_directory(
            Path(directory_path),
            pattern="*",
            recursive=recursive,
        )

    return _format_directory_import_results(all_results)


def _format_import_result(result: ImportResult) -> str:
    """Format a single import result as JSON.

    Args:
        result: Import result to format.

    Returns:
        JSON string representation.
    """
    data = {
        "success": result.success,
        "source_file": str(result.source_file),
        "total_chunks": result.total_chunks,
        "total_elements": result.total_elements,
        "language_detected": result.language_detected,
        "processing_time_seconds": result.processing_time_seconds,
    }

    if result.error_message:
        data["error_message"] = result.error_message

    if result.chunks:
        data["chunks_preview"] = [
            {
                "id": chunk.id,
                "text_preview": chunk.text[:100] + "..." if len(chunk.text) > 100 else chunk.text,
                "token_count": chunk.token_count,
                "related_chunks_count": len(chunk.related_chunk_ids),
            }
            for chunk in result.chunks[:5]  # First 5 chunks only
        ]

    return json.dumps(data, ensure_ascii=False, indent=2)


def _format_directory_import_results(results: list[ImportResult]) -> str:
    """Format multiple import results as JSON.

    Args:
        results: List of import results to format.

    Returns:
        JSON string representation.
    """
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    data = {
        "total_files": len(results),
        "successful_count": len(successful),
        "failed_count": len(failed),
        "total_chunks": sum(r.total_chunks for r in successful),
        "results": [
            {
                "source_file": str(r.source_file),
                "success": r.success,
                "chunks_count": r.total_chunks,
                "language": r.language_detected,
                "error": r.error_message if not r.success else None,
            }
            for r in results
        ],
    }

    return json.dumps(data, ensure_ascii=False, indent=2)
