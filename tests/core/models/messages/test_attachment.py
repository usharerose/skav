#!/usr/bin/env python3
"""
Unit tests for AttachmentMessage model
"""

from typing import Any

from vibehist.core.models.messages.attachment import (
    AttachmentMessage,
    CriticalSystemReminderAttachment,
    PlanModeReminderAttachment,
    TodoReminderAttachment,
)

ATTACHMENT_CRITICAL_SYSTEM_REMINDER: dict[str, Any] = {
    "type": "attachment",
    "uuid": "attachment-uuid-001",
    "timestamp": "2026-02-27T10:00:00.000Z",
    "attachment": {
        "type": "critical_system_reminder",
        "content": "This is a critical reminder",
    },
}

ATTACHMENT_PLAN_MODE_REMINDER_FULL: dict[str, Any] = {
    "type": "attachment",
    "uuid": "attachment-uuid-002",
    "timestamp": "2026-02-27T10:00:01.000Z",
    "attachment": {
        "type": "plan_mode_reminder",
        "isSubAgent": False,
        "planExists": True,
        "planFilePath": "/path/to/plan.md",
        "reminderType": "full",
    },
}

ATTACHMENT_PLAN_MODE_REMINDER_SPARSE: dict[str, Any] = {
    "type": "attachment",
    "uuid": "attachment-uuid-003",
    "timestamp": "2026-02-27T10:00:02.000Z",
    "attachment": {
        "type": "plan_mode_reminder",
        "isSubAgent": True,
        "planExists": False,
        "planFilePath": "/path/to/plan.md",
        "reminderType": "sparse",
    },
}

ATTACHMENT_TODO_REMINDER: dict[str, Any] = {
    "type": "attachment",
    "uuid": "attachment-uuid-004",
    "timestamp": "2026-02-27T10:00:03.000Z",
    "attachment": {
        "type": "todo_reminder",
        "content": [
            {"task": "Implement feature X", "done": False},
            {"task": "Write tests", "done": True},
        ],
        "itemCount": 2,
    },
}


class TestCriticalSystemReminderAttachment:
    """Test CriticalSystemReminderAttachment model"""

    def test_critical_system_reminder(self) -> None:
        """Test creating CriticalSystemReminderAttachment"""
        attachment = CriticalSystemReminderAttachment.model_validate(
            ATTACHMENT_CRITICAL_SYSTEM_REMINDER["attachment"]
        )

        assert attachment.type == "critical_system_reminder"
        assert attachment.content == "This is a critical reminder"

    def test_type_default_value(self) -> None:
        """Test that type has default value 'critical_system_reminder'"""
        attachment = CriticalSystemReminderAttachment.model_validate({"content": "Test content"})

        assert attachment.type == "critical_system_reminder"


class TestPlanModeReminderAttachment:
    """Test PlanModeReminderAttachment model"""

    def test_plan_mode_reminder_full(self) -> None:
        """Test creating PlanModeReminderAttachment with full reminder type"""
        attachment = PlanModeReminderAttachment.model_validate(
            ATTACHMENT_PLAN_MODE_REMINDER_FULL["attachment"]
        )

        assert attachment.type == "plan_mode_reminder"
        assert attachment.isSubAgent is False
        assert attachment.planExists is True
        assert attachment.planFilePath == "/path/to/plan.md"
        assert attachment.reminderType == "full"

    def test_plan_mode_reminder_sparse(self) -> None:
        """Test creating PlanModeReminderAttachment with sparse reminder type"""
        attachment = PlanModeReminderAttachment.model_validate(
            ATTACHMENT_PLAN_MODE_REMINDER_SPARSE["attachment"]
        )

        assert attachment.type == "plan_mode_reminder"
        assert attachment.isSubAgent is True
        assert attachment.planExists is False
        assert attachment.reminderType == "sparse"

    def test_type_default_value(self) -> None:
        """Test that type has default value 'plan_mode_reminder'"""
        attachment = PlanModeReminderAttachment.model_validate(
            {
                "isSubAgent": False,
                "planExists": True,
                "planFilePath": "/test/plan.md",
                "reminderType": "full",
            }
        )

        assert attachment.type == "plan_mode_reminder"


class TestTodoReminderAttachment:
    """Test TodoReminderAttachment model"""

    def test_todo_reminder(self) -> None:
        """Test creating TodoReminderAttachment"""
        attachment = TodoReminderAttachment.model_validate(ATTACHMENT_TODO_REMINDER["attachment"])

        assert attachment.type == "todo_reminder"
        assert len(attachment.content) == 2
        assert attachment.itemCount == 2

    def test_content_list(self) -> None:
        """Test content field is a list"""
        attachment = TodoReminderAttachment.model_validate(ATTACHMENT_TODO_REMINDER["attachment"])

        assert isinstance(attachment.content, list)
        assert attachment.content[0] == {"task": "Implement feature X", "done": False}

    def test_type_default_value(self) -> None:
        """Test that type has default value 'todo_reminder'"""
        attachment = TodoReminderAttachment.model_validate({"content": [], "itemCount": 0})

        assert attachment.type == "todo_reminder"


class TestAttachmentMessage:
    """Test AttachmentMessage model"""

    def test_critical_system_reminder_message(self) -> None:
        """Test AttachmentMessage with CriticalSystemReminderAttachment"""
        message = AttachmentMessage.model_validate(ATTACHMENT_CRITICAL_SYSTEM_REMINDER)

        assert message.type == "attachment"
        assert message.uuid == "attachment-uuid-001"
        assert isinstance(message.attachment, CriticalSystemReminderAttachment)
        assert message.attachment.content == "This is a critical reminder"

    def test_plan_mode_reminder_message(self) -> None:
        """Test AttachmentMessage with PlanModeReminderAttachment"""
        message = AttachmentMessage.model_validate(ATTACHMENT_PLAN_MODE_REMINDER_FULL)

        assert message.type == "attachment"
        assert isinstance(message.attachment, PlanModeReminderAttachment)
        assert message.attachment.reminderType == "full"

    def test_todo_reminder_message(self) -> None:
        """Test AttachmentMessage with TodoReminderAttachment"""
        message = AttachmentMessage.model_validate(ATTACHMENT_TODO_REMINDER)

        assert message.type == "attachment"
        assert isinstance(message.attachment, TodoReminderAttachment)
        assert message.attachment.itemCount == 2

    def test_type_default_value(self) -> None:
        """Test that type has default value 'attachment'"""
        message = AttachmentMessage.model_validate(ATTACHMENT_CRITICAL_SYSTEM_REMINDER)

        assert message.type == "attachment"

    def test_timestamp_parsing(self) -> None:
        """Test ISO 8601 timestamp parsing"""
        message = AttachmentMessage.model_validate(ATTACHMENT_CRITICAL_SYSTEM_REMINDER)

        import datetime

        assert isinstance(message.timestamp, datetime.datetime)
        assert message.timestamp.year == 2026
        assert message.timestamp.month == 2
        assert message.timestamp.day == 27
