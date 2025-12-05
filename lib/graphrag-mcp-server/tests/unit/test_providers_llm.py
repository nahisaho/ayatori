"""Unit tests for LLM providers module (esperanto-based)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from graphrag_mcp_server.config import LLMProvider
from graphrag_mcp_server.providers.llm import (
    LLMConfig,
    BaseLLMAdapter,
    EsperantoAdapter,
    AzureOpenAIAdapter,
    OpenAIAdapter,
    OllamaAdapter,
    MockLLMAdapter,
    create_llm_adapter,
    get_graphrag_llm_config,
)
from graphrag_mcp_server.errors import LLMProviderError


# ============================================================================
# LLMConfig Tests
# ============================================================================

class TestLLMConfig:
    """Tests for LLMConfig dataclass."""

    def test_create_minimal_config(self):
        """Test creating config with minimal parameters."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4o",
        )
        
        assert config.provider == LLMProvider.OPENAI
        assert config.model == "gpt-4o"
        assert config.api_key is None
        assert config.max_tokens == 4096
        assert config.temperature == 0.0
        assert config.embedding_model == "text-embedding-3-small"

    def test_create_full_config(self):
        """Test creating config with all parameters."""
        config = LLMConfig(
            provider=LLMProvider.AZURE_OPENAI,
            model="gpt-4",
            api_key="test-key",
            api_base="https://test.openai.azure.com",
            api_version="2024-02-01",
            deployment_name="test-deployment",
            max_tokens=2048,
            temperature=0.7,
            embedding_model="text-embedding-3-large",
        )
        
        assert config.provider == LLMProvider.AZURE_OPENAI
        assert config.api_key == "test-key"
        assert config.api_base == "https://test.openai.azure.com"
        assert config.deployment_name == "test-deployment"
        assert config.max_tokens == 2048
        assert config.temperature == 0.7
        assert config.embedding_model == "text-embedding-3-large"

    def test_to_dict_minimal(self):
        """Test converting minimal config to dict."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4o",
        )
        
        result = config.to_dict()
        
        assert result["model"] == "gpt-4o"
        assert result["max_tokens"] == 4096
        assert result["temperature"] == 0.0
        assert "api_key" not in result

    def test_to_dict_full(self):
        """Test converting full config to dict."""
        config = LLMConfig(
            provider=LLMProvider.AZURE_OPENAI,
            model="gpt-4",
            api_key="test-key",
            api_base="https://test.openai.azure.com",
            api_version="2024-02-01",
            deployment_name="test-deployment",
        )
        
        result = config.to_dict()
        
        assert result["api_key"] == "test-key"
        assert result["api_base"] == "https://test.openai.azure.com"
        assert result["api_version"] == "2024-02-01"
        assert result["deployment_name"] == "test-deployment"


# ============================================================================
# EsperantoAdapter Tests
# ============================================================================

class TestEsperantoAdapter:
    """Tests for Esperanto unified adapter."""

    @pytest.fixture
    def openai_config(self):
        """Create valid OpenAI config."""
        return LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4o",
            api_key="test-key",
        )

    @pytest.fixture
    def azure_config(self):
        """Create valid Azure OpenAI config."""
        return LLMConfig(
            provider=LLMProvider.AZURE_OPENAI,
            model="gpt-4",
            api_key="test-key",
            api_base="https://test.openai.azure.com",
            deployment_name="test-deployment",
        )

    @pytest.fixture
    def anthropic_config(self):
        """Create valid Anthropic config."""
        return LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-5-sonnet-20241022",
            api_key="test-key",
        )

    @pytest.fixture
    def invalid_openai_config(self):
        """Create invalid OpenAI config (missing API key)."""
        return LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4o",
        )

    @pytest.fixture
    def invalid_azure_config(self):
        """Create invalid Azure OpenAI config."""
        return LLMConfig(
            provider=LLMProvider.AZURE_OPENAI,
            model="gpt-4",
        )

    def test_get_provider_name_openai(self, openai_config):
        """Test provider name mapping for OpenAI."""
        adapter = EsperantoAdapter(openai_config)
        assert adapter._get_provider_name() == "openai"

    def test_get_provider_name_azure(self, azure_config):
        """Test provider name mapping for Azure."""
        adapter = EsperantoAdapter(azure_config)
        assert adapter._get_provider_name() == "azure"

    def test_get_provider_name_anthropic(self, anthropic_config):
        """Test provider name mapping for Anthropic."""
        adapter = EsperantoAdapter(anthropic_config)
        assert adapter._get_provider_name() == "anthropic"

    def test_validate_config_openai_valid(self, openai_config):
        """Test OpenAI config validation with valid config."""
        adapter = EsperantoAdapter(openai_config)
        assert adapter.validate_config() is True

    def test_validate_config_openai_invalid(self, invalid_openai_config):
        """Test OpenAI config validation with missing key."""
        adapter = EsperantoAdapter(invalid_openai_config)
        assert adapter.validate_config() is False

    def test_validate_config_azure_valid(self, azure_config):
        """Test Azure config validation with valid config."""
        adapter = EsperantoAdapter(azure_config)
        assert adapter.validate_config() is True

    def test_validate_config_azure_invalid(self, invalid_azure_config):
        """Test Azure config validation with missing fields."""
        adapter = EsperantoAdapter(invalid_azure_config)
        assert adapter.validate_config() is False

    def test_validate_config_anthropic_valid(self, anthropic_config):
        """Test Anthropic config validation with valid config."""
        adapter = EsperantoAdapter(anthropic_config)
        assert adapter.validate_config() is True

    def test_get_llm_config_openai(self, openai_config):
        """Test LLM config building for OpenAI."""
        adapter = EsperantoAdapter(openai_config)
        config = adapter._get_llm_config()
        
        assert config["api_key"] == "test-key"
        assert config["temperature"] == 0.0
        assert config["max_tokens"] == 4096

    def test_get_llm_config_azure(self, azure_config):
        """Test LLM config building for Azure."""
        adapter = EsperantoAdapter(azure_config)
        config = adapter._get_llm_config()
        
        assert config["api_key"] == "test-key"
        assert config["azure_endpoint"] == "https://test.openai.azure.com"

    @pytest.mark.asyncio
    async def test_generate_invalid_config(self, invalid_openai_config):
        """Test generate with invalid config raises error."""
        adapter = EsperantoAdapter(invalid_openai_config)
        
        with pytest.raises(LLMProviderError):
            await adapter.generate("Test prompt")

    @pytest.mark.asyncio
    async def test_embed_invalid_config(self, invalid_openai_config):
        """Test embed with invalid config raises error."""
        adapter = EsperantoAdapter(invalid_openai_config)
        
        with pytest.raises(LLMProviderError):
            await adapter.embed("Test text")

    @pytest.mark.asyncio
    async def test_generate_with_mock_esperanto(self, openai_config):
        """Test generate with mocked esperanto."""
        adapter = EsperantoAdapter(openai_config)
        
        # Create mock response
        mock_message = MagicMock()
        mock_message.content = "Generated response"
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        
        # Mock the LLM
        mock_llm = AsyncMock()
        mock_llm.achat_complete = AsyncMock(return_value=mock_response)
        
        with patch.object(adapter, '_ensure_llm', return_value=mock_llm):
            result = await adapter.generate("Test prompt")
            assert result == "Generated response"

    @pytest.mark.asyncio
    async def test_embed_with_mock_esperanto(self, openai_config):
        """Test embed with mocked esperanto."""
        adapter = EsperantoAdapter(openai_config)
        
        # Create mock response
        mock_embedding_data = MagicMock()
        mock_embedding_data.embedding = [0.1, 0.2, 0.3]
        
        mock_response = MagicMock()
        mock_response.data = [mock_embedding_data]
        
        # Mock the embedder
        mock_embedder = AsyncMock()
        mock_embedder.aembed = AsyncMock(return_value=mock_response)
        
        with patch.object(adapter, '_ensure_embedder', return_value=mock_embedder):
            result = await adapter.embed("Test text")
            assert result == [0.1, 0.2, 0.3]


# ============================================================================
# Backward Compatibility Adapter Tests
# ============================================================================

class TestAzureOpenAIAdapter:
    """Tests for Azure OpenAI backward compatibility adapter."""

    def test_inherits_from_esperanto(self):
        """Test that AzureOpenAIAdapter inherits from EsperantoAdapter."""
        assert issubclass(AzureOpenAIAdapter, EsperantoAdapter)

    def test_config_provider_override(self):
        """Test that provider is set to AZURE_OPENAI."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,  # Wrong provider
            model="gpt-4",
            api_key="test-key",
            api_base="https://test.openai.azure.com",
            deployment_name="test-deployment",
        )
        adapter = AzureOpenAIAdapter(config)
        assert adapter.config.provider == LLMProvider.AZURE_OPENAI


class TestOpenAIAdapter:
    """Tests for OpenAI backward compatibility adapter."""

    def test_inherits_from_esperanto(self):
        """Test that OpenAIAdapter inherits from EsperantoAdapter."""
        assert issubclass(OpenAIAdapter, EsperantoAdapter)

    def test_config_provider_override(self):
        """Test that provider is set to OPENAI."""
        config = LLMConfig(
            provider=LLMProvider.AZURE_OPENAI,  # Wrong provider
            model="gpt-4o",
            api_key="test-key",
        )
        adapter = OpenAIAdapter(config)
        assert adapter.config.provider == LLMProvider.OPENAI


class TestOllamaAdapter:
    """Tests for Ollama backward compatibility adapter."""

    def test_inherits_from_esperanto(self):
        """Test that OllamaAdapter inherits from EsperantoAdapter."""
        assert issubclass(OllamaAdapter, EsperantoAdapter)

    def test_config_provider_override(self):
        """Test that provider is set to OLLAMA."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,  # Wrong provider
            model="llama3.1",
        )
        adapter = OllamaAdapter(config)
        assert adapter.config.provider == LLMProvider.OLLAMA

    def test_default_base_url(self):
        """Test default base URL for Ollama."""
        config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="llama3.1",
        )
        adapter = OllamaAdapter(config)
        assert adapter.config.api_base == "http://localhost:11434"

    def test_custom_base_url(self):
        """Test custom base URL for remote Ollama (e.g., Windows)."""
        config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="llama3.1",
            api_base="http://windows-pc:11434",
        )
        adapter = OllamaAdapter(config)
        assert adapter.config.api_base == "http://windows-pc:11434"

    def test_validate_config_always_true(self):
        """Test Ollama config validation (no API key required)."""
        config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="llama3.1",
        )
        adapter = OllamaAdapter(config)
        assert adapter.validate_config() is True

    def test_default_embedding_model(self):
        """Test default embedding model for Ollama."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="llama3.1",
        )
        adapter = OllamaAdapter(config)
        assert adapter.config.embedding_model == "nomic-embed-text"


class TestEsperantoAdapterOllama:
    """Tests for EsperantoAdapter with Ollama provider."""

    @pytest.fixture
    def ollama_config(self):
        """Create valid Ollama config."""
        return LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="llama3.1",
            api_base="http://localhost:11434",
            embedding_model="nomic-embed-text",
        )

    @pytest.fixture
    def ollama_remote_config(self):
        """Create Ollama config for remote Windows server."""
        return LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="llama3.1",
            api_base="http://192.168.1.100:11434",
            embedding_model="nomic-embed-text",
        )

    def test_get_provider_name_ollama(self, ollama_config):
        """Test provider name mapping for Ollama."""
        adapter = EsperantoAdapter(ollama_config)
        assert adapter._get_provider_name() == "ollama"

    def test_validate_config_ollama(self, ollama_config):
        """Test Ollama config validation (no API key required)."""
        adapter = EsperantoAdapter(ollama_config)
        assert adapter.validate_config() is True

    def test_get_llm_config_ollama(self, ollama_config):
        """Test LLM config building for Ollama."""
        adapter = EsperantoAdapter(ollama_config)
        config = adapter._get_llm_config()
        
        assert config["base_url"] == "http://localhost:11434"
        assert config["temperature"] == 0.0
        assert config["max_tokens"] == 4096
        assert "api_key" not in config  # Ollama doesn't need API key

    def test_get_llm_config_ollama_remote(self, ollama_remote_config):
        """Test LLM config building for remote Ollama."""
        adapter = EsperantoAdapter(ollama_remote_config)
        config = adapter._get_llm_config()
        
        assert config["base_url"] == "http://192.168.1.100:11434"

    def test_get_embedding_config_ollama(self, ollama_config):
        """Test embedding config building for Ollama."""
        adapter = EsperantoAdapter(ollama_config)
        config = adapter._get_embedding_config()
        
        assert config["base_url"] == "http://localhost:11434"
        assert "api_key" not in config

    @pytest.mark.asyncio
    async def test_generate_with_mock_esperanto_ollama(self, ollama_config):
        """Test generate with mocked esperanto for Ollama."""
        adapter = EsperantoAdapter(ollama_config)
        
        # Create mock response
        mock_message = MagicMock()
        mock_message.content = "Ollama generated response"
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        
        # Mock the LLM
        mock_llm = AsyncMock()
        mock_llm.achat_complete = AsyncMock(return_value=mock_response)
        
        with patch.object(adapter, '_ensure_llm', return_value=mock_llm):
            result = await adapter.generate("Test prompt")
            assert result == "Ollama generated response"

    @pytest.mark.asyncio
    async def test_embed_with_mock_esperanto_ollama(self, ollama_config):
        """Test embed with mocked esperanto for Ollama."""
        adapter = EsperantoAdapter(ollama_config)
        
        # Create mock response
        mock_embedding_data = MagicMock()
        mock_embedding_data.embedding = [0.1, 0.2, 0.3, 0.4]
        
        mock_response = MagicMock()
        mock_response.data = [mock_embedding_data]
        
        # Mock the embedder
        mock_embedder = AsyncMock()
        mock_embedder.aembed = AsyncMock(return_value=mock_response)
        
        with patch.object(adapter, '_ensure_embedder', return_value=mock_embedder):
            result = await adapter.embed("Test text")
            assert result == [0.1, 0.2, 0.3, 0.4]


# ============================================================================
# MockLLMAdapter Tests
# ============================================================================

class TestMockLLMAdapter:
    """Tests for mock LLM adapter."""

    @pytest.fixture
    def config(self):
        """Create mock config."""
        return LLMConfig(
            provider=LLMProvider.OPENAI,
            model="mock",
        )

    def test_validate_config_always_true(self, config):
        """Test mock adapter always validates."""
        adapter = MockLLMAdapter(config)
        assert adapter.validate_config() is True

    @pytest.mark.asyncio
    async def test_generate_returns_mock(self, config):
        """Test generate returns mock response."""
        adapter = MockLLMAdapter(config)
        result = await adapter.generate("Test prompt")
        
        assert "[Mock LLM Response]" in result
        assert "Test prompt" in result

    @pytest.mark.asyncio
    async def test_embed_returns_deterministic(self, config):
        """Test embed returns deterministic values."""
        adapter = MockLLMAdapter(config)
        
        result1 = await adapter.embed("Test text")
        result2 = await adapter.embed("Test text")
        
        assert result1 == result2  # Deterministic
        assert all(isinstance(v, float) for v in result1)


# ============================================================================
# Factory Function Tests
# ============================================================================

class TestCreateLLMAdapter:
    """Tests for create_llm_adapter factory function."""

    def test_create_openai_adapter(self):
        """Test creating OpenAI adapter returns EsperantoAdapter."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4o",
            api_key="test-key",
        )
        
        adapter = create_llm_adapter(config)
        
        assert isinstance(adapter, EsperantoAdapter)

    def test_create_azure_adapter(self):
        """Test creating Azure OpenAI adapter returns EsperantoAdapter."""
        config = LLMConfig(
            provider=LLMProvider.AZURE_OPENAI,
            model="gpt-4",
            api_key="test-key",
            api_base="https://test.openai.azure.com",
            deployment_name="test-deployment",
        )
        
        adapter = create_llm_adapter(config)
        
        assert isinstance(adapter, EsperantoAdapter)

    def test_create_anthropic_adapter(self):
        """Test creating Anthropic adapter returns EsperantoAdapter."""
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-5-sonnet-20241022",
            api_key="test-key",
        )
        
        adapter = create_llm_adapter(config)
        
        assert isinstance(adapter, EsperantoAdapter)

    def test_create_ollama_adapter(self):
        """Test creating Ollama adapter returns EsperantoAdapter."""
        config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="llama3.1",
            api_base="http://localhost:11434",
        )
        
        adapter = create_llm_adapter(config)
        
        assert isinstance(adapter, EsperantoAdapter)

    def test_create_ollama_adapter_remote(self):
        """Test creating Ollama adapter for remote server."""
        config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="llama3.1",
            api_base="http://windows-pc:11434",
        )
        
        adapter = create_llm_adapter(config)
        
        assert isinstance(adapter, EsperantoAdapter)

    def test_create_from_settings(self):
        """Test creating adapter from settings."""
        mock_settings = MagicMock()
        mock_settings.llm_provider = LLMProvider.OPENAI
        mock_settings.llm_model = "gpt-4o"
        mock_settings.llm_api_key = "test-key"
        mock_settings.llm_api_base = None
        mock_settings.llm_api_version = None
        mock_settings.llm_deployment_name = None
        mock_settings.embedding_model = "text-embedding-3-small"
        mock_settings.ollama_base_url = "http://localhost:11434"
        
        with patch(
            "graphrag_mcp_server.providers.llm.get_settings",
            return_value=mock_settings,
        ):
            adapter = create_llm_adapter()
            assert isinstance(adapter, EsperantoAdapter)

    def test_create_from_settings_ollama(self):
        """Test creating Ollama adapter from settings."""
        mock_settings = MagicMock()
        mock_settings.llm_provider = LLMProvider.OLLAMA
        mock_settings.llm_model = "llama3.1"
        mock_settings.llm_api_key = None
        mock_settings.llm_api_base = None
        mock_settings.llm_api_version = None
        mock_settings.llm_deployment_name = None
        mock_settings.embedding_model = "nomic-embed-text"
        mock_settings.ollama_base_url = "http://windows-pc:11434"
        
        with patch(
            "graphrag_mcp_server.providers.llm.get_settings",
            return_value=mock_settings,
        ):
            adapter = create_llm_adapter()
            assert isinstance(adapter, EsperantoAdapter)
            assert adapter.config.api_base == "http://windows-pc:11434"


class TestGetGraphRAGLLMConfig:
    """Tests for get_graphrag_llm_config function."""

    def test_get_basic_config(self):
        """Test getting basic config."""
        mock_settings = MagicMock()
        mock_settings.llm_provider = LLMProvider.OPENAI
        mock_settings.llm_model = "gpt-4o"
        mock_settings.llm_api_key = "test-key"
        mock_settings.llm_api_base = None
        mock_settings.llm_api_version = None
        mock_settings.llm_deployment_name = None
        
        with patch(
            "graphrag_mcp_server.providers.llm.get_settings",
            return_value=mock_settings,
        ):
            config = get_graphrag_llm_config()
            
            assert config["type"] == "openai"
            assert config["model"] == "gpt-4o"
            assert config["api_key"] == "test-key"

    def test_get_azure_config(self):
        """Test getting Azure OpenAI config."""
        mock_settings = MagicMock()
        mock_settings.llm_provider = LLMProvider.AZURE_OPENAI
        mock_settings.llm_model = "gpt-4"
        mock_settings.llm_api_key = "test-key"
        mock_settings.llm_api_base = "https://test.openai.azure.com"
        mock_settings.llm_api_version = "2024-02-01"
        mock_settings.llm_deployment_name = "test-deployment"
        
        with patch(
            "graphrag_mcp_server.providers.llm.get_settings",
            return_value=mock_settings,
        ):
            config = get_graphrag_llm_config()
            
            assert config["type"] == "azure_openai"
            assert config["api_base"] == "https://test.openai.azure.com"
            assert config["api_version"] == "2024-02-01"
            assert config["deployment_name"] == "test-deployment"
