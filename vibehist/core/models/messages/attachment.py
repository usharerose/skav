#!/usr/bin/env python3
"""
Attachment message model
"""

import datetime
from typing import Any, Literal

from pydantic import BaseModel, field_validator


class CriticalSystemReminderAttachment(BaseModel):
    type: Literal["critical_system_reminder"] = "critical_system_reminder"

    content: str


class PlanModeReminderAttachment(BaseModel):
    type: Literal["plan_mode_reminder"] = "plan_mode_reminder"

    isSubAgent: bool
    planExists: bool
    planFilePath: str
    reminderType: Literal["full", "sparse"]


class TodoReminderAttachment(BaseModel):
    type: Literal["todo_reminder"] = "todo_reminder"

    content: list[Any]  # TODO: check the data type of `content`
    itemCount: int


class AttachmentMessage(BaseModel):
    type: Literal["attachment"] = "attachment"

    uuid: str
    timestamp: datetime.datetime

    attachment: (
        CriticalSystemReminderAttachment | PlanModeReminderAttachment | TodoReminderAttachment
    )

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: str | datetime.datetime) -> datetime.datetime:
        if isinstance(v, str):
            return datetime.datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v
