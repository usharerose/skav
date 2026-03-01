#!/usr/bin/env python3
"""
System transcript item model
"""

import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, RootModel


class BaseSystemTranscriptItem(BaseModel):
    type: Literal["system"] = "system"

    # TODO: check the enumerable values of `subtype`
    subtype: (
        Literal[
            "api_error",
            "compact_boundary",
            "local_command",
            "microcompact_boundary",
            "stop_hook_summary",
            "turn_duration",
        ]
        | str
    )

    sessionId: str
    parentUuid: str | None = None
    uuid: str
    timestamp: datetime.datetime
    version: str

    cwd: str
    gitBranch: str = "HEAD"
    isSidechain: bool

    # TODO: check the enumerable values of `userType`
    userType: Literal["external"] | str

    slug: str | None = None


class SystemApiErrorInfo(BaseModel):
    type: Literal["api_error"] | None = None

    # numeric code
    code: str | None = None

    message: str


class SystemApiErrorMetadata(BaseModel):
    # TODO: check the enumerable values of `type`
    type: Literal["error"] | str | None = None

    request_id: str
    error: SystemApiErrorInfo


class SystemApiError(BaseModel):
    # TODO: check the data type of `cause`
    cause: dict[str, Any] | None = None

    error: SystemApiErrorMetadata | None = None

    # TODO: check the data type of `headers`
    headers: dict[str, Any] | None = None

    requestID: str | None = None

    # HTTP status code
    status: int | None = None


class SystemApiErrorTranscriptItem(BaseSystemTranscriptItem):
    subtype: Literal["api_error"] = "api_error"

    error: SystemApiError

    # TODO: check the enumerable values of `level`
    level: Literal["error"] | str

    retryAttempt: int
    retryInMs: float
    maxRetries: int

    # TODO: check the data type of `cause`
    cause: dict[str, Any] | None = None


class CompactMetadata(BaseModel):
    # TODO: check the enumerable values of `trigger`
    trigger: Literal["auto", "manual"] | str

    preTokens: int


class SystemCompactBoundaryTranscriptItem(BaseSystemTranscriptItem):
    subtype: Literal["compact_boundary"] = "compact_boundary"

    compactMetadata: CompactMetadata

    # TODO: check the enumerable values of `content`
    content: Literal["Conversation compacted"] | str

    isMeta: bool

    # TODO: check the enumerable values of `level`
    level: Literal["info"] | str

    logicalParentUuid: str


class SystemLocalCommandTranscriptItem(BaseSystemTranscriptItem):
    subtype: Literal["local_command"] = "local_command"

    content: str
    isMeta: bool

    # TODO: check the enumerable values of `level`
    level: Literal["info"] | str


class MicrocompactMetadata(CompactMetadata):
    tokensSaved: int
    compactedToolIds: list[str]
    clearedAttachmentUUIDs: list[str]


class SystemMicrocompactBoundaryTranscriptItem(BaseSystemTranscriptItem):
    subtype: Literal["microcompact_boundary"] = "microcompact_boundary"

    content: str
    isMeta: bool

    # TODO: check the enumerable values of `level`
    level: Literal["info"] | str

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

    # TODO: check the enumerable values of `level`
    level: Literal["suggestion"] | str

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
