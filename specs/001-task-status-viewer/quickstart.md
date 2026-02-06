# Quickstart: Task Status Viewer

**Phase**: 1 - Design  
**Date**: 2026-02-05

## Installation

### Prerequisites

- Python 3.11 or higher
- `uv` package manager ([installation guide](https://github.com/astral-sh/uv))

### Install with uv

```bash
cd /path/to/sknext
uv pip install -e .
```

This installs the `sknext` command globally.

---

## Basic Usage

### Default View (Next 10 Tasks)

```bash
sknext
```

**What it does**:
- Auto-discovers the latest `tasks.md` from `specs/###-*/`
- Shows next 10 uncompleted tasks with phase/section context
- Uses rich formatting (colors, bold, indentation)

**Example Output**:
```
## Phase 1: Setup
  ### Setup (Shared Infrastructure)
    - [ ] T001 Create project structure per implementation plan
    - [ ] T002 Initialize Python project with uv dependencies
    - [ ] T003 [P] Configure linting and formatting tools

## Phase 2: Foundation (US1)
  ### Core Models
    - [ ] T015 [P] [US1] Create Task dataclass with validation
    ...

Showing 10 of 47 remaining tasks
```

---

## Common Scenarios

### Show More/Fewer Tasks

```bash
# Show next 3 tasks
sknext -n 3

# Show next 25 tasks
sknext --count 25
```

---

### High-Level Project Overview

```bash
# See which phases have remaining work
sknext --phases-only
```

**Output**:
```
## Phase 1: Setup
## Phase 2: Foundation (US1)
## Phase 4: Feature Implementation
```

---

### See Project Structure

```bash
# Show phases and sections (no individual tasks)
sknext --structure
```

**Output**:
```
## Phase 1: Setup
  ### Setup (Shared Infrastructure)
  ### Configuration

## Phase 2: Foundation (US1)
  ### Core Models
  ### Database Schema
```

---

### Compact Task List (No Headings)

```bash
# Get just the task lines for copy/paste
sknext --tasks-only -n 5
```

**Output**:
```
- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize Python project with uv dependencies
- [ ] T003 [P] Configure linting and formatting tools
- [ ] T004 Setup pytest configuration
- [ ] T005 Create base data models
```

---

### Complete Task Inventory

```bash
# See ALL remaining tasks
sknext --all
```

Use this for:
- Final sprint planning
- Handoff documentation
- Comprehensive status reports

---

### Strategic + Tactical View

```bash
# Show all incomplete phases + next 15 tasks
sknext --all-phases -n 15
```

**Output**:
```
=== Phases with Remaining Work ===
## Phase 1: Setup
## Phase 2: Foundation (US1)
## Phase 4: Feature Implementation

=== Next 15 Tasks ===
## Phase 1: Setup
  ### Setup (Shared Infrastructure)
    - [ ] T001 Create project structure per implementation plan
    ...
```

---

### Specify Explicit File

```bash
# Use a specific tasks.md file
sknext specs/042-other-feature/tasks.md

# Absolute path
sknext /home/user/project/specs/001-feature/tasks.md
```

---

## Development Workflows

### Daily Standup

```bash
# Quick check: what's next?
sknext -n 5
```

### Sprint Planning

```bash
# See all phases and next 50 tasks
sknext --all-phases -n 50
```

### Status Report Generation

```bash
# Export task-only view to file
sknext --tasks-only -n 20 > status.txt

# Export full context view
sknext -n 30 > weekly-status.md
```

### Project Health Check

```bash
# How many phases have work left?
sknext --phases-only

# How is work distributed across sections?
sknext --structure
```

---

## Understanding the Output

### Formatting Key

| Element | Format | Example |
|---------|--------|---------|
| Phase | Bold blue `##` | `## Phase 1: Setup` |
| Section | Green `###`, 2-space indent | `  ### Core Models` |
| Task | White text, 4-space indent | `    - [ ] T001 Description` |
| Priority | Yellow `[P]` | `- [ ] T003 [P] Configure tools` |
| Story Tag | Cyan `[US1]` | `- [ ] T015 [US1] Create model` |
| Summary | Gray italic | `Showing 10 of 47 remaining tasks` |

### Task Status Indicators

- `[ ]` - Uncompleted (space in checkbox)
- `[x]` - Completed (will NOT be shown by tool)
- `[X]` - Completed (uppercase also treated as complete)
- `[~]`, `[>]`, etc. - Completed (any non-space = complete)

---

## Error Handling

### File Not Found

If `tasks.md` doesn't exist:
```
Error: tasks.md file not found
Attempted path: specs/001-task-status-viewer/tasks.md

Suggestions:
  - Check that the file exists
  - Provide explicit path: sknext path/to/tasks.md
  - Verify you're running from repository root
```

**Solution**: Run from repo root or provide explicit path

---

### Malformed File

If file has syntax errors:
```
Error: Malformed task syntax at line 67
Line 67: - [] T042 Missing space in checkbox

Expected format: - [ ] TXXX [P] [USX] Description
```

**Solution**: Fix the syntax error in tasks.md (usually an agent issue)

---

### All Tasks Complete

If no uncompleted tasks:
```
✓ All tasks complete!
File: specs/001-task-status-viewer/tasks.md
Total tasks: 42 (all completed)
```

This is success, not an error!

---

## Advanced Tips

### Zero Tasks (Easter Egg)

```bash
sknext -n 0
```

If tasks exist, shows 1 task with message:
```
Showing 0 tasks (for VERY large values of zero)
```

### Piping to Other Tools

```bash
# Count uncompleted tasks
sknext --tasks-only --all | wc -l

# Search for specific task
sknext --all | grep "authentication"

# Filter by priority
sknext --tasks-only --all | grep "\[P\]"

# Filter by story
sknext --all | grep "\[US1\]"
```

### Combining with Git

```bash
# Check tasks before committing
git diff --name-only | grep tasks.md && sknext -n 5

# Add task count to commit message
TASKS=$(sknext --tasks-only --all | wc -l)
git commit -m "Progress update: $TASKS tasks remaining"
```

---

## Help & Version

```bash
# Show help
sknext --help

# Show version
sknext --version
```

---

## Performance

- Default view (<10 tasks): ~0.5 seconds
- Large file (500 tasks): <3 seconds
- All tasks with full context: <5 seconds

Performance is primarily I/O-bound (reading file).

---

## Next Steps

After installation:

1. **Try default view**: `sknext`
2. **Explore modes**: Try `--phases-only`, `--structure`, `--tasks-only`
3. **Adjust count**: Experiment with `-n 5`, `-n 25`, `--all`
4. **Integrate**: Add to daily workflow (standup, status reports)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Command not found | Run `uv pip install -e .` from repo root |
| Permission denied | Check file permissions on tasks.md |
| Wrong spec directory | Provide explicit path with FILE_PATH argument |
| Unexpected output | Verify tasks.md follows speckit format |
| Python version error | Ensure Python 3.11+ is installed |

---

## Getting Help

```bash
# Built-in help
sknext --help

# Check version
sknext --version

# Test with sample file
sknext specs/001-task-status-viewer/tasks.md
```

For issues, check:
1. File exists and is readable
2. Running from repository root
3. File follows speckit tasks.md format
4. Python 3.11+ is active
