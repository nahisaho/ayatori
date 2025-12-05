"""Stats command implementation."""

from typing import Optional

from rich.console import Console

console = Console()


def run_stats(
    index_path: Optional[str] = None,
    format: str = "text",
) -> None:
    """Show index statistics.

    Args:
        index_path: Path to GraphRAG index
        format: Output format (text or json)
    """
    console.print(f"[bold green]Index Statistics[/bold green]")
    if index_path:
        console.print(f"  Index path: {index_path}")
    console.print(f"  Format: {format}")

    # TODO: Implement statistics retrieval (Task 4.2)
    console.print("[yellow]Statistics implementation pending...[/yellow]")
