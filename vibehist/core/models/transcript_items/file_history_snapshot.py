#!/usr/bin/env python3
"""
File history snapshot transcript item model
"""

import datetime
from typing import Literal

from pydantic import BaseModel, field_validator


class TrackedFileBackup(BaseModel):
    backupFileName: str
    backupTime: datetime.datetime
    version: int

    @field_validator("backupTime", mode="before")
    @classmethod
    def parse_backup_time(cls, v: str | datetime.datetime) -> datetime.datetime:
        if isinstance(v, str):
            return datetime.datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class Snapshot(BaseModel):
    messageId: str

    # key is the absolute or relative file path
    trackedFileBackups: dict[str, TrackedFileBackup]

    timestamp: datetime.datetime

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: str | datetime.datetime) -> datetime.datetime:
        if isinstance(v, str):
            return datetime.datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class FileHistorySnapshotTranscriptItem(BaseModel):
    type: Literal["file-history-snapshot"] = "file-history-snapshot"

    isSnapshotUpdate: bool
    messageId: str
    snapshot: Snapshot
