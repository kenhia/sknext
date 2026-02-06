# sknext

Task status viewer for speckit projects - a CLI tool to quickly view and track tasks from your project's tasks.md file.

## Features

- 🚀 **Fast**: View next tasks in <2 seconds
- 🔍 **Multiple Views**: 6 different viewing modes for different workflows
- 📊 **Auto-Discovery**: Automatically finds latest tasks.md in specs/###-*/ directories
- 🎨 **Rich Formatting**: Color-coded output with priority and story tag highlighting
- ✅ **Type Safe**: 100% type-checked with mypy in strict mode
- 🧪 **Well Tested**: 97 tests with 94% coverage

## Installation

### Using uv (recommended)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone <repository-url>
cd sknext
uv sync
```

### Using pip

```bash
pip install -e .
```

## Usage

### Quick Status Check (Default)

Show the next 10 uncompleted tasks with full context:

```bash
sknext
# or
sknext path/to/tasks.md
```

### Custom Task Count

Show a specific number of tasks:

```bash
sknext -n 5          # Show next 5 tasks
sknext -n 25         # Show next 25 tasks
sknext -n 0          # Show header only (no tasks)
```

### Phase Overview

Show only phases with uncompleted work (no sections or tasks):

```bash
sknext --phases-only
```

Perfect for quick status updates or understanding high-level progress.

### Structure View

Show phases and sections with uncompleted work (no individual tasks):

```bash
sknext --structure
```

Useful for sprint planning and understanding work distribution across sections.

### Combined View

Show all incomplete phases followed by N tasks:

```bash
sknext --all-phases -n 10
```

Combines strategic overview with tactical next steps - perfect for standups!

### Task-Only View

Show only task lines without any headings:

```bash
sknext --tasks-only -n 15
```

Great for copy-pasting into status reports or automated processing.

### All Remaining Tasks

Show every uncompleted task with full context:

```bash
sknext --all
```

Perfect for final sprint planning or comprehensive project reviews.

## Troubleshooting

### No tasks.md found

If you get "Error: specs directory not found":

1. Make sure you're in the project root directory
2. Ensure you have a `specs/###-feature-name/tasks.md` file structure
3. Or explicitly specify the path: `sknext path/to/tasks.md`

### Empty output

If sknext shows no tasks:

- ✅ All your tasks are complete! Great job!
- Check if tasks are marked with `- [X]` instead of `- [ ]`

### Performance issues

If sknext is slow:

- Check file size - files with >1000 tasks may take longer
- Expected: <2s for default view, <3s for files with 500 tasks
- Report performance issues with file size and timing

## Development

### Setup Development Environment

```bash
# Clone and setup
git clone <repository-url>
cd sknext
uv sync

# Install pre-commit hooks (optional)
uv run pre-commit install
```

### Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/sknext --cov-report=html

# Run specific test
uv run pytest tests/unit/test_parser.py -xvs
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type check
uv run mypy src/sknext
```

## Architecture

```
src/sknext/
├── __init__.py       # Package initialization
├── __main__.py       # Entry point for python -m sknext
├── cli.py            # Typer CLI interface
├── constants.py      # Regex patterns and defaults
├── models.py         # Frozen dataclasses (Task, Section, Phase)
├── parser.py         # Line-by-line state machine parser
├── discovery.py      # Auto-discover tasks.md in specs/
└── formatter.py      # Rich console output formatters
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass and coverage stays >90%
5. Run ruff format and mypy
6. Submit a pull request

## License

[Add your license here]

```bash
uv run ruff check --fix .
```

### Type Check

```bash
uv run mypy src/
```

## License

MIT
