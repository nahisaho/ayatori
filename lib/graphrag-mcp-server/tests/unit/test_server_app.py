"""Tests for MCP Server application."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from graphrag_mcp_server.server.app import create_server, GraphRAGContext


class TestCreateServer:
    """Tests for create_server function."""
    
    def test_create_server_returns_tuple(self):
        """create_server should return (server, context) tuple."""
        result = create_server()
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_create_server_returns_server_object(self):
        """First element should be a Server instance."""
        server, _ = create_server()
        # Check it has expected MCP server attributes
        assert hasattr(server, "name")
        assert server.name == "graphrag-mcp-server"
    
    def test_create_server_returns_context(self):
        """Second element should be GraphRAGContext."""
        _, context = create_server()
        assert isinstance(context, GraphRAGContext)
    
    def test_context_has_settings(self):
        """Context should have settings attribute."""
        _, context = create_server()
        assert hasattr(context, "settings")
    
    def test_context_has_index_path(self):
        """Context should have index_path attribute."""
        _, context = create_server()
        assert hasattr(context, "index_path")


class TestGraphRAGContext:
    """Tests for GraphRAGContext dataclass."""
    
    def test_context_creation_with_defaults(self):
        """Should create context with default values."""
        from graphrag_mcp_server.config import Settings
        settings = Settings()
        context = GraphRAGContext(settings=settings)
        assert context.settings is settings
        assert context.index_path is None
    
    def test_context_with_index_path(self):
        """Should accept custom index_path."""
        from graphrag_mcp_server.config import Settings
        from pathlib import Path
        settings = Settings()
        context = GraphRAGContext(settings=settings, index_path=Path("/test/path"))
        assert context.index_path == Path("/test/path")


class TestServerToolRegistration:
    """Tests for tool registration."""
    
    def test_server_has_tools_decorator(self):
        """Server should have tools registered."""
        server, _ = create_server()
        # The server should be set up to handle tool listing
        assert hasattr(server, "list_tools")
    
    def test_list_tools_callable(self):
        """list_tools should be callable."""
        server, _ = create_server()
        # Verify the method exists and is callable
        assert callable(getattr(server, "list_tools", None))


class TestServerResourceRegistration:
    """Tests for resource registration."""
    
    def test_server_has_resources_decorator(self):
        """Server should have resources registered."""
        server, _ = create_server()
        assert hasattr(server, "list_resources")
    
    def test_list_resources_callable(self):
        """list_resources should be callable."""
        server, _ = create_server()
        assert callable(getattr(server, "list_resources", None))


class TestServerPromptRegistration:
    """Tests for prompt registration."""
    
    def test_server_has_prompts_decorator(self):
        """Server should have prompts registered."""
        server, _ = create_server()
        assert hasattr(server, "list_prompts")
    
    def test_list_prompts_callable(self):
        """list_prompts should be callable."""
        server, _ = create_server()
        assert callable(getattr(server, "list_prompts", None))
