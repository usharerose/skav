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
    # TODO: check the enumerable values of `type`
    type: (
        Literal[
            "agent_progress",
            "bash_progress",
            "hook_progress",
            "mcp_progress",
            "search_results_received",
        ]
        | str
    )


class AgentProgressMessage(BaseModel):
    # TODO: check the enumerable values of `role`
    role: Literal["user", "assistant"] | str

    content: list[Any]

    id: str | None = None

    # TODO: check the enumerable values of `type`
    type: Literal["message"] | str | None = None

    model: str | None = None

    context_management: Any | None = None  # TODO: check the data type of `context_management`
    stop_reason: str | None = None
    stop_sequence: Any | None = None  # TODO: check the data type of `stop_sequence`
    usage: Usage | None = None


class AgentProgressMessageMetadata(BaseModel):
    # TODO: check the enumerable values of `type`
    type: Literal["user", "assistant"] | str

    uuid: str
    timestamp: datetime.datetime

    message: AgentProgressMessage
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
    message: AgentProgressMessageMetadata

    # TODO: check the enumerable types of `normalizedMessages` item
    normalizedMessages: list[
        AssistantMessage | AttachmentMessage | ProgressMessage | UserMessage | Any
    ]

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

    # TODO: check the enumerable values of `status`
    status: Literal["started", "completed"] | str

    serverName: str
    toolName: str

    # available when status is "completed"
    elapsedTimeMs: int | None = None


class SearchResultsReceivedProgressData(BaseProgressData):
    type: Literal["search_results_received"] = "search_results_received"

    query: str
    resultCount: int


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

    # TODO: check the enumerable values of `userType`
    userType: Literal["external"] | str

    # TODO: check the enumerable types of `data`
    data: (
        AgentProgressData
        | BashProgressData
        | HookProgressData
        | McpProgressData
        | SearchResultsReceivedProgressData
        # | Any
    )

    agentId: str | None = None
    slug: str | None = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: str | datetime.datetime) -> datetime.datetime:
        if isinstance(v, str):
            return datetime.datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v
