"""Tests for discovery module."""

import pytest

from sknext.discovery import discover_latest_tasks_file


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
