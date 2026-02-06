"""Tests for constants module."""

import re

from sknext.constants import (
    DEFAULT_TASK_COUNT,
    MAX_NESTING_DEPTH,
    PHASE_PATTERN,
    SECTION_PATTERN,
    TASK_PATTERN,
)


def test_default_task_count():
    """Test default task count constant."""
    assert DEFAULT_TASK_COUNT == 10
    assert isinstance(DEFAULT_TASK_COUNT, int)


def test_max_nesting_depth():
    """Test max nesting depth constant."""
    assert MAX_NESTING_DEPTH == 5
    assert isinstance(MAX_NESTING_DEPTH, int)


def test_phase_pattern_matches_valid_phase():
    """Test phase pattern matches valid phase headers."""
    valid_phases = [
        "## Phase 1: Setup",
        "## Phase 2: Foundation",
        "## Phase 10: Advanced Features",
    ]
    for phase in valid_phases:
        match = re.match(PHASE_PATTERN, phase)
        assert match is not None, f"Failed to match: {phase}"
        assert match.group("number") is not None
        assert match.group("title") is not None


def test_phase_pattern_rejects_invalid():
    """Test phase pattern rejects invalid headers."""
    invalid = [
        "# Phase 1: Setup",  # Wrong level
        "## Phase: Setup",  # No number
        "## Phase A: Setup",  # Letter instead of number
        "### Phase 1: Setup",  # Wrong level
    ]
    for line in invalid:
        assert re.match(PHASE_PATTERN, line) is None


def test_section_pattern_matches_valid_sections():
    """Test section pattern matches valid section headers."""
    valid_sections = [
        "### Parser Implementation",
        "#### Sub-section Title",
        "##### Deep Section",
    ]
    for section in valid_sections:
        match = re.match(SECTION_PATTERN, section)
        assert match is not None, f"Failed to match: {section}"
        assert match.group("level") is not None
        assert match.group("title") is not None


def test_section_pattern_extracts_level():
    """Test section pattern correctly extracts heading level."""
    test_cases = [
        ("### Title", 3),
        ("#### Title", 4),
        ("##### Title", 5),
    ]
    for line, expected_level in test_cases:
        match = re.match(SECTION_PATTERN, line)
        assert match is not None
        hashes = match.group("level")
        assert len(hashes) == expected_level


def test_task_pattern_matches_valid_tasks():
    """Test task pattern matches valid task lines."""
    valid_tasks = [
        "- [ ] T001 Create project structure",
        "- [X] T042 Implement parser logic",
        "- [x] T100 Write tests",
        "- [ ] T001 [P] Parallel task",
        "- [ ] T001 [US1] User story task",
        "- [ ] T001 [P] [US2] Combined markers",
    ]
    for task in valid_tasks:
        match = re.match(TASK_PATTERN, task)
        assert match is not None, f"Failed to match: {task}"


def test_task_pattern_extracts_components():
    """Test task pattern extracts all components correctly."""
    task = "- [ ] T042 [P] [US1] Implement feature"
    match = re.match(TASK_PATTERN, task)
    assert match is not None
    assert match.group("checkbox") == " "
    assert match.group("task_id") == "T042"
    assert match.group("description") == "[P] [US1] Implement feature"


def test_task_pattern_handles_completed_checkbox():
    """Test task pattern recognizes completed tasks."""
    completed_tasks = [
        "- [X] T001 Task",
        "- [x] T001 Task",
        "- [~] T001 Task",
        "- [*] T001 Task",
    ]
    for task in completed_tasks:
        match = re.match(TASK_PATTERN, task)
        assert match is not None
        checkbox = match.group("checkbox")
        assert checkbox != " "


def test_task_pattern_rejects_invalid():
    """Test task pattern rejects malformed tasks."""
    invalid = [
        "- [] T001 No space in checkbox",
        "- [ ]T001 No space after checkbox",
        "- [ ] 001 No T prefix",
        "- [ ] T1 Too few digits",
        "* [ ] T001 Wrong bullet",
    ]
    for line in invalid:
        assert re.match(TASK_PATTERN, line) is None, f"Should not match: {line}"
