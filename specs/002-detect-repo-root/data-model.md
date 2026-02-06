# Data Model: Repository Root Detection

**Phase**: 1 - Design  
**Date**: February 6, 2026  
**Feature**: [spec.md](spec.md) | [plan.md](plan.md) | [research.md](research.md)

## Overview

This feature introduces repository root detection logic to the existing discovery module. Since this is a CLI tool without persistent storage, the "data model" describes the runtime data structures and flow rather than database entities.

## Core Concepts

### Repository Root (Path)

**Definition**: The topmost directory containing version control markers (`.git`, `.hg`, `.svn`) or a `specs/` folder, representing the project boundary.

**Representation**: `pathlib.Path` object (absolute, resolved path)

**Attributes**:
- Absolute filesystem path
- Resolved (symlinks followed)
- Must exist and be accessible

**Relationships**:
- Contains zero or one `specs/` directory
- Contains zero or one VCS marker (`.git`, `.hg`, `.svn`)
- Parent of current working directory (or is current working directory)

**Validation Rules**:
- Must be a directory (not a file)
- Must be an ancestor of the starting search path
- If multiple candidates exist, select nearest ancestor (closest to start path)

**State Transitions**: N/A (immutable once determined)

---

### Version Control Marker (str)

**Definition**: Specific file or directory name that indicates a repository boundary.

**Representation**: String literal from ordered list

**Values** (priority order):
1. `.git` (Git repository or worktree)
2. `.hg` (Mercurial repository)
3. `.svn` (Subversion repository)

**Attributes**:
- Name: string constant
- Type: Can be file (git worktree) or directory
- Priority: Lower index = higher priority

**Relationships**:
- Located directly within a Repository Root directory
- Used to identify Repository Root candidates

**Validation Rules**:
- Must exist as file or directory (checked via `Path.exists()`)
- Case-sensitive on Unix, case-insensitive on Windows (handled by pathlib)

---

### Discovery Path (Sequence[Path])

**Definition**: The sequence of directories searched from current working directory up to repository root or filesystem root.

**Representation**: Implicit (not stored, generated during traversal)

**Attributes**:
- Start: Current working directory (or provided start path)
- Direction: Upward (child → parent)
- Termination: Repository root found, filesystem root reached, or max depth (10 levels)

**Relationships**:
- Each element is parent of previous element
- Last element is either Repository Root or filesystem root
- Length ≤ max_depth (10) to prevent excessive traversal

**Validation Rules**:
- Each directory in path must be accessible (readable)
- Path must not exceed max depth limit
- Symlinks resolved before traversal begins

**State Transitions**:
```
Initial → Traversing → Found | NotFound | MaxDepthReached
```

---

## Data Flow

### Primary Flow: Successful Detection

```
1. User invokes CLI from subdirectory: /repo/src/sknext/models/
2. CLI calls: find_repository_root(Path.cwd())
3. find_repository_root() attempts git command:
   - subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=Path.cwd())
   - Returns: Path("/repo")
4. CLI calls: discover_latest_tasks_file(Path("/repo"))
5. discover_latest_tasks_file() searches: /repo/specs/###-*/
6. Returns: Path("/repo/specs/002-detect-repo-root/tasks.md")
```

**Data Types**:
- Input: Path (current working directory)
- Intermediate: Path (repository root)
- Output: Path (tasks.md file)

---

### Fallback Flow: Git Not Available

```
1. User invokes CLI from subdirectory: /repo/src/sknext/models/
2. find_repository_root() attempts git command: fails (git not installed)
3. Fallback: find_vcs_root_filesystem() traverses parents:
   - /repo/src/sknext/models/ → no VCS marker
   - /repo/src/sknext/ → no VCS marker
   - /repo/src/ → no VCS marker
   - /repo/ → .git directory found!
4. Returns: Path("/repo")
5. Continues with discover_latest_tasks_file() as in primary flow
```

---

### Fallback Flow: Non-Git Project

```
1. User invokes CLI from subdirectory: /project/deep/nested/dir/
2. find_repository_root() attempts git command: fails
3. find_vcs_root_filesystem() traverses parents: no .git, .hg, or .svn found
4. Fallback: find_specs_root() traverses parents:
   - /project/deep/nested/dir/ → no specs/
   - /project/deep/nested/ → no specs/
   - /project/deep/ → no specs/
   - /project/ → specs/ directory found!
5. Returns: Path("/project")
6. Continues with discover_latest_tasks_file()
```

---

### Error Flow: No Repository Root

```
1. User invokes CLI from home directory: /home/user/
2. find_repository_root() attempts all detection methods
3. After 10 levels or filesystem root: no repository root found
4. Returns: None
5. CLI displays error: "No Git repository or speckit project detected"
6. Exit code: 1
```

---

## Function Signatures (Contracts)

### find_repository_root(start_path: Path) -> Path | None

**Purpose**: Detect repository root from given starting path

**Algorithm**:
1. Try `git rev-parse --show-toplevel` (fast path)
2. If fails, traverse parents looking for VCS markers (.git, .hg, .svn)
3. If fails, traverse parents looking for specs/ directory
4. Return None if nothing found within max depth

**Returns**:
- `Path`: Absolute, resolved path to repository root
- `None`: No repository root detected

**Raises**: No exceptions (returns None on all failures)

---

### find_git_root(start_path: Path) -> Path | None

**Purpose**: Use git command to find repository root (internal helper)

**Implementation**: `subprocess.run(["git", "rev-parse", "--show-toplevel"], ...)`

**Returns**:
- `Path`: Git repository root (handles worktrees correctly)
- `None`: Not in a git repository, git not installed, or command timeout

**Performance**: <10ms typical, 2s timeout

---

### find_vcs_root_filesystem(start_path: Path, max_levels: int = 10) -> Path | None

**Purpose**: Search parent directories for VCS markers (fallback)

**Returns**:
- `Path`: Directory containing .git, .hg, or .svn
- `None`: No VCS marker found within max_levels

**Performance**: <50ms for 10 levels

---

### find_specs_root(start_path: Path, max_levels: int = 10) -> Path | None

**Purpose**: Search parent directories for specs/ folder (final fallback)

**Returns**:
- `Path`: Directory containing specs/ subdirectory
- `None`: No specs/ found within max_levels

**Performance**: <50ms for 10 levels

---

## Error Handling

### Subprocess Errors (Git Command)

| Exception | Meaning | Handling |
|-----------|---------|----------|
| `subprocess.CalledProcessError` | Not in git repository (exit code 128) | Return None, try fallback |
| `FileNotFoundError` | Git not installed | Return None, try fallback |
| `subprocess.TimeoutExpired` | Git command hung (network FS?) | Return None, try fallback |
| `OSError` | Permission denied, I/O error | Return None, try fallback |

**Principle**: Git command failure is non-fatal, always try fallbacks

---

### Filesystem Errors (Traversal)

| Exception | Meaning | Handling |
|-----------|---------|----------|
| `PermissionError` | Cannot read parent directory | Stop traversal, return None |
| `OSError` | I/O error during traversal | Stop traversal, return None |

**Principle**: Filesystem errors are non-fatal, return None and let CLI show user-friendly error

---

## Edge Cases

### Nested Repositories

**Scenario**: Child git repo inside parent git repo

**Behavior**: `git rev-parse --show-toplevel` returns innermost repo (correct per FR-003)

**Example**:
```
/workspace/parent-repo/.git
/workspace/parent-repo/child-repo/.git
Current dir: /workspace/parent-repo/child-repo/src/
Result: /workspace/parent-repo/child-repo/  ✓ (nearest)
```

---

### Git Worktree

**Scenario**: `.git` is a file, not a directory

**Behavior**: `git rev-parse` handles correctly, filesystem fallback treats file as valid marker

**Example**:
```
/main-repo/.git/              (directory)
/worktree-branch/.git         (file pointing to main repo)
Current dir: /worktree-branch/src/
Result: /worktree-branch/  ✓
```

---

### Symbolic Links

**Scenario**: Current directory is accessed via symlink

**Behavior**: `Path.resolve()` called once at start, traverses real path

**Example**:
```
/home/user/project → /opt/projects/myproject  (symlink)
Current dir: /home/user/project/src/
Resolved: /opt/projects/myproject/src/
Search path: /opt/projects/myproject/src/ → /opt/projects/myproject/ → ...
Result: /opt/projects/myproject/  ✓
```

---

### No Repository Root

**Scenario**: User runs from home directory or non-project location

**Behavior**: All detection methods fail, return None

**Error Message**: "No Git repository or speckit project detected within 10 parent directories. Run from a project directory or specify file path explicitly."

---

## Performance Characteristics

### Best Case: Git Repository

- Git command: <10ms
- Total detection time: <10ms
- No filesystem traversal needed

### Typical Case: Non-Git with VCS Marker (3 levels deep)

- Git command fails: ~5ms
- Filesystem traversal: ~15ms (3 directories × ~5ms each)
- Total: ~20ms

### Worst Case: Non-VCS Project (10 levels deep)

- Git command fails: ~5ms
- VCS traversal (10 levels): ~50ms
- Specs traversal (10 levels): ~50ms
- Total: ~105ms

**Meets Performance Goal**: All scenarios <200ms (SC-005) ✓

---

## Backward Compatibility

### Existing Behavior Preserved

**When**: User runs from repository root

**Before**:
```python
discover_latest_tasks_file(Path.cwd())  # Searches ./specs/
```

**After**:
```python
repo_root = find_repository_root(Path.cwd())  # Returns Path.cwd()
discover_latest_tasks_file(repo_root)          # Searches ./specs/ (same!)
```

**Result**: Identical behavior, zero breaking changes (SC-004) ✓

---

### Explicit Path Override

**When**: User provides file path explicitly

**Before**:
```python
sknext /path/to/tasks.md
# Uses provided path directly
```

**After**:
```python
sknext /path/to/tasks.md
# Still uses provided path directly (FR-009)
# Repository root detection not invoked
```

**Result**: Explicit paths bypass auto-detection ✓
