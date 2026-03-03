#!/usr/bin/env python3
"""
Unit tests for UserMessage model
"""

from typing import Any, cast

import pytest

from skav.transcripts.models.contents import (
    DocumentContentItem,
    TextContentItem,
    ToolResultContentItem,
)
from skav.transcripts.models.messages.user import UserMessage

USER_MESSAGE_STRING_CONTENT: dict[str, Any] = {
    "role": "user",
    "content": "Implement the following feature: support multi-type transcript items.",
}

USER_MESSAGE_EMPTY_CONTENT: dict[str, Any] = {
    "role": "user",
    "content": "",
}

USER_MESSAGE_UNICODE_CONTENT: dict[str, Any] = {
    "role": "user",
    "content": "可以为我解释下你实现的内容么",
}

USER_MESSAGE_TOOL_RESULT_SUCCESS: dict[str, Any] = {
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": "call_98a174fc29634f1aa752b66f",
            "content": (
                "     1→#!/usr/bin/env python3\n"
                '     2→"""\n'
                "     3→Type definitions for Claude Code Hook events\n"
                "     4→Based on official documentation\n"
            ),
        }
    ],
}

USER_MESSAGE_TOOL_RESULT_ERROR: dict[str, Any] = {
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

USER_MESSAGE_TEXT_ITEMS: dict[str, Any] = {
    "role": "user",
    "content": [
        {"type": "text", "text": "First message"},
        {"type": "text", "text": "Second message"},
    ],
}

USER_MESSAGE_DOCUMENT: dict[str, Any] = {
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

USER_MESSAGE_MIXED_CONTENT: dict[str, Any] = {
    "role": "user",
    "content": [
        {"type": "text", "text": "Here's the result:"},
        {
            "type": "tool_result",
            "tool_use_id": "tool-123",
            "content": "Output",
            "is_error": False,
        },
        {"type": "text", "text": "What's next?"},
    ],
}


class TestUserMessage:
    """Test UserMessage model validation and parsing"""

    def test_required_fields(self) -> None:
        """Test creating message with required fields"""
        message = UserMessage.model_validate(USER_MESSAGE_STRING_CONTENT)

        assert message.role == "user"
        assert "multi-type" in message.content

    def test_role_default_value(self) -> None:
        """Test that role has default value 'user'"""
        message = UserMessage.model_validate({"content": "Test message"})

        assert message.role == "user"

    def test_content_as_string(self) -> None:
        """Test message with string content"""
        message = UserMessage.model_validate(USER_MESSAGE_STRING_CONTENT)

        assert isinstance(message.content, str)
        assert "multi-type" in message.content

    def test_content_empty_string(self) -> None:
        """Test message with empty string content"""
        message = UserMessage.model_validate(USER_MESSAGE_EMPTY_CONTENT)

        assert message.content == ""

    def test_content_unicode_string(self) -> None:
        """Test message with unicode string content"""
        message = UserMessage.model_validate(USER_MESSAGE_UNICODE_CONTENT)

        assert "可以为我解释" in message.content

    def test_content_as_list_of_text_items(self) -> None:
        """Test message with list of TextContentItem"""
        message = UserMessage.model_validate(USER_MESSAGE_TEXT_ITEMS)

        assert isinstance(message.content, list)
        assert len(message.content) == 2
        assert isinstance(message.content[0], TextContentItem)
        assert message.content[0].text == "First message"
        assert isinstance(message.content[1], TextContentItem)
        assert message.content[1].text == "Second message"

    def test_content_as_list_of_tool_result_items(self) -> None:
        """Test message with list of ToolResultContentItem"""
        message = UserMessage.model_validate(USER_MESSAGE_TOOL_RESULT_SUCCESS)

        assert isinstance(message.content, list)
        assert len(message.content) == 1
        assert isinstance(message.content[0], ToolResultContentItem)
        assert message.content[0].tool_use_id == "call_98a174fc29634f1aa752b66f"
        assert "#!/usr/bin/env python3" in message.content[0].content

    def test_content_as_list_of_document_items(self) -> None:
        """Test message with list of DocumentContentItem"""
        message = UserMessage.model_validate(USER_MESSAGE_DOCUMENT)

        assert isinstance(message.content, list)
        assert len(message.content) == 1
        assert isinstance(message.content[0], DocumentContentItem)
        assert message.content[0].source.media_type == "application/pdf"

    def test_content_as_mixed_list(self) -> None:
        """Test message with mixed content types"""
        message = UserMessage.model_validate(USER_MESSAGE_MIXED_CONTENT)

        assert isinstance(message.content, list)
        assert len(message.content) == 3
        assert isinstance(message.content[0], TextContentItem)
        assert isinstance(message.content[1], ToolResultContentItem)
        assert isinstance(message.content[2], TextContentItem)
        assert message.content[0].text == "Here's the result:"
        assert message.content[1].tool_use_id == "tool-123"
        assert message.content[2].text == "What's next?"

    def test_content_empty_list(self) -> None:
        """Test message with empty list content"""
        message = UserMessage.model_validate({"content": []})

        assert message.content == []
        assert len(message.content) == 0

    def test_content_single_item_list(self) -> None:
        """Test message with single item list"""
        message_data = {"content": [{"type": "text", "text": "Single item"}]}
        message = UserMessage.model_validate(message_data)

        assert isinstance(message.content, list)
        assert len(message.content) == 1
        assert isinstance(message.content[0], TextContentItem)
        assert message.content[0].text == "Single item"

    def test_tool_result_with_is_error(self) -> None:
        """Test tool result content with is_error field"""
        message = UserMessage.model_validate(USER_MESSAGE_TOOL_RESULT_ERROR)

        assert isinstance(message.content, list)
        assert isinstance(message.content[0], ToolResultContentItem)
        assert message.content[0].is_error is True
        assert "File does not exist" in message.content[0].content

    def test_document_with_full_source(self) -> None:
        """Test document content with full source data"""
        message = UserMessage.model_validate(USER_MESSAGE_DOCUMENT)

        assert isinstance(message.content, list)
        assert isinstance(message.content[0], DocumentContentItem)
        assert message.content[0].source.type == "base64"
        assert message.content[0].source.media_type == "application/pdf"

    def test_invalid_role_rejected(self) -> None:
        """Test that invalid role is rejected"""
        with pytest.raises(ValueError):
            UserMessage(role=cast(Any, "assistant"), content="Test")

    @pytest.mark.skip(
        reason="TODO: implement when the enumerable values of `type` for content item are defined"
    )
    def test_invalid_text_item_type_rejected(self) -> None:
        """Test that invalid type in text content item is rejected"""
        with pytest.raises(ValueError):
            UserMessage(content=[cast(Any, {"type": "invalid", "text": "Test"})])

    @pytest.mark.skip(
        reason="TODO: implement when the enumerable values of `type` for content item are defined"
    )
    def test_invalid_tool_result_item_type_rejected(self) -> None:
        """Test that invalid type in tool result content item is rejected"""
        with pytest.raises(ValueError):
            UserMessage(
                content=[cast(Any, {"type": "invalid", "tool_use_id": "123", "content": "Test"})]
            )

    def test_model_dump_string_content(self) -> None:
        """Test model_dump with string content"""
        message = UserMessage.model_validate(USER_MESSAGE_STRING_CONTENT)

        dumped = message.model_dump()

        assert dumped["role"] == "user"
        assert "multi-type" in dumped["content"]
        assert isinstance(dumped["content"], str)

    def test_model_dump_list_content(self) -> None:
        """Test model_dump with list content"""
        message = UserMessage.model_validate(USER_MESSAGE_TOOL_RESULT_SUCCESS)

        dumped = message.model_dump()

        assert dumped["role"] == "user"
        assert isinstance(dumped["content"], list)
        assert len(dumped["content"]) == 1
        assert dumped["content"][0]["tool_use_id"] == "call_98a174fc29634f1aa752b66f"

    def test_model_dump_json(self) -> None:
        """Test model_dump_json returns JSON string"""
        message = UserMessage.model_validate(USER_MESSAGE_UNICODE_CONTENT)

        json_str = message.model_dump_json()

        assert isinstance(json_str, str)
        assert "user" in json_str
        assert "可以为我解释" in json_str
