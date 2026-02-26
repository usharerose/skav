#!/usr/bin/env python3
"""
User transcript item model
"""

import datetime
from typing import Any, Literal

from pydantic import BaseModel, field_validator

from ..messages import UserMessage
from ..thinking_metadata import ThinkingMetadata
from ..tool_use_result import ToolUseResult


class UserTranscriptItem(BaseModel):
    type: Literal["user"] = "user"

    sessionId: str
    parentUuid: str | None = None
    uuid: str
    timestamp: datetime.datetime
    version: str

    cwd: str
    gitBranch: str = "HEAD"
    isSidechain: bool
    userType: Literal["external"] = "external"

    message: UserMessage

    agentId: str | None = None
    isCompactSummary: bool | None = None
    isMeta: bool | None = None
    isVisibleInTranscriptOnly: bool | None = None
    permissionMode: Literal["default"] | None = None
    planContent: str | None = None
    slug: str | None = None
    sourceToolUseID: str | None = None
    sourceToolAssistantUUID: str | None = None
    thinkingMetadata: ThinkingMetadata | None = None
    todos: list[Any] | None = None
    # Error message when toolUseResult is a string
    toolUseResult: ToolUseResult | str | None = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: str | datetime.datetime) -> datetime.datetime:
        if isinstance(v, str):
            return datetime.datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v
