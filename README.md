# Skav

<div align="center">

**A Python-based service for vibe coding observability**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![type-checked: mypy](https://img.shields.io/badge/type--checked-mypy-blue)](https://mypy-lang.org/)

Scavenge value from your Claude Code coding sessions

</div>

## Overview

Skav parses and analyzes Claude Code transcript data with type-safe Pydantic models, enabling deep analysis of AI-assisted coding sessions.

## Features

- **Structured Access**: Session, project, and workspace-level APIs for navigating transcript data
- **Validation First**: All transcript data validated on load using Pydantic models
- **Comprehensive Coverage**: Supports all Claude Code hook events, transcript items, and content types
- **Error Tolerant**: Logs parsing errors without failing entire sessions
- **HTML Rendering**: Render sessions as beautiful HTML files for review and sharing

## Installation

### Option 1: Local Development (Poetry)

```bash
# Clone the repository
git clone https://github.com/usharerose/skav.git
cd skav

# Install with Poetry (recommended)
make setup

# Or manually
poetry install
```

### Option 2: Docker (Containerized)

```bash
# Build and run with Docker
make run

# Enter the container
make ssh

# Inside the container, dependencies are already installed
skav --help
```

## Quick Start

### Python API

```python
from skav.transcripts import ProjectWorkspace, ProjectStoragePath

# Access all sessions in workspace
workspace = ProjectWorkspace()  # ~/.claude/projects
for project in workspace.iter_project_storages():
    for item in project.iter_transcript_items():
        # Process each transcript item
        print(item)

# Or access a specific session
storage = ProjectStoragePath.encode("/path/to/project")
project = ProjectStorage(storage)
session = project.get_session("session-uuid")

# Iterate through transcripts
for item in session.iter_transcripts():
    # item is a properly discriminated union type
    if hasattr(item, 'content'):
        print(f"Content: {item.content}")
```

### CLI: Render Sessions to HTML

Skav includes a command-line tool for rendering Claude Code sessions as HTML files:

```bash
# Render a session from current directory
skav abc123-def4-5678-9abc

# Render a session from a specific project
skav -p /path/to/project abc123-def4-5678-9abc

# Render with custom output path
skav abc123-def4 -o session.html

# Render from current directory explicitly
skav -p . abc123-def4
```

**Parameters:**
- `-p, --project`: Project directory path (default: current directory)
- `-o, --output`: Output HTML file path (default: `<session_id>.html`)
- `session_id`: Session UUID to render (required)

**Example Output:**
The generated HTML file includes:
- All messages with syntax-highlighted code blocks
- Tool use cards with inputs and results
- Thinking process display
- Session metadata (timestamp, git branch, etc.)

## Development

### Using Make (Recommended)

```bash
# Development
make setup       # Install dependencies (requires Poetry)
make test        # Run tests with pytest
make type-check  # Run type checking with mypy
make lint        # Check code style with ruff
make prettier    # Check code formatting

# Docker
make build       # Build Docker image
make run         # Run Docker container
make ssh         # Enter running container
```

### Using Poetry Directly

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Type checking (strict mode enabled)
poetry run mypy skav

# Linting
poetry run ruff check skav

# Format code
poetry run ruff format skav
```
