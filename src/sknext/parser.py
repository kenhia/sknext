"""Parser for tasks.md files.

Implements line-by-line state machine parsing to extract phases, sections, and tasks
from speckit tasks.md files.
"""

import re
from pathlib import Path

from sknext.constants import PHASE_PATTERN, SECTION_PATTERN, TASK_PATTERN
from sknext.models import ParseError, Phase, Section, Task, TasksFile


def parse_tasks_file(file_path: Path) -> TasksFile:
    """Parse a tasks.md file and return structured representation.

    Args:
        file_path: Path to the tasks.md file to parse

    Returns:
        TasksFile containing all phases, sections, tasks and any parse errors

    Raises:
        FileNotFoundError: If file_path does not exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    phases: list[Phase] = []
    parse_errors: list[ParseError] = []

    current_phase: Phase | None = None
    current_phase_sections: list[Section] = []
    current_section: Section | None = None
    current_section_tasks: list[Task] = []

    for line_num, line in enumerate(lines, start=1):
        line = line.rstrip("\n")

        # Try to match phase header
        phase_match = PHASE_PATTERN.match(line)
        if phase_match:
            # Save previous section if exists
            if current_section is not None:
                current_phase_sections.append(
                    Section(
                        title=current_section.title,
                        level=current_section.level,
                        tasks=current_section_tasks,
                        line_number=current_section.line_number,
                        purpose=current_section.purpose,
                    )
                )
                current_section = None
                current_section_tasks = []

            # Save previous phase if exists
            if current_phase is not None:
                phases.append(
                    Phase(
                        number=current_phase.number,
                        title=current_phase.title,
                        sections=current_phase_sections,
                        line_number=current_phase.line_number,
                    )
                )
                current_phase_sections = []

            # Start new phase
            phase_number = int(phase_match.group("number"))
            phase_title = phase_match.group("title").strip()
            current_phase = Phase(
                number=phase_number,
                title=phase_title,
                sections=[],
                line_number=line_num,
            )
            continue

        # Try to match section header
        section_match = SECTION_PATTERN.match(line)
        if section_match:
            # Save previous section if exists
            if current_section is not None:
                current_phase_sections.append(
                    Section(
                        title=current_section.title,
                        level=current_section.level,
                        tasks=current_section_tasks,
                        line_number=current_section.line_number,
                        purpose=current_section.purpose,
                    )
                )
                current_section_tasks = []

            # Start new section
            section_level = len(section_match.group("level"))
            section_title = section_match.group("title").strip()
            current_section = Section(
                title=section_title,
                level=section_level,
                tasks=[],
                line_number=line_num,
                purpose=None,
            )
            continue

        # Try to match task
        task_match = TASK_PATTERN.match(line)
        if task_match:
            # If we have a task but no section, create an implicit section
            if current_section is None and current_phase is not None:
                current_section = Section(
                    title="",  # Empty title for implicit section
                    level=3,
                    tasks=[],
                    line_number=line_num,
                    purpose=None,
                )

            checkbox = task_match.group("checkbox")
            task_id = task_match.group("task_id")
            description = task_match.group("description").strip()

            # Determine if task is completed (non-space character in checkbox)
            completed = checkbox != " "

            # Extract priority marker [P]
            priority = "[P]" in description

            # Extract story tag [USX]
            story_tag = None
            story_match = re.search(r"\[US(\d+)\]", description)
            if story_match:
                story_tag = f"US{story_match.group(1)}"

            task = Task(
                id=task_id,
                description=description,
                completed=completed,
                priority=priority,
                story_tag=story_tag,
                line_number=line_num,
                raw_line=line,
            )
            current_section_tasks.append(task)
            continue

    # Save final section if exists
    if current_section is not None:
        current_phase_sections.append(
            Section(
                title=current_section.title,
                level=current_section.level,
                tasks=current_section_tasks,
                line_number=current_section.line_number,
                purpose=current_section.purpose,
            )
        )

    # Save final phase if exists
    if current_phase is not None:
        phases.append(
            Phase(
                number=current_phase.number,
                title=current_phase.title,
                sections=current_phase_sections,
                line_number=current_phase.line_number,
            )
        )

    return TasksFile(
        file_path=file_path,
        phases=phases,
        parse_errors=parse_errors,
    )
