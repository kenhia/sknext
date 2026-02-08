# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- PyPI publishing infrastructure with GitHub Actions workflows
- Trusted publishing support for PyPI and TestPyPI
- Comprehensive publishing documentation

## [0.1.0] - TBD

### Added
- Task status viewer for speckit projects
- Auto-discovery of tasks.md files from repository root
- Multiple viewing modes: default, phases-only, structure, all
- Rich formatted output with color-coding
- Support for priority tags (P0, P1, P2, P3)
- Support for story tags ([MVP], [Nice-to-Have], etc.)
- Git repository detection for auto-discovery
- CLI built with Typer
- Full type safety with mypy strict mode
- Comprehensive test suite (97 tests, 94% coverage)

### Features
- `sknext` - Show next 10 uncompleted tasks (default)
- `sknext -n N` - Show next N uncompleted tasks
- `sknext --phases-only` - Show only phases with uncompleted work
- `sknext --structure` - Show phases and sections with uncompleted work
- `sknext --all` - Show all tasks including completed
- `sknext --stats-only` - Show statistics summary only

[Unreleased]: https://github.com/kenhia/sknext/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/kenhia/sknext/releases/tag/v0.1.0
