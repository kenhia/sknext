# CLI Contract: Repository Root Detection

**Phase**: 1 - Design  
**Date**: February 6, 2026  
**Feature**: [spec.md](../spec.md) | [plan.md](../plan.md)

## Purpose

This contract defines the CLI behavior guarantees for the repository root detection feature, ensuring backward compatibility and documenting expected behavior for all scenarios.

---

## Command Signature (Unchanged)

```bash
sknext [FILE_PATH] [OPTIONS]
```

**Backward Compatibility**: Command signature remains identical, no new required arguments (FR-009, FR-010).

---

## Behavior Contracts

### Contract 1: Explicit File Path (Existing Behavior)

**When**: User provides explicit file path

**Command**:
```bash
sknext /absolute/path/to/tasks.md
sknext relative/path/to/tasks.md
```

**Behavior**:
- MUST use the provided path directly
- MUST NOT invoke repository root detection
- MUST fail with clear error if file doesn't exist
- MUST work identically to previous version

**Success Criteria**:
- File loaded and displayed
- Performance: <1s total

**Error Cases**:
- File not found: "File not found: <path>"
- Not readable: "Cannot read file: <path>"

**Test Coverage**: Existing tests must continue passing

---

### Contract 2: Auto-Detection from Repository Root (Existing Behavior)

**When**: User runs from repository root without file path

**Command**:
```bash
cd /path/to/repo
sknext
```

**Behavior**:
- Repository root detection returns current directory
- Searches `./specs/###-*/tasks.md`
- Identical to previous version behavior

**Success Criteria**:
- Tasks displayed from latest spec directory
- Performance: <2s total
- Zero breaking changes (SC-004)

**Error Cases**:
- No specs/ directory: "No specs/ directory found in /path/to/repo"
- No feature directories: "No feature directories found in ./specs/ (expected format: ###-name)"
- No tasks.md: "No tasks.md found in ./specs/###-name/"

**Test Coverage**: All existing integration tests must pass

---

### Contract 3: Auto-Detection from Subdirectory (New Behavior)

**When**: User runs from any subdirectory without file path

**Command**:
```bash
cd /path/to/repo/src/sknext/models
sknext
```

**Behavior**:
- MUST detect repository root: `/path/to/repo`
- MUST search `<repo_root>/specs/###-*/tasks.md`
- MUST display: "Found: /path/to/repo/specs/###-name/tasks.md"
- MUST behave identically to running from repo root

**Success Criteria**:
- Works from any depth (5+ levels, SC-005)
- Performance: <2s total (SC-001)
- Discovery overhead: <200ms (SC-005)

**Error Cases**:
- No repo root found: "No Git repository or speckit project detected within 10 parent directories. Run from a project directory or specify file path explicitly."
- Repo root found but no specs/: "Git repository found at /path/to/repo but no specs/ directory present"

**Test Coverage**: New integration tests required

---

### Contract 4: Nested Repositories (New Behavior)

**When**: User runs from nested repository subdirectory

**Command**:
```bash
# Structure:
# /workspace/parent-repo/.git
# /workspace/parent-repo/child-repo/.git
# /workspace/parent-repo/child-repo/specs/

cd /workspace/parent-repo/child-repo/src
sknext
```

**Behavior**:
- MUST detect nearest repository root: `/workspace/parent-repo/child-repo`
- MUST NOT use parent repository root
- MUST search child repository's specs/ directory

**Success Criteria**:
- Correct repository selected (100%, SC-003)
- Clear indication of which repo: "Found: /workspace/parent-repo/child-repo/specs/..."

**Error Cases**:
- Child repo has no specs/: "Git repository found at /workspace/parent-repo/child-repo but no specs/ directory present"

**Test Coverage**: New integration test with nested git repos

---

### Contract 5: Non-Git Project (Fallback Behavior)

**When**: User runs from non-git project subdirectory

**Command**:
```bash
# No .git, .hg, or .svn
# Has specs/ directory at /project/specs/

cd /project/deep/nested/dir
sknext
```

**Behavior**:
- Git command fails (not a repo)
- VCS marker search fails
- MUST fallback to specs/ directory search
- MUST search up to 10 parent levels
- MUST find repository root: `/project`

**Success Criteria**:
- Fallback succeeds within 200ms
- Tasks displayed from /project/specs/###-*/tasks.md

**Error Cases**:
- No specs/ within 10 levels: "No Git repository or speckit project detected within 10 parent directories..."

**Test Coverage**: New integration test without VCS markers

---

### Contract 6: No Project Detected (Error Case)

**When**: User runs from non-project directory

**Command**:
```bash
cd /home/user
sknext
```

**Behavior**:
- All detection methods fail
- MUST display clear error message (FR-006)
- MUST suggest explicit path usage
- MUST exit with code 1

**Error Message**:
```
No Git repository or speckit project detected within 10 parent directories.
Run from a project directory or specify file path explicitly:
  sknext /path/to/tasks.md
```

**Success Criteria**:
- Clear distinction from other errors (FR-006)
- Actionable guidance for user
- Non-zero exit code

**Test Coverage**: New integration test from non-project directory

---

## Output Format Contracts

### Success Output (Unchanged)

**Format**:
```
Found: /path/to/repo/specs/002-feature/tasks.md

[Task output as before...]
```

**Changes**:
- New first line showing discovered file path (dim formatting)
- Task display format completely unchanged

---

### Error Output (Enhanced)

**Format**:
```
[bold red]Error:[/bold red] <specific error message>
```

**New Error Messages**:
1. "No Git repository or speckit project detected within 10 parent directories..."
2. "Git repository found at <path> but no specs/ directory present"
3. "No feature directories found in <path>/specs/ (expected format: ###-name)"

**Existing Error Messages** (unchanged):
1. "File not found: <path>"
2. "Cannot read file: <path>"
3. "Parse errors found:" (followed by parse error details)

---

## Performance Contracts

### Time Budgets

| Scenario | Detection Time | Total Time | Status |
|----------|---------------|------------|--------|
| From repo root | <10ms | <2s | SC-001 ✓ |
| From subdirectory (git) | <10ms | <2s | SC-001 ✓ |
| From subdirectory (3 levels, no git) | <20ms | <2s | SC-005 ✓ |
| From subdirectory (10 levels, no vcs) | <110ms | <2s | SC-005 ✓ |

**Constraints**:
- Discovery overhead: <200ms (SC-005)
- Total execution: <2s (SC-001)

---

## Exit Codes

| Code | Meaning | When |
|------|---------|------|
| 0 | Success | Tasks displayed successfully |
| 1 | General error | No repo found, file not found, no specs/ |
| 2 | Parse error | tasks.md has syntax errors (existing behavior) |

**Backward Compatibility**: Exit codes unchanged from previous version

---

## Platform Compatibility

### Supported Platforms

- Linux (tested)
- macOS (git command compatible)
- Windows (pathlib handles path separators, git command available via Git for Windows)

### Git Availability

**When git installed**:
- Use `git rev-parse --show-toplevel` (primary method)
- Fast and reliable

**When git NOT installed**:
- Gracefully fallback to filesystem traversal
- No error messages about missing git
- Slightly slower but fully functional

---

## Testing Requirements

### Unit Tests (discovery.py)

- `test_find_git_root_success()`: Mock subprocess, verify git command called correctly
- `test_find_git_root_not_repo()`: Mock CalledProcessError, verify returns None
- `test_find_git_root_not_installed()`: Mock FileNotFoundError, verify returns None
- `test_find_vcs_root_git_dir()`: Temp dir with .git folder
- `test_find_vcs_root_git_file()`: Temp dir with .git file (worktree)
- `test_find_vcs_root_hg()`: Temp dir with .hg folder
- `test_find_vcs_root_svn()`: Temp dir with .svn folder
- `test_find_specs_root()`: Temp dir with specs/ folder
- `test_find_specs_root_max_depth()`: Verify stops at 10 levels
- `test_symlink_resolution()`: Temp dir with symlink, verify resolves correctly

### Integration Tests (test_cli.py)

- `test_explicit_path_unchanged()`: Verify explicit path still works
- `test_from_repo_root_unchanged()`: Verify behavior from repo root unchanged
- `test_from_subdirectory_git()`: Run from subdirectory, verify finds tasks.md
- `test_from_deep_subdirectory()`: Run from 5+ levels deep
- `test_nested_repositories()`: Create nested git repos, verify nearest selected
- `test_no_git_fallback()`: Directory without .git but with specs/
- `test_no_project_error()`: Run from temp dir, verify error message

### Contract Tests

- Verify all error messages match contract
- Verify exit codes match contract
- Verify performance within time budgets
- Verify backward compatibility (all existing tests pass)

---

## Deprecation & Migration

**No Deprecations**: All existing behavior preserved, no migration required.

**New Capability**: Repository root detection is transparent enhancement, users automatically benefit.

---

## Security Considerations

### Command Injection

**Risk**: Subprocess execution of git command

**Mitigation**:
- Use `subprocess.run()` with list arguments (not shell=True)
- No user input passed to git command
- Fixed command: `["git", "rev-parse", "--show-toplevel"]`

### Path Traversal

**Risk**: Malicious symlinks could cause infinite loops or escape directory boundaries

**Mitigation**:
- `Path.resolve()` normalizes paths and follows symlinks safely
- Max depth limit (10 levels) prevents excessive traversal
- No path concatenation with user input

### Permission Escalation

**Risk**: None - tool only reads directories, never writes

**Mitigation**: N/A (read-only operations)

---

## Documentation Updates Required

### README.md

Add section:
```markdown
### Auto-Discovery

sknext automatically finds your project's tasks.md file by detecting the repository root:

- From any subdirectory: `cd src/models && sknext`
- Works with git, mercurial, or SVN repositories
- Fallback: searches for specs/ directory up to 10 parent levels
```

### Help Text (--help)

Update description:
```
Auto-discovers the latest tasks.md from specs/###-*/ if no path is provided.
Works from any subdirectory by detecting repository root.
```

---

## Version Compatibility

**Minimum Python Version**: 3.11 (unchanged)

**Minimum Git Version**: Any (git rev-parse is very old command, available since git 1.x)

**No New Dependencies**: Uses only Python standard library (subprocess, pathlib)
