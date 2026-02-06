# Implementation Plan: Repository Root Detection

**Branch**: `002-detect-repo-root` | **Date**: February 6, 2026 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/002-detect-repo-root/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enhance sknext to automatically detect repository root by searching parent directories for version control markers (`.git`, `.hg`, `.svn`) or `specs/` folder, enabling users to run the tool from any subdirectory without providing explicit paths. Primary approach: Use `git rev-parse --show-toplevel` when available for fast, native git root detection, with fallback to filesystem traversal for non-git projects.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: typer (CLI), rich (formatting), subprocess (git command execution), pathlib (filesystem operations)  
**Storage**: N/A (CLI tool, no persistent storage)  
**Testing**: pytest (unit + integration tests)  
**Target Platform**: Linux/macOS/Windows (cross-platform CLI)  
**Project Type**: single (CLI tool)  
**Performance Goals**: <200ms discovery overhead from deep subdirectories (5+ levels)  
**Constraints**: <2 seconds total execution time from any subdirectory, zero breaking changes to current behavior  
**Scale/Scope**: Single-user CLI tool, no concurrency requirements, handles nested repositories and symbolic links

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Code Quality & Standards
- ✅ **PASS** - Feature enhances existing module (discovery.py) with clear, testable functions
- ✅ **PASS** - All functions will have docstrings explaining purpose, parameters, exceptions
- ✅ **PASS** - Will use type hints consistently (Path, Optional, subprocess.CompletedProcess)
- ✅ **PASS** - Will follow existing codebase patterns and pass ruff formatting/linting

### Principle II: Test-Driven Development (TDD)
- ✅ **PASS** - Each user story (P1, P2, P3) is independently testable as per spec requirements
- ✅ **PASS** - Will implement TDD: write unit tests for repository root detection → implement → refactor
- ✅ **PASS** - Will add integration tests for CLI behavior from subdirectories
- ✅ **PASS** - Will add contract tests verifying backward compatibility with current behavior
- ✅ **PASS** - All tests must pass before commit (enforced by pre-commit workflow)

### Principle III: User Experience Consistency
- ✅ **PASS** - Maintains backward compatibility: explicit file paths still work (FR-009)
- ✅ **PASS** - Clear error messages for "no repo root" vs "no specs/" scenarios (FR-006)
- ✅ **PASS** - No changes to output format or CLI interface (only internal discovery logic)
- ✅ **PASS** - Preserves current working directory (FR-005), no side effects

### Principle IV: Performance & Optimization
- ✅ **PASS** - Performance target explicitly defined: <200ms overhead, <2s total (SC-001, SC-005)
- ✅ **PASS** - Will use fast git command (`git rev-parse --show-toplevel`) when available
- ✅ **PASS** - Will implement max-depth limit (10 levels) for filesystem traversal fallback
- ✅ **PASS** - Will resolve symlinks once, not repeatedly during traversal (FR-007)

### Principle V: Pre-Commit Validation
- ✅ **PASS** - Will run `uv run ruff format .` before commit
- ✅ **PASS** - Will run `uv run ruff check --fix .` before commit  
- ✅ **PASS** - Will run `uv run pytest` and verify all tests pass before commit
- ✅ **PASS** - Feature modifies source code (discovery.py, cli.py) requiring pre-commit validation

**CONSTITUTION GATE: ✅ PASSED - No violations, proceed to Phase 0**

## Project Structure

### Documentation (this feature)

```text
specs/002-detect-repo-root/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── cli.md          # CLI behavior contract (backward compatibility)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/sknext/
├── __init__.py
├── __main__.py
├── cli.py              # MODIFIED: Update discover_latest_tasks_file call to use repo root
├── discovery.py        # MODIFIED: Add find_repository_root(), update discover_latest_tasks_file()
├── constants.py
├── formatter.py
├── models.py
└── parser.py

tests/
├── fixtures/           # EXISTING
│   ├── malformed_tasks.md
│   ├── nested_tasks.md
│   └── sample_tasks.md
├── integration/
│   └── test_cli.py     # MODIFIED: Add tests for subdirectory execution
└── unit/
    ├── test_discovery.py  # MODIFIED: Add tests for find_repository_root()
    ├── test_constants.py
    ├── test_formatter.py
    ├── test_models.py
    └── test_parser.py
```

**Structure Decision**: Single project structure maintained (existing pattern). Changes localized to discovery.py (new function) and cli.py (call site update). Test structure follows existing unit/integration split.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitutional principles satisfied.

---

## Phase Summary

### Phase 0: Research (Completed)

**Deliverable**: [research.md](research.md)

**Key Decisions**:
- Use `git rev-parse --show-toplevel` as primary detection method (user suggestion incorporated)
- Fallback chain: git command → VCS markers (.git, .hg, .svn) → specs/ directory
- Max depth limit: 10 levels to prevent excessive traversal
- Symlink resolution: Single `.resolve()` call at start for performance
- No new dependencies: Use Python standard library only (subprocess, pathlib)

**Research Questions Resolved**: 5/5
- Q1: Git repository root detection approach ✓
- Q2: Non-git project fallback strategy ✓
- Q3: Mercurial/SVN support implementation ✓
- Q4: Symbolic link handling ✓
- Q5: Backward compatibility approach ✓

---

### Phase 1: Design (Completed)

**Deliverables**:
- [data-model.md](data-model.md) - Data flow, function signatures, error handling
- [contracts/cli.md](contracts/cli.md) - CLI behavior contracts and backward compatibility
- [quickstart.md](quickstart.md) - Implementation guide with code examples

**Design Highlights**:
- 4 new functions: `find_repository_root()`, `find_git_root()`, `find_vcs_root_filesystem()`, `find_specs_root()`
- Minimal changes to existing code: CLI update to call new function, pass result to existing discovery
- Comprehensive error handling: Distinguishes between "no git", "no VCS", "no specs", "no project"
- Performance optimization: <10ms git command, <50ms filesystem traversal, total <200ms

**Contract Coverage**:
- 6 behavior contracts defined (explicit path, repo root, subdirectory, nested repos, non-git, no project)
- All error messages specified with exact wording
- Performance budgets documented (SC-001, SC-005)
- Security considerations addressed (command injection, path traversal)

**Constitution Re-Check**: ✅ PASSED (all principles satisfied post-design)

---

### Phase 2: Task Generation (Next)

**Command**: `/speckit.tasks`

**Expected Output**: `tasks.md` with detailed implementation tasks organized by:
- Phase 0: Environment setup and test infrastructure
- Phase 1: Core repository root detection (P1 user story)
- Phase 2: Nested repository support (P2 user story)
- Phase 3: Non-git fallback (P3 user story)
- Phase 4: Documentation and polish

**Estimated Tasks**: 25-35 tasks across 5 phases

---

## Next Steps

1. **Run `/speckit.tasks`** to generate detailed task breakdown from this plan
2. **Begin TDD implementation**: Follow quickstart.md guide, write tests first
3. **Iterative development**: Implement one user story at a time (P1 → P2 → P3)
4. **Validate constitution compliance**: Run pre-commit workflow before each commit

---

## Plan Metadata

**Planning Time**: Phase 0 + Phase 1 completed  
**Research Artifacts**: 1 research.md (5 questions resolved)  
**Design Artifacts**: 1 data-model.md, 1 contract, 1 quickstart guide  
**Agent Context**: Updated (subprocess, pathlib added to technology stack)  
**Constitution Status**: ✅ All principles satisfied (pre- and post-design)  
**Ready for Implementation**: Yes - all NEEDS CLARIFICATION markers resolved
