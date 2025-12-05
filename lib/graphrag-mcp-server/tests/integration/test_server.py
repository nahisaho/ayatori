"""Integration tests for MCP Server."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from graphrag_mcp_server.server.app import (
    server,
    list_tools,
    call_tool,
    list_resources,
    read_resource,
    list_prompts,
    get_prompt,
)


class TestServerTools:
    """Integration tests for server tools."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_expected_tools(self):
        """Test that list_tools returns all expected tools."""
        tools = await list_tools()
        
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "global_search",
            "local_search",
            "drift_search",
            "basic_search",
            "build_index",
            "get_statistics",
        ]
        
        for expected in expected_tools:
            assert expected in tool_names, f"Expected tool '{expected}' not found"

    @pytest.mark.asyncio
    async def test_call_tool_global_search_with_mock_index(self):
        """Test global_search tool call with mocked index."""
        with patch("graphrag_mcp_server.handlers.search.get_settings") as mock_settings:
            mock_settings.return_value.index_path = MagicMock()
            mock_settings.return_value.index_path.exists.return_value = True
            mock_settings.return_value.llm_provider.value = "openai"
            
            result = await call_tool(
                "global_search",
                {"query": "test query", "community_level": 2}
            )
            
            assert len(result) == 1
            assert result[0].type == "text"
            # Mock response should be returned since graphrag API is not configured
            assert "Mock" in result[0].text or "test query" in result[0].text

    @pytest.mark.asyncio
    async def test_call_tool_get_statistics_with_mock_index(self):
        """Test get_statistics tool call."""
        with patch("graphrag_mcp_server.handlers.index.get_settings") as mock_settings:
            mock_settings.return_value.index_path = MagicMock()
            mock_settings.return_value.index_path.exists.return_value = True
            
            result = await call_tool("get_statistics", {})
            
            assert len(result) == 1
            assert result[0].type == "text"

    @pytest.mark.asyncio
    async def test_call_tool_unknown_tool(self):
        """Test calling an unknown tool."""
        result = await call_tool("unknown_tool", {})
        
        assert len(result) == 1
        assert "Unknown tool" in result[0].text


class TestServerResources:
    """Integration tests for server resources."""

    @pytest.mark.asyncio
    async def test_list_resources_returns_expected_resources(self):
        """Test that list_resources returns all expected resources."""
        resources = await list_resources()
        
        # Convert AnyUrl to string for comparison
        resource_uris = [str(r.uri) for r in resources]
        expected_uris = [
            "graphrag://entities",
            "graphrag://communities",
            "graphrag://relationships",
            "graphrag://statistics",
        ]
        
        for expected in expected_uris:
            assert expected in resource_uris, f"Expected resource '{expected}' not found"

    @pytest.mark.asyncio
    async def test_read_resource_statistics(self):
        """Test reading statistics resource."""
        with patch("graphrag_mcp_server.handlers.resources.get_settings") as mock_settings:
            mock_settings.return_value.index_path = MagicMock()
            mock_settings.return_value.index_path.exists.return_value = True
            
            result = await read_resource("graphrag://statistics")
            
            # Should return valid JSON
            data = json.loads(result)
            assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_read_resource_unknown(self):
        """Test reading unknown resource."""
        result = await read_resource("graphrag://unknown")
        
        data = json.loads(result)
        assert "error" in data


class TestServerPrompts:
    """Integration tests for server prompts."""

    @pytest.mark.asyncio
    async def test_list_prompts_returns_expected_prompts(self):
        """Test that list_prompts returns all expected prompts."""
        prompts = await list_prompts()
        
        prompt_names = [p.name for p in prompts]
        expected_prompts = [
            "analyze_topic",
            "explore_entity",
            "summarize_community",
            "compare_entities",
        ]
        
        for expected in expected_prompts:
            assert expected in prompt_names, f"Expected prompt '{expected}' not found"

    @pytest.mark.asyncio
    async def test_get_prompt_analyze_topic(self):
        """Test getting analyze_topic prompt."""
        result = await get_prompt("analyze_topic", {"topic": "AI", "depth": "brief"})
        
        assert result.description is not None
        assert "AI" in result.description
        assert len(result.messages) > 0

    @pytest.mark.asyncio
    async def test_get_prompt_explore_entity(self):
        """Test getting explore_entity prompt."""
        result = await get_prompt("explore_entity", {"entity_name": "Microsoft"})
        
        assert result.description is not None
        assert "Microsoft" in result.description

    @pytest.mark.asyncio
    async def test_get_prompt_unknown(self):
        """Test getting unknown prompt."""
        result = await get_prompt("unknown_prompt", {})
        
        assert "Unknown" in result.description


class TestServerEndToEnd:
    """End-to-end integration tests."""

    @pytest.mark.asyncio
    async def test_full_query_workflow(self):
        """Test a full query workflow: list tools -> call search -> format result."""
        # Step 1: List available tools
        tools = await list_tools()
        assert len(tools) > 0
        
        # Step 2: Find global_search tool
        search_tool = next((t for t in tools if t.name == "global_search"), None)
        assert search_tool is not None
        
        # Step 3: Execute search with mock
        with patch("graphrag_mcp_server.handlers.search.get_settings") as mock_settings:
            mock_settings.return_value.index_path = MagicMock()
            mock_settings.return_value.index_path.exists.return_value = True
            mock_settings.return_value.llm_provider.value = "openai"
            
            result = await call_tool("global_search", {"query": "What is GraphRAG?"})
            
            assert len(result) == 1
            assert result[0].type == "text"

    @pytest.mark.asyncio
    async def test_resource_and_stats_workflow(self):
        """Test resource listing and statistics retrieval."""
        # Step 1: List available resources
        resources = await list_resources()
        assert len(resources) > 0
        
        # Step 2: Read statistics resource
        with patch("graphrag_mcp_server.handlers.resources.get_settings") as mock_settings:
            mock_settings.return_value.index_path = MagicMock()
            mock_settings.return_value.index_path.exists.return_value = True
            
            result = await read_resource("graphrag://statistics")
            data = json.loads(result)
            assert isinstance(data, dict)
