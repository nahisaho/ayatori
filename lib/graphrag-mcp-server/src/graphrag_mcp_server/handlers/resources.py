"""Resource handlers for GraphRAG MCP Server."""

import logging
from typing import Any

from graphrag_mcp_server.config import get_settings
from graphrag_mcp_server.errors import IndexNotFoundError

logger = logging.getLogger(__name__)


async def get_entities(limit: int = 100) -> dict[str, Any]:
    """Get entities from the knowledge graph.

    Args:
        limit: Maximum number of entities to return

    Returns:
        Dictionary with entities data.
    """
    settings = get_settings()
    index_path = settings.index_path

    if not index_path.exists():
        raise IndexNotFoundError(str(index_path))

    try:
        import pandas as pd

        output_path = index_path / "output"
        entities_files = list(output_path.glob("**/entities.parquet"))

        if not entities_files:
            return {"entities": [], "count": 0, "message": "No entities found"}

        df = pd.read_parquet(entities_files[0])

        # Select relevant columns if they exist
        columns = ["id", "name", "type", "description"]
        available_columns = [c for c in columns if c in df.columns]

        entities = df[available_columns].head(limit).to_dict(orient="records")

        return {
            "entities": entities,
            "count": len(df),
            "returned": len(entities),
        }

    except Exception as e:
        logger.exception("Failed to get entities")
        return {"error": str(e), "entities": []}


async def get_communities(limit: int = 50) -> dict[str, Any]:
    """Get communities from the knowledge graph.

    Args:
        limit: Maximum number of communities to return

    Returns:
        Dictionary with communities data.
    """
    settings = get_settings()
    index_path = settings.index_path

    if not index_path.exists():
        raise IndexNotFoundError(str(index_path))

    try:
        import pandas as pd

        output_path = index_path / "output"
        communities_files = list(output_path.glob("**/communities.parquet"))

        if not communities_files:
            return {"communities": [], "count": 0, "message": "No communities found"}

        df = pd.read_parquet(communities_files[0])

        # Select relevant columns if they exist
        columns = ["id", "title", "level", "size"]
        available_columns = [c for c in columns if c in df.columns]

        communities = df[available_columns].head(limit).to_dict(orient="records")

        return {
            "communities": communities,
            "count": len(df),
            "returned": len(communities),
        }

    except Exception as e:
        logger.exception("Failed to get communities")
        return {"error": str(e), "communities": []}


async def get_relationships(limit: int = 100) -> dict[str, Any]:
    """Get relationships from the knowledge graph.

    Args:
        limit: Maximum number of relationships to return

    Returns:
        Dictionary with relationships data.
    """
    settings = get_settings()
    index_path = settings.index_path

    if not index_path.exists():
        raise IndexNotFoundError(str(index_path))

    try:
        import pandas as pd

        output_path = index_path / "output"
        relationships_files = list(output_path.glob("**/relationships.parquet"))

        if not relationships_files:
            return {"relationships": [], "count": 0, "message": "No relationships found"}

        df = pd.read_parquet(relationships_files[0])

        # Select relevant columns if they exist
        columns = ["id", "source", "target", "description", "weight"]
        available_columns = [c for c in columns if c in df.columns]

        relationships = df[available_columns].head(limit).to_dict(orient="records")

        return {
            "relationships": relationships,
            "count": len(df),
            "returned": len(relationships),
        }

    except Exception as e:
        logger.exception("Failed to get relationships")
        return {"error": str(e), "relationships": []}


async def get_statistics() -> dict[str, Any]:
    """Get index statistics.

    Returns:
        Dictionary with statistics.
    """
    from graphrag_mcp_server.handlers.index import handle_get_statistics

    try:
        stats = await handle_get_statistics()
        return stats.to_dict()
    except IndexNotFoundError as e:
        return {"error": str(e)}
    except Exception as e:
        logger.exception("Failed to get statistics")
        return {"error": str(e)}
