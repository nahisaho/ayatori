"""Main CLI application for GraphRAG MCP Server."""

from typing import Optional

import typer
from rich.console import Console

from graphrag_mcp_server import __version__

app = typer.Typer(
    name="graphrag-mcp",
    help="MCP Server for Microsoft GraphRAG - Query knowledge graphs from AI assistants",
    no_args_is_help=True,
)

console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"graphrag-mcp-server version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """GraphRAG MCP Server - MCP Server for Microsoft GraphRAG."""
    pass


@app.command()
def serve(
    transport: str = typer.Option(
        "stdio",
        "--transport",
        "-t",
        help="Transport mode: stdio or sse",
    ),
    port: int = typer.Option(
        8080,
        "--port",
        "-p",
        help="Port for SSE transport (only used with --transport sse)",
    ),
    index_path: Optional[str] = typer.Option(
        None,
        "--index-path",
        "-i",
        help="Path to GraphRAG index (overrides GRAPHRAG_INDEX_PATH env var)",
    ),
) -> None:
    """Start the MCP server."""
    from graphrag_mcp_server.cli.serve import run_serve

    run_serve(transport=transport, port=port, index_path=index_path)


@app.command()
def index(
    data_path: str = typer.Argument(..., help="Path to data directory"),
    mode: str = typer.Option(
        "incremental",
        "--mode",
        "-m",
        help="Index mode: full or incremental",
    ),
    watch: bool = typer.Option(
        False,
        "--watch",
        "-w",
        help="Watch for file changes and update index automatically",
    ),
) -> None:
    """Build or update the GraphRAG index."""
    from graphrag_mcp_server.cli.index import run_index

    run_index(data_path=data_path, mode=mode, watch=watch)


@app.command()
def query(
    query_text: str = typer.Argument(..., help="Query text"),
    query_type: str = typer.Option(
        "global",
        "--type",
        "-t",
        help="Query type: global, local, drift, or basic",
    ),
    community_level: int = typer.Option(
        2,
        "--community-level",
        "-c",
        help="Community hierarchy level (for global search)",
    ),
    top_k: int = typer.Option(
        10,
        "--top-k",
        "-k",
        help="Number of results (for basic search)",
    ),
) -> None:
    """Execute a query (for debugging)."""
    from graphrag_mcp_server.cli.query import run_query

    run_query(
        query_text=query_text,
        query_type=query_type,
        community_level=community_level,
        top_k=top_k,
    )


@app.command()
def stats(
    index_path: Optional[str] = typer.Option(
        None,
        "--index-path",
        "-i",
        help="Path to GraphRAG index",
    ),
    format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Output format: text or json",
    ),
) -> None:
    """Show index statistics."""
    from graphrag_mcp_server.cli.stats import run_stats

    run_stats(index_path=index_path, format=format)


if __name__ == "__main__":
    app()
