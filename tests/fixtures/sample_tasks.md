# Tasks: Sample Feature

**Feature**: Sample Feature for Testing
**Branch**: `001-sample`

## Format: `- [ ] [ID] [P?] [Story?] Description`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure with src/ and tests/
- [X] T002 Initialize project with package manager
- [X] T003 Create configuration files
- [ ] T004 [P] Configure linting tools
- [ ] T005 [P] Configure testing framework
- [ ] T006 Write initial documentation

---

## Phase 2: Foundation (Core Components)

**Purpose**: Build core infrastructure

### Data Models

- [X] T007 Define Task entity with validation
- [ ] T008 Define Section entity with computed properties
- [ ] T009 Define Phase entity with aggregation methods
- [ ] T010 [P] [US1] Write unit tests for models

### Parser Implementation

- [ ] T011 Implement line-by-line parser
- [ ] T012 [US1] Add phase heading detection
- [ ] T013 [US1] Add section heading detection
- [ ] T014 [US1] Add task line parsing
- [ ] T015 [P] Handle parse errors gracefully

---

## Phase 3: User Features

**Purpose**: Implement user-facing functionality

### CLI Interface

- [ ] T016 [US1] Create basic CLI with typer
- [ ] T017 [US1] Add file path argument
- [ ] T018 [US2] Add count option (-n)
- [ ] T019 [US3] Add phases-only flag
- [ ] T020 [P] Add help documentation

### Output Formatting

- [ ] T021 [US1] Implement default view formatter
- [ ] T022 [US1] Add rich console output
- [ ] T023 [US2] Handle custom task counts
- [ ] T024 [US3] Implement phase-only view
- [ ] T025 [P] Add color coding for priorities

---

## Phase 4: Advanced Features

**Purpose**: Additional viewing modes and optimizations

### Alternative Views

- [ ] T026 [US4] Implement structure view (--structure)
- [ ] T027 [US5] Implement combined view (--all-phases)
- [ ] T028 [US6] Implement task-only view (--tasks-only)
- [ ] T029 [US7] Implement all-tasks view (--all)
- [ ] T030 [P] Add filtering options

### Discovery and Auto-detection

- [ ] T031 Find specs/ directory automatically
- [ ] T032 Extract numeric prefixes from directories
- [ ] T033 Sort and select highest-numbered spec
- [ ] T034 Handle missing specs/ gracefully
- [ ] T035 [P] Cache discovery results

---

## Phase 5: Error Handling & Polish

**Purpose**: Robustness and user experience improvements

### Error Handling

- [ ] T036 Implement strict mode parsing
- [ ] T037 Add detailed error messages with line numbers
- [ ] T038 Handle malformed task syntax
- [ ] T039 Handle orphaned tasks and sections
- [ ] T040 [P] Add validation for deep nesting

### Testing & Documentation

- [ ] T041 Write integration tests for all views
- [ ] T042 Write performance tests
- [ ] T043 [P] Add docstrings to all functions
- [ ] T044 [P] Update README with examples
- [ ] T045 Create user guide

### Final Validation

- [ ] T046 Run full test suite with coverage
- [ ] T047 Run type checking with mypy
- [ ] T048 Run linting and formatting
- [ ] T049 Test with real-world tasks.md files
- [ ] T050 [P] Measure and optimize performance
