#!/usr/bin/env python3
"""
System transcript item model
"""

import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, RootModel


class BaseSystemTranscriptItem(BaseModel):
    type: Literal["system"] = "system"
    subtype: Literal[
        "api_error",
        "compact_boundary",
        "local_command",
        "microcompact_boundary",
        "stop_hook_summary",
        "turn_duration",
    ]

    sessionId: str
    parentUuid: str | None = None
    uuid: str
    timestamp: datetime.datetime
    version: str

    cwd: str
    gitBranch: str = "HEAD"
    isSidechain: bool
    userType: Literal["external"] = "external"

    slug: str | None = None


class ApiErrorInfo(BaseModel):
    type: Literal["api_error"] | None = None

    # numeric code
    code: str | None = None

    message: str


class ErrorMetadata(BaseModel):
    type: Literal["error"] | None = None
    request_id: str
    error: ApiErrorInfo


class Error(BaseModel):
    cause: dict[str, Any] | None = None  # TODO: check the data type of `cause`
    error: ErrorMetadata | None = None
    headers: dict[str, Any] | None = None
    requestID: str | None = None

    # HTTP status code
    status: int | None = None


class SystemApiErrorTranscriptItem(BaseSystemTranscriptItem):
    subtype: Literal["api_error"] = "api_error"

    error: Error
    level: Literal["error"]
    retryAttempt: int
    retryInMs: float
    maxRetries: int

    cause: dict[str, Any] | None = None  # TODO: check the data type of `cause`


class CompactMetadata(BaseModel):
    trigger: Literal["auto", "manual"]
    preTokens: int


class SystemCompactBoundaryTranscriptItem(BaseSystemTranscriptItem):
    subtype: Literal["compact_boundary"] = "compact_boundary"

    compactMetadata: CompactMetadata
    content: Literal["Conversation compacted"] = "Conversation compacted"
    isMeta: bool
    level: Literal["info"] = "info"
    logicalParentUuid: str


class SystemLocalCommandTranscriptItem(BaseSystemTranscriptItem):
    subtype: Literal["local_command"] = "local_command"

    content: str
    isMeta: bool
    level: Literal["info"] = "info"


class MicrocompactMetadata(CompactMetadata):
    tokensSaved: int
    compactedToolIds: list[str]
    clearedAttachmentUUIDs: list[str]


class SystemMicrocompactBoundaryTranscriptItem(BaseSystemTranscriptItem):
    subtype: Literal["microcompact_boundary"] = "microcompact_boundary"

    content: str
    isMeta: bool
    level: Literal["info"] = "info"
    microcompactMetadata: MicrocompactMetadata


class HookInfo(BaseModel):
    command: str
    durationMs: int | None = None


class SystemStopHookSummaryTranscriptItem(BaseSystemTranscriptItem):
    subtype: Literal["stop_hook_summary"] = "stop_hook_summary"

    hasOutput: bool
    hookCount: int
    hookErrors: list[str]
    hookInfos: list[HookInfo]
    level: Literal["suggestion"]
    preventedContinuation: bool
    stopReason: str
    toolUseID: str


class SystemTurnDurationTranscriptItem(BaseSystemTranscriptItem):
    subtype: Literal["turn_duration"] = "turn_duration"

    durationMs: int
    isMeta: bool


SystemTranscriptItemType = Annotated[
    SystemApiErrorTranscriptItem
    | SystemCompactBoundaryTranscriptItem
    | SystemLocalCommandTranscriptItem
    | SystemMicrocompactBoundaryTranscriptItem
    | SystemStopHookSummaryTranscriptItem
    | SystemTurnDurationTranscriptItem,
    Field(discriminator="subtype"),
]


# This is a wrapper
# via `root` property to get the actual model instance
SystemTranscriptItem = RootModel[SystemTranscriptItemType]
