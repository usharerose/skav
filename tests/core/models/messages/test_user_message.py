#!/usr/bin/env python3
"""
Unit tests for UserMessage model
"""

from typing import Any, cast

import pytest

from vibehist.core.models.messages.user_message import UserMessage
from vibehist.core.models.messages.content import (
    DocumentContentItem,
    TextContentItem,
    ToolResultContentItem,
)


SAMPLE_USER_MESSAGE_STRING_CONTENT = {
    "role": "user",
    "content": (
        "Implement the following plan:\n\n# VibeHist Transcript JSON Schema Design\n\n"
        "## Context\n\n"
        "This document designs a comprehensive schema for Claude Code transcript JSONL data "
        "based on analysis of:\n"
        "1. Actual transcript data from `/Users/root/.claude/projects/-Users-root-workspace-project/`\n\n"
        "The goal is to understand the structure and patterns of Claude Code transcript data"
    ),
}

SAMPLE_USER_MESSAGE_TOOL_RESULT_SUCCESS = {
    "role": "user",
    "content": [
        {
            "tool_use_id": "call_98a174fc29634f1aa752b66f",
            "type": "tool_result",
            "content": (
                "     1→#!/usr/bin/env python3\n"
                '     2→"""\n'
                "     3→Type definitions for Claude Code Hook events\n"
                "     4→Based on official documentation: https://code.claude.com/docs/en/hooks\n"
            ),
        }
    ],
}

SAMPLE_USER_MESSAGE_TOOL_RESULT_ERROR = {
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "content": (
                "File does not exist. "
                "Note: your current working directory is /Users/root/workspace/project. "
                "Did you mean models?"
            ),
            "is_error": True,
            "tool_use_id": "call_d9860daaecc9416e94d7c2f3",
        }
    ],
}

SAMPLE_USER_MESSAGE_EMPTY_CONTENT = {
    "role": "user",
    "content": "",
}


SAMPLE_USER_MESSAGE_UNICODE_CONTENT = {
    "role": "user",
    "content": "可以为我解释下你实现的内容么",
}


SAMPLE_USER_MESSAGE_DOCUMENT = {
    "role": "user",
    "content": [
        {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": "JVBERi0xLjcKCjEgMCBvYmogICUgZW50cnkgcG9pbnQKPDwKICAvVHlwZSAvQ2F0YWxvZwog",
            },
        }
    ],
}


class TestUserMessage:
    """Test UserMessage model validation and parsing"""

    def test_required_fields_with_model_validate(self) -> None:
        """Test creating message using model_validate with real data"""
        message = UserMessage.model_validate(SAMPLE_USER_MESSAGE_STRING_CONTENT)

        assert message.role == "user"
        assert "VibeHist" in message.content
        assert "Transcript JSON Schema" in message.content

    def test_role_default_value(self) -> None:
        """Test that role has default value 'user'"""
        message = UserMessage.model_validate({"content": "Test message"})

        assert message.role == "user"

    def test_content_as_string_real_data(self) -> None:
        """Test message with string content using real data"""
        message = UserMessage.model_validate(SAMPLE_USER_MESSAGE_STRING_CONTENT)

        assert isinstance(message.content, str)
        assert "VibeHist" in message.content
        assert "/Users/root/.claude/projects/-Users-root-workspace-project/" in message.content

    def test_content_empty_string_real_data(self) -> None:
        """Test message with empty string content using real data"""
        message = UserMessage.model_validate(SAMPLE_USER_MESSAGE_EMPTY_CONTENT)

        assert message.content == ""

    def test_content_multiline_string_real_data(self) -> None:
        """Test message with multiline string content using real data"""
        message = UserMessage.model_validate(SAMPLE_USER_MESSAGE_STRING_CONTENT)

        assert "\n" in message.content
        assert "## Context" in message.content

    def test_content_unicode_string_real_data(self) -> None:
        """Test message with unicode string content using real data"""
        message = UserMessage.model_validate(SAMPLE_USER_MESSAGE_UNICODE_CONTENT)

        assert "可以为我解释" in message.content

    def test_content_as_list_of_text_items_with_model_validate(self) -> None:
        """Test message with list of TextContentItem using model_validate"""
        message_data = {
            "content": [
                {"type": "text", "text": "First message"},
                {"type": "text", "text": "Second message"},
            ]
        }
        message = UserMessage.model_validate(message_data)

        assert isinstance(message.content, list)
        assert len(message.content) == 2
        assert isinstance(message.content[0], TextContentItem)
        assert message.content[0].text == "First message"
        assert message.content[1].text == "Second message"

    def test_content_as_list_of_tool_result_items_real_data(self) -> None:
        """Test message with list of ToolResultContentItem using real data"""
        message = UserMessage.model_validate(SAMPLE_USER_MESSAGE_TOOL_RESULT_SUCCESS)

        assert isinstance(message.content, list)
        assert len(message.content) == 1
        assert isinstance(message.content[0], ToolResultContentItem)
        assert message.content[0].tool_use_id == "call_98a174fc29634f1aa752b66f"
        assert "#!/usr/bin/env python3" in message.content[0].content

    def test_content_as_list_of_document_items_with_model_validate(self) -> None:
        """Test message with list of DocumentContentItem using model_validate"""
        message = UserMessage.model_validate(SAMPLE_USER_MESSAGE_DOCUMENT)

        assert isinstance(message.content, list)
        assert len(message.content) == 1
        assert isinstance(message.content[0], DocumentContentItem)
        assert message.content[0].source.media_type == "application/pdf"

    def test_content_as_mixed_list_with_model_validate(self) -> None:
        """Test message with mixed content types using model_validate"""
        message_data = {
            "content": [
                {"type": "text", "text": "Here's the result:"},
                {
                    "type": "tool_result",
                    "tool_use_id": "tool-123",
                    "content": "Output",
                    "is_error": False,
                },
                {"type": "text", "text": "What's next?"},
            ]
        }
        message = UserMessage.model_validate(message_data)

        assert isinstance(message.content, list)
        assert len(message.content) == 3
        assert isinstance(message.content[0], TextContentItem)
        assert isinstance(message.content[1], ToolResultContentItem)
        assert isinstance(message.content[2], TextContentItem)
        assert message.content[0].text == "Here's the result:"
        assert message.content[1].tool_use_id == "tool-123"
        assert message.content[2].text == "What's next?"

    def test_content_empty_list_with_model_validate(self) -> None:
        """Test message with empty list content using model_validate"""
        message = UserMessage.model_validate({"content": []})

        assert message.content == []
        assert len(message.content) == 0

    def test_content_single_item_list_with_model_validate(self) -> None:
        """Test message with single item list using model_validate"""
        message_data = {"content": [{"type": "text", "text": "Single item"}]}
        message = UserMessage.model_validate(message_data)

        assert isinstance(message.content, list)
        assert len(message.content) == 1
        assert message.content[0].text == "Single item"

    def test_tool_result_with_is_error_real_data(self) -> None:
        """Test tool result content with is_error field using real data"""
        message = UserMessage.model_validate(SAMPLE_USER_MESSAGE_TOOL_RESULT_ERROR)

        assert isinstance(message.content, list)
        assert isinstance(message.content[0], ToolResultContentItem)
        assert message.content[0].is_error is True
        assert "File does not exist" in message.content[0].content

    def test_document_with_full_source_with_model_validate(self) -> None:
        """Test document content with full source data using model_validate"""
        message = UserMessage.model_validate(SAMPLE_USER_MESSAGE_DOCUMENT)

        assert isinstance(message.content, list)
        assert isinstance(message.content[0], DocumentContentItem)
        assert message.content[0].source.type == "base64"
        assert message.content[0].source.media_type == "application/pdf"

    def test_invalid_role_rejected(self) -> None:
        """Test that invalid role is rejected"""
        with pytest.raises(ValueError):
            UserMessage(role=cast(Any, "assistant"), content="Test")

    def test_invalid_text_item_type_rejected(self) -> None:
        """Test that invalid type in text content item is rejected"""
        with pytest.raises(ValueError):
            UserMessage(content=[cast(Any, {"type": "invalid", "text": "Test"})])

    def test_invalid_tool_result_item_type_rejected(self) -> None:
        """Test that invalid type in tool result content item is rejected"""
        with pytest.raises(ValueError):
            UserMessage(
                content=[cast(Any, {"type": "invalid", "tool_use_id": "123", "content": "Test"})]
            )

    def test_model_dump_string_content_real_data(self) -> None:
        """Test model_dump with string content using real data"""
        message = UserMessage.model_validate(SAMPLE_USER_MESSAGE_STRING_CONTENT)

        dumped = message.model_dump()

        assert dumped["role"] == "user"
        assert "VibeHist" in dumped["content"]
        assert isinstance(dumped["content"], str)

    def test_model_dump_list_content_real_data(self) -> None:
        """Test model_dump with list content using real data"""
        message = UserMessage.model_validate(SAMPLE_USER_MESSAGE_TOOL_RESULT_SUCCESS)

        dumped = message.model_dump()

        assert dumped["role"] == "user"
        assert isinstance(dumped["content"], list)
        assert len(dumped["content"]) == 1
        assert dumped["content"][0]["tool_use_id"] == "call_98a174fc29634f1aa752b66f"

    def test_model_dump_json_real_data(self) -> None:
        """Test model_dump_json returns JSON string using real data"""
        message = UserMessage.model_validate(SAMPLE_USER_MESSAGE_UNICODE_CONTENT)

        json_str = message.model_dump_json()

        assert isinstance(json_str, str)
        assert "user" in json_str
        assert "可以为我解释" in json_str
