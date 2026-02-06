"""Data models for task file structure."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Task:
    """Represents a single work item with completion status and metadata.

    Attributes:
        id: Task identifier (e.g., "T001", "T042")
        description: Full task description text
        completed: True if checkbox contains non-space character
        priority: True if [P] marker present
        story_tag: Story identifier if present (e.g., "US1", "US2")
        line_number: Source line number for error reporting
        raw_line: Original line text for debugging
    """

    id: str
    description: str
    completed: bool
    priority: bool
    story_tag: str | None
    line_number: int
    raw_line: str


@dataclass(frozen=True)
class Section:
    """Represents a grouping of related tasks within a phase.

    Attributes:
        title: Section heading text (without markdown ##)
        level: Heading depth (3 for ###, 4 for ####, etc.)
        tasks: Tasks within this section (in file order)
        line_number: Source line number
        purpose: Purpose description if using **Purpose**: format
    """

    title: str
    level: int
    tasks: list[Task]
    line_number: int
    purpose: str | None

    def has_uncompleted_tasks(self) -> bool:
        """Return True if any task in section is not completed."""
        return any(not task.completed for task in self.tasks)

    def uncompleted_count(self) -> int:
        """Return count of uncompleted tasks."""
        return sum(1 for task in self.tasks if not task.completed)

    def total_count(self) -> int:
        """Return total number of tasks."""
        return len(self.tasks)


@dataclass(frozen=True)
class Phase:
    """Represents a major development stage containing multiple sections.

    Attributes:
        number: Phase number (e.g., 1, 2, 3)
        title: Phase name (without "Phase N:" prefix)
        sections: Sections within this phase (in file order)
        line_number: Source line number
    """

    number: int
    title: str
    sections: list[Section]
    line_number: int

    def has_uncompleted_work(self) -> bool:
        """Return True if any section has uncompleted tasks."""
        return any(section.has_uncompleted_tasks() for section in self.sections)

    def uncompleted_task_count(self) -> int:
        """Return total uncompleted tasks across all sections."""
        return sum(section.uncompleted_count() for section in self.sections)

    def total_task_count(self) -> int:
        """Return total tasks across all sections."""
        return sum(section.total_count() for section in self.sections)


@dataclass(frozen=True)
class TasksFile:
    """Represents the entire parsed tasks.md file structure.

    Attributes:
        file_path: Absolute path to the tasks.md file
        phases: All phases in file order
        parse_errors: Any errors encountered (strict mode: should be empty on success)
    """

    file_path: Path
    phases: list[Phase]
    parse_errors: list["ParseError"]

    def get_all_tasks(self) -> list[Task]:
        """Return flattened list of all tasks across all phases."""
        return [
            task for phase in self.phases for section in phase.sections for task in section.tasks
        ]

    def get_uncompleted_tasks(self) -> list[Task]:
        """Return all uncompleted tasks in file order."""
        return [task for task in self.get_all_tasks() if not task.completed]

    def get_phases_with_uncompleted_work(self) -> list[Phase]:
        """Return phases that have remaining work."""
        return [phase for phase in self.phases if phase.has_uncompleted_work()]

    def is_complete(self) -> bool:
        """Return True if all tasks completed."""
        return len(self.get_uncompleted_tasks()) == 0


@dataclass(frozen=True)
class ParseError:
    """Represents a parsing error with context for debugging.

    Attributes:
        line_number: Line where error occurred
        line_content: The problematic line text
        error_type: Error category (e.g., "MalformedTask", "InvalidHeading")
        message: Human-readable error description
    """

    line_number: int
    line_content: str
    error_type: str
    message: str
