# Research: Task Status Viewer

**Phase**: 0 - Research & Technology Selection  
**Date**: 2026-02-05

## Research Questions

### Q1: Best approach for parsing markdown task lists in Python?

**Decision**: Use line-by-line parsing with regex patterns

**Rationale**:
- Tasks.md has predictable structure (phases → sections → tasks)
- No need for full markdown AST (overkill for simple line patterns)
- Regex for checkbox detection: `r'^\s*-\s*\[(.)\]\s*(.*)$'`
- Heading detection: `r'^(#{2,3})\s+(.+)$'` for ## and ###
- Lightweight, fast, no external markdown parser dependencies

**Alternatives considered**:
- **python-markdown**: Full markdown parser, too heavy for our needs
- **mistune**: Fast markdown parser, but we only need line patterns
- **marko**: AST-based, excellent but unnecessary complexity

### Q2: How to implement auto-discovery of latest spec directory?

**Decision**: Scan specs/ for ###-* pattern, sort numerically, pick highest

**Rationale**:
- Use `Path.glob('specs/[0-9][0-9][0-9]-*/')` to find candidates
- Extract leading digits with `int(dir.name[:3])`
- Sort and take max for latest spec
- Check for `tasks.md` within that directory
- Simple, explicit, no assumptions about naming

**Alternatives considered**:
- **mtime-based**: Fragile (git clone loses timestamps)
- **git log**: Too slow, requires git, not portable
- **Numeric directory names**: Chosen - reliable and explicit

### Q3: Best practices for typer CLI design?

**Decision**: Use typer's option/argument decorators with rich for output

**Rationale**:
- Typer provides clean CLI interface with automatic --help
- Use `typer.Option()` for flags: `--phases-only`, `--all`, etc.
- Use `typer.Argument()` for optional file path
- Rich provides colored output, progress bars, tables
- Both integrate seamlessly: `rich.console.Console()` for output

**Alternatives considered**:
- **click**: More verbose than typer, less intuitive
- **argparse**: Standard library but more boilerplate
- **typer + rich**: Chosen - modern, clean, excellent UX

### Q4: How to handle nested section depth limits gracefully?

**Decision**: Track depth during parsing, cap display at MAX_NESTING_DEPTH

**Rationale**:
- Count heading levels during parse (##=1, ###=2, ####=3, etc.)
- Store full hierarchy in data model
- During display: if depth > MAX_NESTING_DEPTH, show Phase + immediate parent only
- Constant `MAX_NESTING_DEPTH = 5` in constants.py
- No error - graceful degradation

**Alternatives considered**:
- **Flatten all sections**: Loses context
- **Error on deep nesting**: Too strict, fails on valid files
- **Depth cap with graceful display**: Chosen - handles edge case smoothly

### Q5: Error handling strategy for malformed files?

**Decision**: Strict mode - fail fast with descriptive errors including line numbers

**Rationale**:
- Files are agent-managed, should be well-formed
- Early failure prevents incorrect output
- Rich traceback shows line numbers and context
- Exit codes: 0=success, 1=file not found, 2=parse error, 3=invalid args

**Alternatives considered**:
- **Lenient mode**: Skip bad lines, continue parsing (considered for future)
- **Warnings only**: May miss critical issues
- **Strict mode**: Chosen - aligns with agent-managed workflow

### Q6: Testing strategy for CLI tool?

**Decision**: Unit tests for components + integration tests for CLI

**Rationale**:
- **Unit tests**: parser.py (line patterns), discovery.py (directory scan), models.py (data structures)
- **Integration tests**: Full CLI invocation with fixture files using `typer.testing.CliRunner`
- **Fixtures**: sample_tasks.md (well-formed), malformed_tasks.md (errors), nested_tasks.md (depth test)
- **Coverage target**: >90% for core logic

**Alternatives considered**:
- **Manual testing only**: Not repeatable, violates TDD principle
- **Unit tests only**: Misses integration issues
- **Both unit + integration**: Chosen - comprehensive coverage

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Language | Python | 3.11+ | Modern Python features, type hints, dataclasses |
| Package Manager | uv | latest | Fast, reliable dependency resolution |
| CLI Framework | typer | 0.9+ | Clean API, automatic help, rich integration |
| Terminal Output | rich | 13+ | Beautiful formatting, colors, progress bars |
| Testing | pytest | 7+ | Industry standard, excellent fixtures/plugins |
| Linting | ruff | latest | Fast linter+formatter, replaces flake8/black |
| Type Checking | mypy | 1+ | Static type verification for type hints |

## Key Design Decisions

1. **Data Model**: Use Python dataclasses for Task, Section, Phase (immutable, type-safe)
2. **Parser**: State machine tracking current phase/section as we scan lines
3. **Discovery**: Explicit specs/ directory scanning with numeric sorting
4. **Output**: Rich console with conditional formatting based on view mode
5. **Constants**: Single constants.py for MAX_NESTING_DEPTH, default task count (10)
6. **Entry Point**: Support both `python -m task_viewer` and installed `sknext` command

## Implementation Notes

- Start with parser (TDD: write parser tests first)
- Build data models (Task, Section, Phase as dataclasses)
- Implement discovery logic with unit tests
- Build CLI with typer, wire up to parser
- Add rich formatting for output modes
- Integration tests with fixture files
- Performance testing with large files (500 tasks)

## Open Questions

None - all research complete, ready for Phase 1 design.
