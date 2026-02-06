"""Auto-discovery of tasks.md files in speckit projects.

Performance characteristics:
- Git command detection: ~10-50ms (subprocess overhead)
- VCS marker filesystem search: ~5-20ms per level (I/O bound)
- specs/ directory search: ~5-20ms per level (I/O bound)
- Total overhead target: <200ms for repository detection
- Combined with file discovery: <2s total execution time

Optimization strategies:
- Git command preferred (single syscall, no traversal)
- Early termination on first match (git → vcs → specs)
- Max 10 levels prevents excessive filesystem traversal
- 2s timeout on git command prevents network filesystem hangs
"""

import re
import subprocess
from pathlib import Path


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

    Performance: ~5-20ms per level traversed (filesystem I/O bound)
    Typical case: 2-3 levels, ~30-60ms total

    Args:
        start_path: Directory to start searching from
        max_levels: Maximum parent directories to check (default: 10)

    Returns:
        Path to directory containing VCS marker, or None if not found
    """
    VCS_MARKERS = [".git", ".hg", ".svn"]
    current = start_path.resolve()  # Resolve symlinks once (~1-5ms)

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


def discover_latest_tasks_file(workspace_root: Path) -> Path:
    """Discover the latest tasks.md file by finding highest-numbered spec directory.

    Searches for specs/###-*/ directories and selects the one with the highest
    numeric prefix, then returns the path to its tasks.md file.

    Args:
        workspace_root: Root directory of the workspace to search from

    Returns:
        Path to the tasks.md file in the highest-numbered spec directory

    Raises:
        FileNotFoundError: If specs/ doesn't exist, no feature dirs found, or no tasks.md
    """
    specs_dir = workspace_root / "specs"

    if not specs_dir.exists():
        raise FileNotFoundError(f"No specs/ directory found in {workspace_root}")

    # Find all directories with numeric prefix pattern (###-*)
    feature_dirs = []
    for item in specs_dir.iterdir():
        if not item.is_dir():
            continue

        # Extract numeric prefix
        match = re.match(r"^(\d+)-", item.name)
        if match:
            number = int(match.group(1))
            feature_dirs.append((number, item))

    if not feature_dirs:
        raise FileNotFoundError(
            f"No feature directories found in {specs_dir} (expected format: ###-name)"
        )

    # Sort by number and get highest
    feature_dirs.sort(key=lambda x: x[0], reverse=True)
    latest_dir = feature_dirs[0][1]

    tasks_file = latest_dir / "tasks.md"
    if not tasks_file.exists():
        raise FileNotFoundError(f"No tasks.md found in {latest_dir}")

    return tasks_file
