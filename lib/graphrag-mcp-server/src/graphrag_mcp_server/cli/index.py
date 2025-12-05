"""Index command implementation."""

from rich.console import Console

console = Console()


def run_index(
    data_path: str,
    mode: str = "incremental",
    watch: bool = False,
) -> None:
    """Build or update the GraphRAG index.

    Args:
        data_path: Path to data directory
        mode: Index mode (full or incremental)
        watch: Watch for file changes
    """
    console.print(f"[bold green]Building GraphRAG Index[/bold green]")
    console.print(f"  Data path: {data_path}")
    console.print(f"  Mode: {mode}")
    console.print(f"  Watch: {watch}")

    # TODO: Implement index building (Task 4.1)
    console.print("[yellow]Index implementation pending...[/yellow]")
