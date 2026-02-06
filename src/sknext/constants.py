"""Constants and regex patterns for parsing tasks.md files."""

import re

# Display constants
DEFAULT_TASK_COUNT = 10
MAX_NESTING_DEPTH = 5

# Regex patterns for parsing
PHASE_PATTERN = re.compile(r"^## Phase (?P<number>\d+):\s*(?P<title>.+)$")

SECTION_PATTERN = re.compile(r"^(?P<level>#{3,})\s+(?P<title>.+)$")

TASK_PATTERN = re.compile(r"^-\s+\[(?P<checkbox>.)\]\s+(?P<task_id>T\d{3,})\s+(?P<description>.+)$")
