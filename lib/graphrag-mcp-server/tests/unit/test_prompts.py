"""Tests for MCP Prompts definitions."""

import pytest

from graphrag_mcp_server.server.prompts import (
    ALL_PROMPTS,
    ANALYZE_ENTITY_PROMPT,
    EXPLORE_TOPIC_PROMPT,
    COMPARE_ENTITIES_PROMPT,
    get_prompt_by_name,
    list_prompt_names,
    get_prompt_template,
)


class TestPromptDefinitions:
    """Tests for prompt definition structure."""
    
    def test_all_prompts_count(self):
        """ALL_PROMPTS should contain 8 prompts."""
        assert len(ALL_PROMPTS) == 8
    
    def test_all_prompts_have_required_fields(self):
        """Each prompt should have name, description, and arguments."""
        for prompt in ALL_PROMPTS:
            assert "name" in prompt
            assert "description" in prompt
            assert "arguments" in prompt
    
    def test_arguments_have_required_fields(self):
        """Each argument should have name, description, and required."""
        for prompt in ALL_PROMPTS:
            for arg in prompt["arguments"]:
                assert "name" in arg
                assert "description" in arg
                assert "required" in arg
    
    def test_analyze_entity_prompt(self):
        """ANALYZE_ENTITY_PROMPT should have correct structure."""
        assert ANALYZE_ENTITY_PROMPT["name"] == "analyze_entity"
        args = {arg["name"]: arg for arg in ANALYZE_ENTITY_PROMPT["arguments"]}
        assert "entity_name" in args
        assert args["entity_name"]["required"] is True
    
    def test_explore_topic_prompt(self):
        """EXPLORE_TOPIC_PROMPT should have correct structure."""
        assert EXPLORE_TOPIC_PROMPT["name"] == "explore_topic"
        args = {arg["name"]: arg for arg in EXPLORE_TOPIC_PROMPT["arguments"]}
        assert "topic" in args
        assert args["topic"]["required"] is True
    
    def test_compare_entities_prompt(self):
        """COMPARE_ENTITIES_PROMPT should have correct structure."""
        assert COMPARE_ENTITIES_PROMPT["name"] == "compare_entities"
        args = {arg["name"]: arg for arg in COMPARE_ENTITIES_PROMPT["arguments"]}
        assert "entity_names" in args


class TestGetPromptByName:
    """Tests for get_prompt_by_name function."""
    
    def test_get_existing_prompt(self):
        """Should return prompt for existing name."""
        prompt = get_prompt_by_name("analyze_entity")
        assert prompt is not None
        assert prompt["name"] == "analyze_entity"
    
    def test_get_all_prompts_by_name(self):
        """Should be able to retrieve all prompts by name."""
        expected_names = [
            "analyze_entity",
            "explore_topic",
            "compare_entities",
            "summarize_community",
            "trace_relationship",
            "generate_questions",
            "corpus_overview",
            "find_similar",
        ]
        for name in expected_names:
            prompt = get_prompt_by_name(name)
            assert prompt is not None
    
    def test_get_nonexistent_prompt(self):
        """Should return None for nonexistent prompt."""
        prompt = get_prompt_by_name("nonexistent_prompt")
        assert prompt is None


class TestListPromptNames:
    """Tests for list_prompt_names function."""
    
    def test_list_returns_all_names(self):
        """Should return all 8 prompt names."""
        names = list_prompt_names()
        assert len(names) == 8
    
    def test_list_contains_expected_names(self):
        """Should contain expected prompt names."""
        names = list_prompt_names()
        expected = ["analyze_entity", "explore_topic", "compare_entities"]
        for name in expected:
            assert name in names
    
    def test_list_returns_strings(self):
        """All items should be strings."""
        names = list_prompt_names()
        assert all(isinstance(name, str) for name in names)


class TestGetPromptTemplate:
    """Tests for get_prompt_template function."""
    
    def test_render_analyze_entity(self):
        """Should render analyze_entity template."""
        result = get_prompt_template("analyze_entity", {"entity_name": "TestEntity"})
        assert result is not None
        assert "TestEntity" in result
        assert "medium" in result  # default depth
    
    def test_render_analyze_entity_with_depth(self):
        """Should respect depth parameter."""
        result = get_prompt_template("analyze_entity", {
            "entity_name": "TestEntity",
            "depth": "deep"
        })
        assert result is not None
        assert "deep" in result
    
    def test_render_explore_topic(self):
        """Should render explore_topic template."""
        result = get_prompt_template("explore_topic", {"topic": "AI Safety"})
        assert result is not None
        assert "AI Safety" in result
    
    def test_render_compare_entities(self):
        """Should render compare_entities template."""
        result = get_prompt_template("compare_entities", {
            "entity_names": "Entity1, Entity2, Entity3"
        })
        assert result is not None
        assert "Entity1, Entity2, Entity3" in result
    
    def test_render_trace_relationship(self):
        """Should render trace_relationship template."""
        result = get_prompt_template("trace_relationship", {
            "source_entity": "Source",
            "target_entity": "Target"
        })
        assert result is not None
        assert "Source" in result
        assert "Target" in result
    
    def test_render_nonexistent_prompt(self):
        """Should return None for nonexistent prompt."""
        result = get_prompt_template("nonexistent", {})
        assert result is None
    
    def test_render_corpus_overview(self):
        """Should render corpus_overview template."""
        result = get_prompt_template("corpus_overview", {})
        assert result is not None
        assert "overview" in result.lower()
    
    def test_render_find_similar(self):
        """Should render find_similar template."""
        result = get_prompt_template("find_similar", {"entity_name": "TestEntity"})
        assert result is not None
        assert "TestEntity" in result
