# Quickstart: Repository Root Detection

**Phase**: 1 - Design  
**Date**: February 6, 2026  
**Feature**: [spec.md](spec.md) | [plan.md](plan.md) | [research.md](research.md)

## Overview

This guide helps developers implement the repository root detection feature for sknext. The feature enables users to run `sknext` from any subdirectory within a project by automatically detecting the repository root.

**Implementation Time**: ~2-3 hours  
**Difficulty**: Medium  
**Prerequisites**: Python 3.11+, understanding of subprocess and pathlib

---

## Quick Implementation Guide

### Step 1: Add Repository Root Detection Functions (30 mins)

**File**: `src/sknext/discovery.py`

Add these new functions before `discover_latest_tasks_file()`:

```python
import subprocess
from pathlib import Path

def find_repository_root(start_path: Path) -> Path | None:
    """Find repository root by trying multiple detection methods.
    
    Tries in order:
    1. Git command (fast, handles worktrees)
    2. VCS marker search (.git, .hg, .svn)
    3. specs/ directory search (non-VCS fallback)
    
    Args:
        start_path: Directory to start searching from
        
    Returns:
        Path to repository root, or None if not found within 10 levels
    """
    # Try git command first (fastest)
    git_root = find_git_root(start_path)
    if git_root:
        return git_root
    
    # Fallback to VCS marker search
    vcs_root = find_vcs_root_filesystem(start_path)
    if vcs_root:
        return vcs_root
    
    # Final fallback: search for specs/ directory
    return find_specs_root(start_path)


def find_git_root(start_path: Path) -> Path | None:
    """Use git command to find repository root.
    
    Uses 'git rev-parse --show-toplevel' which:
    - Handles git worktrees correctly (.git as file)
    - Resolves symlinks automatically
    - Returns innermost repo in nested scenarios
    
    Args:
        start_path: Directory to run git command from
        
    Returns:
        Path to git repository root, or None if:
        - Not in a git repository
        - Git not installed
        - Command times out (network filesystem)
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=2.0,  # Prevent hanging on network filesystems
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


def find_vcs_root_filesystem(start_path: Path, max_levels: int = 10) -> Path | None:
    """Search parent directories for VCS markers (.git, .hg, .svn).
    
    Args:
        start_path: Directory to start searching from
        max_levels: Maximum parent directories to check (default: 10)
        
    Returns:
        Path to directory containing VCS marker, or None if not found
    """
    VCS_MARKERS = [".git", ".hg", ".svn"]
    current = start_path.resolve()  # Resolve symlinks once
    
    for _ in range(max_levels):
        for marker in VCS_MARKERS:
            if (current / marker).exists():  # Works for both files and dirs
                return current
        
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent
    
    return None


def find_specs_root(start_path: Path, max_levels: int = 10) -> Path | None:
    """Search parent directories for specs/ folder (non-VCS fallback).
    
    Args:
        start_path: Directory to start searching from
        max_levels: Maximum parent directories to check (default: 10)
        
    Returns:
        Path to directory containing specs/ subdirectory, or None if not found
    """
    current = start_path.resolve()
    
    for _ in range(max_levels):
        if (current / "specs").is_dir():
            return current
        
        parent = current.parent
        if parent == current:
            break
        current = parent
    
    return None
```

**Test**: Run `python -m pytest tests/unit/test_discovery.py` (will fail until tests added)

---

### Step 2: Update CLI to Use Repository Root Detection (15 mins)

**File**: `src/sknext/cli.py`

**Change 1**: Add import for subprocess at top:
```python
import subprocess  # Add this line
from pathlib import Path
```

**Change 2**: Update the auto-discovery section in `main()` function:

**Before**:
```python
    # Auto-discover if no path provided
    if file_path is None:
        file_path = discover_latest_tasks_file(Path.cwd())
        console.print(f"[dim]Found: {file_path}[/dim]\n")
```

**After**:
```python
    # Auto-discover if no path provided
    if file_path is None:
        # Detect repository root
        repo_root = find_repository_root(Path.cwd())
        
        if repo_root is None:
            console.print(
                "[bold red]Error:[/bold red] No Git repository or speckit project detected "
                "within 10 parent directories.\n"
                "Run from a project directory or specify file path explicitly:\n"
                "  [dim]sknext /path/to/tasks.md[/dim]"
            )
            raise typer.Exit(code=1)
        
        try:
            file_path = discover_latest_tasks_file(repo_root)
            console.print(f"[dim]Found: {file_path}[/dim]\n")
        except FileNotFoundError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            raise typer.Exit(code=1)
```

**Test**: Run `sknext` from repository root (should work as before)

---

### Step 3: Add Unit Tests (45 mins)

**File**: `tests/unit/test_discovery.py`

Add these test functions:

```python
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from sknext.discovery import (
    find_repository_root,
    find_git_root,
    find_vcs_root_filesystem,
    find_specs_root,
)


def test_find_git_root_success(tmp_path):
    """Test git command returns repository root."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="/repo/path\n")
        result = find_git_root(tmp_path)
        assert result == Path("/repo/path")
        mock_run.assert_called_once_with(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=2.0,
        )


def test_find_git_root_not_a_repo(tmp_path):
    """Test git command fails when not in a repository."""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(128, "git")
        result = find_git_root(tmp_path)
        assert result is None


def test_find_git_root_not_installed(tmp_path):
    """Test git command fails when git not installed."""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError()
        result = find_git_root(tmp_path)
        assert result is None


def test_find_vcs_root_with_git_dir(tmp_path):
    """Test finding .git directory."""
    (tmp_path / ".git").mkdir()
    result = find_vcs_root_filesystem(tmp_path)
    assert result == tmp_path


def test_find_vcs_root_with_git_file(tmp_path):
    """Test finding .git file (worktree)."""
    (tmp_path / ".git").write_text("gitdir: /main/repo/.git/worktrees/branch")
    result = find_vcs_root_filesystem(tmp_path)
    assert result == tmp_path


def test_find_vcs_root_in_parent(tmp_path):
    """Test finding VCS marker in parent directory."""
    (tmp_path / ".git").mkdir()
    subdir = tmp_path / "src" / "nested"
    subdir.mkdir(parents=True)
    
    result = find_vcs_root_filesystem(subdir)
    assert result == tmp_path


def test_find_vcs_root_max_depth(tmp_path):
    """Test respects max depth limit."""
    # Create deep nesting without VCS marker
    deep_path = tmp_path
    for i in range(15):
        deep_path = deep_path / f"level{i}"
    deep_path.mkdir(parents=True)
    
    result = find_vcs_root_filesystem(deep_path, max_levels=10)
    assert result is None


def test_find_specs_root(tmp_path):
    """Test finding specs/ directory."""
    (tmp_path / "specs").mkdir()
    subdir = tmp_path / "src" / "nested"
    subdir.mkdir(parents=True)
    
    result = find_specs_root(subdir)
    assert result == tmp_path


def test_find_repository_root_git_priority(tmp_path):
    """Test git command has priority over filesystem search."""
    (tmp_path / "specs").mkdir()
    
    with patch("sknext.discovery.find_git_root") as mock_git:
        mock_git.return_value = tmp_path / "git-root"
        result = find_repository_root(tmp_path)
        assert result == tmp_path / "git-root"


def test_find_repository_root_fallback_chain(tmp_path):
    """Test fallback from git -> vcs -> specs."""
    (tmp_path / "specs").mkdir()
    
    with patch("sknext.discovery.find_git_root") as mock_git:
        mock_git.return_value = None
        with patch("sknext.discovery.find_vcs_root_filesystem") as mock_vcs:
            mock_vcs.return_value = None
            result = find_repository_root(tmp_path)
            assert result == tmp_path  # Found via specs/
```

**Run**: `uv run pytest tests/unit/test_discovery.py -v`

---

### Step 4: Add Integration Tests (30 mins)

**File**: `tests/integration/test_cli.py`

Add these test functions:

```python
import subprocess
from pathlib import Path
import pytest


def test_from_subdirectory_git_repo(tmp_path):
    """Test running from subdirectory in git repository."""
    # Setup: Create git repo with specs
    (tmp_path / ".git").mkdir()
    specs_dir = tmp_path / "specs" / "001-test"
    specs_dir.mkdir(parents=True)
    (specs_dir / "tasks.md").write_text("# Phase 0\n- [ ] Task 1\n")
    
    # Create subdirectory
    subdir = tmp_path / "src" / "nested" / "deep"
    subdir.mkdir(parents=True)
    
    # Run from subdirectory
    result = subprocess.run(
        ["sknext"],
        cwd=subdir,
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    assert "Task 1" in result.stdout
    assert str(specs_dir / "tasks.md") in result.stdout


def test_from_repo_root_unchanged(tmp_path):
    """Test running from repo root works as before (backward compatibility)."""
    specs_dir = tmp_path / "specs" / "001-test"
    specs_dir.mkdir(parents=True)
    (specs_dir / "tasks.md").write_text("# Phase 0\n- [ ] Task 1\n")
    
    result = subprocess.run(
        ["sknext"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    assert "Task 1" in result.stdout


def test_no_project_detected_error(tmp_path):
    """Test error message when no repository root found."""
    # Empty temp directory, no VCS markers, no specs/
    result = subprocess.run(
        ["sknext"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 1
    assert "No Git repository or speckit project detected" in result.stdout


def test_nested_repositories(tmp_path):
    """Test selects nearest repository in nested repo scenario."""
    # Parent repo
    parent_repo = tmp_path / "parent"
    parent_repo.mkdir()
    (parent_repo / ".git").mkdir()
    parent_specs = parent_repo / "specs" / "001-parent"
    parent_specs.mkdir(parents=True)
    (parent_specs / "tasks.md").write_text("# Parent\n- [ ] Parent task\n")
    
    # Child repo
    child_repo = parent_repo / "child"
    child_repo.mkdir()
    (child_repo / ".git").mkdir()
    child_specs = child_repo / "specs" / "001-child"
    child_specs.mkdir(parents=True)
    (child_specs / "tasks.md").write_text("# Child\n- [ ] Child task\n")
    
    # Run from child subdirectory
    subdir = child_repo / "src"
    subdir.mkdir()
    
    result = subprocess.run(
        ["sknext"],
        cwd=subdir,
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    assert "Child task" in result.stdout
    assert "Parent task" not in result.stdout
```

**Run**: `uv run pytest tests/integration/test_cli.py -v`

---

### Step 5: Pre-Commit Validation (10 mins)

Run the complete pre-commit workflow:

```bash
# Format code
uv run ruff format .

# Lint and auto-fix
uv run ruff check --fix .

# Run all tests
uv run pytest

# Type check (optional but recommended)
uv run mypy src/sknext
```

**All commands must pass before committing.**

---

### Step 6: Manual Testing (15 mins)

Test all scenarios:

```bash
# From repository root (should work as before)
sknext

# From subdirectory (new behavior)
cd src/sknext
sknext

# From deep subdirectory
cd tests/unit
sknext

# Explicit path (should still work)
sknext specs/002-detect-repo-root/tasks.md

# Error case: from home directory
cd ~
sknext  # Should show error
```

---

## Common Issues & Solutions

### Issue 1: Import Error for subprocess

**Error**: `NameError: name 'subprocess' is not defined`

**Solution**: Add `import subprocess` at top of `cli.py` and `discovery.py`

---

### Issue 2: Git Command Returns Bytes

**Error**: `TypeError: expected str, bytes or os.PathLike object, not ...`

**Solution**: Ensure `text=True` in `subprocess.run()` call (converts output to string)

---

### Issue 3: Tests Fail with Real Git Repo

**Problem**: Tests run in actual git repository, git command returns real path

**Solution**: Mock `subprocess.run()` in unit tests:
```python
with patch("subprocess.run") as mock_run:
    mock_run.return_value = MagicMock(stdout="/expected/path\n")
```

---

### Issue 4: Symlink Tests Fail on Windows

**Problem**: Symlinks may require admin privileges on Windows

**Solution**: Skip symlink tests on Windows:
```python
@pytest.mark.skipif(sys.platform == "win32", reason="Symlinks require admin on Windows")
def test_symlink_resolution(tmp_path):
    ...
```

---

## Performance Validation

After implementation, verify performance meets success criteria:

```bash
# From deep subdirectory
cd src/sknext/models  # 3 levels deep
time sknext  # Should complete in <2s

# Measure just discovery time (add debug timing in code)
# Discovery should be <200ms
```

---

## Next Steps

1. **Run `/speckit.tasks`**: Generate detailed task breakdown
2. **Implement TDD**: Write failing tests first, then implement
3. **Update README.md**: Document new auto-discovery behavior
4. **Update --help text**: Mention subdirectory support

---

## Verification Checklist

Before considering feature complete:

- [ ] All unit tests pass (`pytest tests/unit/test_discovery.py`)
- [ ] All integration tests pass (`pytest tests/integration/test_cli.py`)
- [ ] Backward compatibility verified (existing tests pass)
- [ ] Pre-commit workflow passes (format, lint, test)
- [ ] Manual testing from subdirectories works
- [ ] Error messages match contract specifications
- [ ] Performance within budgets (<200ms discovery, <2s total)
- [ ] Documentation updated (README, help text)

---

## References

- [spec.md](spec.md) - Feature specification
- [plan.md](plan.md) - Implementation plan
- [research.md](research.md) - Technical research and decisions
- [contracts/cli.md](contracts/cli.md) - CLI behavior contracts
- [data-model.md](data-model.md) - Data flow and error handling
