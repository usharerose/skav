#!/usr/bin/env python3
"""
Queue operation transcript item model
"""

import datetime
from typing import Literal

from pydantic import BaseModel, field_validator


class QueueOperationTranscriptItem(BaseModel):
    type: Literal["queue-operation"] = "queue-operation"

    operation: Literal["enqueue", "dequeue", "remove", "popAll"]
    sessionId: str
    timestamp: datetime.datetime

    # could be
    # - JSON string
    # - natural language
    # - None for `remove` operation
    content: str | None = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: str | datetime.datetime) -> datetime.datetime:
        if isinstance(v, str):
            return datetime.datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v
