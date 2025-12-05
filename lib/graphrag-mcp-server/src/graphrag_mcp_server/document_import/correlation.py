"""Correlation builder for chunk relationship graphs.

This module builds correlation graphs between chunks,
identifying relationships like adjacency, semantic similarity,
and hierarchical structure.
"""

from __future__ import annotations

from uuid import uuid4

from graphrag_mcp_server.document_import.models import (
    ChunkCorrelation,
    CorrelationGraph,
    CorrelationType,
    TextChunk,
)


class CorrelationBuilder:
    """Builds correlation graphs between text chunks.
    
    Analyzes chunks to identify relationships:
    - Adjacent: Sequential chunks in document
    - Semantic: Similar content (requires embeddings)
    - Hierarchical: Parent-child from headings
    - Cooccurrence: Shared entities/terms
    
    Example:
        >>> builder = CorrelationBuilder()
        >>> graph = await builder.build_graph(chunks)
        >>> print(f"Found {graph.edge_count} correlations")
    """
    
    def __init__(
        self,
        *,
        similarity_threshold: float = 0.7,
        build_adjacent: bool = True,
        build_semantic: bool = True,
    ):
        """Initialize the correlation builder.
        
        Args:
            similarity_threshold: Threshold for semantic similarity (0-1).
            build_adjacent: Whether to build adjacent correlations.
            build_semantic: Whether to build semantic correlations.
        """
        self.similarity_threshold = similarity_threshold
        self.build_adjacent = build_adjacent
        self.build_semantic = build_semantic
    
    async def build_graph(self, chunks: list[TextChunk]) -> CorrelationGraph:
        """Build a correlation graph from chunks.
        
        Args:
            chunks: List of text chunks to analyze.
            
        Returns:
            CorrelationGraph with identified relationships.
        """
        if not chunks:
            return CorrelationGraph(
                document_id=uuid4(),
                node_count=0,
                edge_count=0,
            )
        
        # Create graph with nodes
        graph = CorrelationGraph(
            document_id=chunks[0].document_id,
            nodes=[c.id for c in chunks],
            node_count=len(chunks),
        )
        
        # Build adjacent correlations
        if self.build_adjacent:
            self._add_adjacent_correlations(graph, chunks)
        
        # Build semantic correlations (placeholder - requires embeddings)
        if self.build_semantic:
            await self._add_semantic_correlations(graph, chunks)
        
        return graph
    
    def _add_adjacent_correlations(
        self,
        graph: CorrelationGraph,
        chunks: list[TextChunk],
    ) -> None:
        """Add correlations between adjacent chunks.
        
        Adjacent chunks are those that are sequential in the document.
        
        Args:
            graph: Graph to add correlations to.
            chunks: List of chunks.
        """
        # Sort by chunk index to ensure correct ordering
        sorted_chunks = sorted(chunks, key=lambda c: c.chunk_index)
        
        for i in range(len(sorted_chunks) - 1):
            current = sorted_chunks[i]
            next_chunk = sorted_chunks[i + 1]
            
            correlation = ChunkCorrelation(
                source_chunk_id=current.id,
                target_chunk_id=next_chunk.id,
                correlation_type=CorrelationType.ADJACENT,
                weight=1.0,
                metadata={"distance": 1},
            )
            graph.add_correlation(correlation)
    
    async def _add_semantic_correlations(
        self,
        graph: CorrelationGraph,
        chunks: list[TextChunk],
    ) -> None:
        """Add correlations based on semantic similarity.
        
        This is a placeholder that uses simple text overlap.
        Full implementation would use embeddings.
        
        Args:
            graph: Graph to add correlations to.
            chunks: List of chunks.
        """
        # Simple implementation using term overlap
        # In production, this would use embeddings
        
        for i, chunk_a in enumerate(chunks):
            words_a = set(chunk_a.text.lower().split())
            
            for j, chunk_b in enumerate(chunks):
                if i >= j:  # Skip self and already-processed pairs
                    continue
                
                if abs(chunk_a.chunk_index - chunk_b.chunk_index) <= 1:
                    # Skip adjacent chunks (already covered)
                    continue
                
                words_b = set(chunk_b.text.lower().split())
                
                # Calculate Jaccard similarity
                intersection = len(words_a & words_b)
                union = len(words_a | words_b)
                similarity = intersection / union if union > 0 else 0
                
                if similarity >= self.similarity_threshold:
                    correlation = ChunkCorrelation(
                        source_chunk_id=chunk_a.id,
                        target_chunk_id=chunk_b.id,
                        correlation_type=CorrelationType.SEMANTIC,
                        weight=similarity,
                        metadata={"similarity_score": similarity},
                    )
                    graph.add_correlation(correlation)
