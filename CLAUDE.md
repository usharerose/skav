# Skav

Parse and analyze Claude Code transcript data with type-safe models.

## Overview

Skav reads Claude Code's local transcript files (.jsonl) and tool results, validates them with Pydantic models, and provides structured access for analysis. It's designed for vibe coding observability - understanding AI-assisted coding patterns through session data.

Skav includes a CLI tool for rendering sessions as HTML files, making it easy to review and share coding sessions.

## Quick Start

### CLI: Render Sessions to HTML

```bash
# Render a session from current directory
skav abc123-def4-5678-9abc

# Render from a specific project
skav -p /path/to/project abc123-def4-5678-9abc

# Custom output path
skav abc123-def4 -o my_session.html
```

### Python API

```python
from skav.transcripts import ProjectWorkspace, ProjectStoragePath

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
CLI: skav <session_id>
    ↓
app.py (CLI entry point)
    ↓
ProjectStorage → Session → HTMLRenderer
    ↓
Context → compose() → Message normalization
    ↓
Jinja2 templates → HTML output

Data Flow:
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
| `app.py` | CLI tool for rendering sessions to HTML |
| `log.py` | Structured JSON logging with service name injection |

### Rendering
| Module | Purpose |
|--------|---------|
| `renders/renderer.py` | HTMLRenderer: renders sessions to HTML |
| `renders/context.py` | Context: template rendering data container |
| `renders/compose.py` | Message normalization and composition |
| `renders/models/message.py` | Message Pydantic models for templates |

### Transcript & Session
| Module | Purpose |
|--------|---------|
| `transcripts/session.py` | Session: aggregates transcripts + tool results |
| `transcripts/transcript_file.py` | TranscriptFile: parses .jsonl, validates items |
| `transcripts/tool_result_file.py` | ToolResultFile: reads tool execution outputs |

### Storage Management
| Module | Purpose |
|--------|---------|
| `transcripts/project_workspace.py` | ProjectWorkspace: workspace directory access |
| `transcripts/project_storage.py` | ProjectStorage: project-level session management |
| `transcripts/project_storage_path.py` | ProjectStoragePath: path encoding/decoding |

### Data Models
| Module | Purpose |
|--------|---------|
| `transcripts/models/transcript_items/` | All transcript item types (User, Assistant, System, etc.) |
| `transcripts/models/messages/` | Message models (UserMessage, AssistantMessage, etc.) |
| `transcripts/models/contents/` | Content types (Text, Thinking, ToolUse, ToolResult, etc.) |
| `transcripts/models/tool_use_result.py` | Tool execution result models |
| `transcripts/models/usage.py` | Token usage and caching metadata |
| `transcripts/models/thinking_metadata.py` | Thinking mode configuration |

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

# CLI usage
skav <session_id>        # Render session from current directory
skav -p /path <id>       # Render session from specific project
skav -h                  # Show help
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

## HTML Rendering

Skav includes a powerful HTML rendering system for visualizing Claude Code sessions.

### Rendering Features

- **Message Display**: User, assistant, and system messages with proper formatting
- **Tool Use Cards**: Detailed display of tool invocations with inputs and results
- **Syntax Highlighting**: Code blocks are highlighted based on programming language
- **Thinking Process**: Displays AI reasoning when thinking mode is enabled
- **Session Metadata**: Shows timestamp, git branch, and working directory
- **Responsive Design**: Clean, readable interface for desktop and mobile

### Template Structure

```
templates/
├── index.html                    # Main template
└── partials/                     # Reusable components
    ├── assistant_message.html    # Assistant message display
    ├── system_message.html       # System message display
    ├── user_message.html         # User message display
    ├── tool_card.html            # Tool use/result card
    ├── thinking.html             # Thinking process display
    └── node_macros.html          # Common template macros
```

### Customization

To customize the HTML output:

1. **Modify templates**: Edit files in `skav/templates/`
2. **Adjust styling**: Templates use inline CSS for easy customization
3. **Extend message models**: Add fields to `renders/models/message.py`
4. **Custom composition**: Modify `renders/compose.py` for different message structures

### Rendering Pipeline

```
Session → Context → compose() → Messages → HTMLRenderer → HTML
         (metadata)  (normalize)  (Pydantic)   (Jinja2)
```

1. **Load Session**: `ProjectStorage.get_session()`
2. **Build Context**: `Context.from_session()` - extracts metadata
3. **Compose Messages**: `compose()` - flattens and normalizes transcript items
4. **Render**: `HTMLRenderer.render_session()` - applies Jinja2 templates
5. **Output**: HTML file with all session data
