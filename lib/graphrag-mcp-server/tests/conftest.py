"""Pytest configuration and fixtures for GraphRAG MCP Server tests."""

import os
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def temp_index_path(tmp_path: Path) -> Path:
    """Create a temporary index path.

    Args:
        tmp_path: Pytest temporary directory fixture

    Returns:
        Path to temporary index directory
    """
    index_path = tmp_path / "graphrag_index"
    index_path.mkdir(parents=True, exist_ok=True)
    return index_path


@pytest.fixture
def mock_env_vars(temp_index_path: Path) -> Generator[dict[str, str], None, None]:
    """Set up mock environment variables.

    Args:
        temp_index_path: Temporary index path

    Yields:
        Dictionary of environment variables
    """
    env_vars = {
        "GRAPHRAG_INDEX_PATH": str(temp_index_path),
        "GRAPHRAG_LLM_PROVIDER": "openai",
        "GRAPHRAG_LLM_API_KEY": "test-api-key",
        "GRAPHRAG_LLM_MODEL": "gpt-4o",
    }

    # Save original values
    original = {k: os.environ.get(k) for k in env_vars}

    # Set test values
    os.environ.update(env_vars)

    yield env_vars

    # Restore original values
    for key, value in original.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest.fixture
def mock_graphrag_result() -> dict:
    """Create a mock GraphRAG search result.

    Returns:
        Mock search result dictionary
    """
    return {
        "response": "This is a test response from GraphRAG.",
        "context_data": {
            "entities": [
                {"name": "Entity1", "type": "PERSON", "description": "Test entity 1"},
                {"name": "Entity2", "type": "ORGANIZATION", "description": "Test entity 2"},
            ],
            "relationships": [
                {
                    "source": "Entity1",
                    "target": "Entity2",
                    "description": "works at",
                }
            ],
            "sources": [
                {"id": "doc1", "text": "Sample text from document 1"},
            ],
        },
        "llm_calls": 1,
        "prompt_tokens": 100,
        "completion_tokens": 50,
    }


@pytest.fixture
def mock_llm_response() -> MagicMock:
    """Create a mock LLM response.

    Returns:
        MagicMock configured as LLM response
    """
    mock = MagicMock()
    mock.content = "Mock LLM response"
    mock.usage = {"prompt_tokens": 100, "completion_tokens": 50}
    return mock


@pytest.fixture
def sample_query() -> str:
    """Sample query for testing.

    Returns:
        Sample query string
    """
    return "What are the main entities in the dataset?"


@pytest.fixture
def sample_documents() -> list[dict]:
    """Sample documents for testing.

    Returns:
        List of sample document dictionaries
    """
    return [
        {
            "id": "doc1",
            "title": "Document 1",
            "text": "This is the first test document. It contains information about Entity1.",
        },
        {
            "id": "doc2",
            "title": "Document 2",
            "text": "This is the second test document. It discusses Entity2 and its relationship with Entity1.",
        },
    ]
