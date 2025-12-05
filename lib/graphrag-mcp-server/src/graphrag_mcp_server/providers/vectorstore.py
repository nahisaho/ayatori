"""Vector Store adapters for GraphRAG MCP Server.

Provides adapters for different vector stores (LanceDB, Azure AI Search, etc.)
that conform to GraphRAG's expected interface.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from graphrag_mcp_server.config import VectorStoreType, get_settings
from graphrag_mcp_server.errors import IndexNotFoundError

logger = logging.getLogger(__name__)


@dataclass
class VectorStoreConfig:
    """Configuration for vector store."""

    store_type: VectorStoreType
    connection_string: str | None = None
    api_key: str | None = None
    index_name: str = "graphrag_index"
    embedding_dimension: int = 1536

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for GraphRAG config."""
        config: dict[str, Any] = {
            "type": self.store_type.value,
            "index_name": self.index_name,
            "embedding_dimension": self.embedding_dimension,
        }
        
        if self.connection_string:
            config["connection_string"] = self.connection_string
        if self.api_key:
            config["api_key"] = self.api_key
            
        return config


@dataclass
class SearchResult:
    """Result from vector store search."""

    id: str
    text: str
    score: float
    metadata: dict[str, Any]


class BaseVectorStoreAdapter(ABC):
    """Base class for vector store adapters."""

    def __init__(self, config: VectorStoreConfig):
        """Initialize adapter with configuration.

        Args:
            config: Vector store configuration.
        """
        self.config = config

    @abstractmethod
    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        **kwargs: Any,
    ) -> list[SearchResult]:
        """Search for similar vectors.

        Args:
            query_embedding: Query embedding vector.
            top_k: Number of results to return.
            **kwargs: Additional search parameters.

        Returns:
            List of search results.
        """
        pass

    @abstractmethod
    async def upsert(
        self,
        id: str,
        embedding: list[float],
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Insert or update a vector.

        Args:
            id: Unique identifier.
            embedding: Vector embedding.
            text: Source text.
            metadata: Optional metadata.
        """
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete a vector by ID.

        Args:
            id: Vector ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the configuration.

        Returns:
            True if configuration is valid.
        """
        pass


class LanceDBAdapter(BaseVectorStoreAdapter):
    """Adapter for LanceDB (local vector store)."""

    def __init__(self, config: VectorStoreConfig, db_path: Path | None = None):
        """Initialize LanceDB adapter.

        Args:
            config: Vector store configuration.
            db_path: Optional path to database directory.
        """
        super().__init__(config)
        self.db_path = db_path or Path("./lancedb")
        self._db = None
        self._table = None

    def validate_config(self) -> bool:
        """LanceDB requires minimal config."""
        return True

    async def _ensure_connection(self) -> None:
        """Ensure database connection is established."""
        if self._db is not None:
            return

        try:
            import lancedb

            self._db = lancedb.connect(str(self.db_path))
            
            # Try to open existing table or create new one
            table_name = self.config.index_name
            try:
                self._table = self._db.open_table(table_name)
            except Exception:
                # Table doesn't exist, will be created on first upsert
                self._table = None
                logger.debug(f"Table {table_name} not found, will create on first upsert")

        except ImportError:
            logger.error("lancedb package not installed")
            raise

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        **kwargs: Any,
    ) -> list[SearchResult]:
        """Search LanceDB for similar vectors."""
        await self._ensure_connection()

        if self._table is None:
            return []

        try:
            results = (
                self._table.search(query_embedding)
                .limit(top_k)
                .to_list()
            )

            return [
                SearchResult(
                    id=str(r.get("id", "")),
                    text=str(r.get("text", "")),
                    score=float(r.get("_distance", 0.0)),
                    metadata=r.get("metadata", {}),
                )
                for r in results
            ]

        except Exception as e:
            logger.error(f"LanceDB search error: {e}")
            return []

    async def upsert(
        self,
        id: str,
        embedding: list[float],
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Insert or update vector in LanceDB."""
        await self._ensure_connection()

        try:
            import lancedb
            import pyarrow as pa

            data = [{
                "id": id,
                "text": text,
                "vector": embedding,
                "metadata": metadata or {},
            }]

            if self._table is None:
                # Create table with first record
                self._table = self._db.create_table(
                    self.config.index_name,
                    data,
                    mode="overwrite",
                )
            else:
                # Add to existing table
                self._table.add(data)

        except Exception as e:
            logger.error(f"LanceDB upsert error: {e}")
            raise

    async def delete(self, id: str) -> bool:
        """Delete vector from LanceDB."""
        await self._ensure_connection()

        if self._table is None:
            return False

        try:
            self._table.delete(f'id = "{id}"')
            return True
        except Exception as e:
            logger.error(f"LanceDB delete error: {e}")
            return False


class AzureAISearchAdapter(BaseVectorStoreAdapter):
    """Adapter for Azure AI Search."""

    def validate_config(self) -> bool:
        """Validate Azure AI Search configuration."""
        return bool(self.config.connection_string and self.config.api_key)

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        **kwargs: Any,
    ) -> list[SearchResult]:
        """Search Azure AI Search."""
        if not self.validate_config():
            raise IndexNotFoundError("Invalid Azure AI Search configuration")

        try:
            from azure.search.documents import SearchClient
            from azure.core.credentials import AzureKeyCredential

            client = SearchClient(
                endpoint=self.config.connection_string,
                index_name=self.config.index_name,
                credential=AzureKeyCredential(self.config.api_key),
            )

            # Use vector search
            results = client.search(
                search_text="*",
                vector_queries=[{
                    "vector": query_embedding,
                    "k_nearest_neighbors": top_k,
                    "fields": "embedding",
                }],
                top=top_k,
            )

            return [
                SearchResult(
                    id=str(r.get("id", "")),
                    text=str(r.get("text", "")),
                    score=float(r.get("@search.score", 0.0)),
                    metadata=r.get("metadata", {}),
                )
                for r in results
            ]

        except ImportError:
            logger.warning("azure-search-documents not available")
            return []
        except Exception as e:
            logger.error(f"Azure AI Search error: {e}")
            return []

    async def upsert(
        self,
        id: str,
        embedding: list[float],
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Insert or update in Azure AI Search."""
        if not self.validate_config():
            raise IndexNotFoundError("Invalid Azure AI Search configuration")

        try:
            from azure.search.documents import SearchClient
            from azure.core.credentials import AzureKeyCredential

            client = SearchClient(
                endpoint=self.config.connection_string,
                index_name=self.config.index_name,
                credential=AzureKeyCredential(self.config.api_key),
            )

            document = {
                "id": id,
                "text": text,
                "embedding": embedding,
                "metadata": metadata or {},
            }

            client.merge_or_upload_documents([document])

        except ImportError:
            logger.warning("azure-search-documents not available")
        except Exception as e:
            logger.error(f"Azure AI Search upsert error: {e}")
            raise

    async def delete(self, id: str) -> bool:
        """Delete from Azure AI Search."""
        if not self.validate_config():
            return False

        try:
            from azure.search.documents import SearchClient
            from azure.core.credentials import AzureKeyCredential

            client = SearchClient(
                endpoint=self.config.connection_string,
                index_name=self.config.index_name,
                credential=AzureKeyCredential(self.config.api_key),
            )

            client.delete_documents([{"id": id}])
            return True

        except Exception as e:
            logger.error(f"Azure AI Search delete error: {e}")
            return False


class MockVectorStoreAdapter(BaseVectorStoreAdapter):
    """Mock adapter for testing."""

    def __init__(self, config: VectorStoreConfig):
        """Initialize mock adapter."""
        super().__init__(config)
        self._store: dict[str, dict[str, Any]] = {}

    def validate_config(self) -> bool:
        """Always valid for mock."""
        return True

    async def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        **kwargs: Any,
    ) -> list[SearchResult]:
        """Return mock results."""
        results = list(self._store.values())[:top_k]
        return [
            SearchResult(
                id=r["id"],
                text=r["text"],
                score=0.9,
                metadata=r.get("metadata", {}),
            )
            for r in results
        ]

    async def upsert(
        self,
        id: str,
        embedding: list[float],
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Store in memory."""
        self._store[id] = {
            "id": id,
            "embedding": embedding,
            "text": text,
            "metadata": metadata or {},
        }

    async def delete(self, id: str) -> bool:
        """Delete from memory."""
        if id in self._store:
            del self._store[id]
            return True
        return False


def create_vector_store_adapter(
    config: VectorStoreConfig | None = None,
) -> BaseVectorStoreAdapter:
    """Create a vector store adapter based on configuration.

    Args:
        config: Optional vector store configuration.

    Returns:
        Configured vector store adapter instance.
    """
    if config is None:
        settings = get_settings()
        config = VectorStoreConfig(
            store_type=settings.vector_store_type,
            connection_string=settings.vector_store_connection_string,
            api_key=settings.vector_store_api_key,
        )

    adapters = {
        VectorStoreType.LANCEDB: LanceDBAdapter,
        VectorStoreType.AZURE_SEARCH: AzureAISearchAdapter,
    }

    adapter_class = adapters.get(config.store_type)
    if adapter_class is None:
        logger.warning(f"Unknown store type {config.store_type}, using mock")
        return MockVectorStoreAdapter(config)

    return adapter_class(config)


def get_graphrag_vector_store_config() -> dict[str, Any]:
    """Get vector store configuration formatted for GraphRAG.

    Returns:
        Dictionary compatible with GraphRAG configuration.
    """
    settings = get_settings()
    
    config = {
        "type": settings.vector_store_type.value,
    }

    if settings.vector_store_connection_string:
        config["connection_string"] = settings.vector_store_connection_string
    if settings.vector_store_api_key:
        config["api_key"] = settings.vector_store_api_key

    return config
