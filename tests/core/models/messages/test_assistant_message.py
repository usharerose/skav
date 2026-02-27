#!/usr/bin/env python3
"""
Unit tests for AssistantMessage model
"""

from typing import Any

import pytest

from vibehist.core.models.messages.assistant_message import AssistantMessage

SAMPLE_ASSISTANT_MESSAGE_TEXT_ONLY: dict[str, Any] = {
    "id": "msg_2026022222573947d4e82262af4dc8",
    "type": "message",
    "role": "assistant",
    "model": "glm-4.7",
    "content": [
        {
            "type": "text",
            "text": (
                "I'll analyze the plan and implement the Pydantic models "
                "for VibeHist transcript JSON schema."
            ),
        }
    ],
    "stop_reason": None,
    "stop_sequence": None,
    "usage": {
        "input_tokens": 0,
        "output_tokens": 0,
    },
}

SAMPLE_ASSISTANT_MESSAGE_WITH_TOOL_USE: dict[str, Any] = {
    "id": "msg_2026022222573947d4e82262af4dc8",
    "type": "message",
    "role": "assistant",
    "model": "glm-4.7",
    "content": [
        {
            "type": "tool_use",
            "id": "call_d9860daaecc9416e94d7c2f3",
            "name": "Read",
            "input": {
                "file_path": ("/Users/root/workspace/project/core/models.py"),
            },
        }
    ],
    "stop_reason": None,
    "stop_sequence": None,
    "usage": {
        "input_tokens": 0,
        "output_tokens": 0,
    },
}

SAMPLE_ASSISTANT_MESSAGE_STOP_REASON_TOOL_USE: dict[str, Any] = {
    "id": "msg_test",
    "type": "message",
    "role": "assistant",
    "model": "glm-4.7",
    "content": [
        {
            "type": "tool_use",
            "id": "call_test",
            "name": "Bash",
            "input": {"command": "echo test"},
        }
    ],
    "stop_reason": "tool_use",
    "stop_sequence": None,
    "usage": {
        "input_tokens": 100,
        "output_tokens": 50,
    },
}


class TestAssistantMessage:
    """Test AssistantMessage model validation and parsing"""

    def test_required_fields_real_data(self) -> None:
        """Test that all required fields are present using real data"""
        message = AssistantMessage.model_validate(SAMPLE_ASSISTANT_MESSAGE_TEXT_ONLY)

        assert message.type == "message"
        assert message.role == "assistant"
        assert message.id == "msg_2026022222573947d4e82262af4dc8"
        assert message.model == "glm-4.7"
        assert message.stop_reason is None
        assert message.stop_sequence is None
        assert isinstance(message.content, list)

    def test_usage_field_real_data(self) -> None:
        """Test usage field using real data"""
        message = AssistantMessage.model_validate(SAMPLE_ASSISTANT_MESSAGE_TEXT_ONLY)

        assert message.usage.input_tokens == 0
        assert message.usage.output_tokens == 0

    def test_content_with_text_real_data(self) -> None:
        """Test content with text item using real data"""
        message = AssistantMessage.model_validate(SAMPLE_ASSISTANT_MESSAGE_TEXT_ONLY)

        assert isinstance(message.content, list)
        assert len(message.content) == 1
        assert message.content[0].type == "text"
        assert "Pydantic models" in message.content[0].text

    def test_content_with_tool_use_real_data(self) -> None:
        """Test content with tool_use item using real data"""
        message = AssistantMessage.model_validate(SAMPLE_ASSISTANT_MESSAGE_WITH_TOOL_USE)

        assert isinstance(message.content, list)
        assert len(message.content) == 1
        assert message.content[0].type == "tool_use"
        assert message.content[0].id == "call_d9860daaecc9416e94d7c2f3"
        assert message.content[0].name == "Read"
        assert (
            message.content[0].input["file_path"] == "/Users/root/workspace/project/core/models.py"
        )

    def test_stop_reason_none(self) -> None:
        """Test stop_reason as None"""
        message = AssistantMessage.model_validate(SAMPLE_ASSISTANT_MESSAGE_TEXT_ONLY)

        assert message.stop_reason is None

    def test_stop_reason_tool_use(self) -> None:
        """Test stop_reason as 'tool_use'"""
        message = AssistantMessage.model_validate(SAMPLE_ASSISTANT_MESSAGE_STOP_REASON_TOOL_USE)

        assert message.stop_reason == "tool_use"

    def test_stop_sequence_none(self) -> None:
        """Test stop_sequence as None"""
        message = AssistantMessage.model_validate(SAMPLE_ASSISTANT_MESSAGE_TEXT_ONLY)

        assert message.stop_sequence is None

    def test_type_default_value(self) -> None:
        """Test that type field has default value 'message'"""
        message = AssistantMessage.model_validate(
            {
                "id": "msg_test",
                "role": "assistant",
                "model": "test-model",
                "content": [{"type": "text", "text": "test"}],
                "stop_reason": None,
                "stop_sequence": None,
                "usage": {"input_tokens": 0, "output_tokens": 0},
            }
        )
        assert message.type == "message"

    def test_role_default_value(self) -> None:
        """Test that role field has default value 'assistant'"""
        message = AssistantMessage.model_validate(
            {
                "id": "msg_test",
                "model": "test-model",
                "content": [{"type": "text", "text": "test"}],
                "stop_reason": None,
                "stop_sequence": None,
                "usage": {"input_tokens": 0, "output_tokens": 0},
            }
        )
        assert message.role == "assistant"

    def test_invalid_stop_reason_rejected(self) -> None:
        """Test that invalid stop_reason is rejected"""
        from typing import cast

        data = {
            **SAMPLE_ASSISTANT_MESSAGE_TEXT_ONLY,
            "stop_reason": cast(Any, "invalid_reason"),
        }
        with pytest.raises(ValueError):
            AssistantMessage.model_validate(data)

    def test_invalid_role_rejected(self) -> None:
        """Test that invalid role is rejected"""
        from typing import cast

        data = {
            **SAMPLE_ASSISTANT_MESSAGE_TEXT_ONLY,
            "role": cast(Any, "user"),
        }
        with pytest.raises(ValueError):
            AssistantMessage.model_validate(data)
