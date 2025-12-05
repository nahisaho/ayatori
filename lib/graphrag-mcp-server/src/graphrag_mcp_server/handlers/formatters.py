"""Response formatters for GraphRAG MCP Server.

Provides formatting utilities for search results, supporting
multiple output formats (markdown, text, JSON).
"""

import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class OutputFormat(str, Enum):
    """Supported output formats."""

    MARKDOWN = "markdown"
    TEXT = "text"
    JSON = "json"


@dataclass
class FormattedResponse:
    """A formatted search response."""

    content: str
    format: OutputFormat
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "format": self.format.value,
            "metadata": self.metadata,
        }


class ResponseFormatter:
    """Formats search responses for different output types."""

    def __init__(self, default_format: OutputFormat = OutputFormat.MARKDOWN):
        """Initialize formatter.

        Args:
            default_format: Default output format to use.
        """
        self.default_format = default_format

    def format(
        self,
        response: str,
        context_data: dict[str, Any] | None = None,
        output_format: OutputFormat | None = None,
        include_sources: bool = True,
    ) -> FormattedResponse:
        """Format a search response.

        Args:
            response: The raw response text.
            context_data: Optional context data from the search.
            output_format: Desired output format.
            include_sources: Whether to include source references.

        Returns:
            FormattedResponse with the formatted content.
        """
        fmt = output_format or self.default_format
        context_data = context_data or {}

        if fmt == OutputFormat.MARKDOWN:
            content = self._format_markdown(response, context_data, include_sources)
        elif fmt == OutputFormat.TEXT:
            content = self._format_text(response, context_data, include_sources)
        elif fmt == OutputFormat.JSON:
            content = self._format_json(response, context_data)
        else:
            content = response

        return FormattedResponse(
            content=content,
            format=fmt,
            metadata={"source_count": len(context_data.get("sources", []))},
        )

    def _format_markdown(
        self, response: str, context_data: dict[str, Any], include_sources: bool
    ) -> str:
        """Format response as Markdown.

        Args:
            response: Raw response text.
            context_data: Context data with sources.
            include_sources: Whether to append sources.

        Returns:
            Markdown-formatted string.
        """
        parts = [response]

        if include_sources and context_data:
            sources = self._extract_sources(context_data)
            if sources:
                parts.append("\n\n---\n")
                parts.append("### Sources\n")
                for i, source in enumerate(sources, 1):
                    parts.append(f"{i}. {source}\n")

        return "".join(parts)

    def _format_text(
        self, response: str, context_data: dict[str, Any], include_sources: bool
    ) -> str:
        """Format response as plain text.

        Args:
            response: Raw response text.
            context_data: Context data with sources.
            include_sources: Whether to append sources.

        Returns:
            Plain text formatted string.
        """
        # Remove markdown formatting
        text = response
        text = text.replace("**", "")
        text = text.replace("*", "")
        text = text.replace("###", "")
        text = text.replace("##", "")
        text = text.replace("#", "")

        parts = [text]

        if include_sources and context_data:
            sources = self._extract_sources(context_data)
            if sources:
                parts.append("\n\n" + "=" * 40 + "\n")
                parts.append("Sources:\n")
                for i, source in enumerate(sources, 1):
                    parts.append(f"  {i}. {source}\n")

        return "".join(parts)

    def _format_json(
        self, response: str, context_data: dict[str, Any]
    ) -> str:
        """Format response as JSON.

        Args:
            response: Raw response text.
            context_data: Context data.

        Returns:
            JSON-formatted string.
        """
        data = {
            "response": response,
            "sources": self._extract_sources(context_data),
            "entities": self._extract_entities(context_data),
            "communities": self._extract_communities(context_data),
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _extract_sources(self, context_data: dict[str, Any]) -> list[str]:
        """Extract source references from context data.

        Args:
            context_data: Context data dictionary.

        Returns:
            List of source reference strings.
        """
        sources = []

        # Try different possible source fields
        if "sources" in context_data:
            sources = context_data["sources"]
        elif "text_units" in context_data:
            for unit in context_data["text_units"][:5]:  # Limit to 5
                if isinstance(unit, dict):
                    text = unit.get("text", "")[:100]
                    sources.append(f"Text Unit: {text}...")
                elif isinstance(unit, str):
                    sources.append(f"Text Unit: {unit[:100]}...")

        return sources

    def _extract_entities(self, context_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract entity information from context data.

        Args:
            context_data: Context data dictionary.

        Returns:
            List of entity dictionaries.
        """
        entities = []

        if "entities" in context_data:
            for entity in context_data["entities"][:10]:  # Limit to 10
                if isinstance(entity, dict):
                    entities.append({
                        "name": entity.get("name", "Unknown"),
                        "type": entity.get("type", "Unknown"),
                        "description": entity.get("description", "")[:200],
                    })

        return entities

    def _extract_communities(self, context_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract community information from context data.

        Args:
            context_data: Context data dictionary.

        Returns:
            List of community dictionaries.
        """
        communities = []

        if "communities" in context_data:
            for community in context_data["communities"][:5]:  # Limit to 5
                if isinstance(community, dict):
                    communities.append({
                        "id": community.get("id", ""),
                        "title": community.get("title", "Unknown"),
                        "summary": community.get("summary", "")[:200],
                    })

        return communities


def format_search_result(
    response: str,
    context_data: dict[str, Any] | None = None,
    output_format: str = "markdown",
    include_sources: bool = True,
) -> str:
    """Convenience function to format a search result.

    Args:
        response: Raw response text.
        context_data: Optional context data.
        output_format: Output format string.
        include_sources: Whether to include sources.

    Returns:
        Formatted response string.
    """
    try:
        fmt = OutputFormat(output_format.lower())
    except ValueError:
        fmt = OutputFormat.MARKDOWN

    formatter = ResponseFormatter()
    result = formatter.format(
        response=response,
        context_data=context_data,
        output_format=fmt,
        include_sources=include_sources,
    )
    return result.content


def format_statistics(
    entity_count: int,
    relationship_count: int,
    community_count: int,
    text_unit_count: int,
    document_count: int,
    output_format: str = "markdown",
) -> str:
    """Format index statistics.

    Args:
        entity_count: Number of entities.
        relationship_count: Number of relationships.
        community_count: Number of communities.
        text_unit_count: Number of text units.
        document_count: Number of documents.
        output_format: Output format string.

    Returns:
        Formatted statistics string.
    """
    if output_format == "json":
        return json.dumps({
            "entities": entity_count,
            "relationships": relationship_count,
            "communities": community_count,
            "text_units": text_unit_count,
            "documents": document_count,
        }, indent=2)
    
    if output_format == "text":
        return (
            f"Index Statistics\n"
            f"================\n"
            f"Entities: {entity_count}\n"
            f"Relationships: {relationship_count}\n"
            f"Communities: {community_count}\n"
            f"Text Units: {text_unit_count}\n"
            f"Documents: {document_count}"
        )
    
    # Default: markdown
    return (
        f"## Index Statistics\n\n"
        f"| Metric | Count |\n"
        f"|--------|-------|\n"
        f"| Entities | {entity_count:,} |\n"
        f"| Relationships | {relationship_count:,} |\n"
        f"| Communities | {community_count:,} |\n"
        f"| Text Units | {text_unit_count:,} |\n"
        f"| Documents | {document_count:,} |"
    )
