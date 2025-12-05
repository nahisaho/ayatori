"""LLM Provider adapters for GraphRAG MCP Server.

Provides adapters using esperanto library for unified LLM access.
Supports Azure OpenAI, OpenAI, Anthropic, and other providers.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from graphrag_mcp_server.config import LLMProvider, get_settings
from graphrag_mcp_server.errors import LLMProviderError

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM provider."""

    provider: LLMProvider
    model: str
    api_key: str | None = None
    api_base: str | None = None
    api_version: str | None = None
    deployment_name: str | None = None
    max_tokens: int = 4096
    temperature: float = 0.0
    embedding_model: str = "text-embedding-3-small"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for GraphRAG config."""
        config: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        
        if self.api_key:
            config["api_key"] = self.api_key
        if self.api_base:
            config["api_base"] = self.api_base
        if self.api_version:
            config["api_version"] = self.api_version
        if self.deployment_name:
            config["deployment_name"] = self.deployment_name
            
        return config


class BaseLLMAdapter(ABC):
    """Base class for LLM adapters."""

    def __init__(self, config: LLMConfig):
        """Initialize adapter with configuration.

        Args:
            config: LLM configuration.
        """
        self.config = config

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: The prompt to send to the LLM.
            **kwargs: Additional parameters.

        Returns:
            Generated text response.
        """
        pass

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Generate embeddings for text.

        Args:
            text: Text to embed.

        Returns:
            List of float values representing the embedding.
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the configuration.

        Returns:
            True if configuration is valid.
        """
        pass


class EsperantoAdapter(BaseLLMAdapter):
    """Unified adapter using esperanto library.
    
    Supports multiple providers through esperanto's AIFactory:
    - OpenAI
    - Azure OpenAI
    - Anthropic
    - Google Vertex AI
    - Ollama
    - Groq
    - Mistral
    - OpenRouter
    - OpenAI-compatible endpoints
    """

    def __init__(self, config: LLMConfig):
        """Initialize esperanto adapter.

        Args:
            config: LLM configuration.
        """
        super().__init__(config)
        self._llm = None
        self._embedder = None

    def _get_provider_name(self) -> str:
        """Map LLMProvider enum to esperanto provider name."""
        provider_map = {
            LLMProvider.OPENAI: "openai",
            LLMProvider.AZURE_OPENAI: "azure",
            LLMProvider.ANTHROPIC: "anthropic",
            LLMProvider.OLLAMA: "ollama",
        }
        return provider_map.get(self.config.provider, "openai")

    def _get_llm_config(self) -> dict[str, Any]:
        """Build esperanto config for LLM."""
        config: dict[str, Any] = {
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        
        if self.config.api_key:
            config["api_key"] = self.config.api_key
            
        # Azure-specific config
        if self.config.provider == LLMProvider.AZURE_OPENAI:
            if self.config.api_base:
                config["azure_endpoint"] = self.config.api_base
            if self.config.api_version:
                config["api_version"] = self.config.api_version
                
        # Ollama-specific config
        elif self.config.provider == LLMProvider.OLLAMA:
            if self.config.api_base:
                config["base_url"] = self.config.api_base
                
        return config

    def _get_embedding_config(self) -> dict[str, Any]:
        """Build esperanto config for embeddings."""
        config: dict[str, Any] = {}
        
        if self.config.api_key:
            config["api_key"] = self.config.api_key
            
        # Azure-specific config
        if self.config.provider == LLMProvider.AZURE_OPENAI:
            if self.config.api_base:
                config["azure_endpoint"] = self.config.api_base
            if self.config.api_version:
                config["api_version"] = self.config.api_version
                
        # Ollama-specific config
        elif self.config.provider == LLMProvider.OLLAMA:
            if self.config.api_base:
                config["base_url"] = self.config.api_base
                
        return config

    def _ensure_llm(self) -> Any:
        """Ensure LLM model is initialized."""
        if self._llm is None:
            try:
                from esperanto.factory import AIFactory
                
                provider = self._get_provider_name()
                model_name = self.config.deployment_name or self.config.model
                
                self._llm = AIFactory.create_language(
                    provider,
                    model_name,
                    config=self._get_llm_config(),
                )
            except ImportError:
                logger.warning("esperanto package not available")
                raise LLMProviderError(
                    self.config.provider.value,
                    "esperanto package not installed. Run: pip install esperanto"
                )
        return self._llm

    def _ensure_embedder(self) -> Any:
        """Ensure embedding model is initialized."""
        if self._embedder is None:
            try:
                from esperanto.factory import AIFactory
                
                provider = self._get_provider_name()
                
                self._embedder = AIFactory.create_embedding(
                    provider,
                    self.config.embedding_model,
                    config=self._get_embedding_config(),
                )
            except ImportError:
                logger.warning("esperanto package not available")
                raise LLMProviderError(
                    self.config.provider.value,
                    "esperanto package not installed. Run: pip install esperanto"
                )
        return self._embedder

    def validate_config(self) -> bool:
        """Validate configuration based on provider."""
        if self.config.provider == LLMProvider.AZURE_OPENAI:
            return bool(
                self.config.api_key and
                self.config.api_base and
                self.config.deployment_name
            )
        elif self.config.provider == LLMProvider.OPENAI:
            return bool(self.config.api_key)
        elif self.config.provider == LLMProvider.ANTHROPIC:
            return bool(self.config.api_key)
        elif self.config.provider == LLMProvider.OLLAMA:
            # Ollama doesn't require API key, just needs a valid base URL
            return True
        return False

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate response using esperanto.

        Args:
            prompt: The prompt to send to the LLM.
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Generated text response.
        """
        if not self.validate_config():
            raise LLMProviderError(
                self.config.provider.value,
                f"Invalid {self.config.provider.value} configuration"
            )

        try:
            llm = self._ensure_llm()
            messages = [{"role": "user", "content": prompt}]
            
            # Use async completion
            response = await llm.achat_complete(messages)
            
            # esperanto returns standardized response
            return response.choices[0].message.content or ""
            
        except ImportError:
            logger.warning("esperanto package not available, returning mock")
            return f"[Mock {self.config.provider.value} Response]\nPrompt: {prompt[:100]}..."
        except Exception as e:
            raise LLMProviderError(self.config.provider.value, str(e)) from e

    async def embed(self, text: str) -> list[float]:
        """Generate embeddings using esperanto.

        Args:
            text: Text to embed.

        Returns:
            List of float values representing the embedding.
        """
        if not self.validate_config():
            raise LLMProviderError(
                self.config.provider.value,
                f"Invalid {self.config.provider.value} configuration"
            )

        try:
            embedder = self._ensure_embedder()
            
            # Use async embedding
            response = await embedder.aembed([text])
            
            # esperanto returns standardized response
            return response.data[0].embedding
            
        except ImportError:
            logger.warning("esperanto package not available, returning mock")
            return [0.0] * 1536
        except Exception as e:
            raise LLMProviderError(self.config.provider.value, str(e)) from e


# Backward compatibility aliases
class AzureOpenAIAdapter(EsperantoAdapter):
    """Azure OpenAI adapter using esperanto."""
    
    def __init__(self, config: LLMConfig):
        # Ensure provider is set correctly
        if config.provider != LLMProvider.AZURE_OPENAI:
            config = LLMConfig(
                provider=LLMProvider.AZURE_OPENAI,
                model=config.model,
                api_key=config.api_key,
                api_base=config.api_base,
                api_version=config.api_version,
                deployment_name=config.deployment_name,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                embedding_model=config.embedding_model,
            )
        super().__init__(config)


class OpenAIAdapter(EsperantoAdapter):
    """OpenAI adapter using esperanto."""
    
    def __init__(self, config: LLMConfig):
        # Ensure provider is set correctly
        if config.provider != LLMProvider.OPENAI:
            config = LLMConfig(
                provider=LLMProvider.OPENAI,
                model=config.model,
                api_key=config.api_key,
                api_base=config.api_base,
                api_version=config.api_version,
                deployment_name=config.deployment_name,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                embedding_model=config.embedding_model,
            )
        super().__init__(config)


class OllamaAdapter(EsperantoAdapter):
    """Ollama adapter using esperanto.
    
    Connects to Ollama server (local or remote, e.g., Windows).
    No API key required.
    """
    
    def __init__(self, config: LLMConfig):
        # Always create a proper Ollama config with defaults
        config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model=config.model,
            api_key=None,  # Ollama doesn't need API key
            api_base=config.api_base or "http://localhost:11434",
            api_version=None,
            deployment_name=None,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            embedding_model=config.embedding_model if config.embedding_model != "text-embedding-3-small" else "nomic-embed-text",
        )
        super().__init__(config)


class MockLLMAdapter(BaseLLMAdapter):
    """Mock adapter for testing and development."""

    def validate_config(self) -> bool:
        """Always valid for mock."""
        return True

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Return mock response."""
        return f"[Mock LLM Response]\nPrompt received: {prompt[:200]}..."

    async def embed(self, text: str) -> list[float]:
        """Return mock embedding."""
        import hashlib
        # Generate deterministic mock embedding based on text hash
        hash_bytes = hashlib.sha256(text.encode()).digest()
        return [float(b) / 255.0 for b in hash_bytes[:1536 % 32] * 48]


def create_llm_adapter(config: LLMConfig | None = None) -> BaseLLMAdapter:
    """Create an LLM adapter based on configuration.

    Uses esperanto library for unified provider access.

    Args:
        config: Optional LLM configuration. If not provided,
                uses settings from environment.

    Returns:
        Configured LLM adapter instance.
    """
    if config is None:
        settings = get_settings()
        
        # Determine api_base based on provider
        api_base = settings.llm_api_base
        if settings.llm_provider == LLMProvider.OLLAMA and not api_base:
            api_base = settings.ollama_base_url
        
        config = LLMConfig(
            provider=settings.llm_provider,
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            api_base=api_base,
            api_version=settings.llm_api_version,
            deployment_name=settings.llm_deployment_name,
            embedding_model=settings.embedding_model,
        )

    # All providers use EsperantoAdapter
    supported_providers = {
        LLMProvider.AZURE_OPENAI,
        LLMProvider.OPENAI,
        LLMProvider.ANTHROPIC,
        LLMProvider.OLLAMA,
    }

    if config.provider in supported_providers:
        return EsperantoAdapter(config)
    else:
        logger.warning(f"Unknown provider {config.provider}, using mock")
        return MockLLMAdapter(config)


def get_graphrag_llm_config() -> dict[str, Any]:
    """Get LLM configuration formatted for GraphRAG.

    Returns:
        Dictionary compatible with GraphRAG configuration.
    """
    settings = get_settings()
    
    config = {
        "type": settings.llm_provider.value,
        "model": settings.llm_model,
    }

    if settings.llm_api_key:
        config["api_key"] = settings.llm_api_key
    if settings.llm_api_base:
        config["api_base"] = settings.llm_api_base
    if settings.llm_api_version:
        config["api_version"] = settings.llm_api_version
    if settings.llm_deployment_name:
        config["deployment_name"] = settings.llm_deployment_name

    return config
