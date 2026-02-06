# Feature Specification: Repository Root Detection

**Feature Branch**: `002-detect-repo-root`  
**Created**: February 6, 2026  
**Status**: Draft  
**Input**: User description: "Enhance sknext to better detect location of the tasks.md by attempting to located the repository root"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run from Subdirectory (Priority: P1)

A developer working deep in a project subdirectory (e.g., `src/sknext/models/`) runs `sknext` without providing a file path, expecting the tool to automatically find the repository's tasks.md file by searching upward through parent directories until it locates the repository root (identified by `.git` directory or similar markers).

**Why this priority**: Core value proposition - users shouldn't need to navigate to the project root or provide explicit paths. This is the primary pain point being addressed.

**Independent Test**: Can be fully tested by running `sknext` from any subdirectory within a git repository and verifying it locates the correct tasks.md file, delivering immediate value without any other enhancements.

**Acceptance Scenarios**:

1. **Given** a developer is in `<repo>/src/sknext/models/`, **When** they run `sknext`, **Then** the tool finds `<repo>/specs/###-*/tasks.md` successfully
2. **Given** a developer is in `<repo>/tests/unit/`, **When** they run `sknext`, **Then** the tool displays tasks from the correct project repository
3. **Given** a developer is in the repository root, **When** they run `sknext`, **Then** behavior remains unchanged from current implementation

---

### User Story 2 - Multi-Repository Workspace (Priority: P2)

A developer working in a monorepo or multi-project workspace with nested git repositories runs `sknext` and expects it to find the tasks.md file for the most immediate repository (closest parent with `.git` directory), not a distant ancestor.

**Why this priority**: Critical for developers working in complex workspace structures, prevents confusion about which project's tasks are being displayed.

**Independent Test**: Can be tested independently by creating nested repository structures and verifying correct repository root detection, useful for monorepo users even if P1 isn't implemented.

**Acceptance Scenarios**:

1. **Given** nested repos at `/workspace/parent-repo/` and `/workspace/parent-repo/child-repo/`, **When** running `sknext` from `/workspace/parent-repo/child-repo/src/`, **Then** the tool finds tasks.md in `/workspace/parent-repo/child-repo/specs/`
2. **Given** a workspace with multiple sibling repositories, **When** running `sknext` from any repo, **Then** it only searches within that repository's boundaries

---

### User Story 3 - Non-Git Projects (Priority: P3)

A developer working in a non-git project (or before git init) runs `sknext` and expects reasonable fallback behavior that searches parent directories for a `specs/` directory up to a reasonable limit or filesystem root.

**Why this priority**: Ensures tool remains usable in all development scenarios, not just git-based projects. Lower priority since most speckit projects use git.

**Independent Test**: Can be tested independently by running in directories without .git, verifying graceful fallback to alternative root detection methods.

**Acceptance Scenarios**:

1. **Given** a project without git initialization, **When** running `sknext` from a subdirectory, **Then** the tool searches parent directories for `specs/` folder up to filesystem root or 10 levels
2. **Given** no `specs/` directory found in any parent, **When** running `sknext`, **Then** tool displays clear error message indicating no speckit project detected

---

### Edge Cases

- What happens when running `sknext` from a directory outside any repository (e.g., home directory)?
- How does the system handle symbolic links when traversing to find repository root?
- What happens when `.git` exists but is a file (git worktree) rather than a directory?
- How does the tool behave if user has read permissions to current directory but not parent directories?
- What happens when multiple specs/ directories exist at different levels of the directory tree?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect repository root by searching parent directories for version control markers (`.git`, `.hg`, `.svn`)
- **FR-002**: System MUST search for `specs/` directory starting from detected repository root, falling back to current working directory behavior if repo root detection fails
- **FR-003**: System MUST prioritize the nearest repository root when nested repositories are encountered (closest parent directory with version control markers)
- **FR-004**: System MUST fallback to searching parent directories for `specs/` folder when no version control markers are found, up to a maximum of 10 parent levels or filesystem root
- **FR-005**: System MUST preserve current working directory after repository root detection (no side effects on execution environment)
- **FR-006**: System MUST provide clear error messages distinguishing between "repository root found but no specs/" and "no repository root detected"
- **FR-007**: System MUST handle symbolic links by resolving them before traversing parent directories
- **FR-008**: System MUST treat `.git` files (git worktrees) as valid repository markers, not just `.git` directories
- **FR-009**: Users MUST be able to override automatic detection by providing explicit file path (current behavior preserved)
- **FR-010**: System MUST maintain backward compatibility with current behavior when run from repository root directory

### Key Entities

- **Repository Root**: The topmost directory containing version control markers (`.git`, `.hg`, `.svn`) or a `specs/` folder, represents the project boundary for task discovery
- **Version Control Marker**: Specific files or directories (`.git`, `.hg`, `.svn`) that indicate repository boundaries, ordered by priority
- **Discovery Path**: The sequence of directories searched from current working directory up to repository root or filesystem root, determines task file location

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can run `sknext` successfully from any subdirectory within a repository and receive correct tasks.md content within 2 seconds
- **SC-002**: Tool correctly identifies repository root in 100% of standard git repository structures (includes worktrees and submodules)
- **SC-003**: In nested repository scenarios, tool selects the closest repository root in 100% of cases
- **SC-004**: Users experience zero breaking changes when running `sknext` from repository root (100% backward compatibility)
- **SC-005**: Discovery overhead adds less than 200ms to execution time when searching from deep subdirectories (5+ levels)
