#!/usr/bin/env python3
"""
Unit tests for AssistantMessage model
"""

from typing import Any, cast

import pytest

from skav.transcripts.models.contents import (
    ServerToolUseContentItem,
    TextContentItem,
    ThinkingContentItem,
    ToolUseContentItem,
)
from skav.transcripts.models.messages.assistant import AssistantMessage

ASSISTANT_MESSAGE_TEXT: dict[str, Any] = {
    "id": "msg_2026022410205336ab47e8f8734425",
    "type": "message",
    "role": "assistant",
    "model": "glm-4.7",
    "content": [
        {
            "type": "text",
            "text": "I'll help you find the information about configuration.",
        }
    ],
    "stop_reason": None,
    "stop_sequence": None,
    "usage": {
        "input_tokens": 100,
        "output_tokens": 50,
    },
}

ASSISTANT_MESSAGE_TOOL_USE: dict[str, Any] = {
    "id": "msg_20260228181708897b1498148641ce",
    "type": "message",
    "role": "assistant",
    "model": "glm-4.7",
    "content": [
        {
            "type": "tool_use",
            "id": "call_f9a34faddbe441b18b8d1964",
            "name": "Bash",
            "input": {
                "command": "echo 'hello world'",
            },
        }
    ],
    "stop_reason": "tool_use",
    "stop_sequence": None,
    "usage": {
        "input_tokens": 4270,
        "output_tokens": 150,
    },
}

ASSISTANT_MESSAGE_THINKING: dict[str, Any] = {
    "id": "msg_20260211091823ead29ab0958947b9",
    "type": "message",
    "role": "assistant",
    "model": "glm-4.7",
    "content": [
        {
            "type": "thinking",
            "thinking": (
                "User is asking about finding code in the codebase. I should explore the codebase."
            ),
            "signature": "",
        }
    ],
    "stop_reason": None,
    "stop_sequence": None,
    "usage": {
        "input_tokens": 200,
        "output_tokens": 50,
    },
}

ASSISTANT_MESSAGE_SERVER_TOOL_USE: dict[str, Any] = {
    "id": "msg_2026022410261163a9e4c2ee9e4c3b",
    "type": "message",
    "role": "assistant",
    "model": "glm-4.7",
    "content": [
        {
            "type": "server_tool_use",
            "id": "call_127247113f964b76b06cfbf2",
            "name": "webReader",
            "input": {
                "url": "https://example.com",
            },
        }
    ],
    "stop_reason": None,
    "stop_sequence": None,
    "usage": {
        "input_tokens": 500,
        "output_tokens": 100,
    },
}

ASSISTANT_MESSAGE_END_TURN: dict[str, Any] = {
    "id": "msg_end_turn",
    "type": "message",
    "role": "assistant",
    "model": "glm-4.7",
    "content": [
        {
            "type": "text",
            "text": "Here's the result you requested.",
        }
    ],
    "stop_reason": "end_turn",
    "stop_sequence": None,
    "usage": {
        "input_tokens": 1000,
        "output_tokens": 200,
    },
}

ASSISTANT_MESSAGE_DIFFERENT_MODEL: dict[str, Any] = {
    "id": "msg_air_model",
    "type": "message",
    "role": "assistant",
    "model": "glm-4.5-air",
    "content": [
        {
            "type": "text",
            "text": "Response from air model",
        }
    ],
    "stop_reason": None,
    "stop_sequence": None,
    "usage": {
        "input_tokens": 100,
        "output_tokens": 50,
    },
}


class TestAssistantMessage:
    """Test AssistantMessage model validation and parsing"""

    def test_required_fields(self) -> None:
        """Test that all required fields are present"""
        message = AssistantMessage.model_validate(ASSISTANT_MESSAGE_TEXT)

        assert message.type == "message"
        assert message.role == "assistant"
        assert message.id == "msg_2026022410205336ab47e8f8734425"
        assert message.model == "glm-4.7"
        assert message.stop_reason is None
        assert message.stop_sequence is None
        assert isinstance(message.content, list)

    def test_usage_field(self) -> None:
        """Test usage field"""
        message = AssistantMessage.model_validate(ASSISTANT_MESSAGE_TEXT)

        assert message.usage.input_tokens == 100
        assert message.usage.output_tokens == 50

    def test_content_with_text(self) -> None:
        """Test content with text item"""
        message = AssistantMessage.model_validate(ASSISTANT_MESSAGE_TEXT)

        assert isinstance(message.content, list)
        assert len(message.content) == 1
        content_item, *_ = message.content
        assert isinstance(content_item, TextContentItem)
        assert "information" in content_item.text

    def test_content_with_tool_use(self) -> None:
        """Test content with tool_use item"""
        message = AssistantMessage.model_validate(ASSISTANT_MESSAGE_TOOL_USE)

        assert isinstance(message.content, list)
        assert len(message.content) == 1
        content_item, *_ = message.content
        assert isinstance(content_item, ToolUseContentItem)
        assert content_item.id == "call_f9a34faddbe441b18b8d1964"
        assert content_item.name == "Bash"

    def test_content_with_thinking(self) -> None:
        """Test content with thinking item"""
        message = AssistantMessage.model_validate(ASSISTANT_MESSAGE_THINKING)

        assert isinstance(message.content, list)
        assert len(message.content) == 1
        content_item, *_ = message.content
        assert isinstance(content_item, ThinkingContentItem)
        assert "codebase" in content_item.thinking

    def test_content_with_server_tool_use(self) -> None:
        """Test content with server_tool_use item"""
        message = AssistantMessage.model_validate(ASSISTANT_MESSAGE_SERVER_TOOL_USE)

        assert isinstance(message.content, list)
        assert len(message.content) == 1
        content_item, *_ = message.content
        assert isinstance(content_item, ServerToolUseContentItem)
        assert content_item.name == "webReader"

    def test_stop_reason_none(self) -> None:
        """Test stop_reason as None"""
        message = AssistantMessage.model_validate(ASSISTANT_MESSAGE_TEXT)

        assert message.stop_reason is None

    def test_stop_reason_tool_use(self) -> None:
        """Test stop_reason as 'tool_use'"""
        message = AssistantMessage.model_validate(ASSISTANT_MESSAGE_TOOL_USE)

        assert message.stop_reason == "tool_use"

    def test_stop_reason_end_turn(self) -> None:
        """Test stop_reason as 'end_turn'"""
        message = AssistantMessage.model_validate(ASSISTANT_MESSAGE_END_TURN)

        assert message.stop_reason == "end_turn"

    def test_stop_sequence_none(self) -> None:
        """Test stop_sequence as None"""
        message = AssistantMessage.model_validate(ASSISTANT_MESSAGE_TEXT)

        assert message.stop_sequence is None

    def test_different_model(self) -> None:
        """Test with different model (glm-4.5-air)"""
        message = AssistantMessage.model_validate(ASSISTANT_MESSAGE_DIFFERENT_MODEL)

        assert message.model == "glm-4.5-air"

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

    @pytest.mark.skip(
        reason="TODO: implement when the enumerable values of `stop_reason` are defined"
    )
    def test_invalid_stop_reason_rejected(self) -> None:
        """Test that invalid stop_reason is rejected"""
        data = {
            **ASSISTANT_MESSAGE_TEXT,
            "stop_reason": cast(Any, "invalid_reason"),
        }
        with pytest.raises(ValueError):
            AssistantMessage.model_validate(data)

    def test_invalid_role_rejected(self) -> None:
        """Test that invalid role is rejected"""
        data = {
            **ASSISTANT_MESSAGE_TEXT,
            "role": cast(Any, "user"),
        }
        with pytest.raises(ValueError):
            AssistantMessage.model_validate(data)
