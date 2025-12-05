"""Tests for MCP Tools definitions."""

import pytest

from graphrag_mcp_server.server.tools import (
    ALL_TOOLS,
    GLOBAL_SEARCH_TOOL,
    LOCAL_SEARCH_TOOL,
    DRIFT_SEARCH_TOOL,
    BASIC_SEARCH_TOOL,
    BUILD_INDEX_TOOL,
    GET_STATISTICS_TOOL,
    IMPORT_DOCUMENT_TOOL,
    IMPORT_DIRECTORY_TOOL,
    get_tool_by_name,
    list_tool_names,
)


class TestToolDefinitions:
    """Tests for tool definition structure."""
    
    def test_all_tools_contains_expected_count(self):
        """ALL_TOOLS should contain exactly 8 tools."""
        assert len(ALL_TOOLS) == 8
    
    def test_all_tools_have_required_fields(self):
        """Each tool should have name, description, and inputSchema."""
        for tool in ALL_TOOLS:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
    
    def test_input_schema_is_valid_json_schema(self):
        """Each inputSchema should be a valid JSON Schema object."""
        for tool in ALL_TOOLS:
            schema = tool["inputSchema"]
            assert schema["type"] == "object"
            assert "properties" in schema
            assert "required" in schema
    
    def test_global_search_tool_structure(self):
        """GLOBAL_SEARCH_TOOL should have correct structure."""
        assert GLOBAL_SEARCH_TOOL["name"] == "global_search"
        assert "query" in GLOBAL_SEARCH_TOOL["inputSchema"]["properties"]
        assert "community_level" in GLOBAL_SEARCH_TOOL["inputSchema"]["properties"]
        assert "response_type" in GLOBAL_SEARCH_TOOL["inputSchema"]["properties"]
        assert GLOBAL_SEARCH_TOOL["inputSchema"]["required"] == ["query"]
    
    def test_local_search_tool_structure(self):
        """LOCAL_SEARCH_TOOL should have correct structure."""
        assert LOCAL_SEARCH_TOOL["name"] == "local_search"
        assert "query" in LOCAL_SEARCH_TOOL["inputSchema"]["properties"]
        assert LOCAL_SEARCH_TOOL["inputSchema"]["required"] == ["query"]
    
    def test_drift_search_tool_structure(self):
        """DRIFT_SEARCH_TOOL should have correct structure."""
        assert DRIFT_SEARCH_TOOL["name"] == "drift_search"
        assert "query" in DRIFT_SEARCH_TOOL["inputSchema"]["properties"]
        assert DRIFT_SEARCH_TOOL["inputSchema"]["required"] == ["query"]
    
    def test_basic_search_tool_structure(self):
        """BASIC_SEARCH_TOOL should have correct structure."""
        assert BASIC_SEARCH_TOOL["name"] == "basic_search"
        assert "query" in BASIC_SEARCH_TOOL["inputSchema"]["properties"]
        assert "top_k" in BASIC_SEARCH_TOOL["inputSchema"]["properties"]
        assert BASIC_SEARCH_TOOL["inputSchema"]["required"] == ["query"]
    
    def test_build_index_tool_structure(self):
        """BUILD_INDEX_TOOL should have correct structure."""
        assert BUILD_INDEX_TOOL["name"] == "build_index"
        assert "input_path" in BUILD_INDEX_TOOL["inputSchema"]["properties"]
        assert "resume" in BUILD_INDEX_TOOL["inputSchema"]["properties"]
        assert BUILD_INDEX_TOOL["inputSchema"]["required"] == []
    
    def test_get_statistics_tool_structure(self):
        """GET_STATISTICS_TOOL should have correct structure."""
        assert GET_STATISTICS_TOOL["name"] == "get_statistics"
        assert GET_STATISTICS_TOOL["inputSchema"]["required"] == []

    def test_import_document_tool_structure(self):
        """IMPORT_DOCUMENT_TOOL should have correct structure."""
        assert IMPORT_DOCUMENT_TOOL["name"] == "import_document"
        assert "file_path" in IMPORT_DOCUMENT_TOOL["inputSchema"]["properties"]
        assert "chunk_size" in IMPORT_DOCUMENT_TOOL["inputSchema"]["properties"]
        assert "chunk_overlap" in IMPORT_DOCUMENT_TOOL["inputSchema"]["properties"]
        assert "auto_detect_language" in IMPORT_DOCUMENT_TOOL["inputSchema"]["properties"]
        assert IMPORT_DOCUMENT_TOOL["inputSchema"]["required"] == ["file_path"]

    def test_import_directory_tool_structure(self):
        """IMPORT_DIRECTORY_TOOL should have correct structure."""
        assert IMPORT_DIRECTORY_TOOL["name"] == "import_directory"
        assert "directory_path" in IMPORT_DIRECTORY_TOOL["inputSchema"]["properties"]
        assert "extensions" in IMPORT_DIRECTORY_TOOL["inputSchema"]["properties"]
        assert "recursive" in IMPORT_DIRECTORY_TOOL["inputSchema"]["properties"]
        assert IMPORT_DIRECTORY_TOOL["inputSchema"]["required"] == ["directory_path"]


class TestGetToolByName:
    """Tests for get_tool_by_name function."""
    
    def test_get_existing_tool(self):
        """Should return tool definition for existing tool."""
        tool = get_tool_by_name("global_search")
        assert tool is not None
        assert tool["name"] == "global_search"
    
    def test_get_all_tools_by_name(self):
        """Should be able to retrieve all tools by name."""
        tool_names = ["global_search", "local_search", "drift_search", 
                      "basic_search", "build_index", "get_statistics",
                      "import_document", "import_directory"]
        for name in tool_names:
            tool = get_tool_by_name(name)
            assert tool is not None
            assert tool["name"] == name
    
    def test_get_nonexistent_tool(self):
        """Should return None for nonexistent tool."""
        tool = get_tool_by_name("nonexistent_tool")
        assert tool is None


class TestListToolNames:
    """Tests for list_tool_names function."""
    
    def test_list_returns_all_names(self):
        """Should return all 8 tool names."""
        names = list_tool_names()
        assert len(names) == 8
    
    def test_list_contains_expected_names(self):
        """Should contain all expected tool names."""
        names = list_tool_names()
        expected = ["global_search", "local_search", "drift_search",
                    "basic_search", "build_index", "get_statistics",
                    "import_document", "import_directory"]
        for name in expected:
            assert name in names
    
    def test_list_returns_strings(self):
        """All items should be strings."""
        names = list_tool_names()
        assert all(isinstance(name, str) for name in names)
