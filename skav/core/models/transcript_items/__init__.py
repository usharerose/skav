#!/usr/bin/env python3
"""
Transcript Item Models

This package defines Pydantic models for all types of items that can appear
in Claude Code transcript files. Each line in a JSONL transcript file is
validated against one of these item types.

Transcript Item Types:

Conversation Items:
    - UserTranscriptItem: User messages and prompts
    - AssistantTranscriptItem: AI assistant responses

Progress Items:
    - ProgressTranscriptItem: Task progress updates with subject and description

System Items:
    - SystemSyntheticTranscriptItem: System-generated synthetic events
    - SystemLocalCommandTranscriptItem: Local command executions
    - SystemTurnDurationTranscriptItem: Turn timing information
    - SystemApiErrorTranscriptItem: API error events
    - SystemCompactBoundaryTranscriptItem: Transcript compaction boundaries
    - SystemMicrocompactBoundaryTranscriptItem: Micro-compaction boundaries
    - SystemStopHookSummaryTranscriptItem: Session end summaries

Operation Items:
    - QueueOperationTranscriptItem: Task queue operations (create, update, delete)
    - FileHistorySnapshotTranscriptItem: File change tracking snapshots
    - SummaryTranscriptItem: Session summaries

Type Discrimination:
    TranscriptItemType is a discriminated union of all item types.
    WrappedTranscriptItem is a RootModel wrapper for validation.

Usage:
    >>> from skav.core.models import WrappedTranscriptItem
    >>> item = WrappedTranscriptItem.model_validate(json_dict)
    >>> # item.root is the actual discriminated union type
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
