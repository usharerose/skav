#!/usr/bin/env python3
"""
Assistant transcript item model
"""

import datetime
from typing import Literal

from pydantic import BaseModel, field_validator

from ..messages import AssistantMessage


class AssistantTranscriptItem(BaseModel):
    type: Literal["assistant"] = "assistant"

    sessionId: str
    parentUuid: str
    uuid: str
    timestamp: datetime.datetime
    version: str

    cwd: str
    gitBranch: str = "HEAD"
    isSidechain: bool

    # TODO: check the enumerable values of `userType`
    userType: Literal["external"] | str

    message: AssistantMessage

    agentId: str | None = None
    error: str | None = None
    isApiErrorMessage: bool | None = None
    slug: str | None = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: str | datetime.datetime) -> datetime.datetime:
        if isinstance(v, str):
            return datetime.datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v
