"""MCP Resources definitions for GraphRAG MCP Server.

This module defines all MCP resources exposed by the server.
Resources provide read access to the knowledge graph data.
"""

from typing import Any

# MCP Resource template definitions
# These follow the MCP 1.0 specification

ENTITIES_RESOURCE = {
    "uri": "graphrag://entities",
    "name": "Entities",
    "description": """Knowledge graph entities extracted from the corpus.

Entities represent the key concepts, people, places, organizations,
and other named items identified in the documents.

Each entity includes:
- name: The entity name
- type: Entity type (PERSON, ORGANIZATION, LOCATION, etc.)
- description: Summary description
- rank: Importance rank based on graph centrality
""",
    "mimeType": "application/json"
}

ENTITIES_BY_TYPE_RESOURCE = {
    "uriTemplate": "graphrag://entities/{entity_type}",
    "name": "Entities by Type",
    "description": """Filter entities by type.

Available types depend on the indexed corpus but typically include:
- PERSON: People mentioned in documents
- ORGANIZATION: Companies, agencies, groups
- LOCATION: Places, addresses, regions
- EVENT: Named events
- CONCEPT: Abstract concepts and ideas
""",
    "mimeType": "application/json"
}

ENTITY_DETAIL_RESOURCE = {
    "uriTemplate": "graphrag://entities/{entity_id}",
    "name": "Entity Details",
    "description": """Get detailed information about a specific entity.

Returns:
- Entity attributes
- Related entities and relationships
- Source text units
- Community membership
""",
    "mimeType": "application/json"
}

RELATIONSHIPS_RESOURCE = {
    "uri": "graphrag://relationships",
    "name": "Relationships",
    "description": """Knowledge graph relationships between entities.

Relationships capture how entities are connected, including:
- source: Source entity
- target: Target entity
- description: Relationship description
- weight: Relationship strength
- rank: Importance rank
""",
    "mimeType": "application/json"
}

COMMUNITIES_RESOURCE = {
    "uri": "graphrag://communities",
    "name": "Communities",
    "description": """Community hierarchy in the knowledge graph.

Communities are clusters of related entities detected using
the Leiden algorithm. They form a hierarchy where:
- Level 0: Highest-level communities (most abstract)
- Higher levels: More granular communities

Each community includes:
- id: Community identifier
- level: Hierarchy level
- title: Generated title
- summary: Generated summary
- entities: Member entities
""",
    "mimeType": "application/json"
}

COMMUNITIES_BY_LEVEL_RESOURCE = {
    "uriTemplate": "graphrag://communities/level/{level}",
    "name": "Communities by Level",
    "description": """Get communities at a specific hierarchy level.

Level 0 contains the highest-level, most abstract communities.
Higher levels contain more granular, specific communities.
""",
    "mimeType": "application/json"
}

COMMUNITY_DETAIL_RESOURCE = {
    "uriTemplate": "graphrag://communities/{community_id}",
    "name": "Community Details",
    "description": """Get detailed information about a specific community.

Returns:
- Community summary and report
- Member entities
- Sub-communities (for non-leaf communities)
- Parent community (for non-root communities)
""",
    "mimeType": "application/json"
}

TEXT_UNITS_RESOURCE = {
    "uri": "graphrag://text_units",
    "name": "Text Units",
    "description": """Source text chunks used for indexing.

Text units are the chunked segments of source documents.
Each includes:
- id: Text unit identifier
- text: The text content
- document_id: Source document reference
- entities: Entities mentioned in this unit
""",
    "mimeType": "application/json"
}

STATISTICS_RESOURCE = {
    "uri": "graphrag://statistics",
    "name": "Index Statistics",
    "description": """Current index statistics and metadata.

Returns:
- Total entity count
- Total relationship count
- Community counts per level
- Text unit count
- Index creation timestamp
- Last update timestamp
""",
    "mimeType": "application/json"
}

DOCUMENTS_RESOURCE = {
    "uri": "graphrag://documents",
    "name": "Source Documents",
    "description": """List of source documents in the index.

Each document includes:
- id: Document identifier
- title: Document title
- path: Source file path
- text_unit_count: Number of text units from this document
""",
    "mimeType": "application/json"
}

COVARIATES_RESOURCE = {
    "uri": "graphrag://covariates",
    "name": "Covariates",
    "description": """Covariates (claims/assertions) extracted from documents.

Covariates are factual claims or assertions extracted from the text,
typically associated with specific entities.
""",
    "mimeType": "application/json"
}


# Static resources (fixed URIs)
STATIC_RESOURCES = [
    ENTITIES_RESOURCE,
    RELATIONSHIPS_RESOURCE,
    COMMUNITIES_RESOURCE,
    TEXT_UNITS_RESOURCE,
    STATISTICS_RESOURCE,
    DOCUMENTS_RESOURCE,
    COVARIATES_RESOURCE,
]

# Resource templates (parameterized URIs)
RESOURCE_TEMPLATES = [
    ENTITIES_BY_TYPE_RESOURCE,
    ENTITY_DETAIL_RESOURCE,
    COMMUNITIES_BY_LEVEL_RESOURCE,
    COMMUNITY_DETAIL_RESOURCE,
]


def get_resource_by_uri(uri: str) -> dict[str, Any] | None:
    """Get a static resource definition by URI.
    
    Args:
        uri: The resource URI to look up
        
    Returns:
        Resource definition dictionary or None if not found
    """
    for resource in STATIC_RESOURCES:
        if resource["uri"] == uri:
            return resource
    return None


def list_resource_uris() -> list[str]:
    """Get list of all static resource URIs.
    
    Returns:
        List of resource URI strings
    """
    return [resource["uri"] for resource in STATIC_RESOURCES]


def list_resource_templates() -> list[dict[str, Any]]:
    """Get list of all resource templates.
    
    Returns:
        List of resource template definitions
    """
    return RESOURCE_TEMPLATES.copy()
