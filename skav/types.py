#!/usr/bin/env python3
"""
Type definitions for Claude Code Hook events

This module provides TypedDict definitions for all Claude Code hook event inputs.
These types represent the JSON structure that Claude Code sends to hook handlers.

Based on official documentation: https://code.claude.com/docs/en/hooks

Type Hierarchy:
    EventCommonInput
    ├── EventSessionStartInput
    ├── EventUserPromptSubmitInput
    ├── EventPreToolUseInput
    ├── EventPermissionRequestInput
    ├── EventPostToolUseInput
    ├── EventPostToolUseFailureInput
    ├── EventNotificationInput
    ├── EventSubagentStartInput
    ├── EventSubagentStopInput
    ├── EventStopInput
    ├── EventTeammateIdleInput
    ├── EventTaskCompletedInput
    ├── EventPreCompactInput
    └── EventSessionEndInput

Tool Input Types:
    Each tool (Bash, Read, Write, Edit, etc.) has its own input type definition
    representing the parameters passed to that tool.
"""

import sys
from typing import Any, Literal

if sys.version_info >= (3, 11):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


class EventCommonInput(TypedDict, total=False):
    """Common fields present in all Claude Code hook events.

    :ivar session_id: Unique identifier for the session
    :vartype session_id: str
    :ivar transcript_path: Path to the session's transcript file
    :vartype transcript_path: str
    :ivar cwd: Current working directory during the event
    :vartype cwd: str
    :ivar permission_mode: Permission mode in effect (may be None in some cases)
    :vartype permission_mode: str or None
    :ivar hook_event_name: Type of hook event being triggered
    :vartype hook_event_name: str
    """

    session_id: str
    transcript_path: str
    cwd: str
    # permission_mode is documented but NOT actually present in some cases
    permission_mode: (
        Literal["default", "plan", "acceptEdits", "dontAsk", "bypassPermissions"] | None
    )
    hook_event_name: Literal[
        "SessionStart",
        "UserPromptSubmit",
        "PreToolUse",
        "PermissionRequest",
        "PostToolUse",
        "PostToolUseFailure",
        "Notification",
        "SubagentStart",
        "SubagentStop",
        "Stop",
        "TeammateIdle",
        "TaskCompleted",
        "PreCompact",
        "SessionEnd",
    ]


# =================
# Tool Input Types
# =================


class ToolBashInput(TypedDict):
    command: str
    description: str | None
    timeout: int | None
    run_in_background: bool | None


class ToolWriteInput(TypedDict):
    file_path: str
    content: str


class ToolEditInput(TypedDict):
    file_path: str
    old_string: str
    new_string: str
    replace_all: bool | None


class ToolReadInput(TypedDict):
    file_path: str
    offset: int | None
    limit: int | None


class ToolGlobInput(TypedDict):
    pattern: str
    path: str | None


class ToolGrepInput(TypedDict):
    pattern: str
    path: str | None
    glob: str | None
    output_mode: Literal[
        "content",
        "files_with_matches",
        "count",
    ]
    multiline: bool | None


# Define "-i" key outside class body to bypass Python syntax limitations
ToolGrepInput.__annotations__["-i"] = bool | None


class ToolWebFetchInput(TypedDict):
    url: str
    prompt: str | None


class ToolWebSearchInput(TypedDict):
    query: str
    allowed_domains: list[str] | None
    blocked_domains: list[str] | None


class ToolTaskInput(TypedDict):
    prompt: str
    description: str | None
    subagent_type: str | None
    model: str | None


class ToolCustomInput(TypedDict): ...


ToolInput = (
    ToolBashInput
    | ToolWriteInput
    | ToolEditInput
    | ToolReadInput
    | ToolGlobInput
    | ToolGrepInput
    | ToolWebFetchInput
    | ToolWebSearchInput
    | ToolTaskInput
    | ToolCustomInput
)


# ============================================================================
# Hook Event Input Types
# ============================================================================
class EventSessionStartInput(EventCommonInput):
    """Input for SessionStart hook event.

    :ivar source: Source of the session start (startup/resume/clear/compact)
    :vartype source: str
    :ivar model: Model name being used (e.g., "claude-sonnet-4-6")
    :vartype model: str
    :ivar agent_type: Agent type if using --agent flag, None otherwise
    :vartype agent_type: str or None
    """

    source: Literal["startup", "resume", "clear", "compact"]
    model: str
    # agent_type is only present when using --agent flag
    agent_type: str | None


class EventUserPromptSubmitInput(EventCommonInput):
    """Input for UserPromptSubmit hook event.

    :ivar prompt: The user's prompt text
    :vartype prompt: str
    """

    prompt: str


class EventPreToolUseInput(EventCommonInput):
    tool_name: str
    tool_input: ToolInput
    tool_use_id: str


class EventPermissionRequestInput(EventCommonInput):
    tool_name: str
    tool_input: ToolInput
    permission_suggestions: list[dict[str, Any]] | None


class EventPostToolUseInput(EventCommonInput):
    tool_name: str
    tool_input: ToolInput
    tool_response: dict[str, Any]
    tool_use_id: str


class EventPostToolUseFailureInput(EventCommonInput):
    tool_name: str
    tool_input: ToolInput
    tool_use_id: str
    error: str
    is_interrupt: bool | None


class EventNotificationInput(EventCommonInput):
    message: str
    title: str | None
    notification_type: Literal[
        "permission_prompt",
        "idle_prompt",
        "auth_success",
        "elicitation_dialog",
    ]


class EventSubagentStartInput(EventCommonInput):
    agent_id: str
    agent_type: str


class EventSubagentStopInput(EventCommonInput):
    stop_hook_active: bool
    agent_id: str
    agent_type: str
    agent_transcript_path: str


class EventStopInput(EventCommonInput):
    stop_hook_active: bool


class EventTeammateIdleInput(EventCommonInput):
    teammate_name: str
    team_name: str


class EventTaskCompletedInput(EventCommonInput):
    task_id: str
    task_subject: str
    task_description: str | None
    teammate_name: str | None
    team_name: str | None


class EventPreCompactInput(EventCommonInput):
    trigger: Literal["manual", "auto"]
    custom_instructions: str


class EventSessionEndInput(EventCommonInput):
    """Input for SessionEnd hook event.

    :ivar reason: Reason for session ending
    :vartype reason: str
    """

    reason: Literal[
        "clear",
        "logout",
        "prompt_input_exit",
        "bypass_permissions_disabled",
        "other",
    ]


EventInput = (
    EventSessionStartInput
    | EventUserPromptSubmitInput
    | EventPreToolUseInput
    | EventPermissionRequestInput
    | EventPostToolUseInput
    | EventPostToolUseFailureInput
    | EventNotificationInput
    | EventSubagentStartInput
    | EventSubagentStopInput
    | EventStopInput
    | EventTeammateIdleInput
    | EventTaskCompletedInput
    | EventPreCompactInput
    | EventSessionEndInput
)
