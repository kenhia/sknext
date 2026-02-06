# Implementation Plan: Task Status Viewer

**Branch**: `001-task-status-viewer` | **Date**: 2026-02-05 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-task-status-viewer/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a CLI tool that reads speckit tasks.md files and displays uncompleted tasks with flexible viewing options. The tool will auto-discover the latest tasks.md from the specs/ directory structure, parse markdown to extract phases/sections/tasks, and offer 7 different viewing modes (default 10 tasks, custom count, phase-only, structure-only, combined, task-only, all). Uses Python with uv for dependency management, typer for CLI argument parsing, and rich for enhanced terminal output formatting. Operates in strict mode with immediate failure on malformed input.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: typer (CLI), rich (terminal output), pytest (testing)  
**Storage**: N/A (read-only file parsing)  
**Testing**: pytest with coverage for unit tests, integration tests for end-to-end CLI behavior  
**Target Platform**: Linux/macOS/Windows (cross-platform CLI tool)  
**Project Type**: single (standalone CLI tool)  
**Performance Goals**: <2 seconds for default view, <3 seconds for files with 500 tasks  
**Constraints**: Strict parsing mode (fail on malformation), MAX_NESTING_DEPTH=5 constant, must handle zero-padded 3-digit spec directories  
**Scale/Scope**: Process tasks.md files up to 500 tasks, support 7 viewing modes, auto-discover from specs/###-*/ directories

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Code Quality & Standards
✅ **PASS** - Will use type hints, docstrings, ruff for linting/formatting, modular design

### II. Test-Driven Development (TDD)
✅ **PASS** - TDD workflow: write tests for parser → CLI → viewing modes → then implement

### III. User Experience Consistency
✅ **PASS** - CLI follows standard conventions, clear error messages with line numbers, consistent flag naming

### IV. Performance & Optimization
✅ **PASS** - Performance requirements defined: <2s default, <3s for 500 tasks; will measure during testing

### V. Pre-Commit Validation (MANDATORY)
✅ **PASS** - Will configure: `uv run ruff format .`, `uv run ruff check --fix .`, `uv run pytest`

**Gate Status**: ✅ ALL CHECKS PASSED - Proceeding to Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── task_viewer/
│   ├── __init__.py
│   ├── __main__.py          # Entry point for `python -m task_viewer`
│   ├── cli.py               # Typer CLI interface
│   ├── parser.py            # Markdown parsing logic
│   ├── models.py            # Task, Section, Phase data classes
│   ├── discovery.py         # Auto-discovery of latest tasks.md
│   ├── formatter.py         # Rich output formatting
│   └── constants.py         # MAX_NESTING_DEPTH and other constants

tests/
├── unit/
│   ├── test_parser.py       # Parser unit tests
│   ├── test_discovery.py    # Auto-discovery unit tests
│   ├── test_models.py       # Data model tests
│   └── test_formatter.py    # Formatter unit tests
├── integration/
│   └── test_cli.py          # End-to-end CLI tests
└── fixtures/
    ├── sample_tasks.md      # Well-formed test file
    ├── malformed_tasks.md   # Test error handling
    └── nested_tasks.md      # Deep nesting test

pyproject.toml               # uv project config, dependencies, ruff settings
README.md                    # Installation and usage instructions
.python-version              # Python version specification (3.11+)
```

**Structure Decision**: Single project structure selected. This is a standalone CLI tool with no backend/frontend separation needed. All logic lives in `src/task_viewer/` as a Python package that can be invoked via `python -m task_viewer` or installed as a command-line tool.

---

## Phase 0: Research & Technology Selection

**Status**: ✅ COMPLETE

**Deliverables**:
- [research.md](research.md) - Technology decisions and design patterns

**Key Decisions**:
1. Line-by-line regex parsing (no full markdown AST needed)
2. Auto-discovery via numeric directory sorting
3. Typer + rich for CLI with excellent UX
4. Depth cap at MAX_NESTING_DEPTH=5 with graceful degradation
5. Strict error handling (fail fast with line numbers)
6. TDD approach: unit tests + integration tests with fixtures

---

## Phase 1: Design & Contracts

**Status**: ✅ COMPLETE

**Deliverables**:
- [data-model.md](data-model.md) - Immutable dataclasses for Task, Section, Phase, TasksFile
- [contracts/cli.md](contracts/cli.md) - Complete CLI interface specification
- [quickstart.md](quickstart.md) - Installation and usage guide
- [.github/agents/copilot-instructions.md](../../.github/agents/copilot-instructions.md) - Updated agent context

**Architecture Decisions**:
1. **Data Model**: Frozen dataclasses (Task, Section, Phase, TasksFile, ParseError)
2. **Parsing**: State machine tracking current phase/section during line scan
3. **CLI Interface**: 7 viewing modes with typer options (phases-only, structure, tasks-only, etc.)
4. **Output**: Rich console with conditional formatting based on view mode
5. **Error Handling**: ParseError collection with strict mode enforcement

---

## Post-Design Constitution Check

*Re-evaluation after Phase 1 design completion*

### I. Code Quality & Standards
✅ **PASS** - Architecture uses dataclasses with type hints, modular separation (parser, models, CLI, formatter), comprehensive docstrings planned

### II. Test-Driven Development (TDD)
✅ **PASS** - Test strategy defined: unit tests per module, integration tests for CLI, fixture files for various scenarios, >90% coverage target

### III. User Experience Consistency
✅ **PASS** - CLI contract specifies consistent flag naming, rich formatted output, clear error messages with line numbers and suggestions, helpful examples in quickstart

### IV. Performance & Optimization
✅ **PASS** - Performance targets reaffirmed (<2s default, <3s for 500 tasks), data model uses immutable structures (no mutation overhead), parser is single-pass

### V. Pre-Commit Validation (MANDATORY)
✅ **PASS** - Technology stack selected: uv (deps), ruff (format + lint), pytest (tests), mypy (type check)

**Final Gate Status**: ✅ ALL CHECKS PASSED - Ready for Phase 2 (Implementation Planning via `/speckit.tasks`)

---

## Next Steps

Run `/speckit.tasks` to generate [tasks.md](tasks.md) with:
- Phase 1: Setup (project initialization, uv configuration, pytest setup)
- Phase 2: Foundation (data models, constants, parser logic)
- Phase 3: CLI Implementation (typer interface, discovery, formatter)
- Phase 4: Testing (unit tests, integration tests, fixtures)
- Phase 5: Polish (documentation, error messages, performance validation)

Each user story from spec.md will map to independently testable task groups.

