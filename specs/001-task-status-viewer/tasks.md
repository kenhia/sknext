# Tasks: Task Status Viewer

**Feature**: Task Status Viewer CLI Tool  
**Branch**: `001-task-status-viewer`  
**Input**: Design documents from `/specs/001-task-status-viewer/`

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, etc.)
- Include exact file paths in descriptions

## Path Conventions

This is a single project structure:
- Source code: `src/task_viewer/`
- Tests: `tests/unit/`, `tests/integration/`, `tests/fixtures/`
- Configuration: `pyproject.toml`, `.python-version`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure with src/task_viewer/ and tests/
- [X] T002 Initialize Python project with uv (create pyproject.toml with dependencies: typer, rich, pytest)
- [X] T003 Create .python-version file specifying Python 3.11+
- [X] T004 [P] Configure ruff in pyproject.toml (line length, linting rules, formatting)
- [X] T005 [P] Configure pytest in pyproject.toml (test paths, coverage settings)
- [X] T006 [P] Configure mypy in pyproject.toml (strict mode, type checking)
- [X] T007 Create README.md with installation instructions and basic usage
- [X] T008 Create src/task_viewer/__init__.py with version info

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Write test for constants.py (MAX_NESTING_DEPTH, DEFAULT_TASK_COUNT, regex patterns)
- [X] T010 Create src/task_viewer/constants.py with all constants and regex patterns
- [X] T011 Write tests for Task dataclass in tests/unit/test_models.py (validation, attributes)
- [X] T012 Write tests for Section dataclass in tests/unit/test_models.py (computed properties)
- [X] T013 Write tests for Phase dataclass in tests/unit/test_models.py (has_uncompleted_work)
- [X] T014 Write tests for TasksFile dataclass in tests/unit/test_models.py (get_uncompleted_tasks)
- [X] T015 Write tests for ParseError dataclass in tests/unit/test_models.py
- [X] T016 Create src/task_viewer/models.py with all frozen dataclasses (Task, Section, Phase, TasksFile, ParseError)
- [X] T017 Run tests for models.py and verify all pass
- [X] T018 Create tests/fixtures/sample_tasks.md (well-formed file with 50 tasks, mixed completion)
- [X] T019 [P] Create tests/fixtures/malformed_tasks.md (various syntax errors for error handling tests)
- [X] T020 [P] Create tests/fixtures/nested_tasks.md (deep nesting beyond MAX_NESTING_DEPTH)

---

## Phase 3: User Story 1 - Quick Status Check (P1)

**Goal**: Display next 10 uncompleted tasks with phase/section context (default behavior)

**Independent Test**: Run tool with no args, verify shows exactly 10 tasks with hierarchical context

### Parser Implementation

- [X] T021 [US1] Write test for parsing phase headings in tests/unit/test_parser.py
- [X] T022 [US1] Write test for parsing section headings in tests/unit/test_parser.py
- [X] T023 [US1] Write test for parsing task lines with checkboxes in tests/unit/test_parser.py
- [X] T024 [US1] Write test for task ID extraction and validation in tests/unit/test_parser.py
- [X] T025 [US1] Write test for priority marker [P] detection in tests/unit/test_parser.py
- [X] T026 [US1] Write test for story tag [USX] extraction in tests/unit/test_parser.py
- [X] T027 [US1] Write test for building phase/section/task hierarchy in tests/unit/test_parser.py
- [X] T028 [US1] Create src/task_viewer/parser.py with parse_tasks_file() function (state machine implementation)
- [X] T029 [US1] Implement line-by-line parsing with regex patterns from constants
- [X] T030 [US1] Implement hierarchy building (track current phase/section as we scan)
- [X] T031 [US1] Run parser tests and verify all pass

### Auto-Discovery Implementation

- [X] T032 [P] [US1] Write test for finding specs/ directory in tests/unit/test_discovery.py
- [X] T033 [P] [US1] Write test for extracting numeric prefixes from directory names in tests/unit/test_discovery.py
- [X] T034 [P] [US1] Write test for sorting and selecting highest-numbered directory in tests/unit/test_discovery.py
- [X] T035 [P] [US1] Write test for handling missing specs/ directory in tests/unit/test_discovery.py
- [X] T036 [P] [US1] Create src/task_viewer/discovery.py with discover_latest_tasks_file() function
- [X] T037 [P] [US1] Run discovery tests and verify all pass

### Formatter Implementation (Default View)

- [X] T038 [P] [US1] Write test for formatting phase headings with rich in tests/unit/test_formatter.py
- [X] T039 [P] [US1] Write test for formatting section headings with indentation in tests/unit/test_formatter.py
- [X] T040 [P] [US1] Write test for formatting task lines with proper indentation in tests/unit/test_formatter.py
- [X] T041 [P] [US1] Write test for limiting output to N tasks in tests/unit/test_formatter.py
- [X] T042 [P] [US1] Write test for displaying summary line (Showing X of Y remaining) in tests/unit/test_formatter.py
- [X] T043 [P] [US1] Create src/task_viewer/formatter.py with format_default_view() function
- [X] T044 [P] [US1] Implement rich Console output with colors and formatting
- [X] T045 [P] [US1] Run formatter tests and verify all pass

### CLI Integration

- [X] T046 [US1] Create src/task_viewer/cli.py with typer app and main() function
- [X] T047 [US1] Implement file_path argument (Optional[Path], defaults to None for auto-discovery)
- [X] T048 [US1] Implement count option (-n/--count, default=10)
- [X] T049 [US1] Wire up discovery.discover_latest_tasks_file() when no path provided
- [X] T050 [US1] Wire up parser.parse_tasks_file() to load and parse file
- [X] T051 [US1] Wire up formatter.format_default_view() for output
- [X] T052 [US1] Create src/task_viewer/__main__.py to enable python -m task_viewer execution
- [X] T053 [US1] Write integration test in tests/integration/test_cli.py for default view with sample_tasks.md
- [X] T054 [US1] Write integration test for auto-discovery behavior
- [X] T055 [US1] Run integration tests and verify CLI works end-to-end

---

## Phase 4: User Story 2 - Custom Task Count (P2)

**Goal**: Allow users to specify custom number of tasks to display

**Independent Test**: Run with -n 5, -n 25, -n 100 and verify output matches count

- [X] T056 [US2] Write test for count parameter validation in tests/unit/test_cli.py
- [X] T057 [US2] Write test for handling count > available tasks in tests/unit/test_formatter.py
- [X] T058 [US2] Write test for zero tasks edge case (VERY large values of zero) in tests/unit/test_formatter.py
- [X] T059 [US2] Update formatter.format_default_view() to use custom count parameter
- [X] T060 [US2] Implement zero tasks special case with humorous message
- [X] T061 [US2] Write integration test for custom count (n=3, n=25) in tests/integration/test_cli.py
- [X] T062 [US2] Write integration test for n=0 edge case in tests/integration/test_cli.py
- [X] T063 [US2] Run tests and verify custom count works correctly

---

## Phase 5: User Story 3 - Phase Overview (P2)

**Goal**: Show only phases with uncompleted work (no sections or tasks)

**Independent Test**: Run with --phases-only, verify only phase headings displayed

- [X] T064 [US3] Write test for --phases-only flag in tests/unit/test_cli.py
- [X] T065 [US3] Write test for format_phases_only() function in tests/unit/test_formatter.py
- [X] T066 [US3] Write test for filtering phases with uncompleted work in tests/unit/test_formatter.py
- [X] T067 [US3] Write test for "all phases complete" message in tests/unit/test_formatter.py
- [X] T068 [US3] Create format_phases_only() function in src/task_viewer/formatter.py
- [X] T069 [US3] Implement filtering using Phase.has_uncompleted_work() method
- [X] T070 [US3] Add --phases-only flag to CLI in src/task_viewer/cli.py
- [X] T071 [US3] Wire up format_phases_only() when flag is set
- [X] T072 [US3] Write integration test for --phases-only in tests/integration/test_cli.py
- [X] T073 [US3] Run tests and verify phases-only view works correctly

---

## Phase 6: User Story 4 - Phase and Section Overview (P3)

**Goal**: Show phases and sections with uncompleted work (no individual tasks)

**Independent Test**: Run with --structure, verify phases and sections displayed without tasks

- [X] T074 [US4] Write test for --structure flag in tests/unit/test_cli.py
- [X] T075 [US4] Write test for format_structure_view() function in tests/unit/test_formatter.py
- [X] T076 [US4] Write test for filtering sections with uncompleted tasks in tests/unit/test_formatter.py
- [X] T077 [US4] Create format_structure_view() function in src/task_viewer/formatter.py
- [X] T078 [US4] Implement section filtering using Section.has_uncompleted_tasks() method
- [X] T079 [US4] Add --structure flag to CLI in src/task_viewer/cli.py
- [X] T080 [US4] Wire up format_structure_view() when flag is set
- [X] T081 [US4] Write integration test for --structure in tests/integration/test_cli.py
- [X] T082 [US4] Run tests and verify structure view works correctly

---

## Phase 7: User Story 5 - Combined Phase and Task View (P3)

**Goal**: Show all incomplete phases followed by N tasks

**Independent Test**: Run with --all-phases -n 10, verify two distinct sections in output

- [X] T083 [US5] Write test for --all-phases flag in tests/unit/test_cli.py
- [X] T084 [US5] Write test for format_combined_view() function in tests/unit/test_formatter.py
- [X] T085 [US5] Write test for two-section output (phases then tasks) in tests/unit/test_formatter.py
- [X] T086 [US5] Create format_combined_view() function in src/task_viewer/formatter.py
- [X] T087 [US5] Implement phase list section with separator
- [X] T088 [US5] Implement task list section with count limit
- [X] T089 [US5] Add --all-phases flag to CLI in src/task_viewer/cli.py
- [X] T090 [US5] Wire up format_combined_view() when flag is set
- [X] T091 [US5] Write integration test for --all-phases in tests/integration/test_cli.py
- [X] T092 [US5] Run tests and verify combined view works correctly

---

## Phase 8: User Story 6 - Task-Only View (P3)

**Goal**: Show only task lines without any heading context

**Independent Test**: Run with --tasks-only -n 10, verify only task lines in output (no headings)

- [X] T093 [US6] Write test for --tasks-only flag in tests/unit/test_cli.py
- [X] T094 [US6] Write test for format_tasks_only() function in tests/unit/test_formatter.py
- [X] T095 [US6] Write test for task-only output format (no phase/section headings) in tests/unit/test_formatter.py
- [X] T096 [US6] Create format_tasks_only() function in src/task_viewer/formatter.py
- [X] T097 [US6] Implement task line output without hierarchy context
- [X] T098 [US6] Add --tasks-only flag to CLI in src/task_viewer/cli.py
- [X] T099 [US6] Wire up format_tasks_only() when flag is set
- [X] T100 [US6] Write integration test for --tasks-only in tests/integration/test_cli.py
- [X] T101 [US6] Run tests and verify tasks-only view works correctly

---

## Phase 9: User Story 7 - All Remaining Tasks View (P4)

**Goal**: Show absolutely all uncompleted tasks with full context

**Independent Test**: Run with --all, verify every uncompleted task is displayed

- [X] T102 [US7] Write test for --all flag in tests/unit/test_cli.py
- [X] T103 [US7] Write test for format_all_tasks() function in tests/unit/test_formatter.py
- [X] T104 [US7] Write test for no task count limit in tests/unit/test_formatter.py
- [X] T105 [US7] Create format_all_tasks() function in src/task_viewer/formatter.py (reuse default view logic with no limit)
- [X] T106 [US7] Add --all flag to CLI in src/task_viewer/cli.py
- [X] T107 [US7] Wire up format_all_tasks() when flag is set
- [X] T108 [US7] Write integration test for --all with large fixture in tests/integration/test_cli.py
- [X] T109 [US7] Run tests and verify all-tasks view works correctly

---

## Phase 10: Error Handling & Edge Cases

**Purpose**: Strict mode error handling with clear messages

- [X] T110 Write test for file not found error in tests/integration/test_cli.py
- [X] T111 Write test for unreadable file error in tests/integration/test_cli.py
- [X] T112 Write test for empty file handling in tests/integration/test_cli.py
- [X] T113 Write test for malformed task syntax detection in tests/unit/test_parser.py
- [X] T114 Write test for malformed phase heading detection in tests/unit/test_parser.py
- [X] T115 Write test for orphaned tasks (no section) detection in tests/unit/test_parser.py
- [X] T116 Write test for orphaned sections (no phase) detection in tests/unit/test_parser.py
- [X] T117 Implement strict mode parsing with ParseError collection in src/task_viewer/parser.py
- [X] T118 Implement error message formatting with line numbers in src/task_viewer/formatter.py
- [X] T119 Implement exit code handling (0=success, 1=not found, 2=parse error, 3=invalid args)
- [X] T120 Write test for non-standard checkbox handling ([x], [X], [~] = complete) in tests/unit/test_parser.py
- [X] T121 Implement non-space checkbox character detection in src/task_viewer/parser.py
- [X] T122 Write test for deep nesting graceful degradation in tests/unit/test_formatter.py
- [X] T123 Implement MAX_NESTING_DEPTH enforcement in src/task_viewer/formatter.py
- [X] T124 Write test for conflicting flags error in tests/integration/test_cli.py
- [X] T125 Implement mutually exclusive flag validation in src/task_viewer/cli.py
- [X] T126 Run all error handling tests and verify strict mode works correctly

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, final integration, and quality assurance

### Documentation

- [X] T127 [P] Update README.md with complete installation instructions
- [X] T128 [P] Add usage examples to README.md for all viewing modes
- [X] T129 [P] Add troubleshooting section to README.md
- [X] T130 [P] Create docstrings for all public functions in parser.py
- [X] T131 [P] Create docstrings for all public functions in formatter.py
- [X] T132 [P] Create docstrings for all public functions in discovery.py
- [X] T133 [P] Create docstrings for CLI main() function with examples

### Integration & Testing

- [X] T134 Write integration test for end-to-end workflow with all flags in tests/integration/test_cli.py
- [X] T135 Write performance test for 500-task file (must complete in <3 seconds) in tests/integration/test_cli.py
- [X] T136 Run full test suite with coverage report (target >90%)
- [X] T137 Run mypy type checking on all source files
- [X] T138 Run ruff format and ruff check on all files
- [X] T139 Fix any remaining type errors or linting issues

### Validation

- [X] T140 Test tool with actual speckit tasks.md files from other projects
- [X] T141 Validate all 7 viewing modes produce correct output
- [X] T142 Validate error messages are clear and actionable
- [X] T143 Validate performance meets requirements (<2s default, <3s for 500 tasks)
- [X] T144 Create pyproject.toml scripts section for sknext command entry point

### Pre-Commit Validation

- [X] T145 Run `uv run ruff format .`
- [X] T146 Run `uv run ruff check --fix .`
- [X] T147 Run `uv run pytest` (all tests must pass)
- [X] T148 Verify constitution compliance (all 5 principles satisfied)

---

## Dependencies

### Critical Path (Must Complete in Order)

1. **Phase 1: Setup** → Phase 2 (need project structure and dependencies)
2. **Phase 2: Foundation** → Phase 3 (need models and constants before parser)
3. **Phase 3: US1** → Phases 4-9 (other user stories build on US1's core functionality)

### Story Independence (Can Implement in Parallel After US1)

- **US2 (Custom Count)**: Extends US1's formatter
- **US3 (Phases Only)**: Independent formatter mode
- **US4 (Structure)**: Independent formatter mode
- **US5 (Combined)**: Uses US3's phase filtering + US1's task display
- **US6 (Tasks Only)**: Independent formatter mode
- **US7 (All Tasks)**: Reuses US1's formatter with no limit

### Dependency Graph

```
Setup (P1) → Foundation (P2) → US1 (P3) → US2, US3, US4, US6, US7 (parallel)
                                        → US5 (depends on US3 concepts)
                                        → Error Handling (P10)
                                        → Polish (P11)
```

---

## Parallel Execution Examples

### Within Phase 2 (Foundation)
- T018 (sample_tasks.md), T019 (malformed_tasks.md), T020 (nested_tasks.md) can be created in parallel

### Within Phase 3 (US1)
- T032-T037 (discovery tests + implementation) can run parallel to T021-T031 (parser)
- T038-T045 (formatter tests + implementation) can run parallel to both

### Across User Stories (After US1 Complete)
- US2, US3, US4, US6, US7 can all be implemented in parallel
- US5 should wait until US3 is complete (uses phase filtering concepts)

---

## Implementation Strategy

### MVP (Minimum Viable Product)
**Focus**: User Story 1 only (Quick Status Check)
- Completes Phases 1, 2, and 3
- Delivers core value: view next 10 tasks
- 55 tasks total

### Incremental Delivery
1. **MVP**: US1 (55 tasks) - Core default view
2. **Iteration 1**: US2 + US3 (24 tasks) - Flexibility (custom count, phase overview)
3. **Iteration 2**: US4 + US6 (18 tasks) - Alternative views (structure, tasks-only)
4. **Iteration 3**: US5 + US7 (16 tasks) - Advanced views (combined, all)
5. **Iteration 4**: Error Handling (17 tasks) - Robustness
6. **Final**: Polish (22 tasks) - Documentation and quality

**Total**: 152 tasks
