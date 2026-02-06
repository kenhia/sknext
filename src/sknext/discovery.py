"""Auto-discovery of tasks.md files in speckit projects."""

import re
from pathlib import Path


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
