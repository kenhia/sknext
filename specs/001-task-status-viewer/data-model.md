# Data Model: Task Status Viewer

**Phase**: 1 - Design  
**Date**: 2026-02-05

## Overview

The data model captures the hierarchical structure of a tasks.md file: Phases contain Sections, Sections contain Tasks. All entities are immutable dataclasses for type safety and clarity.

## Core Entities

### Task

Represents a single work item with completion status and metadata.

**Attributes**:
- `id: str` - Task identifier (e.g., "T001", "T042")
- `description: str` - Full task description text
- `completed: bool` - True if checkbox contains non-space character
- `priority: bool` - True if `[P]` marker present
- `story_tag: Optional[str]` - Story identifier if present (e.g., "US1", "US2")
- `line_number: int` - Source line number for error reporting
- `raw_line: str` - Original line text for debugging

**Validation**:
- `id` must match pattern `T\d{3,}` (T followed by 3+ digits)
- `description` cannot be empty
- `line_number` must be positive

**Example**:
```python
Task(
    id="T001",
    description="Create project structure per implementation plan",
    completed=False,
    priority=False,
    story_tag=None,
    line_number=52,
    raw_line="- [ ] T001 Create project structure per implementation plan"
)
```

---

### Section

Represents a grouping of related tasks within a phase.

**Attributes**:
- `title: str` - Section heading text (without markdown ##)
- `level: int` - Heading depth (3 for ###, 4 for ####, etc.)
- `tasks: List[Task]` - Tasks within this section (in file order)
- `line_number: int` - Source line number
- `purpose: Optional[str]` - Purpose description if using **Purpose**: format

**Computed Properties**:
- `has_uncompleted_tasks() -> bool` - True if any task in section is not completed
- `uncompleted_count() -> int` - Count of uncompleted tasks
- `total_count() -> int` - Total number of tasks

**Validation**:
- `title` cannot be empty
- `level` must be >= 3 (sections are ### or deeper)
- `tasks` can be empty (section with no tasks yet)

**Example**:
```python
Section(
    title="Setup (Shared Infrastructure)",
    level=3,
    tasks=[task1, task2, task3],
    line_number=45,
    purpose="Project initialization and basic structure"
)
```

---

### Phase

Represents a major development stage containing multiple sections.

**Attributes**:
- `number: int` - Phase number (e.g., 1, 2, 3)
- `title: str` - Phase name (without "Phase N:" prefix)
- `sections: List[Section]` - Sections within this phase (in file order)
- `line_number: int` - Source line number

**Computed Properties**:
- `has_uncompleted_work() -> bool` - True if any section has uncompleted tasks
- `uncompleted_task_count() -> int` - Total uncompleted tasks across all sections
- `total_task_count() -> int` - Total tasks across all sections

**Validation**:
- `number` must be positive integer
- `title` cannot be empty
- `sections` can be empty (phase not yet started)

**Example**:
```python
Phase(
    number=1,
    title="Setup",
    sections=[section1, section2],
    line_number=40
)
```

---

### TasksFile

Represents the entire parsed tasks.md file structure.

**Attributes**:
- `file_path: Path` - Absolute path to the tasks.md file
- `phases: List[Phase]` - All phases in file order
- `parse_errors: List[ParseError]` - Any errors encountered (strict mode: should be empty on success)

**Computed Properties**:
- `get_all_tasks() -> List[Task]` - Flattened list of all tasks across all phases
- `get_uncompleted_tasks() -> List[Task]` - All uncompleted tasks in file order
- `get_phases_with_uncompleted_work() -> List[Phase]` - Phases that have remaining work
- `is_complete() -> bool` - True if all tasks completed

**Validation**:
- `file_path` must exist and be readable
- In strict mode, `parse_errors` must be empty

**Example**:
```python
TasksFile(
    file_path=Path("/home/user/project/specs/001-feature/tasks.md"),
    phases=[phase1, phase2, phase3],
    parse_errors=[]
)
```

---

### ParseError

Represents a parsing error with context for debugging.

**Attributes**:
- `line_number: int` - Line where error occurred
- `line_content: str` - The problematic line text
- `error_type: str` - Error category (e.g., "MalformedTask", "InvalidHeading")
- `message: str` - Human-readable error description

**Example**:
```python
ParseError(
    line_number=67,
    line_content="- [] T042 Missing space in checkbox",
    error_type="MalformedTask",
    message="Task checkbox must have single space: '[ ]' or '[x]'"
)
```

---

## Relationships

```
TasksFile
  ├── phases: List[Phase]
  │     ├── sections: List[Section]
  │     │     └── tasks: List[Task]
  └── parse_errors: List[ParseError]
```

**Hierarchy Rules**:
1. Phases contain Sections (## Phase N: → ### Section)
2. Sections contain Tasks (### Section → - [ ] Task)
3. Tasks never contain child elements (leaf nodes)
4. Orphaned tasks (tasks without section) are errors in strict mode
5. Orphaned sections (sections without phase) are errors in strict mode

---

## View Mode Filtering

Different view modes require different filtering/projection of the data model:

| View Mode | Data Transformation |
|-----------|-------------------|
| Default (10 tasks) | `get_uncompleted_tasks()[:10]` with parent context |
| Custom (N tasks) | `get_uncompleted_tasks()[:N]` with parent context |
| Phase-only | `get_phases_with_uncompleted_work()` (no sections/tasks) |
| Structure | `get_phases_with_uncompleted_work()` with filtered sections (no tasks) |
| Combined | `get_phases_with_uncompleted_work()` + `get_uncompleted_tasks()[:N]` |
| Task-only | `get_uncompleted_tasks()[:N]` (no context) |
| All tasks | `get_uncompleted_tasks()` (no limit) with full context |

---

## Immutability & Type Safety

All dataclasses are frozen (`@dataclass(frozen=True)`) to prevent accidental mutation:

```python
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

@dataclass(frozen=True)
class Task:
    id: str
    description: str
    completed: bool
    priority: bool
    story_tag: Optional[str]
    line_number: int
    raw_line: str
```

Type hints are comprehensive for mypy verification and IDE autocomplete.

---

## Constants

Defined in `src/task_viewer/constants.py`:

```python
# Maximum nesting depth before graceful degradation
MAX_NESTING_DEPTH: int = 5

# Default number of tasks to display
DEFAULT_TASK_COUNT: int = 10

# Regex patterns
TASK_PATTERN = r'^\s*-\s*\[(.)\]\s*(T\d{3,})\s*(\[P\])?\s*(\[US\d+\])?\s*(.+)$'
PHASE_HEADING_PATTERN = r'^##\s+Phase\s+(\d+):\s*(.+)$'
SECTION_HEADING_PATTERN = r'^(#{3,})\s+(.+)$'
PURPOSE_PATTERN = r'^\*\*Purpose\*\*:\s*(.+)$'

# Exit codes
EXIT_SUCCESS = 0
EXIT_FILE_NOT_FOUND = 1
EXIT_PARSE_ERROR = 2
EXIT_INVALID_ARGS = 3
```

---

## Usage Example

```python
from task_viewer.parser import parse_tasks_file
from task_viewer.models import TasksFile

# Parse file
tasks_file: TasksFile = parse_tasks_file(Path("specs/001-feature/tasks.md"))

# Get uncompleted tasks
uncompleted = tasks_file.get_uncompleted_tasks()
print(f"Remaining: {len(uncompleted)} tasks")

# Check if phase has work
for phase in tasks_file.phases:
    if phase.has_uncompleted_work():
        print(f"Phase {phase.number}: {phase.uncompleted_task_count()} tasks remaining")
```
