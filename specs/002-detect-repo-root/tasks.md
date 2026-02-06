# Tasks: Repository Root Detection

**Branch**: `002-detect-repo-root`  
**Input**: Design documents from `/specs/002-detect-repo-root/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Test infrastructure and environment preparation

- [X] T001 Verify Python 3.11+ environment with `python --version`
- [X] T002 Verify uv environment with `uv --version` and `uv sync`
- [X] T003 [P] Verify pytest installation with `uv run pytest --version`
- [X] T004 [P] Verify ruff installation with `uv run ruff --version`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core repository root detection infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Add subprocess import to src/sknext/discovery.py
- [X] T006 Create `find_git_root(start_path: Path) -> Path | None` function in src/sknext/discovery.py
- [X] T007 Create `find_vcs_root_filesystem(start_path: Path, max_levels: int = 10) -> Path | None` function in src/sknext/discovery.py
- [X] T008 Create `find_specs_root(start_path: Path, max_levels: int = 10) -> Path | None` function in src/sknext/discovery.py
- [X] T009 Create `find_repository_root(start_path: Path) -> Path | None` orchestration function in src/sknext/discovery.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Run from Subdirectory (Priority: P1) 🎯 MVP

**Goal**: Enable users to run `sknext` from any subdirectory within a git repository and automatically find tasks.md

**Independent Test**: Run `sknext` from `src/sknext/models/` and verify it finds correct tasks.md file

### Tests for User Story 1 (TDD - Write First)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US1] Unit test `test_find_git_root_success()` mock subprocess in tests/unit/test_discovery.py
- [X] T011 [P] [US1] Unit test `test_find_git_root_not_a_repo()` mock CalledProcessError in tests/unit/test_discovery.py
- [X] T012 [P] [US1] Unit test `test_find_git_root_not_installed()` mock FileNotFoundError in tests/unit/test_discovery.py
- [X] T013 [P] [US1] Unit test `test_find_git_root_timeout()` mock TimeoutExpired in tests/unit/test_discovery.py
- [X] T014 [P] [US1] Unit test `test_find_repository_root_git_priority()` verify git tried first in tests/unit/test_discovery.py
- [X] T015 [P] [US1] Integration test `test_from_subdirectory_git_repo()` create temp git repo in tests/integration/test_cli.py
- [X] T016 [P] [US1] Integration test `test_from_repo_root_unchanged()` verify backward compatibility in tests/integration/test_cli.py

### Implementation for User Story 1

- [X] T017 [US1] Run tests T010-T016 and verify they FAIL (red phase)
- [X] T018 [US1] Implement `find_git_root()` function with subprocess.run() git command in src/sknext/discovery.py
- [X] T019 [US1] Add error handling for CalledProcessError, FileNotFoundError, TimeoutExpired in src/sknext/discovery.py
- [X] T020 [US1] Implement `find_repository_root()` to call find_git_root() first in src/sknext/discovery.py
- [X] T021 [US1] Update CLI main() function to call find_repository_root(Path.cwd()) in src/sknext/cli.py
- [X] T022 [US1] Add error handling for repo_root is None with clear error message in src/sknext/cli.py
- [X] T023 [US1] Update CLI to pass repo_root to discover_latest_tasks_file() in src/sknext/cli.py
- [X] T024 [US1] Run tests T010-T016 and verify they PASS (green phase)
- [X] T025 [US1] Manual test: run `sknext` from src/sknext/ subdirectory
- [X] T026 [US1] Manual test: run `sknext` from tests/unit/ subdirectory
- [X] T027 [US1] Manual test: run `sknext` from repository root (verify unchanged)

**Checkpoint**: User Story 1 complete - sknext works from any subdirectory in git repos

---

## Phase 4: User Story 2 - Multi-Repository Workspace (Priority: P2)

**Goal**: Correctly detect nearest repository root in nested git repository scenarios

**Independent Test**: Create nested repos, run from child subdirectory, verify selects child repo

### Tests for User Story 2 (TDD - Write First)

- [X] T028 [P] [US2] Unit test `test_find_vcs_root_with_git_dir()` temp dir with .git folder in tests/unit/test_discovery.py
- [X] T029 [P] [US2] Unit test `test_find_vcs_root_with_git_file()` temp dir with .git file (worktree) in tests/unit/test_discovery.py
- [X] T030 [P] [US2] Unit test `test_find_vcs_root_in_parent()` verify finds VCS marker in parent in tests/unit/test_discovery.py
- [X] T031 [P] [US2] Unit test `test_find_vcs_root_max_depth()` verify 10-level limit in tests/unit/test_discovery.py
- [X] T032 [P] [US2] Integration test `test_nested_repositories()` create parent and child repos in tests/integration/test_cli.py

### Implementation for User Story 2

- [X] T033 [US2] Run tests T028-T032 and verify they FAIL (red phase)
- [X] T034 [US2] Implement `find_vcs_root_filesystem()` with VCS_MARKERS list in src/sknext/discovery.py
- [X] T035 [US2] Add parent directory traversal loop with max_levels=10 in src/sknext/discovery.py
- [X] T036 [US2] Add symlink resolution via Path.resolve() at start in src/sknext/discovery.py
- [X] T037 [US2] Handle .git as both file and directory via .exists() in src/sknext/discovery.py
- [X] T038 [US2] Update `find_repository_root()` to call find_vcs_root_filesystem() as fallback in src/sknext/discovery.py
- [X] T039 [US2] Run tests T028-T032 and verify they PASS (green phase)
- [X] T040 [US2] Manual test: create nested git repos and verify innermost detected
- [X] T041 [US2] Manual test: test with git worktree (.git file instead of directory)

**Checkpoint**: User Story 2 complete - handles nested repositories correctly

---

## Phase 5: User Story 3 - Non-Git Projects (Priority: P3)

**Goal**: Fallback to searching for specs/ directory in non-git projects

**Independent Test**: Run from directory without .git but with specs/ folder, verify works

### Tests for User Story 3 (TDD - Write First)

- [X] T042 [P] [US3] Unit test `test_find_specs_root()` temp dir with specs/ folder in tests/unit/test_discovery.py
- [X] T043 [P] [US3] Unit test `test_find_specs_root_in_parent()` specs/ in parent directory in tests/unit/test_discovery.py
- [X] T044 [P] [US3] Unit test `test_find_specs_root_max_depth()` verify 10-level limit in tests/unit/test_discovery.py
- [X] T045 [P] [US3] Unit test `test_find_repository_root_fallback_chain()` verify git → vcs → specs in tests/unit/test_discovery.py
- [X] T046 [P] [US3] Integration test `test_no_git_fallback()` directory without .git but with specs/ in tests/integration/test_cli.py
- [X] T047 [P] [US3] Integration test `test_no_project_detected_error()` verify error message in tests/integration/test_cli.py

### Implementation for User Story 3

- [X] T048 [US3] Run tests T042-T047 and verify they FAIL (red phase)
- [X] T049 [US3] Implement `find_specs_root()` with parent directory traversal in src/sknext/discovery.py
- [X] T050 [US3] Add check for (current / "specs").is_dir() in traversal loop in src/sknext/discovery.py
- [X] T051 [US3] Add max_levels=10 limit and filesystem root detection in src/sknext/discovery.py
- [X] T052 [US3] Update `find_repository_root()` to call find_specs_root() as final fallback in src/sknext/discovery.py
- [X] T053 [US3] Enhance CLI error message to distinguish "no git" vs "no specs" vs "no project" in src/sknext/cli.py
- [X] T054 [US3] Run tests T042-T047 and verify they PASS (green phase)
- [X] T055 [US3] Manual test: create directory without .git but with specs/, verify works
- [X] T056 [US3] Manual test: run from /tmp or home directory, verify clear error message

**Checkpoint**: All user stories complete - full repository root detection working

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, performance validation, and final quality checks

- [X] T057 [P] Update README.md with auto-discovery section and examples
- [X] T058 [P] Update --help text in src/sknext/cli.py to mention subdirectory support
- [X] T059 [P] Add docstrings to all new functions with type hints in src/sknext/discovery.py
- [X] T060 [P] Add performance comments documenting <200ms goal in src/sknext/discovery.py
- [X] T061 Run ruff format on all modified files: `uv run ruff format .`
- [X] T062 Run ruff linting with auto-fix: `uv run ruff check --fix .`
- [X] T063 Run full test suite: `uv run pytest`
- [X] T064 Run type checking: `uv run mypy src/sknext`
- [X] T065 Performance test: verify <200ms overhead from 5+ levels deep
- [X] T066 Performance test: verify <2s total execution from any subdirectory
- [X] T067 [P] Review quickstart.md and verify all steps completed
- [X] T068 [P] Update CHANGELOG or release notes with feature description
- [X] T069 Final integration test: run sknext from various subdirectories in real project
- [X] T070 Pre-commit validation: format → lint → test all pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) - BLOCKS all user stories
- **User Stories (Phase 3, 4, 5)**: All depend on Foundational (Phase 2) completion
  - User stories CAN proceed in parallel (if staffed)
  - OR sequentially in priority order: P1 (Phase 3) → P2 (Phase 4) → P3 (Phase 5)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

```
Setup (Phase 1)
    ↓
Foundational (Phase 2) ← BLOCKING GATE
    ↓
    ├─→ User Story 1 (P1) - Phase 3 [PARALLEL START POINT]
    ├─→ User Story 2 (P2) - Phase 4 [PARALLEL START POINT]
    └─→ User Story 3 (P3) - Phase 5 [PARALLEL START POINT]
         ↓
    Polish (Phase 6)
```

- **User Story 1 (P1)**: Independent - no dependencies on other stories
- **User Story 2 (P2)**: Independent - builds on P1's functions but testable separately
- **User Story 3 (P3)**: Independent - adds final fallback, testable separately

### Within Each User Story (TDD Flow)

1. Write tests FIRST (all [P] tests can be written in parallel)
2. Run tests and verify they FAIL (red phase)
3. Implement functionality to make tests pass
4. Run tests and verify they PASS (green phase)
5. Manual testing
6. Move to next story

### Parallel Opportunities

**Within Setup (Phase 1)**:
- T003 and T004 can run in parallel (different tool checks)

**Within Foundational (Phase 2)**:
- T005-T009 must be sequential (same file, functions call each other)

**Within User Story 1 Tests**:
- T010, T011, T012, T013, T014 can run in parallel (different test functions)
- T015, T016 can run in parallel (different test files/scenarios)

**Within User Story 2 Tests**:
- T028, T029, T030, T031 can run in parallel (different test functions)
- T032 independent (different test scenario)

**Within User Story 3 Tests**:
- T042, T043, T044, T045 can run in parallel (different test functions)
- T046, T047 can run in parallel (different test scenarios)

**Within Polish (Phase 6)**:
- T057, T058, T059, T060 can run in parallel (different files)
- T061-T066 must be sequential (validation pipeline)
- T067, T068 can run in parallel with each other (different files)

**Across User Stories** (if team has multiple developers):
- After Foundational (Phase 2) completes:
  - Developer 1: User Story 1 (T010-T027)
  - Developer 2: User Story 2 (T028-T041)
  - Developer 3: User Story 3 (T042-T056)
- All three stories are independently testable and deliverable

---

## Parallel Example: User Story 1 (After Foundational Complete)

```bash
# Developer 1: Write all unit tests in parallel
git checkout -b us1-tests
# Write T010, T011, T012, T013, T014 in parallel (different test functions)
pytest tests/unit/test_discovery.py  # Verify they all FAIL

# Developer 2: Write integration tests in parallel
git checkout -b us1-integration
# Write T015, T016 in parallel
pytest tests/integration/test_cli.py  # Verify they FAIL

# After tests written and failing:
# Developer 1: Implement core functionality
git checkout -b us1-implementation
# T017-T024: Implement functions, update CLI
pytest  # Verify tests PASS

# Developer 2: Manual testing
# T025-T027: Test from various subdirectories
```

---

## MVP Scope Recommendation

**Minimum Viable Product**: User Story 1 only (Phase 1, 2, 3)

**Rationale**:
- Delivers 80% of user value (git repositories are 95%+ of use cases)
- Fully testable and deployable independently
- Total tasks: T001-T027 (27 tasks, ~2-3 hours)
- Can ship and get user feedback before building P2/P3

**Incremental Delivery**:
1. **MVP**: Ship P1 (subdirectory support for git repos)
2. **Enhancement 1**: Ship P2 (nested repository handling)
3. **Enhancement 2**: Ship P3 (non-git project support)

Each increment is independently valuable and testable.

---

## Implementation Strategy

### Recommended Approach: Sequential TDD

1. **Setup** (Phase 1): Verify environment (10 mins)
2. **Foundational** (Phase 2): Build core functions (30 mins)
3. **User Story 1** (Phase 3): TDD implementation (1-1.5 hours)
   - Write tests → verify fail → implement → verify pass → manual test
4. **User Story 2** (Phase 4): TDD implementation (45 mins)
5. **User Story 3** (Phase 5): TDD implementation (45 mins)
6. **Polish** (Phase 6): Documentation and validation (30 mins)

**Total Estimated Time**: 2-3 hours for complete feature

### Alternative: Parallel Development (if team size allows)

- After Foundational (Phase 2): Split team across US1, US2, US3
- Each developer implements one user story independently
- Merge in priority order: P1 → P2 → P3
- **Time Savings**: ~50% reduction (parallel work on user stories)

---

## Success Validation

Before considering feature complete, verify:

- ✅ All 70 tasks completed and checked off
- ✅ All tests pass: `uv run pytest` (100% pass rate)
- ✅ Code formatted: `uv run ruff format .` (no changes)
- ✅ Linting passes: `uv run ruff check .` (zero errors)
- ✅ Type checking passes: `uv run mypy src/sknext` (zero errors)
- ✅ Performance validated: <200ms discovery, <2s total (SC-005, SC-001)
- ✅ Backward compatibility: Existing tests still pass (SC-004)
- ✅ Manual testing: Works from repo root and all subdirectories
- ✅ Documentation updated: README.md and --help text
- ✅ quickstart.md steps all verified

---

## Task Count Summary

- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 5 tasks (BLOCKING)
- **Phase 3 (User Story 1 - P1)**: 18 tasks (7 tests + 11 implementation)
- **Phase 4 (User Story 2 - P2)**: 14 tasks (5 tests + 9 implementation)
- **Phase 5 (User Story 3 - P3)**: 15 tasks (6 tests + 9 implementation)
- **Phase 6 (Polish)**: 14 tasks

**Total**: 70 tasks organized across 6 phases

**Test Coverage**: 18 test tasks (TDD approach for all user stories)

**Parallel Opportunities**: 15+ tasks marked [P] for parallel execution
