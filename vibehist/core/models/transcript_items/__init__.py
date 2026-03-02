#!/usr/bin/env python3
"""
Claude Code local type-specific transcript models
"""

from pydantic import RootModel

from .assistant import AssistantTranscriptItem
from .file_history_snapshot import FileHistorySnapshotTranscriptItem
from .progress import ProgressTranscriptItem
from .queue_operation import QueueOperationTranscriptItem
from .summary import SummaryTranscriptItem
from .system import (
    SystemApiErrorTranscriptItem,
    SystemCompactBoundaryTranscriptItem,
    SystemLocalCommandTranscriptItem,
    SystemMicrocompactBoundaryTranscriptItem,
    SystemStopHookSummaryTranscriptItem,
    SystemSyntheticTranscriptItem,
    SystemTurnDurationTranscriptItem,
)
from .user import UserTranscriptItem

__all__ = [
    "AssistantTranscriptItem",
    "FileHistorySnapshotTranscriptItem",
    "ProgressTranscriptItem",
    "QueueOperationTranscriptItem",
    "SummaryTranscriptItem",
    "SystemApiErrorTranscriptItem",
    "SystemCompactBoundaryTranscriptItem",
    "SystemLocalCommandTranscriptItem",
    "SystemMicrocompactBoundaryTranscriptItem",
    "SystemStopHookSummaryTranscriptItem",
    "SystemTurnDurationTranscriptItem",
    "SystemSyntheticTranscriptItem",
    "TranscriptItemType",
    "UserTranscriptItem",
    "WrappedTranscriptItem",
]


TranscriptItemType = (
    AssistantTranscriptItem
    | FileHistorySnapshotTranscriptItem
    | ProgressTranscriptItem
    | QueueOperationTranscriptItem
    | SummaryTranscriptItem
    | SystemApiErrorTranscriptItem
    | SystemCompactBoundaryTranscriptItem
    | SystemLocalCommandTranscriptItem
    | SystemMicrocompactBoundaryTranscriptItem
    | SystemStopHookSummaryTranscriptItem
    | SystemTurnDurationTranscriptItem
    | SystemSyntheticTranscriptItem
    | UserTranscriptItem
)


WrappedTranscriptItem = RootModel[TranscriptItemType]
