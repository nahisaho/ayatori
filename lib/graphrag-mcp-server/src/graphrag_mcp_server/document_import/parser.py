"""Document parser using Unstructured library.

This module provides document parsing capabilities for various file formats,
extracting structured elements that can be normalized and chunked.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from unstructured.documents.elements import Element


class DocumentParseError(Exception):
    """Raised when document parsing fails."""
    
    def __init__(self, message: str, file_path: Path | None = None):
        self.file_path = file_path
        super().__init__(message)


class UnsupportedFormatError(Exception):
    """Raised when file format is not supported."""
    
    def __init__(self, format: str, supported: set[str]):
        self.format = format
        self.supported = supported
        super().__init__(
            f"Unsupported format: {format}. "
            f"Supported formats: {', '.join(sorted(supported))}"
        )


class DocumentParser:
    """Parser for extracting structured elements from documents.
    
    Uses the Unstructured library to parse various document formats
    and extract structured elements for further processing.
    
    Supported formats:
    - PDF (.pdf)
    - Microsoft Word (.docx)
    - Microsoft PowerPoint (.pptx)
    - HTML (.html, .htm)
    - Markdown (.md)
    - Plain text (.txt)
    
    Example:
        >>> parser = DocumentParser()
        >>> elements = parser.parse(Path("document.pdf"))
        >>> for elem in elements:
        ...     print(f"{elem.category}: {elem.text[:50]}...")
    """
    
    SUPPORTED_FORMATS: set[str] = {
        ".pdf",
        ".docx",
        ".pptx",
        ".html",
        ".htm",
        ".md",
        ".txt",
    }
    
    def __init__(
        self,
        *,
        extract_images: bool = False,
        include_page_breaks: bool = True,
        **kwargs: Any,
    ):
        """Initialize the document parser.
        
        Args:
            extract_images: Whether to extract image elements.
            include_page_breaks: Whether to include page break elements.
            **kwargs: Additional options passed to Unstructured partition.
        """
        self.extract_images = extract_images
        self.include_page_breaks = include_page_breaks
        self.partition_kwargs = kwargs
        self._unstructured_available: bool | None = None
    
    def _check_unstructured(self) -> None:
        """Check if unstructured library is available."""
        if self._unstructured_available is None:
            try:
                import unstructured  # noqa: F401
                self._unstructured_available = True
            except ImportError:
                self._unstructured_available = False
        
        if not self._unstructured_available:
            raise ImportError(
                "The 'unstructured' library is required for document parsing. "
                "Install it with: pip install 'graphrag-mcp-server[import]'"
            )
    
    def is_supported(self, file_path: Path) -> bool:
        """Check if a file format is supported.
        
        Args:
            file_path: Path to the file to check.
            
        Returns:
            True if the format is supported, False otherwise.
        """
        return file_path.suffix.lower() in self.SUPPORTED_FORMATS
    
    def parse(self, file_path: Path) -> list[Element]:
        """Parse a document and extract structured elements.
        
        Args:
            file_path: Path to the document to parse.
            
        Returns:
            List of Unstructured Element objects.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            UnsupportedFormatError: If the file format is not supported.
            DocumentParseError: If parsing fails.
        """
        # Validate file first (before checking unstructured)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise DocumentParseError(f"Not a file: {file_path}", file_path)
        
        suffix = file_path.suffix.lower()
        if suffix not in self.SUPPORTED_FORMATS:
            raise UnsupportedFormatError(suffix, self.SUPPORTED_FORMATS)
        
        # Now check for unstructured
        self._check_unstructured()
        
        # Import here to defer dependency
        from unstructured.partition.auto import partition
        
        # Parse document
        try:
            elements = partition(
                filename=str(file_path),
                include_page_breaks=self.include_page_breaks,
                **self.partition_kwargs,
            )
            
            # Filter out images if not requested
            if not self.extract_images:
                from unstructured.documents.elements import Image
                elements = [e for e in elements if not isinstance(e, Image)]
            
            return elements
            
        except Exception as e:
            raise DocumentParseError(
                f"Failed to parse {file_path}: {e}",
                file_path
            ) from e
    
    async def parse_async(self, file_path: Path) -> list[Element]:
        """Parse a document asynchronously.
        
        This is a convenience wrapper that runs the synchronous parse
        method in a thread pool executor.
        
        Args:
            file_path: Path to the document to parse.
            
        Returns:
            List of Unstructured Element objects.
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            elements = await loop.run_in_executor(
                executor,
                self.parse,
                file_path
            )
        return elements
    
    def get_file_metadata(self, file_path: Path) -> dict[str, Any]:
        """Get metadata about a file without parsing its contents.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Dictionary with file metadata.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = file_path.stat()
        
        return {
            "file_name": file_path.name,
            "file_type": file_path.suffix.lower(),
            "file_size": stat.st_size,
            "created_time": stat.st_ctime,
            "modified_time": stat.st_mtime,
            "is_supported": self.is_supported(file_path),
        }
