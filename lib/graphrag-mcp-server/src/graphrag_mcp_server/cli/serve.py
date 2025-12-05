"""Serve command implementation."""

import asyncio
import logging
import os
from typing import Optional

from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)


def run_serve(
    transport: str = "stdio",
    port: int = 8080,
    index_path: Optional[str] = None,
) -> None:
    """Start the MCP server.

    Args:
        transport: Transport mode (stdio or sse)
        port: Port for SSE transport
        index_path: Path to GraphRAG index
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Set index path environment variable if provided
    if index_path:
        os.environ["GRAPHRAG_INDEX_PATH"] = index_path

    console.print(f"[bold green]Starting GraphRAG MCP Server[/bold green]")
    console.print(f"  Transport: {transport}")
    if transport == "sse":
        console.print(f"  Port: {port}")
    if index_path:
        console.print(f"  Index path: {index_path}")

    if transport == "stdio":
        _run_stdio_server()
    elif transport == "sse":
        _run_sse_server(port)
    else:
        console.print(f"[red]Unknown transport: {transport}[/red]")
        raise SystemExit(1)


def _run_stdio_server() -> None:
    """Run the MCP server with stdio transport."""
    from graphrag_mcp_server.server.app import run_stdio_server

    console.print("[dim]Running with stdio transport...[/dim]")
    asyncio.run(run_stdio_server())


def _run_sse_server(port: int) -> None:
    """Run the MCP server with SSE transport.

    Args:
        port: Port to listen on.
    """
    import uvicorn
    from starlette.applications import Starlette
    from starlette.responses import Response
    from starlette.routing import Mount, Route

    from mcp.server.sse import SseServerTransport

    from graphrag_mcp_server.server.app import server

    # Create SSE transport
    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        """Handle SSE connection."""
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await server.run(
                streams[0], streams[1], server.create_initialization_options()
            )
        return Response()

    # Create Starlette application with routes
    routes = [
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Mount("/messages/", app=sse.handle_post_message),
    ]

    starlette_app = Starlette(routes=routes)

    console.print(f"[dim]Running with SSE transport on http://127.0.0.1:{port}[/dim]")
    console.print(f"[dim]SSE endpoint: http://127.0.0.1:{port}/sse[/dim]")
    
    uvicorn.run(starlette_app, host="127.0.0.1", port=port, log_level="info")
