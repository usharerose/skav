#!/usr/bin/env python3
"""
Progress transcript item model
"""

import datetime
from typing import Any, Literal

from pydantic import BaseModel, field_validator

from ..messages import AssistantMessage, AttachmentMessage, ProgressMessage, UserMessage
from ..tool_use_result import ToolUseResult
from ..usage import Usage


class BaseProgressData(BaseModel):
    type: Literal[
        "agent_progress",
        "bash_progress",
        "hook_progress",
        "mcp_progress",
        "search_results_received",
        "waiting_for_task",
    ]


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: list[Any]

    id: str | None = None
    type: Literal["message"] = "message"
    model: str | None = None

    context_management: Any | None = None  # TODO: check the data type of `context_management`
    stop_reason: str | None = None
    stop_sequence: Any | None = None  # TODO: check the data type of `stop_sequence`
    usage: Usage | None = None


class MessageMetadata(BaseModel):
    type: Literal["user", "assistant"]

    uuid: str
    timestamp: datetime.datetime

    message: Message
    toolUseResult: str | ToolUseResult | None = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: str | datetime.datetime) -> datetime.datetime:
        if isinstance(v, str):
            return datetime.datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class AgentProgressData(BaseProgressData):
    type: Literal["agent_progress"] = "agent_progress"

    agentId: str
    message: MessageMetadata
    normalizedMessages: list[AssistantMessage | AttachmentMessage | ProgressMessage | UserMessage]
    prompt: str

    # TODO: check the meaning of `resume`
    # seems the value is as same as `agentId` when appeared
    resume: str | None = None


class BashProgressData(BaseProgressData):
    type: Literal["bash_progress"] = "bash_progress"

    elapsedTimeSeconds: int
    fullOutput: str
    output: str
    taskId: str | None = None
    timeoutMs: int | None = None
    totalBytes: int | None = None
    totalLines: int


class HookProgressData(BaseProgressData):
    type: Literal["hook_progress"] = "hook_progress"

    hookEvent: str
    hookName: str
    command: str


class McpProgressData(BaseProgressData):
    type: Literal["mcp_progress"] = "mcp_progress"

    status: Literal["started", "completed"]
    serverName: str
    toolName: str

    # available when status is "completed"
    elapsedTimeMs: int | None = None


class SearchResultsReceivedProgressData(BaseProgressData):
    type: Literal["search_results_received"] = "search_results_received"

    query: str
    resultCount: int


class WaitingForTaskProgressData(BaseProgressData):
    type: Literal["waiting_for_task"] = "waiting_for_task"

    taskDescription: str
    taskType: str


class ProgressTranscriptItem(BaseModel):
    type: Literal["progress"] = "progress"

    sessionId: str
    parentUuid: str | None = None
    parentToolUseID: str
    toolUseID: str
    uuid: str
    timestamp: datetime.datetime
    version: str

    cwd: str
    gitBranch: str = "HEAD"
    isSidechain: bool
    userType: Literal["external"] = "external"

    data: (
        AgentProgressData
        | BashProgressData
        | HookProgressData
        | McpProgressData
        | SearchResultsReceivedProgressData
        | WaitingForTaskProgressData
    )

    agentId: str | None = None
    slug: str | None = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: str | datetime.datetime) -> datetime.datetime:
        if isinstance(v, str):
            return datetime.datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v
