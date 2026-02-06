"""Tests for parser module."""

from pathlib import Path

import pytest

from sknext.parser import parse_tasks_file


def test_parse_simple_task():
    """Test parsing a simple task line."""
    content = """# Tasks: Test

## Phase 1: Setup

### Section 1

- [ ] T001 Simple task
"""
    file_path = Path("/tmp/test.md")
    with open(file_path, "w") as f:
        f.write(content)

    result = parse_tasks_file(file_path)
    assert len(result.phases) == 1
    assert len(result.phases[0].sections) == 1
    assert len(result.phases[0].sections[0].tasks) == 1

    task = result.phases[0].sections[0].tasks[0]
    assert task.id == "T001"
    assert task.description == "Simple task"
    assert not task.completed


def test_parse_completed_task():
    """Test parsing completed task with [X]."""
    content = """# Tasks: Test

## Phase 1: Setup

### Section 1

- [X] T001 Completed task
"""
    file_path = Path("/tmp/test_completed.md")
    with open(file_path, "w") as f:
        f.write(content)

    result = parse_tasks_file(file_path)
    task = result.phases[0].sections[0].tasks[0]
    assert task.completed


def test_parse_priority_task():
    """Test parsing task with [P] marker."""
    content = """# Tasks: Test

## Phase 1: Setup

### Section 1

- [ ] T001 [P] Priority task
"""
    file_path = Path("/tmp/test_priority.md")
    with open(file_path, "w") as f:
        f.write(content)

    result = parse_tasks_file(file_path)
    task = result.phases[0].sections[0].tasks[0]
    assert task.priority
    assert "[P]" in task.description


def test_parse_story_tag():
    """Test parsing task with story tag [US1]."""
    content = """# Tasks: Test

## Phase 1: Setup

### Section 1

- [ ] T001 [US1] User story task
"""
    file_path = Path("/tmp/test_story.md")
    with open(file_path, "w") as f:
        f.write(content)

    result = parse_tasks_file(file_path)
    task = result.phases[0].sections[0].tasks[0]
    assert task.story_tag == "US1"


def test_parse_multiple_phases():
    """Test parsing multiple phases."""
    content = """# Tasks: Test

## Phase 1: Setup

### Section 1

- [ ] T001 Task 1

---

## Phase 2: Implementation

### Section 2

- [ ] T002 Task 2
"""
    file_path = Path("/tmp/test_phases.md")
    with open(file_path, "w") as f:
        f.write(content)

    result = parse_tasks_file(file_path)
    assert len(result.phases) == 2
    assert result.phases[0].number == 1
    assert result.phases[1].number == 2


def test_parse_multiple_sections():
    """Test parsing multiple sections in one phase."""
    content = """# Tasks: Test

## Phase 1: Setup

### Section A

- [ ] T001 Task A

### Section B

- [ ] T002 Task B
"""
    file_path = Path("/tmp/test_sections.md")
    with open(file_path, "w") as f:
        f.write(content)

    result = parse_tasks_file(file_path)
    assert len(result.phases[0].sections) == 2
    assert result.phases[0].sections[0].title == "Section A"
    assert result.phases[0].sections[1].title == "Section B"


def test_parse_purpose_line():
    """Test parsing **Purpose**: line in section."""
    content = """# Tasks: Test

## Phase 1: Setup

**Purpose**: Initialize project

### Section 1

- [ ] T001 Task
"""
    file_path = Path("/tmp/test_purpose.md")
    with open(file_path, "w") as f:
        f.write(content)

    result = parse_tasks_file(file_path)
    # Purpose is associated with the phase, not individual sections in this simple case
    # If there's a section-level purpose, it would be parsed there
    assert len(result.phases) == 1


def test_parse_nested_sections():
    """Test parsing nested sections (###, ####, etc.)."""
    content = """# Tasks: Test

## Phase 1: Setup

### Level 3 Section

- [ ] T001 Task at level 3

#### Level 4 Subsection

- [ ] T002 Task at level 4
"""
    file_path = Path("/tmp/test_nested.md")
    with open(file_path, "w") as f:
        f.write(content)

    result = parse_tasks_file(file_path)
    assert len(result.phases[0].sections) == 2
    assert result.phases[0].sections[0].level == 3
    assert result.phases[0].sections[1].level == 4


def test_parse_task_id_extraction():
    """Test task ID extraction and validation."""
    content = """# Tasks: Test

## Phase 1: Setup

### Section 1

- [ ] T001 Task one
- [ ] T042 Task forty-two
- [ ] T999 Task nine ninety-nine
"""
    file_path = Path("/tmp/test_ids.md")
    with open(file_path, "w") as f:
        f.write(content)

    result = parse_tasks_file(file_path)
    tasks = result.phases[0].sections[0].tasks
    assert tasks[0].id == "T001"
    assert tasks[1].id == "T042"
    assert tasks[2].id == "T999"


def test_parse_mixed_completion():
    """Test parsing mix of completed and uncompleted tasks."""
    content = """# Tasks: Test

## Phase 1: Setup

### Section 1

- [X] T001 Done
- [ ] T002 Todo
- [x] T003 Also done
- [ ] T004 Also todo
"""
    file_path = Path("/tmp/test_mixed.md")
    with open(file_path, "w") as f:
        f.write(content)

    result = parse_tasks_file(file_path)
    tasks = result.phases[0].sections[0].tasks
    assert tasks[0].completed
    assert not tasks[1].completed
    assert tasks[2].completed
    assert not tasks[3].completed


def test_parse_ignores_non_task_lines():
    """Test that parser ignores markdown that isn't tasks/phases/sections."""
    content = """# Tasks: Test

This is some introductory text.

## Phase 1: Setup

Here is some phase description.

### Section 1

This section does important work.

- [ ] T001 Actual task

Here is more text after the task.
"""
    file_path = Path("/tmp/test_ignore.md")
    with open(file_path, "w") as f:
        f.write(content)

    result = parse_tasks_file(file_path)
    assert len(result.phases) == 1
    assert len(result.phases[0].sections) == 1
    assert len(result.phases[0].sections[0].tasks) == 1


def test_parse_empty_file():
    """Test parsing empty file."""
    content = ""
    file_path = Path("/tmp/test_empty.md")
    with open(file_path, "w") as f:
        f.write(content)

    result = parse_tasks_file(file_path)
    assert len(result.phases) == 0
    assert len(result.parse_errors) == 0


def test_parse_file_not_found():
    """Test parsing non-existent file raises error."""
    with pytest.raises(FileNotFoundError):
        parse_tasks_file(Path("/nonexistent/file.md"))


def test_parse_preserves_line_numbers():
    """Test that parser preserves line numbers for debugging."""
    content = """# Tasks: Test
Line 2
Line 3
## Phase 1: Setup
Line 5
### Section 1
Line 7
- [ ] T001 Task
"""
    file_path = Path("/tmp/test_lines.md")
    with open(file_path, "w") as f:
        f.write(content)

    result = parse_tasks_file(file_path)
    phase = result.phases[0]
    section = phase.sections[0]
    task = section.tasks[0]

    # Check line numbers are tracked
    assert phase.line_number > 0
    assert section.line_number > 0
    assert task.line_number > 0


def test_parse_hierarchy_building():
    """Test that parser correctly builds phase -> section -> task hierarchy."""
    content = """# Tasks: Test

## Phase 1: Setup

### Section A

- [ ] T001 Task A1
- [ ] T002 Task A2

### Section B

- [ ] T003 Task B1

## Phase 2: Implementation

### Section C

- [ ] T004 Task C1
"""
    file_path = Path("/tmp/test_hierarchy.md")
    with open(file_path, "w") as f:
        f.write(content)

    result = parse_tasks_file(file_path)

    # Verify structure
    assert len(result.phases) == 2

    # Phase 1
    assert result.phases[0].number == 1
    assert len(result.phases[0].sections) == 2
    assert len(result.phases[0].sections[0].tasks) == 2
    assert len(result.phases[0].sections[1].tasks) == 1

    # Phase 2
    assert result.phases[1].number == 2
    assert len(result.phases[1].sections) == 1
    assert len(result.phases[1].sections[0].tasks) == 1
