"""Output formatting with rich console."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from sknext.models import Phase, Section, Task, TasksFile


def format_default_view(console: Console, tasks_file: TasksFile, count: int) -> None:
    """Format and display the default view: next N uncompleted tasks with context.

    Args:
        console: Rich console for output
        tasks_file: Parsed tasks file
        count: Number of tasks to display
    """
    uncompleted_tasks = tasks_file.get_uncompleted_tasks()

    if not uncompleted_tasks:
        console.print(
            Panel.fit(
                "[bold green]✓ All tasks complete![/bold green]",
                border_style="green",
            )
        )
        return

    # Easter Egg: If count=0 but tasks exist, show 1 task with humorous message
    if count == 0:
        tasks_to_show = uncompleted_tasks[:1]
        easter_egg_message = True
    else:
        # Take first N tasks
        tasks_to_show = uncompleted_tasks[:count]
        easter_egg_message = False

    total_remaining = len(uncompleted_tasks)

    # Build output with hierarchical context
    current_phase: Phase | None = None
    current_section: Section | None = None

    for task in tasks_to_show:
        # Find which phase and section this task belongs to
        task_phase, task_section = _find_task_context(tasks_file, task)

        # Show phase heading if changed
        if task_phase != current_phase:
            console.print()
            console.print(
                f"[bold cyan]## Phase {task_phase.number}: {task_phase.title}[/bold cyan]"
            )
            current_phase = task_phase
            current_section = None

        # Show section heading if changed (skip if empty title - implicit section)
        if task_section != current_section:
            if task_section.title:  # Only show section if it has a title
                console.print()
                console.print(f"[bold]{'#' * task_section.level} {task_section.title}[/bold]")
            current_section = task_section

        # Show task
        task_text = Text()
        task_text.append("- [ ] ", style="dim")
        task_text.append(f"{task.id} ", style="yellow")

        # Highlight priority and story tags
        desc = task.description
        if "[P]" in desc:
            desc = desc.replace("[P]", "")
            task_text.append("[P] ", style="bold magenta")

        if task.story_tag:
            desc = desc.replace(f"[{task.story_tag}]", "")
            task_text.append(f"[{task.story_tag}] ", style="bold blue")

        task_text.append(desc.strip())
        console.print(task_text)

    # Show summary
    console.print()
    if easter_egg_message:
        console.print("[dim]Showing 0 tasks (for VERY large values of zero)[/dim]")
    elif len(tasks_to_show) < total_remaining:
        console.print(
            f"[dim]Showing {len(tasks_to_show)} of {total_remaining} remaining tasks[/dim]"
        )
    else:
        console.print(f"[dim]Showing all {total_remaining} remaining tasks[/dim]")


def format_phases_only(console: Console, tasks_file: TasksFile) -> None:
    """Format and display phases-only view: show only phases with uncompleted work.

    Args:
        console: Rich console for output
        tasks_file: Parsed tasks file
    """
    # Filter to phases with uncompleted work
    phases_with_work = [phase for phase in tasks_file.phases if phase.has_uncompleted_work()]

    if not phases_with_work:
        console.print(
            Panel.fit(
                "[bold green]✓ All phases complete![/bold green]",
                border_style="green",
            )
        )
        return

    # Display each phase heading only
    console.print("[bold]Phases with uncompleted work:[/bold]")
    console.print()

    for phase in phases_with_work:
        console.print(f"[bold cyan]## Phase {phase.number}: {phase.title}[/bold cyan]")

    # Show summary
    console.print()
    console.print(f"[dim]Showing {len(phases_with_work)} of {len(tasks_file.phases)} phases[/dim]")


def format_structure_view(console: Console, tasks_file: TasksFile) -> None:
    """Format and display structure view: phases and sections with uncompleted work.

    Args:
        console: Rich console for output
        tasks_file: Parsed tasks file
    """
    # Filter to phases with uncompleted work
    phases_with_work = [phase for phase in tasks_file.phases if phase.has_uncompleted_work()]

    if not phases_with_work:
        console.print(
            Panel.fit(
                "[bold green]✓ All work complete![/bold green]",
                border_style="green",
            )
        )
        return

    # Display phases and their sections (but not tasks)
    console.print("[bold]Project structure with uncompleted work:[/bold]")
    console.print()

    section_count = 0
    for phase in phases_with_work:
        console.print(f"[bold cyan]## Phase {phase.number}: {phase.title}[/bold cyan]")

        # Show only sections with uncompleted work
        for section in phase.sections:
            if section.has_uncompleted_tasks():
                # Skip implicit sections (empty title)
                if section.title:
                    console.print(f"  [bold]{'#' * section.level} {section.title}[/bold]")
                    section_count += 1

        console.print()

    # Show summary
    console.print(
        f"[dim]Showing {len(phases_with_work)} phases with {section_count} sections[/dim]"
    )


def format_combined_view(console: Console, tasks_file: TasksFile, count: int) -> None:
    """Format and display combined view: all incomplete phases, then N tasks.

    Args:
        console: Rich console for output
        tasks_file: Parsed tasks file
        count: Number of tasks to display
    """
    uncompleted_tasks = tasks_file.get_uncompleted_tasks()

    if not uncompleted_tasks:
        console.print(
            Panel.fit(
                "[bold green]✓ All tasks complete![/bold green]",
                border_style="green",
            )
        )
        return

    # Section 1: Show all incomplete phases
    phases_with_work = [phase for phase in tasks_file.phases if phase.has_uncompleted_work()]

    console.print("[bold]Incomplete phases:[/bold]")
    console.print()

    for phase in phases_with_work:
        console.print(f"[bold cyan]## Phase {phase.number}: {phase.title}[/bold cyan]")

    # Separator
    console.print()
    console.print("[dim]" + "─" * 60 + "[/dim]")
    console.print()

    # Section 2: Show next N tasks with context
    console.print(f"[bold]Next {min(count, len(uncompleted_tasks))} tasks:[/bold]")
    console.print()

    tasks_to_show = uncompleted_tasks[:count]
    current_phase: Phase | None = None
    current_section: Section | None = None

    for task in tasks_to_show:
        # Find which phase and section this task belongs to
        task_phase, task_section = _find_task_context(tasks_file, task)

        # Show phase heading if changed
        if task_phase != current_phase:
            console.print()
            console.print(
                f"[bold cyan]## Phase {task_phase.number}: {task_phase.title}[/bold cyan]"
            )
            current_phase = task_phase
            current_section = None

        # Show section heading if changed (skip if empty title)
        if task_section != current_section:
            if task_section.title:
                console.print()
                console.print(f"[bold]{'#' * task_section.level} {task_section.title}[/bold]")
            current_section = task_section

        # Show task
        task_text = Text()
        task_text.append("- [ ] ", style="dim")
        task_text.append(f"{task.id} ", style="yellow")

        # Highlight priority and story tags
        desc = task.description
        if "[P]" in desc:
            desc = desc.replace("[P]", "")
            task_text.append("[P] ", style="bold magenta")

        if task.story_tag:
            desc = desc.replace(f"[{task.story_tag}]", "")
            task_text.append(f"[{task.story_tag}] ", style="bold blue")

        task_text.append(desc.strip())
        console.print(task_text)

    # Show summary
    console.print()
    total_remaining = len(uncompleted_tasks)
    if len(tasks_to_show) < total_remaining:
        console.print(
            f"[dim]Showing {len(phases_with_work)} phases and "
            f"{len(tasks_to_show)} of {total_remaining} remaining tasks[/dim]"
        )
    else:
        console.print(
            f"[dim]Showing {len(phases_with_work)} phases and "
            f"all {total_remaining} remaining tasks[/dim]"
        )


def format_tasks_only(console: Console, tasks_file: TasksFile, count: int) -> None:
    """Format and display tasks-only view: task lines without any headings.

    Args:
        console: Rich console for output
        tasks_file: Parsed tasks file
        count: Number of tasks to display
    """
    uncompleted_tasks = tasks_file.get_uncompleted_tasks()

    if not uncompleted_tasks:
        console.print(
            Panel.fit(
                "[bold green]✓ All tasks complete![/bold green]",
                border_style="green",
            )
        )
        return

    # Show tasks without any phase/section context
    tasks_to_show = uncompleted_tasks[:count]

    for task in tasks_to_show:
        task_text = Text()
        task_text.append("- [ ] ", style="dim")
        task_text.append(f"{task.id} ", style="yellow")

        # Highlight priority and story tags
        desc = task.description
        if "[P]" in desc:
            desc = desc.replace("[P]", "")
            task_text.append("[P] ", style="bold magenta")

        if task.story_tag:
            desc = desc.replace(f"[{task.story_tag}]", "")
            task_text.append(f"[{task.story_tag}] ", style="bold blue")

        task_text.append(desc.strip())
        console.print(task_text)

    # Show summary
    console.print()
    total_remaining = len(uncompleted_tasks)
    if len(tasks_to_show) < total_remaining:
        console.print(
            f"[dim]Showing {len(tasks_to_show)} of {total_remaining} remaining tasks[/dim]"
        )
    else:
        console.print(f"[dim]Showing all {total_remaining} remaining tasks[/dim]")


def _find_task_context(tasks_file: TasksFile, target_task: Task) -> tuple[Phase, Section]:
    """Find which phase and section a task belongs to.

    Args:
        tasks_file: The parsed tasks file
        target_task: The task to find context for

    Returns:
        Tuple of (Phase, Section) containing the task
    """
    for phase in tasks_file.phases:
        for section in phase.sections:
            for task in section.tasks:
                if task.id == target_task.id and task.line_number == target_task.line_number:
                    return (phase, section)

    # Should never reach here if task came from tasks_file
    raise ValueError(f"Task {target_task.id} not found in tasks file")
