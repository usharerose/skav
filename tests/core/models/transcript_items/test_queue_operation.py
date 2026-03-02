#!/usr/bin/env python3
"""
Unit tests for QueueOperationTranscriptItem model
"""

from typing import Any

import pytest

from skav.core.models.transcript_items.queue_operation import (
    QueueOperationTranscriptItem,
)

SAMPLE_QUEUE_OPERATION_ENQUEUE: dict[str, Any] = {
    "type": "queue-operation",
    "operation": "enqueue",
    "timestamp": "2026-02-27T08:22:03.232Z",
    "sessionId": "6536ce47-699c-4e07-bb3c-6312f8789222",
    "content": (
        "{"
        '"task_id":"b7f6f80",'
        '"tool_use_id":"call_67306ff6dd1a4e6c8b50055e",'
        '"description":"Search for addressing_style config",'
        '"task_type":"local_bash"'
        "}"
    ),
}

SAMPLE_QUEUE_OPERATION_REMOVE: dict[str, Any] = {
    "type": "queue-operation",
    "operation": "remove",
    "timestamp": "2026-02-27T08:30:25.134Z",
    "sessionId": "6536ce47-699c-4e07-bb3c-6312f8789222",
}

SAMPLE_QUEUE_OPERATION_POPALL: dict[str, Any] = {
    "type": "queue-operation",
    "operation": "popAll",
    "timestamp": "2026-02-17T11:49:23.234Z",
    "sessionId": "bd3743ba-e026-425e-9abe-687dd061aaa4",
    "content": "/exit",
}


class TestQueueOperationTranscriptItem:
    """Test QueueOperationTranscriptItem model"""

    def test_required_fields(self) -> None:
        """Test creating QueueOperationTranscriptItem using model_validate"""
        item = QueueOperationTranscriptItem.model_validate(SAMPLE_QUEUE_OPERATION_ENQUEUE)

        assert item.type == "queue-operation"
        assert item.operation == "enqueue"
        assert item.sessionId == "6536ce47-699c-4e07-bb3c-6312f8789222"

    def test_type_default_value(self) -> None:
        """Test that type has default value 'queue-operation'"""
        item = QueueOperationTranscriptItem.model_validate(SAMPLE_QUEUE_OPERATION_ENQUEUE)

        assert item.type == "queue-operation"

    def test_operation_enqueue(self) -> None:
        """Test with enqueue operation"""
        item = QueueOperationTranscriptItem.model_validate(SAMPLE_QUEUE_OPERATION_ENQUEUE)

        assert item.operation == "enqueue"

    def test_operation_remove(self) -> None:
        """Test with remove operation"""
        item = QueueOperationTranscriptItem.model_validate(SAMPLE_QUEUE_OPERATION_REMOVE)

        assert item.operation == "remove"

    def test_operation_popAll(self) -> None:
        """Test with popAll operation"""
        item = QueueOperationTranscriptItem.model_validate(SAMPLE_QUEUE_OPERATION_POPALL)

        assert item.operation == "popAll"

    def test_timestamp_parsing(self) -> None:
        """Test ISO 8601 timestamp parsing"""
        item = QueueOperationTranscriptItem.model_validate(SAMPLE_QUEUE_OPERATION_ENQUEUE)

        import datetime

        assert isinstance(item.timestamp, datetime.datetime)
        assert item.timestamp.year == 2026
        assert item.timestamp.month == 2
        assert item.timestamp.day == 27
        assert item.timestamp.hour == 8
        assert item.timestamp.minute == 22
        assert item.timestamp.second == 3

    def test_content_with_json_string(self) -> None:
        """Test content field with JSON string"""
        item = QueueOperationTranscriptItem.model_validate(SAMPLE_QUEUE_OPERATION_ENQUEUE)

        assert item.content is not None
        assert "task_id" in item.content
        assert "b7f6f80" in item.content
        assert "local_bash" in item.content

    def test_content_with_plain_string(self) -> None:
        """Test content field with plain string"""
        item = QueueOperationTranscriptItem.model_validate(SAMPLE_QUEUE_OPERATION_POPALL)

        assert item.content == "/exit"

    def test_content_none(self) -> None:
        """Test content field can be None (remove operation has no content)"""
        item = QueueOperationTranscriptItem.model_validate(SAMPLE_QUEUE_OPERATION_REMOVE)

        assert item.content is None

    def test_dequeue_operation(self) -> None:
        """Test with dequeue operation (from documentation)"""
        synthetic_data = {
            "type": "queue-operation",
            "operation": "dequeue",
            "timestamp": "2025-11-17T23:57:17.573Z",
            "sessionId": "7acd37a8-2745-4b58-a8a9-46164b22ad9e",
        }
        item = QueueOperationTranscriptItem.model_validate(synthetic_data)

        assert item.operation == "dequeue"

    @pytest.mark.skip(
        reason="TODO: implement when the enumerable values of `operation` are defined"
    )
    def test_invalid_operation_rejected(self) -> None:
        """Test that invalid operation is rejected"""
        invalid_data = {
            **SAMPLE_QUEUE_OPERATION_ENQUEUE,
            "operation": "invalid_operation",
        }
        with pytest.raises(Exception):
            QueueOperationTranscriptItem.model_validate(invalid_data)
