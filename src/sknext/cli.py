"""Command-line interface using typer."""

from pathlib import Path

import typer
from rich.console import Console

from sknext.constants import DEFAULT_TASK_COUNT
from sknext.discovery import discover_latest_tasks_file
from sknext.formatter import (
    format_combined_view,
    format_default_view,
    format_phases_only,
    format_structure_view,
    format_tasks_only,
)
from sknext.parser import parse_tasks_file

app = typer.Typer(
    name="sknext",
    help="Task status viewer for speckit projects",
    add_completion=False,
)


@app.command()
def main(
    file_path: Path | None = typer.Argument(  # noqa: B008
        None,
        help="Path to tasks.md file (auto-discovers if not provided)",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    count: int = typer.Option(  # noqa: B008
        DEFAULT_TASK_COUNT,
        "-n",
        "--count",
        help="Number of tasks to display",
        min=0,
    ),
    phases_only: bool = typer.Option(  # noqa: B008
        False,
        "--phases-only",
        help="Show only phases with uncompleted work (no sections or tasks)",
    ),
    structure: bool = typer.Option(  # noqa: B008
        False,
        "--structure",
        help="Show phases and sections with uncompleted work (no tasks)",
    ),
    all_phases: bool = typer.Option(  # noqa: B008
        False,
        "--all-phases",
        help="Show all incomplete phases followed by next N tasks",
    ),
    tasks_only: bool = typer.Option(  # noqa: B008
        False,
        "--tasks-only",
        help="Show only task lines without phase or section headings",
    ),
    all_tasks: bool = typer.Option(  # noqa: B008
        False,
        "--all",
        help="Show all remaining tasks with full context (ignores -n)",
    ),
) -> None:
    """Display uncompleted tasks from a speckit tasks.md file.

    By default, shows the next 10 uncompleted tasks with their phase and section context.
    Auto-discovers the latest tasks.md from specs/###-*/ if no path is provided.
    """
    console = Console()

    try:
        # Auto-discover if no path provided
        if file_path is None:
            file_path = discover_latest_tasks_file(Path.cwd())
            console.print(f"[dim]Found: {file_path}[/dim]\n")

        # Parse the file
        tasks_file = parse_tasks_file(file_path)

        # Check for parse errors (strict mode)
        if tasks_file.parse_errors:
            console.print("[bold red]Parse errors found:[/bold red]")
            for error in tasks_file.parse_errors:
                console.print(f"  Line {error.line_number}: {error.error_type} - {error.message}")
                console.print(f"  [dim]{error.line_content}[/dim]")
            raise typer.Exit(code=2)

        # Format and display based on view mode
        if phases_only:
            format_phases_only(console, tasks_file)
        elif structure:
            format_structure_view(console, tasks_file)
        elif all_phases:
            format_combined_view(console, tasks_file, count)
        elif tasks_only:
            format_tasks_only(console, tasks_file, count)
        elif all_tasks:
            # Show all tasks with context (use large count)
            format_default_view(console, tasks_file, count=99999)
        else:
            format_default_view(console, tasks_file, count)

    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(code=3) from None


if __name__ == "__main__":
    app()
