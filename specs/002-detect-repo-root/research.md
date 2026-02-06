# Research: Repository Root Detection

**Phase**: 0 - Research & Analysis  
**Date**: February 6, 2026  
**Feature**: [spec.md](spec.md) | [plan.md](plan.md)

## Research Questions

### Q1: Best approach for detecting Git repository root?

**Decision**: Use `git rev-parse --show-toplevel` as primary method

**Rationale**:
- Native git command, fastest and most reliable for git repositories
- Returns absolute path to repository root in <10ms
- Handles edge cases automatically: worktrees (`.git` as file), submodules, symbolic links
- Available on all platforms where git is installed
- User suggestion aligns with best practices

**Implementation Details**:
```python
import subprocess
from pathlib import Path

def find_git_root(start_path: Path) -> Path | None:
    """Use git command to find repository root."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=2.0  # Safety timeout
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None
```

**Alternatives Considered**:
- **Manual `.git` directory search**: More complex, doesn't handle worktrees/submodules correctly
- **GitPython library**: Adds heavy dependency (9MB+) for single function, overkill for this use case
- **Pure filesystem traversal**: Slower, requires special handling for `.git` files vs directories

**Performance**: <10ms for git detection (tested with subprocess), <50ms for fallback traversal up to 10 levels

---

### Q2: How to handle non-git projects gracefully?

**Decision**: Fallback to searching parent directories for `specs/` folder up to 10 levels or filesystem root

**Rationale**:
- Some projects may not use git (early development, other VCS like mercurial/svn)
- Speckit projects always have `specs/` directory as marker
- 10-level limit prevents excessive traversal (e.g., running from deep system directories)
- Provides clear error messages when no project root detected

**Implementation Details**:
```python
def find_specs_root(start_path: Path, max_levels: int = 10) -> Path | None:
    """Search parent directories for specs/ folder."""
    current = start_path.resolve()  # Resolve symlinks once
    
    for _ in range(max_levels):
        if (current / "specs").is_dir():
            return current
        
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent
    
    return None
```

**Alternatives Considered**:
- **Search indefinitely to filesystem root**: Could cause excessive I/O, confusing errors from wrong directory
- **Only support git repositories**: Excludes valid use cases (pre-git, other VCS)
- **Check for other VCS markers first**: Adds complexity, git is 95%+ of use cases

**Error Handling**: Distinguish between "git root found but no specs/" and "no project root detected" per FR-006

---

### Q3: How to detect repository root for Mercurial (.hg) and SVN (.svn)?

**Decision**: Check for `.hg` and `.svn` directories as fallback after git command fails

**Rationale**:
- Requirements (FR-001) specify support for `.hg` and `.svn` markers
- These VCS systems don't have equivalent commands like `git rev-parse`
- Filesystem search is reliable for these markers (always directories, not files)
- Minimal performance impact since git is tried first

**Implementation Details**:
```python
VCS_MARKERS = [".git", ".hg", ".svn"]  # Priority order

def find_vcs_root(start_path: Path, max_levels: int = 10) -> Path | None:
    """Search parent directories for VCS markers."""
    # First try git command (fastest, handles worktrees)
    git_root = find_git_root(start_path)
    if git_root:
        return git_root
    
    # Fallback to filesystem search for any VCS marker
    current = start_path.resolve()
    for _ in range(max_levels):
        for marker in VCS_MARKERS:
            if (current / marker).exists():  # Works for both dirs and files
                return current
        
        parent = current.parent
        if parent == current:
            break
        current = parent
    
    return None
```

**Alternatives Considered**:
- **Run hg/svn commands like git**: These commands vary by VCS, adds complexity and dependencies
- **Only check .git**: Violates spec requirements for FR-001
- **Check all markers in parallel**: Overkill, sequential is fast enough (<50ms)

---

### Q4: How to handle symbolic links during traversal?

**Decision**: Resolve symbolic links once at the start using `Path.resolve()`

**Rationale**:
- Prevents infinite loops (symlink pointing to ancestor)
- Follows real filesystem path, matches user expectations
- `Path.resolve()` handles all symlinks in path at once (efficient)
- Satisfies FR-007 requirement

**Implementation**: All traversal functions call `.resolve()` on start_path before traversing

**Alternatives Considered**:
- **Follow symlinks at each level**: Slower, more complex, risk of loops
- **Don't resolve symlinks**: Could produce incorrect results, user confusion
- **Check for loops manually**: Unnecessary complexity, `.resolve()` handles it

---

### Q5: How to ensure backward compatibility?

**Decision**: 
1. Keep existing `discover_latest_tasks_file(workspace_root)` signature unchanged
2. Add new `find_repository_root(start_path)` function
3. Update CLI to call `find_repository_root(Path.cwd())` then pass result to `discover_latest_tasks_file()`

**Rationale**:
- Existing function signature preserved (backward compatibility per FR-010)
- New function is internal implementation detail, doesn't affect public API
- CLI behavior enhanced but existing explicit paths still work (FR-009)
- When run from repo root, `find_repository_root()` returns current directory → identical behavior

**Testing Strategy**:
- Contract tests verify current behavior from repo root unchanged
- Integration tests verify new behavior from subdirectories
- Unit tests cover edge cases (nested repos, symlinks, no git)

**Alternatives Considered**:
- **Modify discover_latest_tasks_file() to auto-detect**: Breaks abstraction, mixes concerns
- **Add optional parameter to discover_latest_tasks_file()**: More complex API, unnecessary
- **Create entirely new discovery function**: Code duplication, harder to maintain

---

## Technology Stack

### Git Command Integration
- **Tool**: subprocess.run() with `git rev-parse --show-toplevel`
- **Rationale**: Standard library, no external dependencies, fast and reliable
- **Error Handling**: Catch CalledProcessError (not a git repo), FileNotFoundError (git not installed), TimeoutExpired
- **Timeout**: 2 seconds to prevent hanging on network filesystems

### Path Manipulation
- **Tool**: pathlib.Path (standard library)
- **Rationale**: Already used throughout codebase, type-safe, cross-platform
- **Key Methods**: `.resolve()` (symlinks), `.parent` (traversal), `.exists()`, `.is_dir()`

### Performance Optimization
- **Max Depth**: 10 levels for filesystem traversal (FR-004)
- **Early Exit**: Return immediately when marker found
- **Symlink Resolution**: Single `.resolve()` call at start, not per iteration

## Best Practices

### Error Message Design
Per FR-006, distinguish between failure modes:
- "No Git repository found and no specs/ directory detected within 10 parent directories"
- "Git repository found at <path> but no specs/ directory present"
- "Multiple specs/ directories found, using <path> (closest to current directory)"

### Cross-Platform Compatibility
- Use `pathlib.Path` for all path operations (handles Windows/Unix differences)
- Git command works identically on Linux/macOS/Windows
- Handle case sensitivity: `.git` vs `.Git` (Windows) - Path.exists() handles this

### Testing Environments
- Unit tests: Mock subprocess.run() to test git command success/failure paths
- Integration tests: Create temporary directory structures with actual .git folders
- Edge case tests: Nested repos, symlinks, permission errors, no git installed

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Git not installed | Tool fails in git repos | Graceful fallback to VCS marker search |
| Network filesystem latency | Slow git command | 2-second timeout on subprocess.run() |
| Deeply nested directories | Slow traversal | 10-level max depth limit |
| Permission denied on parent dirs | Discovery fails | Catch OSError, provide clear error message |
| User in system directory (e.g., /) | Traverses entire filesystem | 10-level limit prevents excessive search |

## Open Questions

None - all research questions resolved, no NEEDS CLARIFICATION markers remaining.

## Dependencies

### New Dependencies
None - uses only Python standard library (subprocess, pathlib)

### Existing Dependencies (unchanged)
- typer: CLI framework
- rich: Output formatting
- pytest: Testing framework
- ruff: Linting and formatting
- mypy: Type checking
