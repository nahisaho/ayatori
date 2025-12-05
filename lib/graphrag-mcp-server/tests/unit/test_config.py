"""Tests for configuration module."""

import os
from pathlib import Path

import pytest

from graphrag_mcp_server.config.settings import (
    LLMProvider,
    Settings,
    VectorStoreType,
    get_settings,
)


class TestSettings:
    """Test Settings class."""

    def test_default_settings(self):
        """Test default settings values."""
        # Clear cache to ensure fresh settings
        get_settings.cache_clear()

        settings = Settings()

        assert settings.index_path == Path("./graphrag_index")
        assert settings.llm_provider == LLMProvider.OPENAI
        assert settings.llm_model == "gpt-4o"
        assert settings.vector_store == VectorStoreType.LANCEDB
        assert settings.server_port == 8080
        assert settings.default_community_level == 2
        assert settings.default_top_k == 10

    def test_settings_from_env(self, mock_env_vars: dict[str, str]):
        """Test settings loaded from environment variables."""
        get_settings.cache_clear()

        settings = Settings()

        assert str(settings.index_path) == mock_env_vars["GRAPHRAG_INDEX_PATH"]
        assert settings.llm_provider == LLMProvider.OPENAI
        assert settings.llm_api_key == "test-api-key"

    def test_validate_llm_config_openai_missing_key(self):
        """Test LLM config validation fails without API key."""
        settings = Settings(llm_provider=LLMProvider.OPENAI, llm_api_key=None)

        with pytest.raises(ValueError, match="GRAPHRAG_LLM_API_KEY"):
            settings.validate_llm_config()

    def test_validate_llm_config_openai_with_key(self, mock_env_vars: dict[str, str]):
        """Test LLM config validation passes with API key."""
        get_settings.cache_clear()

        settings = Settings()
        # Should not raise
        settings.validate_llm_config()

    def test_validate_llm_config_azure_missing_endpoint(self):
        """Test Azure OpenAI validation fails without endpoint."""
        settings = Settings(
            llm_provider=LLMProvider.AZURE_OPENAI,
            azure_openai_endpoint=None,
        )

        with pytest.raises(ValueError, match="AZURE_OPENAI_ENDPOINT"):
            settings.validate_llm_config()

    def test_validate_vector_store_azure_missing_endpoint(self):
        """Test Azure Search validation fails without endpoint."""
        settings = Settings(
            vector_store=VectorStoreType.AZURE_SEARCH,
            azure_search_endpoint=None,
        )

        with pytest.raises(ValueError, match="AZURE_SEARCH_ENDPOINT"):
            settings.validate_vector_store_config()

    def test_index_path_string_conversion(self):
        """Test that string index path is converted to Path."""
        settings = Settings(index_path="/tmp/test_index")  # type: ignore

        assert isinstance(settings.index_path, Path)
        assert str(settings.index_path) == "/tmp/test_index"

    def test_get_settings_cached(self):
        """Test that get_settings returns cached instance."""
        get_settings.cache_clear()

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2


class TestLLMProvider:
    """Test LLMProvider enum."""

    def test_provider_values(self):
        """Test provider enum values."""
        assert LLMProvider.OPENAI.value == "openai"
        assert LLMProvider.AZURE_OPENAI.value == "azure_openai"
        assert LLMProvider.ANTHROPIC.value == "anthropic"
        assert LLMProvider.OLLAMA.value == "ollama"


class TestVectorStoreType:
    """Test VectorStoreType enum."""

    def test_store_values(self):
        """Test vector store enum values."""
        assert VectorStoreType.LANCEDB.value == "lancedb"
        assert VectorStoreType.AZURE_SEARCH.value == "azure_search"
