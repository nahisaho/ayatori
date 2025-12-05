"""Tests for CLI commands."""

from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from graphrag_mcp_server.cli.main import app

runner = CliRunner()


class TestCLI:
    """Test CLI commands."""

    def test_cli_help(self):
        """Test that --help works."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "graphrag-mcp" in result.output.lower() or "graphrag" in result.output.lower()

    def test_cli_version(self):
        """Test that --version works."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_serve_help(self):
        """Test serve command help."""
        result = runner.invoke(app, ["serve", "--help"])
        assert result.exit_code == 0
        assert "transport" in result.output.lower()
        assert "stdio" in result.output.lower() or "sse" in result.output.lower()

    def test_index_help(self):
        """Test index command help."""
        result = runner.invoke(app, ["index", "--help"])
        assert result.exit_code == 0
        assert "mode" in result.output.lower()
        assert "incremental" in result.output.lower() or "full" in result.output.lower()

    def test_query_help(self):
        """Test query command help."""
        result = runner.invoke(app, ["query", "--help"])
        assert result.exit_code == 0
        assert "type" in result.output.lower()
        assert "global" in result.output.lower()

    def test_stats_help(self):
        """Test stats command help."""
        result = runner.invoke(app, ["stats", "--help"])
        assert result.exit_code == 0
        assert "format" in result.output.lower()

    def test_serve_default_transport(self):
        """Test serve with default transport (mocked server)."""
        with patch("graphrag_mcp_server.cli.serve._run_stdio_server"):
            result = runner.invoke(app, ["serve"])
            # Should not error
            assert result.exit_code == 0
            assert "stdio" in result.output.lower()

    def test_serve_sse_transport(self):
        """Test serve with SSE transport (mocked server)."""
        with patch("graphrag_mcp_server.cli.serve._run_sse_server"):
            result = runner.invoke(app, ["serve", "--transport", "sse", "--port", "9000"])
            assert result.exit_code == 0
            assert "sse" in result.output.lower()
            assert "9000" in result.output

    def test_stats_json_format(self):
        """Test stats with JSON format."""
        result = runner.invoke(app, ["stats", "--format", "json"])
        assert result.exit_code == 0
        assert "json" in result.output.lower()
