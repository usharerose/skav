#!/usr/bin/env python3
"""
Progress message model
"""

import datetime
from typing import Literal

from pydantic import BaseModel, field_validator


class ProgressData(BaseModel):
    # TODO: check the enumerable values of `type`
    type: (
        Literal[
            "agent_progress",
            "bash_progress",
            "hook_progress",
            "mcp_progress",
            "search_results_received",
            "waiting_for_task",
        ]
        | str
    )

    elapsedTimeSeconds: int
    fullOutput: str
    output: str
    totalLines: int


class ProgressMessage(BaseModel):
    type: Literal["progress"] = "progress"

    uuid: str
    timestamp: datetime.datetime
    parentToolUseID: str | None = None
    toolUseID: str

    data: ProgressData

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: str | datetime.datetime) -> datetime.datetime:
        if isinstance(v, str):
            return datetime.datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v
