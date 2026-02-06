# Feature Specification: Task Status Viewer

**Feature Branch**: `001-task-status-viewer`  
**Created**: 2026-02-05  
**Status**: Draft  
**Input**: User description: "Create a tool that will read a speckit tasks.md and report the headings and tasks that have not been completed yet with options to allow varying level and number of items to be shown."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Quick Status Check (Priority: P1)

A developer working on a feature wants to quickly see what tasks remain without opening the full tasks.md file. They run the tool and see the next 10 uncompleted tasks with their context (phase and section headings).

**Why this priority**: This is the primary use case and provides immediate value for day-to-day development work. Most developers just need to know "what's next" without overwhelming detail.

**Independent Test**: Can be fully tested by creating a sample tasks.md with mixed completed/uncompleted tasks, running the tool with no arguments, and verifying it shows exactly 10 uncompleted tasks with their hierarchical context.

**Acceptance Scenarios**:

1. **Given** a tasks.md file with 50 tasks (20 completed, 30 uncompleted), **When** developer runs the tool with no arguments, **Then** the tool displays the next 10 uncompleted tasks with their Phase and Section headings
2. **Given** a tasks.md file with only 5 uncompleted tasks, **When** developer runs the tool with no arguments, **Then** the tool displays all 5 tasks (not 10) with their headings
3. **Given** a tasks.md file where all tasks are completed, **When** developer runs the tool, **Then** the tool displays a message indicating all tasks are complete

---

### User Story 2 - Custom Task Count (Priority: P2)

A developer wants to see more or fewer tasks than the default 10. They specify a custom number (e.g., 5, 25, or 100) and the tool shows exactly that many uncompleted tasks.

**Why this priority**: Flexibility in viewing is important for different work contexts (sprint planning might need 25 tasks, quick check might need 3).

**Independent Test**: Can be tested independently by running the tool with various N values and verifying the output count matches the requested number.

**Acceptance Scenarios**:

1. **Given** a tasks.md with 30 uncompleted tasks, **When** developer requests 25 tasks, **Then** tool displays exactly 25 tasks with their headings
2. **Given** a tasks.md with 30 uncompleted tasks, **When** developer requests 3 tasks, **Then** tool displays only 3 tasks with their headings
3. **Given** a tasks.md with 5 uncompleted tasks, **When** developer requests 20 tasks, **Then** tool displays all 5 available tasks (not an error)

---

### User Story 3 - Phase Overview (Priority: P2)

A project manager wants to see which phases still have uncompleted work without being overwhelmed by individual task details. They request a phase-only view showing all uncompleted phases.

**Why this priority**: High-level planning and progress tracking requires phase-level visibility without task noise.

**Independent Test**: Can be tested by creating a tasks.md with multiple phases (some fully complete, some with remaining work) and verifying only phases with uncompleted tasks are shown.

**Acceptance Scenarios**:

1. **Given** a tasks.md with 5 phases (2 fully complete, 3 with uncompleted tasks), **When** developer requests phase-only view, **Then** tool displays only the 3 phases with remaining work
2. **Given** a tasks.md where all phases are complete, **When** developer requests phase-only view, **Then** tool displays a message that all phases are complete
3. **Given** a tasks.md with phases and nested sections, **When** developer requests phase-only view, **Then** tool shows only phase headings (no sections or tasks)

---

### User Story 4 - Phase and Section Overview (Priority: P3)

A team lead wants to see the structure of remaining work at phase and section level without individual task details. They request a phase-and-section view.

**Why this priority**: Useful for sprint planning and understanding work distribution across sections without task-level detail.

**Independent Test**: Can be tested by verifying the tool shows phases and their child sections, but no individual tasks, filtering out completed sections.

**Acceptance Scenarios**:

1. **Given** a tasks.md with phases containing sections (some sections fully complete), **When** developer requests phase-and-section view, **Then** tool displays phases and only sections with uncompleted tasks
2. **Given** a phase with 3 sections (2 complete, 1 incomplete), **When** developer requests phase-and-section view, **Then** tool shows the phase and only the 1 incomplete section

---

### User Story 5 - Combined Phase and Task View (Priority: P3)

A developer wants to see all incomplete phases listed at the top, followed by a limited number of tasks. This helps understand both high-level progress and immediate next steps.

**Why this priority**: Combines strategic overview with tactical next steps, useful for daily standups or status reports.

**Independent Test**: Can be tested by verifying the output contains two distinct sections: all incomplete phases, followed by N tasks.

**Acceptance Scenarios**:

1. **Given** a tasks.md with 4 incomplete phases and 30 uncompleted tasks, **When** developer requests all phases + 10 tasks, **Then** tool displays all 4 phase headings followed by 10 tasks with their context
2. **Given** a tasks.md with 2 incomplete phases and 5 uncompleted tasks, **When** developer requests all phases + 10 tasks, **Then** tool displays 2 phases and 5 tasks (not padded)

---

### User Story 6 - Task-Only View (Priority: P3)

A developer wants to see only task items without any heading context for focused work execution (e.g., for a checklist or copy-paste into a status report).

**Why this priority**: Some workflows need compact, heading-free output for specific use cases like automated processing or minimal display.

**Independent Test**: Can be tested by verifying the output contains only task lines (checkbox + ID + description) with no phase or section headings.

**Acceptance Scenarios**:

1. **Given** a tasks.md with tasks under various phases and sections, **When** developer requests task-only view for 10 tasks, **Then** tool displays only 10 task lines without any headings
2. **Given** a request for all remaining tasks in task-only mode, **When** 50 tasks remain, **Then** tool displays all 50 task lines with no headings

---

### User Story 7 - All Remaining Tasks View (Priority: P4)

A developer preparing for a final sprint or handoff wants to see absolutely all remaining tasks with full context. They request an "all tasks" view.

**Why this priority**: Less frequently needed but critical for comprehensive planning, handoffs, or final push to completion.

**Independent Test**: Can be tested by verifying the tool outputs every single uncompleted task found in the file with full hierarchical context.

**Acceptance Scenarios**:

1. **Given** a tasks.md with 100 uncompleted tasks across multiple phases, **When** developer requests all remaining tasks, **Then** tool displays all 100 tasks with their phase and section headings
2. **Given** a tasks.md with tasks at different nesting levels, **When** developer requests all remaining tasks, **Then** tool preserves and displays the hierarchical structure

---

### Edge Cases

- **File not found or unreadable**: Display clear error message indicating the file path that was attempted and exit with non-zero status code. Suggest checking file path or permissions.
- **Empty file or no tasks**: Display message "No tasks found in [file path]" and exit with status code 0 (not an error condition).
- **Malformed task syntax**: Display error message identifying the line number and nature of the malformation (e.g., "Line 42: Task missing checkbox format") and exit with non-zero status code. Tool operates in strict mode - any malformation causes immediate exit.
- **User requests 0 tasks**: If no remaining tasks exist, display "All tasks complete" message. If remaining tasks exist, display 1 task with humorous message "Showing 1 task (for VERY large values of zero)".
- **Missing or inconsistent phase/section headings**: Display error message indicating the issue (e.g., "Phase heading not in expected format at line 15") and exit with non-zero status code.
- **Non-standard checkbox characters**: Any checkbox with non-whitespace character (e.g., `[x]`, `[X]`, `[~]`, `[>]`) is treated as "completed". Only `[ ]` (with single space) indicates uncompleted.
- **Deeply nested structures**: Maximum nesting depth of 5 levels is enforced (configurable constant MAX_NESTING_DEPTH = 5). When exceeded, display only Phase and immediate parent section for each task, omitting intermediate section levels. No error or warning - graceful degradation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Tool MUST read and parse a speckit-formatted tasks.md file
- **FR-002**: Tool MUST identify task items by their checkbox format (`- [ ]` for uncompleted, `- [x]` for completed)
- **FR-003**: Tool MUST identify Phase headings (markdown `## Phase N:` format)
- **FR-004**: Tool MUST identify Section headings (markdown `### Section Name` or `**Purpose**:` format)
- **FR-005**: Tool MUST associate each task with its parent Section and Phase based on markdown hierarchy
- **FR-006**: Tool MUST filter out completed tasks (those with `[x]` checkbox)
- **FR-007**: Tool MUST provide a default view showing 10 uncompleted tasks with their Phase and Section context
- **FR-008**: Tool MUST accept a command-line parameter to specify custom task count (e.g., `-n 25`, `--count 25`)
- **FR-009**: Tool MUST accept a command-line flag for phase-only view (e.g., `--phases-only`)
- **FR-010**: Tool MUST accept a command-line flag for phase-and-section view (e.g., `--structure`)
- **FR-011**: Tool MUST accept a command-line flag for task-only view with no headings (e.g., `--tasks-only`)
- **FR-012**: Tool MUST accept a flag to show all remaining tasks (e.g., `--all`)
- **FR-013**: Tool MUST accept a combined flag to show all phases plus N tasks (e.g., `--all-phases -n 10`)
- **FR-014**: Tool MUST display tasks in the order they appear in the source file
- **FR-015**: Tool MUST handle missing or malformed task files gracefully with clear error messages
- **FR-016**: Tool MUST output to stdout in a human-readable format
- **FR-017**: Tool MUST preserve task IDs and descriptions in output
- **FR-018**: Tool MUST exit with appropriate status codes (0 for success, non-zero for errors)
- **FR-019**: Tool MUST auto-discover the latest tasks.md file when no file path is provided by finding the highest-numbered directory under specs/ (e.g., specs/042-feature/tasks.md > specs/003-feature/tasks.md)
- **FR-020**: Tool MUST accept an optional file path argument to override auto-discovery (e.g., `tool path/to/tasks.md`)
- **FR-021**: Tool MUST enforce a maximum nesting depth limit (default: 5 levels) defined as a configurable constant MAX_NESTING_DEPTH
- **FR-022**: Tool MUST gracefully handle nesting beyond MAX_NESTING_DEPTH by displaying Phase and immediate parent section only, omitting intermediate levels
- **FR-023**: Tool MUST operate in strict mode - any file format violations (malformed syntax, unexpected structure) cause immediate exit with descriptive error message
- **FR-024**: Tool MUST treat any non-space character in task checkbox as "completed" (e.g., `[x]`, `[X]`, `[~]`, `[>]` all indicate completion)
- **FR-025**: Tool MUST provide line numbers in error messages when reporting file format violations

### Key Entities *(include if feature involves data)*

- **Task**: A single work item with checkbox, ID, optional priority marker, optional story tag, and description
  - Checkbox state: `[ ]` (uncompleted) or `[x]` (completed)
  - Task ID: e.g., `T001`, `T042`
  - Optional priority: `[P]` marker
  - Optional story tag: e.g., `[US1]`, `[US2]`
  - Description: Text describing the work

- **Section**: A grouping of tasks, typically representing a coherent unit of work
  - Section heading: Markdown heading (### level) or **Purpose**: format
  - Contains: Multiple tasks
  - Parent: Phase

- **Phase**: A major stage of the project (e.g., Phase 1: Setup, Phase 2: Foundation)
  - Phase heading: Markdown heading (## level) with "Phase N:" format
  - Contains: Multiple sections
  - Parent: None (top-level)

- **Hierarchy**: The tree structure of Phase → Section → Task

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developer can view next tasks in under 2 seconds without opening the full tasks.md file
- **SC-002**: Tool correctly identifies and displays uncompleted tasks with 100% accuracy for well-formed tasks.md files
- **SC-003**: All 7 viewing modes produce correct output for a comprehensive test tasks.md file
- **SC-004**: Tool reduces time to check task status by 80% compared to manually searching through tasks.md
- **SC-005**: Error messages clearly indicate the problem and suggest corrective action for common issues (file not found, malformed syntax)
- **SC-006**: Tool handles tasks.md files with up to 500 tasks without noticeable delay (< 3 seconds)

## Assumptions

1. **File Format**: Tasks.md files follow the speckit tasks-template.md structure consistently (strict enforcement)
2. **Checkbox Format**: Standard markdown checkbox syntax is used (`- [ ]` for uncompleted, any non-space character for completed)
3. **Heading Format**: Phases use `## Phase N:` format, sections use `###` or `**Purpose**:` format
4. **File Location**: Tool is invoked from repository root where specs/ directory exists, or user provides explicit file path
5. **Directory Structure**: Spec directories follow naming pattern `specs/###-feature-name/` where ### is a zero-padded 3-digit number
6. **Auto-Discovery**: When no file path provided, tool finds latest spec by highest directory number, then looks for tasks.md within
7. **Single File**: The tool operates on a single tasks.md file at a time (no multi-file aggregation)
8. **Text Output**: Plain text output is sufficient; no rich formatting (colors, tables) required initially
9. **Sequential Processing**: Tasks are processed in file order without reordering or grouping by priority/story
10. **Agent-Managed Files**: Files are primarily managed by AI agents, so malformation is treated as a critical error requiring immediate attention

## Out of Scope

- Modifying or updating task completion status
- Integration with version control or issue tracking systems
- Visual/GUI interface (CLI only)
- Task filtering by story tag or priority
- Task analytics (completion rates, velocity, etc.)
- Multi-file processing or aggregation
- Real-time file watching or notifications
- Export to formats other than plain text (JSON, CSV, etc.)
