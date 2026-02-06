"""Tests for discovery module."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sknext.discovery import (
    discover_latest_tasks_file,
    find_git_root,
    find_repository_root,
)


def test_discover_finds_specs_directory(tmp_path):
    """Test discovery finds specs/ directory."""
    # Create structure
    specs_dir = tmp_path / "specs"
    specs_dir.mkdir()
    feature_dir = specs_dir / "001-feature"
    feature_dir.mkdir()
    tasks_file = feature_dir / "tasks.md"
    tasks_file.write_text("# Tasks")

    result = discover_latest_tasks_file(tmp_path)
    assert result == tasks_file


def test_discover_extracts_numeric_prefix(tmp_path):
    """Test discovery correctly extracts numeric prefixes."""
    specs_dir = tmp_path / "specs"
    specs_dir.mkdir()

    # Create multiple feature directories
    (specs_dir / "001-first").mkdir()
    (specs_dir / "001-first" / "tasks.md").write_text("# Tasks 1")

    (specs_dir / "005-second").mkdir()
    (specs_dir / "005-second" / "tasks.md").write_text("# Tasks 5")

    (specs_dir / "003-third").mkdir()
    (specs_dir / "003-third" / "tasks.md").write_text("# Tasks 3")

    result = discover_latest_tasks_file(tmp_path)
    assert result == specs_dir / "005-second" / "tasks.md"


def test_discover_sorts_numerically(tmp_path):
    """Test discovery sorts numerically, not lexicographically."""
    specs_dir = tmp_path / "specs"
    specs_dir.mkdir()

    # Create dirs that would sort differently lexicographically
    (specs_dir / "002-feature").mkdir()
    (specs_dir / "002-feature" / "tasks.md").write_text("# Tasks")

    (specs_dir / "010-feature").mkdir()
    (specs_dir / "010-feature" / "tasks.md").write_text("# Tasks")

    (specs_dir / "100-feature").mkdir()
    (specs_dir / "100-feature" / "tasks.md").write_text("# Tasks")

    result = discover_latest_tasks_file(tmp_path)
    # Should select 100, not 010
    assert result == specs_dir / "100-feature" / "tasks.md"


def test_discover_selects_highest_number(tmp_path):
    """Test discovery selects highest-numbered directory."""
    specs_dir = tmp_path / "specs"
    specs_dir.mkdir()

    (specs_dir / "001-old").mkdir()
    (specs_dir / "001-old" / "tasks.md").write_text("# Old")

    (specs_dir / "999-newest").mkdir()
    (specs_dir / "999-newest" / "tasks.md").write_text("# Newest")

    result = discover_latest_tasks_file(tmp_path)
    assert result == specs_dir / "999-newest" / "tasks.md"


def test_discover_missing_specs_directory(tmp_path):
    """Test discovery handles missing specs/ directory."""
    with pytest.raises(FileNotFoundError, match="specs"):
        discover_latest_tasks_file(tmp_path)


def test_discover_empty_specs_directory(tmp_path):
    """Test discovery handles empty specs/ directory."""
    specs_dir = tmp_path / "specs"
    specs_dir.mkdir()

    with pytest.raises(FileNotFoundError, match="No feature directories"):
        discover_latest_tasks_file(tmp_path)


def test_discover_no_tasks_file(tmp_path):
    """Test discovery handles missing tasks.md in feature directory."""
    specs_dir = tmp_path / "specs"
    specs_dir.mkdir()
    feature_dir = specs_dir / "001-feature"
    feature_dir.mkdir()
    # No tasks.md file

    with pytest.raises(FileNotFoundError, match="tasks.md"):
        discover_latest_tasks_file(tmp_path)


def test_discover_ignores_non_numeric_dirs(tmp_path):
    """Test discovery ignores directories without numeric prefix."""
    specs_dir = tmp_path / "specs"
    specs_dir.mkdir()

    # Create valid directory
    (specs_dir / "001-feature").mkdir()
    (specs_dir / "001-feature" / "tasks.md").write_text("# Tasks")

    # Create invalid directories (should be ignored)
    (specs_dir / "template").mkdir()
    (specs_dir / "archive").mkdir()
    (specs_dir / "feature-no-number").mkdir()

    result = discover_latest_tasks_file(tmp_path)
    assert result == specs_dir / "001-feature" / "tasks.md"


def test_discover_handles_three_digit_padding(tmp_path):
    """Test discovery works with zero-padded 3-digit directories."""
    specs_dir = tmp_path / "specs"
    specs_dir.mkdir()

    (specs_dir / "001-feature").mkdir()
    (specs_dir / "001-feature" / "tasks.md").write_text("# Tasks")

    (specs_dir / "042-feature").mkdir()
    (specs_dir / "042-feature" / "tasks.md").write_text("# Tasks")

    result = discover_latest_tasks_file(tmp_path)
    assert result == specs_dir / "042-feature" / "tasks.md"


# User Story 1 Tests: Repository Root Detection


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


def test_find_git_root_timeout(tmp_path):
    """Test git command fails on timeout."""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired("git", 2.0)
        result = find_git_root(tmp_path)
        assert result is None


def test_find_repository_root_git_priority(tmp_path):
    """Test git command has priority over filesystem search."""
    (tmp_path / "specs").mkdir()

    with patch("sknext.discovery.find_git_root") as mock_git:
        mock_git.return_value = tmp_path / "git-root"
        result = find_repository_root(tmp_path)
        assert result == tmp_path / "git-root"


# User Story 2 Tests: Multi-Repository Workspace


def test_find_vcs_root_with_git_dir(tmp_path):
    """Test finding .git directory."""
    (tmp_path / ".git").mkdir()
    from sknext.discovery import find_vcs_root_filesystem

    result = find_vcs_root_filesystem(tmp_path)
    assert result == tmp_path


def test_find_vcs_root_with_git_file(tmp_path):
    """Test finding .git file (worktree)."""
    (tmp_path / ".git").write_text("gitdir: /main/repo/.git/worktrees/branch")
    from sknext.discovery import find_vcs_root_filesystem

    result = find_vcs_root_filesystem(tmp_path)
    assert result == tmp_path


def test_find_vcs_root_in_parent(tmp_path):
    """Test finding VCS marker in parent directory."""
    (tmp_path / ".git").mkdir()
    subdir = tmp_path / "src" / "nested"
    subdir.mkdir(parents=True)

    from sknext.discovery import find_vcs_root_filesystem

    result = find_vcs_root_filesystem(subdir)
    assert result == tmp_path


def test_find_vcs_root_max_depth(tmp_path):
    """Test respects max depth limit."""
    # Create deep nesting without VCS marker
    deep_path = tmp_path
    for i in range(15):
        deep_path = deep_path / f"level{i}"
    deep_path.mkdir(parents=True)

    from sknext.discovery import find_vcs_root_filesystem

    result = find_vcs_root_filesystem(deep_path, max_levels=10)
    assert result is None


# User Story 3 Tests: Non-Git Projects


def test_find_specs_root(tmp_path):
    """Test finding specs/ directory."""
    (tmp_path / "specs").mkdir()
    subdir = tmp_path / "src" / "nested"
    subdir.mkdir(parents=True)

    from sknext.discovery import find_specs_root

    result = find_specs_root(subdir)
    assert result == tmp_path


def test_find_specs_root_in_parent(tmp_path):
    """Test finding specs/ in parent directory."""
    (tmp_path / "specs").mkdir()
    deep_subdir = tmp_path / "a" / "b" / "c" / "d"
    deep_subdir.mkdir(parents=True)

    from sknext.discovery import find_specs_root

    result = find_specs_root(deep_subdir)
    assert result == tmp_path


def test_find_specs_root_max_depth(tmp_path):
    """Test respects max depth limit."""
    # Create specs/ far away
    (tmp_path / "specs").mkdir()

    # Create very deep path (more than 10 levels)
    deep_path = tmp_path
    for i in range(15):
        deep_path = deep_path / f"level{i}"
    deep_path.mkdir(parents=True)

    from sknext.discovery import find_specs_root

    result = find_specs_root(deep_path, max_levels=10)
    assert result is None


def test_find_repository_root_fallback_chain(tmp_path):
    """Test fallback from git → vcs → specs."""
    (tmp_path / "specs").mkdir()

    with patch("sknext.discovery.find_git_root") as mock_git:
        mock_git.return_value = None
        with patch("sknext.discovery.find_vcs_root_filesystem") as mock_vcs:
            mock_vcs.return_value = None
            result = find_repository_root(tmp_path)
            assert result == tmp_path  # Found via specs/
