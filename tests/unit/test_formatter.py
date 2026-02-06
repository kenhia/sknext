"""Tests for formatter module."""

import re
from io import StringIO
from pathlib import Path

from rich.console import Console

from sknext.formatter import (
    format_combined_view,
    format_default_view,
    format_phases_only,
    format_structure_view,
    format_tasks_only,
)
from sknext.models import Phase, Section, Task, TasksFile


def strip_ansi(text: str) -> str:
    """Strip ANSI color codes from text."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


def create_sample_tasks() -> list[Task]:
    """Helper to create sample tasks."""
    return [
        Task("T001", "First task", False, False, None, 10, "- [ ] T001 First task"),
        Task("T002", "Second task", False, False, None, 11, "- [ ] T002 Second task"),
        Task("T003", "Third task", False, True, None, 12, "- [ ] T003 [P] Third task"),
        Task("T004", "Fourth task", False, False, "US1", 13, "- [ ] T004 [US1] Fourth task"),
        Task("T005", "Fifth task", False, False, None, 14, "- [ ] T005 Fifth task"),
    ]


def test_format_default_view_basic():
    """Test basic default view formatting."""
    tasks = create_sample_tasks()[:2]
    section = Section("Test Section", 3, tasks, 5, None)
    phase = Phase(1, "Setup", [section], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_default_view(console, tasks_file, count=2)

    result = strip_ansi(output.getvalue())
    assert "Phase 1: Setup" in result
    assert "Test Section" in result
    assert "T001" in result
    assert "T002" in result


def test_format_default_view_respects_count():
    """Test that default view respects count parameter."""
    tasks = create_sample_tasks()
    section = Section("Test Section", 3, tasks, 5, None)
    phase = Phase(1, "Setup", [section], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_default_view(console, tasks_file, count=3)

    result = output.getvalue()
    # Should show only first 3 tasks
    assert "T001" in result
    assert "T002" in result
    assert "T003" in result
    assert "T004" not in result
    assert "T005" not in result


def test_format_default_view_shows_summary():
    """Test that default view shows summary line."""
    tasks = create_sample_tasks()
    section = Section("Test Section", 3, tasks, 5, None)
    phase = Phase(1, "Setup", [section], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_default_view(console, tasks_file, count=2)

    result = output.getvalue()
    # Should show "Showing X of Y remaining"
    assert "Showing" in result
    assert "of" in result
    assert "remaining" in result


def test_format_default_view_handles_completed_tasks():
    """Test that default view only shows uncompleted tasks."""
    tasks = [
        Task("T001", "Done", True, False, None, 10, "- [X] T001 Done"),
        Task("T002", "Todo", False, False, None, 11, "- [ ] T002 Todo"),
        Task("T003", "Also done", True, False, None, 12, "- [X] T003 Also done"),
        Task("T004", "Also todo", False, False, None, 13, "- [ ] T004 Also todo"),
    ]
    section = Section("Test Section", 3, tasks, 5, None)
    phase = Phase(1, "Setup", [section], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_default_view(console, tasks_file, count=10)

    result = output.getvalue()
    # Should only show uncompleted tasks
    assert "T002" in result
    assert "T004" in result
    assert "Done" not in result or "T001" not in result


def test_format_default_view_shows_phase_context():
    """Test that tasks are shown with phase context."""
    tasks = [Task("T001", "Task", False, False, None, 10, "- [ ] T001 Task")]
    section = Section("Implementation", 3, tasks, 5, None)
    phase = Phase(2, "Foundation", [section], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_default_view(console, tasks_file, count=1)

    result = strip_ansi(output.getvalue())
    # Should show phase heading
    assert "Phase 2" in result
    assert "Foundation" in result


def test_format_default_view_shows_section_context():
    """Test that tasks are shown with section context."""
    tasks = [Task("T001", "Task", False, False, None, 10, "- [ ] T001 Task")]
    section = Section("Parser Implementation", 3, tasks, 5, None)
    phase = Phase(1, "Setup", [section], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_default_view(console, tasks_file, count=1)

    result = output.getvalue()
    # Should show section heading
    assert "Parser Implementation" in result


def test_format_default_view_all_complete():
    """Test default view when all tasks are complete."""
    tasks = [
        Task("T001", "Done 1", True, False, None, 10, "- [X] T001 Done 1"),
        Task("T002", "Done 2", True, False, None, 11, "- [X] T002 Done 2"),
    ]
    section = Section("Test Section", 3, tasks, 5, None)
    phase = Phase(1, "Setup", [section], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_default_view(console, tasks_file, count=10)

    result = output.getvalue()
    # Should show completion message
    assert "complete" in result.lower() or "done" in result.lower()


def test_format_default_view_count_exceeds_available():
    """Test default view when count exceeds available tasks."""
    tasks = [
        Task("T001", "Task 1", False, False, None, 10, "- [ ] T001 Task 1"),
        Task("T002", "Task 2", False, False, None, 11, "- [ ] T002 Task 2"),
    ]
    section = Section("Test Section", 3, tasks, 5, None)
    phase = Phase(1, "Setup", [section], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_default_view(console, tasks_file, count=100)

    result = output.getvalue()
    # Should show both tasks
    assert "T001" in result
    assert "T002" in result


def test_format_default_view_multiple_phases():
    """Test default view with tasks spanning multiple phases."""
    tasks1 = [Task("T001", "Phase 1 task", False, False, None, 10, "- [ ] T001 Phase 1 task")]
    section1 = Section("Section 1", 3, tasks1, 5, None)
    phase1 = Phase(1, "Setup", [section1], 3)

    tasks2 = [Task("T002", "Phase 2 task", False, False, None, 20, "- [ ] T002 Phase 2 task")]
    section2 = Section("Section 2", 3, tasks2, 18, None)
    phase2 = Phase(2, "Implementation", [section2], 16)

    tasks_file = TasksFile(Path("/tmp/test.md"), [phase1, phase2], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_default_view(console, tasks_file, count=5)

    result = output.getvalue()
    # Should show both phases
    assert "Phase 1" in result
    assert "Phase 2" in result


def test_format_default_view_easter_egg_zero_count():
    """Test Easter Egg: count=0 shows 1 task with humorous message."""
    tasks = create_sample_tasks()
    section = Section("Test Section", 3, tasks, 5, None)
    phase = Phase(1, "Setup", [section], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_default_view(console, tasks_file, count=0)

    result = strip_ansi(output.getvalue())
    # Should show exactly 1 task
    assert "T001" in result
    assert "T002" not in result
    # Should show Easter Egg message
    assert "Showing 0 tasks (for VERY large values of zero)" in result


# Tests for format_phases_only


def test_format_phases_only_shows_only_phases():
    """Test phases-only view shows only phase headings."""
    tasks1 = [Task("T001", "Task 1", False, False, None, 10, "- [ ] T001 Task 1")]
    section1 = Section("Section A", 3, tasks1, 5, None)
    phase1 = Phase(1, "Setup", [section1], 3)

    tasks2 = [Task("T002", "Task 2", False, False, None, 20, "- [ ] T002 Task 2")]
    section2 = Section("Section B", 3, tasks2, 18, None)
    phase2 = Phase(2, "Implementation", [section2], 16)

    tasks_file = TasksFile(Path("/tmp/test.md"), [phase1, phase2], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_phases_only(console, tasks_file)

    result = strip_ansi(output.getvalue())
    # Should show phase headings
    assert "Phase 1: Setup" in result
    assert "Phase 2: Implementation" in result
    # Should NOT show sections or tasks
    assert "Section A" not in result
    assert "Section B" not in result
    assert "T001" not in result
    assert "T002" not in result


def test_format_phases_only_filters_completed_phases():
    """Test phases-only view only shows phases with uncompleted work."""
    # Phase 1: all complete
    tasks1 = [Task("T001", "Done", True, False, None, 10, "- [X] T001 Done")]
    section1 = Section("Section A", 3, tasks1, 5, None)
    phase1 = Phase(1, "Complete Phase", [section1], 3)

    # Phase 2: has uncompleted
    tasks2 = [Task("T002", "Todo", False, False, None, 20, "- [ ] T002 Todo")]
    section2 = Section("Section B", 3, tasks2, 18, None)
    phase2 = Phase(2, "Incomplete Phase", [section2], 16)

    tasks_file = TasksFile(Path("/tmp/test.md"), [phase1, phase2], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_phases_only(console, tasks_file)

    result = strip_ansi(output.getvalue())
    # Should only show incomplete phase
    assert "Phase 2: Incomplete Phase" in result
    assert "Complete Phase" not in result or "Phase 1" not in result


def test_format_phases_only_all_complete():
    """Test phases-only view when all phases are complete."""
    tasks = [Task("T001", "Done", True, False, None, 10, "- [X] T001 Done")]
    section = Section("Section", 3, tasks, 5, None)
    phase = Phase(1, "Complete", [section], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_phases_only(console, tasks_file)

    result = strip_ansi(output.getvalue())
    # Should show completion message
    assert "complete" in result.lower() or "✓" in result


# Tests for format_structure_view


def test_format_structure_view_shows_phases_and_sections():
    """Test structure view shows phases and sections but not tasks."""
    tasks1 = [Task("T001", "Task 1", False, False, None, 10, "- [ ] T001 Task 1")]
    section1 = Section("Section A", 3, tasks1, 5, None)

    tasks2 = [Task("T002", "Task 2", False, False, None, 15, "- [ ] T002 Task 2")]
    section2 = Section("Section B", 3, tasks2, 13, None)

    phase = Phase(1, "Setup", [section1, section2], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_structure_view(console, tasks_file)

    result = strip_ansi(output.getvalue())
    # Should show phase and sections
    assert "Phase 1: Setup" in result
    assert "Section A" in result
    assert "Section B" in result
    # Should NOT show tasks
    assert "T001" not in result
    assert "T002" not in result


def test_format_structure_view_filters_completed_sections():
    """Test structure view only shows sections with uncompleted tasks."""
    # Section 1: all complete
    tasks1 = [Task("T001", "Done", True, False, None, 10, "- [X] T001 Done")]
    section1 = Section("Complete Section", 3, tasks1, 5, None)

    # Section 2: has uncompleted
    tasks2 = [Task("T002", "Todo", False, False, None, 20, "- [ ] T002 Todo")]
    section2 = Section("Incomplete Section", 3, tasks2, 18, None)

    phase = Phase(1, "Phase", [section1, section2], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_structure_view(console, tasks_file)

    result = strip_ansi(output.getvalue())
    # Should only show incomplete section
    assert "Incomplete Section" in result
    assert "Complete Section" not in result


def test_format_structure_view_filters_completed_phases():
    """Test structure view only shows phases with uncompleted work."""
    # Phase 1: all complete
    tasks1 = [Task("T001", "Done", True, False, None, 10, "- [X] T001 Done")]
    section1 = Section("Section", 3, tasks1, 5, None)
    phase1 = Phase(1, "Complete Phase", [section1], 3)

    # Phase 2: has uncompleted
    tasks2 = [Task("T002", "Todo", False, False, None, 20, "- [ ] T002 Todo")]
    section2 = Section("Section", 3, tasks2, 18, None)
    phase2 = Phase(2, "Incomplete Phase", [section2], 16)

    tasks_file = TasksFile(Path("/tmp/test.md"), [phase1, phase2], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_structure_view(console, tasks_file)

    result = strip_ansi(output.getvalue())
    # Should only show incomplete phase
    assert "Phase 2: Incomplete Phase" in result
    assert "Complete Phase" not in result or "Phase 1" not in result


def test_format_structure_view_all_complete():
    """Test structure view when all work is complete."""
    tasks = [Task("T001", "Done", True, False, None, 10, "- [X] T001 Done")]
    section = Section("Section", 3, tasks, 5, None)
    phase = Phase(1, "Complete", [section], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_structure_view(console, tasks_file)

    result = strip_ansi(output.getvalue())
    # Should show completion message
    assert "complete" in result.lower() or "✓" in result


# Tests for format_combined_view


def test_format_combined_view_shows_phases_and_tasks():
    """Test combined view shows all incomplete phases followed by N tasks."""
    # Phase 1 with tasks
    tasks1 = [
        Task("T001", "Task 1", False, False, None, 10, "- [ ] T001 Task 1"),
        Task("T002", "Task 2", False, False, None, 11, "- [ ] T002 Task 2"),
    ]
    section1 = Section("Section A", 3, tasks1, 5, None)
    phase1 = Phase(1, "Phase One", [section1], 3)

    # Phase 2 with tasks
    tasks2 = [Task("T003", "Task 3", False, False, None, 20, "- [ ] T003 Task 3")]
    section2 = Section("Section B", 3, tasks2, 18, None)
    phase2 = Phase(2, "Phase Two", [section2], 16)

    tasks_file = TasksFile(Path("/tmp/test.md"), [phase1, phase2], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_combined_view(console, tasks_file, count=2)

    result = strip_ansi(output.getvalue())
    # Should show phase headings
    assert "Phase 1: Phase One" in result
    assert "Phase 2: Phase Two" in result
    # Should show tasks (limited by count)
    assert "T001" in result
    assert "T002" in result
    # Should NOT show T003 (beyond count limit)
    assert "T003" not in result
    # Should have separator between sections
    assert "next" in result.lower() and "tasks" in result.lower()


def test_format_combined_view_respects_count():
    """Test combined view respects task count limit."""
    tasks = [
        Task("T001", "Task 1", False, False, None, 10, "- [ ] T001 Task 1"),
        Task("T002", "Task 2", False, False, None, 11, "- [ ] T002 Task 2"),
        Task("T003", "Task 3", False, False, None, 12, "- [ ] T003 Task 3"),
    ]
    section = Section("Section", 3, tasks, 5, None)
    phase = Phase(1, "Phase", [section], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_combined_view(console, tasks_file, count=1)

    result = strip_ansi(output.getvalue())
    # Should only show 1 task
    assert "T001" in result
    assert "T002" not in result
    assert "T003" not in result


def test_format_combined_view_filters_completed_phases():
    """Test combined view only shows incomplete phases."""
    # Completed phase
    tasks1 = [Task("T001", "Done", True, False, None, 10, "- [X] T001 Done")]
    section1 = Section("Section", 3, tasks1, 5, None)
    phase1 = Phase(1, "Complete Phase", [section1], 3)

    # Incomplete phase
    tasks2 = [Task("T002", "Todo", False, False, None, 20, "- [ ] T002 Todo")]
    section2 = Section("Section", 3, tasks2, 18, None)
    phase2 = Phase(2, "Incomplete Phase", [section2], 16)

    tasks_file = TasksFile(Path("/tmp/test.md"), [phase1, phase2], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_combined_view(console, tasks_file, count=5)

    result = strip_ansi(output.getvalue())
    # Should only show incomplete phase
    assert "Phase 2: Incomplete Phase" in result
    assert "Complete Phase" not in result or "Phase 1" not in result


def test_format_combined_view_all_complete():
    """Test combined view when all work is complete."""
    tasks = [Task("T001", "Done", True, False, None, 10, "- [X] T001 Done")]
    section = Section("Section", 3, tasks, 5, None)
    phase = Phase(1, "Complete", [section], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_combined_view(console, tasks_file, count=10)

    result = strip_ansi(output.getvalue())
    # Should show completion message
    assert "complete" in result.lower() or "✓" in result


# Tests for format_tasks_only


def test_format_tasks_only_shows_only_tasks():
    """Test tasks-only view shows only task lines."""
    tasks1 = [
        Task("T001", "Task 1", False, False, None, 10, "- [ ] T001 Task 1"),
        Task("T002", "Task 2", False, False, None, 11, "- [ ] T002 Task 2"),
    ]
    section1 = Section("Section A", 3, tasks1, 5, None)
    phase1 = Phase(1, "Phase One", [section1], 3)

    tasks2 = [Task("T003", "Task 3", False, False, None, 20, "- [ ] T003 Task 3")]
    section2 = Section("Section B", 3, tasks2, 18, None)
    phase2 = Phase(2, "Phase Two", [section2], 16)

    tasks_file = TasksFile(Path("/tmp/test.md"), [phase1, phase2], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_tasks_only(console, tasks_file, count=3)

    result = strip_ansi(output.getvalue())
    # Should show tasks
    assert "T001" in result
    assert "T002" in result
    assert "T003" in result
    # Should NOT show phase or section headings
    assert "Phase 1" not in result
    assert "Phase 2" not in result
    assert "Section A" not in result
    assert "Section B" not in result


def test_format_tasks_only_respects_count():
    """Test tasks-only view respects count limit."""
    tasks = [
        Task("T001", "Task 1", False, False, None, 10, "- [ ] T001 Task 1"),
        Task("T002", "Task 2", False, False, None, 11, "- [ ] T002 Task 2"),
        Task("T003", "Task 3", False, False, None, 12, "- [ ] T003 Task 3"),
    ]
    section = Section("Section", 3, tasks, 5, None)
    phase = Phase(1, "Phase", [section], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_tasks_only(console, tasks_file, count=2)

    result = strip_ansi(output.getvalue())
    # Should only show 2 tasks
    assert "T001" in result
    assert "T002" in result
    assert "T003" not in result


def test_format_tasks_only_handles_priority():
    """Test tasks-only view preserves priority markers."""
    tasks = [
        Task("T001", "[P] Priority task", False, True, None, 10, "- [ ] T001 [P] Priority task")
    ]
    section = Section("Section", 3, tasks, 5, None)
    phase = Phase(1, "Phase", [section], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_tasks_only(console, tasks_file, count=5)

    result = strip_ansi(output.getvalue())
    # Should show priority marker
    assert "T001" in result
    assert "[P]" in result or "P" in result


def test_format_tasks_only_all_complete():
    """Test tasks-only view when all tasks are complete."""
    tasks = [Task("T001", "Done", True, False, None, 10, "- [X] T001 Done")]
    section = Section("Section", 3, tasks, 5, None)
    phase = Phase(1, "Complete", [section], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    format_tasks_only(console, tasks_file, count=10)

    result = strip_ansi(output.getvalue())
    # Should show completion message
    assert "complete" in result.lower() or "✓" in result


# Tests for --all flag (shows all tasks with context)


def test_format_all_tasks_shows_all():
    """Test that we can show all tasks by passing large count to default view."""
    tasks = [
        Task(f"T{i:03d}", f"Task {i}", False, False, None, i * 10, f"- [ ] T{i:03d} Task {i}")
        for i in range(1, 21)  # 20 tasks
    ]
    section = Section("Section", 3, tasks, 5, None)
    phase = Phase(1, "Phase", [section], 3)
    tasks_file = TasksFile(Path("/tmp/test.md"), [phase], [])

    output = StringIO()
    console = Console(file=output, force_terminal=True, width=100)
    # Use default view with very large count
    format_default_view(console, tasks_file, count=1000)

    result = strip_ansi(output.getvalue())
    # Should show all tasks
    assert "T001" in result
    assert "T020" in result
    assert "all 20 remaining tasks" in result.lower()
