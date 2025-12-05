"""Settings management for GraphRAG MCP Server."""

from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class VectorStoreType(str, Enum):
    """Supported vector store types."""

    LANCEDB = "lancedb"
    AZURE_SEARCH = "azure_search"


class Settings(BaseSettings):
    """GraphRAG MCP Server settings.

    All settings can be configured via environment variables with the
    GRAPHRAG_ prefix.
    """

    model_config = SettingsConfigDict(
        env_prefix="GRAPHRAG_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Index settings
    index_path: Path = Field(
        default=Path("./graphrag_index"),
        description="Path to GraphRAG index directory",
    )

    # LLM settings
    llm_provider: LLMProvider = Field(
        default=LLMProvider.OPENAI,
        description="LLM provider to use",
    )
    llm_model: str = Field(
        default="gpt-4o",
        description="LLM model name",
    )
    llm_api_key: Optional[str] = Field(
        default=None,
        description="LLM API key (required for OpenAI/Anthropic)",
    )

    # Azure OpenAI specific
    azure_openai_endpoint: Optional[str] = Field(
        default=None,
        description="Azure OpenAI endpoint URL",
    )
    azure_openai_deployment: Optional[str] = Field(
        default=None,
        description="Azure OpenAI deployment name",
    )
    
    # LLM extended settings (for providers module)
    llm_api_base: Optional[str] = Field(
        default=None,
        description="LLM API base URL",
    )
    
    # Ollama specific settings
    ollama_base_url: Optional[str] = Field(
        default="http://localhost:11434",
        description="Ollama server base URL (e.g., http://windows-pc:11434)",
    )
    llm_api_version: Optional[str] = Field(
        default=None,
        description="LLM API version",
    )
    llm_deployment_name: Optional[str] = Field(
        default=None,
        description="LLM deployment name (Azure)",
    )

    # Embedding settings
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Embedding model name",
    )

    # Vector store settings
    vector_store: VectorStoreType = Field(
        default=VectorStoreType.LANCEDB,
        description="Vector store type",
    )
    vector_store_type: VectorStoreType = Field(
        default=VectorStoreType.LANCEDB,
        description="Vector store type (alias)",
    )
    vector_store_connection_string: Optional[str] = Field(
        default=None,
        description="Vector store connection string",
    )
    vector_store_api_key: Optional[str] = Field(
        default=None,
        description="Vector store API key",
    )

    # Azure AI Search specific
    azure_search_endpoint: Optional[str] = Field(
        default=None,
        description="Azure AI Search endpoint URL",
    )
    azure_search_key: Optional[str] = Field(
        default=None,
        description="Azure AI Search API key",
    )

    # Server settings
    server_port: int = Field(
        default=8080,
        description="Server port for SSE transport",
    )
    request_timeout: int = Field(
        default=60,
        description="Request timeout in seconds",
    )

    # Search defaults
    default_community_level: int = Field(
        default=2,
        description="Default community level for global search",
    )
    default_top_k: int = Field(
        default=10,
        description="Default top-k for basic search",
    )

    @field_validator("index_path", mode="before")
    @classmethod
    def validate_index_path(cls, v: str | Path) -> Path:
        """Convert string to Path."""
        return Path(v) if isinstance(v, str) else v

    def validate_llm_config(self) -> None:
        """Validate LLM configuration.

        Raises:
            ValueError: If required configuration is missing.
        """
        if self.llm_provider == LLMProvider.OPENAI:
            if not self.llm_api_key:
                raise ValueError(
                    "GRAPHRAG_LLM_API_KEY is required for OpenAI provider"
                )
        elif self.llm_provider == LLMProvider.AZURE_OPENAI:
            if not self.azure_openai_endpoint:
                raise ValueError(
                    "GRAPHRAG_AZURE_OPENAI_ENDPOINT is required for Azure OpenAI"
                )
        elif self.llm_provider == LLMProvider.ANTHROPIC:
            if not self.llm_api_key:
                raise ValueError(
                    "GRAPHRAG_LLM_API_KEY is required for Anthropic provider"
                )
        elif self.llm_provider == LLMProvider.OLLAMA:
            # Ollama does not require API key, just base URL
            pass  # ollama_base_url has default value

    def validate_vector_store_config(self) -> None:
        """Validate vector store configuration.

        Raises:
            ValueError: If required configuration is missing.
        """
        if self.vector_store == VectorStoreType.AZURE_SEARCH:
            if not self.azure_search_endpoint:
                raise ValueError(
                    "GRAPHRAG_AZURE_SEARCH_ENDPOINT is required for Azure AI Search"
                )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings instance with values from environment.
    """
    return Settings()
