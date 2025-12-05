"""Japanese chunker using morphological analysis.

This module provides semantic chunking for Japanese text using
fugashi (MeCab wrapper) for morphological analysis. It chunks
at natural linguistic boundaries while respecting context.
"""

from __future__ import annotations

from graphrag_mcp_server.document_import.chunker.base import BaseChunker
from graphrag_mcp_server.document_import.models import Language


class JapaneseChunker(BaseChunker):
    """Japanese chunker using fugashi morphological analysis.
    
    This chunker uses MeCab via fugashi to analyze Japanese text
    and split at natural linguistic boundaries. It respects
    sentence structure and avoids breaking in the middle of phrases.
    
    Chunking strategy:
    1. Split text into morphemes using fugashi
    2. Group morphemes into sentences (ending with 。or other markers)
    3. Combine sentences to meet target chunk size
    4. Respect overlap for context continuity
    
    Example:
        >>> chunker = JapaneseChunker(chunk_size=500)
        >>> chunks = chunker.chunk_text("これは日本語のテキストです。")
    """
    
    # Sentence ending markers in Japanese
    SENTENCE_ENDINGS = {"。", "！", "？", "…", "‥"}
    
    # Phrase boundary markers
    PHRASE_MARKERS = {"、", "　", "\n"}
    
    def __init__(
        self,
        *,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
    ):
        """Initialize the Japanese chunker.
        
        Args:
            chunk_size: Target chunk size in characters.
            chunk_overlap: Overlap between chunks in characters.
        """
        super().__init__(
            language=Language.JAPANESE,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        self._tagger = None
        self._fugashi_available: bool | None = None
    
    def _check_fugashi(self) -> bool:
        """Check if fugashi library is available."""
        if self._fugashi_available is None:
            try:
                import fugashi  # noqa: F401
                self._fugashi_available = True
            except ImportError:
                self._fugashi_available = False
        return self._fugashi_available
    
    def _get_tagger(self):
        """Get or create the fugashi tagger."""
        if self._tagger is None:
            if not self._check_fugashi():
                raise ImportError(
                    "The 'fugashi' library is required for Japanese chunking. "
                    "Install it with: pip install 'graphrag-mcp-server[import]'"
                )
            import fugashi
            self._tagger = fugashi.Tagger()
        return self._tagger
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using morphological analysis.
        
        For Japanese, tokens are morphemes (words/particles)
        identified by the morphological analyzer.
        
        Args:
            text: Text to count tokens in.
            
        Returns:
            Number of tokens (morphemes).
        """
        if not text:
            return 0
        
        if not self._check_fugashi():
            # Fallback: count characters
            return len(text)
        
        tagger = self._get_tagger()
        morphemes = tagger(text)
        return len(list(morphemes))
    
    def _split_sentences(self, text: str) -> list[str]:
        """Split Japanese text into sentences.
        
        Uses sentence ending markers common in Japanese.
        
        Args:
            text: Text to split.
            
        Returns:
            List of sentences.
        """
        if not text:
            return []
        
        sentences: list[str] = []
        current = ""
        
        for char in text:
            current += char
            if char in self.SENTENCE_ENDINGS:
                if current.strip():
                    sentences.append(current.strip())
                current = ""
        
        # Add remaining text
        if current.strip():
            sentences.append(current.strip())
        
        return sentences
    
    def _find_phrase_boundary(
        self,
        text: str,
        position: int,
        direction: int = -1,
    ) -> int:
        """Find the nearest phrase boundary.
        
        Looks for natural breaking points in the text, preferring
        phrase markers over arbitrary positions.
        
        Args:
            text: Text to search in.
            position: Starting position.
            direction: -1 for backward, 1 for forward.
            
        Returns:
            Position of nearest boundary.
        """
        if not self._check_fugashi():
            # Fallback: look for phrase markers
            search_range = (
                range(position - 1, -1, -1) if direction == -1
                else range(position, len(text))
            )
            for i in search_range:
                if text[i] in self.PHRASE_MARKERS or text[i] in self.SENTENCE_ENDINGS:
                    return i + 1 if direction == -1 else i
            return position
        
        # Use morphological analysis to find word boundaries
        tagger = self._get_tagger()
        
        # Analyze text around position
        start = max(0, position - 50)
        end = min(len(text), position + 50)
        context = text[start:end]
        
        morphemes = list(tagger(context))
        
        # Build position map
        pos = 0
        boundaries: list[int] = [start]
        for m in morphemes:
            pos += len(m.surface)
            boundaries.append(start + pos)
        
        # Find nearest boundary
        target = position
        closest = position
        min_dist = float('inf')
        
        for b in boundaries:
            dist = abs(b - target)
            if dist < min_dist:
                min_dist = dist
                closest = b
        
        return closest
    
    def chunk_text(self, text: str) -> list[str]:
        """Chunk Japanese text at natural boundaries.
        
        Uses sentence boundaries as primary split points,
        with morphological analysis for fine-tuning.
        
        Args:
            text: Text to chunk.
            
        Returns:
            List of text chunks.
        """
        if not text:
            return []
        
        sentences = self._split_sentences(text)
        
        if not sentences:
            return self._chunk_by_morphemes(text)
        
        chunks: list[str] = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence exceeds chunk size
            if len(current_chunk) + len(sentence) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    
                    # Handle overlap
                    if self.chunk_overlap > 0 and len(current_chunk) > self.chunk_overlap:
                        # Keep last part for overlap
                        overlap_start = len(current_chunk) - self.chunk_overlap
                        # Find natural boundary
                        overlap_start = self._find_phrase_boundary(
                            current_chunk, overlap_start, direction=1
                        )
                        current_chunk = current_chunk[overlap_start:]
                    else:
                        current_chunk = ""
            
            current_chunk += sentence
        
        # Add remaining chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _chunk_by_morphemes(self, text: str) -> list[str]:
        """Chunk text using morpheme boundaries.
        
        Fallback method when sentence splitting fails.
        
        Args:
            text: Text to chunk.
            
        Returns:
            List of text chunks.
        """
        if not self._check_fugashi():
            # Simple character-based fallback
            chunks: list[str] = []
            start = 0
            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                chunks.append(text[start:end])
                start = end - self.chunk_overlap
                if start <= 0:
                    start = end
            return chunks
        
        tagger = self._get_tagger()
        morphemes = list(tagger(text))
        
        chunks: list[str] = []
        current = ""
        
        for m in morphemes:
            surface = m.surface
            
            if len(current) + len(surface) > self.chunk_size:
                if current:
                    chunks.append(current)
                    
                    # Handle overlap
                    if self.chunk_overlap > 0:
                        overlap_start = max(0, len(current) - self.chunk_overlap)
                        current = current[overlap_start:]
                    else:
                        current = ""
            
            current += surface
        
        if current:
            chunks.append(current)
        
        return chunks
