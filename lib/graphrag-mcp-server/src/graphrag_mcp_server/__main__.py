"""CLI entry point for graphrag-mcp-server."""

import sys

from graphrag_mcp_server.cli.main import app

if __name__ == "__main__":
    sys.exit(app())
