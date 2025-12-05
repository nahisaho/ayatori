"""Tests for response formatters."""

import json
import pytest

from graphrag_mcp_server.handlers.formatters import (
    OutputFormat,
    FormattedResponse,
    ResponseFormatter,
    format_search_result,
    format_statistics,
)


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    def test_markdown_value(self):
        """Should have correct markdown value."""
        assert OutputFormat.MARKDOWN.value == "markdown"

    def test_text_value(self):
        """Should have correct text value."""
        assert OutputFormat.TEXT.value == "text"

    def test_json_value(self):
        """Should have correct json value."""
        assert OutputFormat.JSON.value == "json"


class TestFormattedResponse:
    """Tests for FormattedResponse dataclass."""

    def test_response_creation(self):
        """Should create response with all fields."""
        response = FormattedResponse(
            content="test content",
            format=OutputFormat.MARKDOWN,
            metadata={"key": "value"},
        )
        assert response.content == "test content"
        assert response.format == OutputFormat.MARKDOWN

    def test_to_dict(self):
        """Should convert to dictionary."""
        response = FormattedResponse(
            content="test",
            format=OutputFormat.JSON,
            metadata={},
        )
        d = response.to_dict()
        assert d["content"] == "test"
        assert d["format"] == "json"


class TestResponseFormatter:
    """Tests for ResponseFormatter class."""

    def test_formatter_default_format(self):
        """Should use markdown as default."""
        formatter = ResponseFormatter()
        assert formatter.default_format == OutputFormat.MARKDOWN

    def test_formatter_custom_default(self):
        """Should accept custom default format."""
        formatter = ResponseFormatter(default_format=OutputFormat.TEXT)
        assert formatter.default_format == OutputFormat.TEXT

    def test_format_markdown(self):
        """Should format as markdown."""
        formatter = ResponseFormatter()
        result = formatter.format("Test response", output_format=OutputFormat.MARKDOWN)
        assert result.format == OutputFormat.MARKDOWN
        assert "Test response" in result.content

    def test_format_text(self):
        """Should format as plain text."""
        formatter = ResponseFormatter()
        result = formatter.format("**Bold** text", output_format=OutputFormat.TEXT)
        assert result.format == OutputFormat.TEXT
        # Markdown should be stripped
        assert "**" not in result.content

    def test_format_json(self):
        """Should format as JSON."""
        formatter = ResponseFormatter()
        result = formatter.format(
            "Test response",
            context_data={"entities": []},
            output_format=OutputFormat.JSON,
        )
        assert result.format == OutputFormat.JSON
        # Should be valid JSON
        parsed = json.loads(result.content)
        assert "response" in parsed

    def test_format_with_sources(self):
        """Should include sources in markdown."""
        formatter = ResponseFormatter()
        result = formatter.format(
            "Test response",
            context_data={"sources": ["Source 1", "Source 2"]},
            output_format=OutputFormat.MARKDOWN,
            include_sources=True,
        )
        assert "Sources" in result.content

    def test_format_without_sources(self):
        """Should not include sources when disabled."""
        formatter = ResponseFormatter()
        result = formatter.format(
            "Test response",
            context_data={"sources": ["Source 1"]},
            output_format=OutputFormat.MARKDOWN,
            include_sources=False,
        )
        assert "Sources" not in result.content


class TestFormatSearchResult:
    """Tests for format_search_result convenience function."""

    def test_format_default(self):
        """Should use markdown by default."""
        result = format_search_result("Test response")
        assert "Test response" in result

    def test_format_with_invalid_format(self):
        """Should fall back to markdown for invalid format."""
        result = format_search_result("Test", output_format="invalid")
        assert "Test" in result

    def test_format_json(self):
        """Should format as JSON when requested."""
        result = format_search_result("Test", output_format="json")
        parsed = json.loads(result)
        assert parsed["response"] == "Test"


class TestFormatStatistics:
    """Tests for format_statistics function."""

    def test_format_markdown_table(self):
        """Should format as markdown table."""
        result = format_statistics(
            entity_count=100,
            relationship_count=200,
            community_count=10,
            text_unit_count=50,
            document_count=5,
            output_format="markdown",
        )
        assert "| Entities |" in result
        assert "100" in result

    def test_format_text(self):
        """Should format as plain text."""
        result = format_statistics(
            entity_count=100,
            relationship_count=200,
            community_count=10,
            text_unit_count=50,
            document_count=5,
            output_format="text",
        )
        assert "Entities: 100" in result
        assert "=" in result  # Separator

    def test_format_json(self):
        """Should format as JSON."""
        result = format_statistics(
            entity_count=100,
            relationship_count=200,
            community_count=10,
            text_unit_count=50,
            document_count=5,
            output_format="json",
        )
        parsed = json.loads(result)
        assert parsed["entities"] == 100
        assert parsed["relationships"] == 200
