#!/usr/bin/env python3
"""
Type definitions for Claude Code Hook events
Based on official documentation: https://code.claude.com/docs/en/hooks
"""
import sys
from typing import Any, Dict, List, Literal, Optional

if sys.version_info >= (3, 11):
    from typing import NotRequired, TypedDict
else:
    from typing_extensions import NotRequired, TypedDict



class EventCommonInput(TypedDict, total=False):

    session_id: str
    transcript_path: str
    cwd: str
    # permission_mode is documented but NOT actually present in some cases
    permission_mode: Optional[Literal[
        "default",
        "plan",
        "acceptEdits",
        "dontAsk",
        "bypassPermissions",
    ]]
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
    description: Optional[str]
    timeout: Optional[int]
    run_in_background: Optional[bool]


class ToolWriteInput(TypedDict):

    file_path: str
    content: str


class ToolEditInput(TypedDict):

    file_path: str
    old_string: str
    new_string: str
    replace_all: Optional[bool]


class ToolReadInput(TypedDict):

    file_path: str
    offset: Optional[int]
    limit: Optional[int]


class ToolGlobInput(TypedDict):

    pattern: str
    path: Optional[str]


class ToolGrepInput(TypedDict):

    pattern: str
    path: Optional[str]
    glob: Optional[str]
    output_mode: Literal[
        "content",
        "files_with_matches",
        "count",
    ]
    multiline: Optional[bool]


# Define "-i" key outside class body to bypass Python syntax limitations
ToolGrepInput.__annotations__["-i"] = NotRequired[Optional[bool]]


class ToolWebFetchInput(TypedDict):

    url: str
    prompt: Optional[str]


class ToolWebSearchInput(TypedDict):

    query: str
    allowed_domains: Optional[list[str]]
    blocked_domains: Optional[list[str]]


class ToolTaskInput(TypedDict):

    prompt: str
    description: Optional[str]
    subagent_type: Optional[str]
    model: Optional[str]


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

    source: Literal["startup", "resume", "clear", "compact"]
    model: str
    # agent_type is only present when using --agent flag
    agent_type: Optional[str]


class EventUserPromptSubmitInput(EventCommonInput):

    prompt: str


class EventPreToolUseInput(EventCommonInput):

    tool_name: str
    tool_input: ToolInput
    tool_use_id: str


class EventPermissionRequestInput(EventCommonInput):

    tool_name: str
    tool_input: ToolInput
    permission_suggestions: Optional[List[Dict[str, Any]]]


class EventPostToolUseInput(EventCommonInput):

    tool_name: str
    tool_input: ToolInput
    tool_response: Dict[str, Any]
    tool_use_id: str


class EventPostToolUseFailureInput(EventCommonInput):

    tool_name: str
    tool_input: ToolInput
    tool_use_id: str
    error: str
    is_interrupt: Optional[bool]


class EventNotificationInput(EventCommonInput):

    message: str
    title: Optional[str]
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
    task_description: Optional[str]
    teammate_name: Optional[str]
    team_name: Optional[str]


class EventPreCompactInput(EventCommonInput):

    trigger: Literal["manual", "auto"]
    custom_instructions: str


class EventSessionEndInput(EventCommonInput):

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
