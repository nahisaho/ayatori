"""MCP Prompts definitions for GraphRAG MCP Server.

This module defines all MCP prompts exposed by the server.
Prompts provide reusable templates for common query patterns.
"""

from typing import Any

# MCP Prompt definitions
# These follow the MCP 1.0 specification

ANALYZE_ENTITY_PROMPT = {
    "name": "analyze_entity",
    "description": """Analyze a specific entity in the knowledge graph.

This prompt helps explore an entity's characteristics, relationships,
and role in the corpus. Returns information about:
- Entity attributes and description
- Key relationships with other entities
- Community membership and context
- Relevant text excerpts
""",
    "arguments": [
        {
            "name": "entity_name",
            "description": "Name of the entity to analyze",
            "required": True
        },
        {
            "name": "depth",
            "description": "Analysis depth (shallow, medium, deep)",
            "required": False
        }
    ]
}

EXPLORE_TOPIC_PROMPT = {
    "name": "explore_topic",
    "description": """Explore a topic or theme in the knowledge graph.

This prompt helps discover entities and relationships related to
a given topic. Useful for:
- Understanding topic coverage in the corpus
- Finding related concepts and entities
- Discovering hidden connections
""",
    "arguments": [
        {
            "name": "topic",
            "description": "Topic or theme to explore",
            "required": True
        },
        {
            "name": "scope",
            "description": "Exploration scope (narrow, broad)",
            "required": False
        }
    ]
}

COMPARE_ENTITIES_PROMPT = {
    "name": "compare_entities",
    "description": """Compare two or more entities in the knowledge graph.

This prompt generates a comparative analysis between entities:
- Similarities and differences
- Shared relationships
- Common community membership
- Contrasting attributes
""",
    "arguments": [
        {
            "name": "entity_names",
            "description": "Comma-separated list of entity names to compare",
            "required": True
        },
        {
            "name": "aspects",
            "description": "Aspects to compare (relationships, communities, attributes)",
            "required": False
        }
    ]
}

SUMMARIZE_COMMUNITY_PROMPT = {
    "name": "summarize_community",
    "description": """Summarize a community in the knowledge graph.

This prompt provides an overview of a community's:
- Key themes and topics
- Central entities
- Internal structure and relationships
- Connection to other communities
""",
    "arguments": [
        {
            "name": "community_id",
            "description": "ID of the community to summarize",
            "required": True
        },
        {
            "name": "detail_level",
            "description": "Detail level (brief, standard, comprehensive)",
            "required": False
        }
    ]
}

TRACE_RELATIONSHIP_PROMPT = {
    "name": "trace_relationship",
    "description": """Trace relationship paths between entities.

This prompt finds and explains connection paths:
- Direct relationships
- Indirect paths through other entities
- Path significance and strength
""",
    "arguments": [
        {
            "name": "source_entity",
            "description": "Starting entity name",
            "required": True
        },
        {
            "name": "target_entity",
            "description": "Ending entity name",
            "required": True
        },
        {
            "name": "max_hops",
            "description": "Maximum path length (default: 3)",
            "required": False
        }
    ]
}

GENERATE_QUESTIONS_PROMPT = {
    "name": "generate_questions",
    "description": """Generate relevant questions about the knowledge graph.

This prompt suggests questions that can be answered using the corpus:
- Entity-focused questions
- Relationship exploration questions
- Thematic questions
- Comparative questions
""",
    "arguments": [
        {
            "name": "focus_area",
            "description": "Optional focus area or topic",
            "required": False
        },
        {
            "name": "question_count",
            "description": "Number of questions to generate (default: 5)",
            "required": False
        }
    ]
}

CORPUS_OVERVIEW_PROMPT = {
    "name": "corpus_overview",
    "description": """Get a high-level overview of the indexed corpus.

This prompt provides a comprehensive summary:
- Main themes and topics
- Key entities by importance
- Community structure overview
- Corpus coverage and gaps
""",
    "arguments": [
        {
            "name": "focus",
            "description": "Optional focus area (entities, themes, structure)",
            "required": False
        }
    ]
}

FIND_SIMILAR_PROMPT = {
    "name": "find_similar",
    "description": """Find entities similar to a given entity.

This prompt identifies entities that are:
- Similar in type and attributes
- Related through shared relationships
- Part of the same communities
- Semantically similar based on descriptions
""",
    "arguments": [
        {
            "name": "entity_name",
            "description": "Name of the reference entity",
            "required": True
        },
        {
            "name": "similarity_type",
            "description": "Type of similarity (structural, semantic, relational)",
            "required": False
        },
        {
            "name": "limit",
            "description": "Maximum number of similar entities (default: 10)",
            "required": False
        }
    ]
}


# All available prompts
ALL_PROMPTS = [
    ANALYZE_ENTITY_PROMPT,
    EXPLORE_TOPIC_PROMPT,
    COMPARE_ENTITIES_PROMPT,
    SUMMARIZE_COMMUNITY_PROMPT,
    TRACE_RELATIONSHIP_PROMPT,
    GENERATE_QUESTIONS_PROMPT,
    CORPUS_OVERVIEW_PROMPT,
    FIND_SIMILAR_PROMPT,
]


def get_prompt_by_name(name: str) -> dict[str, Any] | None:
    """Get a prompt definition by name.
    
    Args:
        name: The prompt name to look up
        
    Returns:
        Prompt definition dictionary or None if not found
    """
    for prompt in ALL_PROMPTS:
        if prompt["name"] == name:
            return prompt
    return None


def list_prompt_names() -> list[str]:
    """Get list of all available prompt names.
    
    Returns:
        List of prompt name strings
    """
    return [prompt["name"] for prompt in ALL_PROMPTS]


def get_prompt_template(name: str, arguments: dict[str, str]) -> str | None:
    """Generate a prompt template with filled arguments.
    
    Args:
        name: The prompt name
        arguments: Dictionary of argument values
        
    Returns:
        Rendered prompt template or None if prompt not found
    """
    prompt = get_prompt_by_name(name)
    if prompt is None:
        return None
    
    # Build the rendered prompt based on the template
    templates = {
        "analyze_entity": _render_analyze_entity,
        "explore_topic": _render_explore_topic,
        "compare_entities": _render_compare_entities,
        "summarize_community": _render_summarize_community,
        "trace_relationship": _render_trace_relationship,
        "generate_questions": _render_generate_questions,
        "corpus_overview": _render_corpus_overview,
        "find_similar": _render_find_similar,
    }
    
    renderer = templates.get(name)
    if renderer:
        return renderer(arguments)
    return None


def _render_analyze_entity(args: dict[str, str]) -> str:
    """Render analyze_entity prompt."""
    entity = args.get("entity_name", "")
    depth = args.get("depth", "medium")
    
    return f"""Analyze the entity "{entity}" in the knowledge graph.

Please provide a {depth} analysis including:
1. Entity description and key attributes
2. Important relationships with other entities
3. Community membership and role
4. Relevant context from source documents

Focus on factual information from the indexed corpus."""


def _render_explore_topic(args: dict[str, str]) -> str:
    """Render explore_topic prompt."""
    topic = args.get("topic", "")
    scope = args.get("scope", "broad")
    
    return f"""Explore the topic "{topic}" in the knowledge graph.

Scope: {scope}

Please discover and report:
1. Key entities related to this topic
2. Themes and patterns
3. Important relationships
4. Coverage in the corpus

Use both local and global search to gather comprehensive information."""


def _render_compare_entities(args: dict[str, str]) -> str:
    """Render compare_entities prompt."""
    entities = args.get("entity_names", "")
    aspects = args.get("aspects", "all")
    
    return f"""Compare the following entities: {entities}

Comparison aspects: {aspects}

Please provide a structured comparison including:
1. Key similarities
2. Notable differences
3. Shared relationships or connections
4. Common community membership
5. Distinct characteristics

Base the comparison on indexed knowledge graph data."""


def _render_summarize_community(args: dict[str, str]) -> str:
    """Render summarize_community prompt."""
    community_id = args.get("community_id", "")
    detail = args.get("detail_level", "standard")
    
    return f"""Summarize community {community_id}.

Detail level: {detail}

Please include:
1. Community theme and focus
2. Key member entities
3. Internal relationship patterns
4. Connections to other communities
5. Representative content from the community"""


def _render_trace_relationship(args: dict[str, str]) -> str:
    """Render trace_relationship prompt."""
    source = args.get("source_entity", "")
    target = args.get("target_entity", "")
    max_hops = args.get("max_hops", "3")
    
    return f"""Trace relationship paths between "{source}" and "{target}".

Maximum path length: {max_hops} hops

Please identify:
1. Direct relationships (if any)
2. Shortest path through intermediary entities
3. Alternative connection paths
4. Strength and significance of connections

Explain the nature of each relationship in the path."""


def _render_generate_questions(args: dict[str, str]) -> str:
    """Render generate_questions prompt."""
    focus = args.get("focus_area", "general")
    count = args.get("question_count", "5")
    
    return f"""Generate {count} relevant questions about the knowledge graph.

Focus area: {focus}

Generate diverse questions that:
1. Can be answered from the indexed corpus
2. Span different entity types and relationships
3. Range from factual to analytical
4. Highlight interesting aspects of the data

Format as a numbered list with brief explanations of why each question is relevant."""


def _render_corpus_overview(args: dict[str, str]) -> str:
    """Render corpus_overview prompt."""
    focus = args.get("focus", "all")
    
    return f"""Provide a high-level overview of the indexed corpus.

Focus: {focus}

Include:
1. Main themes and topics covered
2. Most important entities (by centrality and mentions)
3. Community structure and hierarchy
4. Content coverage and notable gaps
5. Key insights from the knowledge graph

Use global search to gather corpus-wide perspective."""


def _render_find_similar(args: dict[str, str]) -> str:
    """Render find_similar prompt."""
    entity = args.get("entity_name", "")
    sim_type = args.get("similarity_type", "all")
    limit = args.get("limit", "10")
    
    return f"""Find entities similar to "{entity}".

Similarity type: {sim_type}
Maximum results: {limit}

Identify similar entities based on:
1. Entity type and attributes
2. Relationship patterns
3. Community co-membership
4. Semantic similarity in descriptions

Rank by relevance and explain the basis for similarity."""
