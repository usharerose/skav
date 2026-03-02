# Skav

Parse and analyze Claude Code transcript data with type-safe models.

## Overview

Skav reads Claude Code's local transcript files (.jsonl) and tool results, validates them with Pydantic models, and provides structured access for analysis. It's designed for vibe coding observability - understanding AI-assisted coding patterns through session data.

## Quick Start

```python
from skav.core import ProjectWorkspace, ProjectStoragePath

# Access all sessions in workspace
workspace = ProjectWorkspace()  # ~/.claude/projects
for project in workspace.iter_project_storages():
    for tf_item in project.iter_transcript_items():
        # Process each transcript item
        print(tf_item)

# Or access a specific session
storage = ProjectStoragePath.encode("/path/to/project")
project = ProjectStorage(storage)
session = project.get_session("session-uuid")
```

## Core Conventions

- **Type Safety**: Complete type annotations - `TypedDict` for hook events, Pydantic for transcripts
- **Validation First**: All transcript data validated on load via Pydantic models
- **Composition Over Inheritance**: Models use discriminated unions, not inheritance
- **Error Tolerance**: Log parsing errors, don't fail sessions for bad records

## Architecture

```
Hook Events (stdin) → app.py → JSON logging
                        ↓
Transcript Files (.jsonl) → transcript_file.py → Pydantic validation
                        ↓
                    session.py → Aggregate transcripts + tool results
                        ↓
                project_storage.py → Multi-session access
                        ↓
                project_workspace.py → Workspace-wide access
```

## Module Reference

### Core Processing
| Module | Purpose |
|--------|---------|
| `app.py` | CLI hook event handler (reads stdin, logs JSON) |
| `types.py` | TypedDict definitions for 15+ hook event types |
| `log.py` | Structured JSON logging with service name injection |

### Transcript & Session
| Module | Purpose |
|--------|---------|
| `core/session.py` | Session: aggregates transcripts + tool results |
| `core/transcript_file.py` | TranscriptFile: parses .jsonl, validates items |
| `core/tool_result_file.py` | ToolResultFile: reads tool execution outputs |

### Storage Management
| Module | Purpose |
|--------|---------|
| `core/project_workspace.py` | ProjectWorkspace: workspace directory access |
| `core/project_storage.py` | ProjectStorage: project-level session management |
| `core/project_storage_path.py` | ProjectStoragePath: path encoding/decoding |

### Data Models
| Module | Purpose |
|--------|---------|
| `core/models/transcript_items/` | All transcript item types (User, Assistant, System, etc.) |
| `core/models/messages/` | Message models (UserMessage, AssistantMessage, etc.) |
| `core/models/contents/` | Content types (Text, Thinking, ToolUse, ToolResult, etc.) |
| `core/models/tool_use_result.py` | Tool execution result models |
| `core/models/usage.py` | Token usage and caching metadata |
| `core/models/thinking_metadata.py` | Thinking mode configuration |

## Development

### Using Make (Recommended)

```bash
# Development
make setup       # Install dependencies via Poetry
make test        # Run pytest
make type-check  # Run mypy type checking
make lint        # Run ruff code style checks
make prettier    # Check code formatting

# Docker
make build       # Build Docker image
make run         # Run Docker container in background
make ssh         # SSH into running container

# Cleanup
make clean-pyc   # Remove Python cache files
make clean-container  # Stop and remove Docker containers
```

### Using Poetry Directly

```bash
poetry install           # Install dependencies
poetry run pytest        # Run tests
poetry run mypy skav     # Type check (strict mode)
poetry run ruff check    # Lint
skav --debug            # Run hook handler in debug mode
```

### Docker Development

```bash
# Build and run container
make run

# Enter container
make ssh

# Inside container, run commands
pytest tests/        # Tests
mypy skav           # Type checking
ruff check .        # Linting
```

## File Format Notes

**Transcripts** (JSONL):
- Main session: `{uuid}.jsonl`
- Subagents: `{uuid}/subagents/agent-{id}.jsonl`
- One JSON object per line, validated against `TranscriptItemType` union

**Tool Results**:
- Stored as `{uuid}/tool-results/{tool_use_id}.txt`
- Large outputs separated from transcripts for performance

**Path Encoding**:
- Project paths encoded as: `/home/user/project` → `-project-user-home`
- Reversed components joined with hyphens, prefixed with `-`
