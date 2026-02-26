#!/usr/bin/env python3
"""
Unit tests for message content models
"""

from typing import Any, cast

import pytest

from vibehist.core.models.messages.content import (
    DocumentContentItem,
    DocumentContentSource,
    TextContentItem,
    ToolResultContentItem,
)


SAMPLE_TEXT_CONTENT_REAL = {
    "type": "text",
    "text": (
        "I'll analyze the plan and implement the Pydantic models for VibeHist transcript JSON schema. "
        "Let me first examine the current state of the codebase."
    ),
}

SAMPLE_TEXT_CONTENT_MULTILINE = {
    "type": "text",
    "text": (
        "Implement the following plan:\n\n"
        "# VibeHist Transcript JSON Schema Design\n\n"
        "## Context\n\n"
        "This document designs a comprehensive schema for Claude Code transcript JSONL data "
        "based on analysis of:\n"
    ),
}

SAMPLE_TEXT_CONTENT_UNICODE = {
    "type": "text",
    "text": "可以为我解释下你实现的内容么",
}

SAMPLE_TOOL_RESULT_SUCCESS = {
    "type": "tool_result",
    "tool_use_id": "call_98a174fc29634f1aa752b66f",
    "content": (
        "     1→#!/usr/bin/env python3\n"
        "     2→\"\"\"\n"
        "     3→Type definitions for Claude Code Hook events\n"
        "     4→Based on official documentation: https://code.claude.com/docs/en/hooks\n"
        "     5→\"\"\"\n"
    ),
}

SAMPLE_TOOL_RESULT_ERROR = {
    "type": "tool_result",
    "content": (
        "File does not exist. "
        "Note: your current working directory is /app/vibehist. "
        "Did you mean models?"
    ),
    "is_error": True,
    "tool_use_id": "call_d9860daaecc9416e94d7c2f3",
}

SAMPLE_TOOL_RESULT_USER_REJECTED = {
    "type": "tool_result",
    "content": (
        "The user doesn't want to proceed with this tool use. "
        "The tool use was rejected "
        "(eg. if it was a file edit, the new_string was NOT written to the file). "
        "To tell you how to proceed, the user said:\n"
        "可以为我解释下你实现的内容么"
    ),
    "is_error": True,
    "tool_use_id": "call_12e235e4093545fbabfc0aa5",
}

# Sample document data (synthetic, as no document samples found in real data)
SAMPLE_DOCUMENT_SOURCE = {
    "type": "base64",
    "media_type": "application/pdf",
    "data": "JVBERi0xLjcKCjEgMCBvYmogICUgZW50cnkgcG9pbnQKPDwKICAvVHlwZSAvQ2F0YWxvZwog==",
}

SAMPLE_DOCUMENT_ITEM = {
    "type": "document",
    "source": SAMPLE_DOCUMENT_SOURCE,
}


class TestDocumentContentSource:
    """Test DocumentContentSource model"""

    def test_minimal_source_with_model_validate(self) -> None:
        """Test creating document source using model_validate with real data"""
        source = DocumentContentSource.model_validate(SAMPLE_DOCUMENT_SOURCE)

        assert source.type == "base64"
        assert source.media_type == "application/pdf"
        assert isinstance(source.data, str)

    def test_type_default_value(self) -> None:
        """Test that type has default value 'base64'"""
        source_data = {
            "media_type": "application/pdf",
            "data": "SGVsbG8gV29ybGQ=",
        }
        source = DocumentContentSource.model_validate(source_data)

        assert source.type == "base64"

    def test_invalid_media_type_rejected(self) -> None:
        """Test that invalid media_type is rejected"""
        invalid_data = {
            "type": "base64",
            "media_type": cast(Any, "image/png"),  # Only "application/pdf" is valid
            "data": "SGVsbG8gV29ybGQ=",
        }
        with pytest.raises(ValueError):
            DocumentContentSource.model_validate(invalid_data)

    def test_invalid_type_rejected(self) -> None:
        """Test that invalid type is rejected"""
        invalid_data = {
            "type": cast(Any, "url"),  # Only "base64" is valid
            "media_type": "application/pdf",
            "data": "SGVsbG8gV29ybGQ=",
        }
        with pytest.raises(ValueError):
            DocumentContentSource.model_validate(invalid_data)


class TestDocumentContentItem:
    """Test DocumentContentItem model"""

    def test_document_content_item_with_model_validate(self) -> None:
        """Test creating document content item using model_validate with real data"""
        item = DocumentContentItem.model_validate(SAMPLE_DOCUMENT_ITEM)

        assert item.type == "document"
        assert item.source.media_type == "application/pdf"
        assert isinstance(item.source.data, str)

    def test_type_default_value(self) -> None:
        """Test that type has default value 'document'"""
        item_data = {
            "source": {
                "media_type": "application/pdf",
                "data": "SGVsbG8gV29ybGQ=",
            }
        }
        item = DocumentContentItem.model_validate(item_data)

        assert item.type == "document"

    def test_nested_source_data(self) -> None:
        """Test accessing nested source data"""
        item_data = {
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": "cGRmZGF0YQ==",
            }
        }
        item = DocumentContentItem.model_validate(item_data)

        assert item.source.type == "base64"
        assert item.source.media_type == "application/pdf"
        assert item.source.data == "cGRmZGF0YQ=="


class TestTextContentItem:
    """Test TextContentItem model"""

    def test_text_content_item_with_model_validate(self) -> None:
        """Test creating text content item using model_validate with real data"""
        item = TextContentItem.model_validate(SAMPLE_TEXT_CONTENT_REAL)

        assert item.type == "text"
        assert "VibeHist" in item.text
        assert "Pydantic" in item.text

    def test_type_default_value(self) -> None:
        """Test that type has default value 'text'"""
        item_data = {"text": "Hello, world!"}
        item = TextContentItem.model_validate(item_data)

        assert item.type == "text"

    def test_empty_text(self) -> None:
        """Test with empty string"""
        item = TextContentItem.model_validate({"text": ""})

        assert item.text == ""

    def test_multiline_text_with_real_data(self) -> None:
        """Test with multiline text using real data sample"""
        item = TextContentItem.model_validate(SAMPLE_TEXT_CONTENT_MULTILINE)

        assert "\n" in item.text
        assert "VibeHist" in item.text
        assert "## Context" in item.text

    def test_unicode_text_with_real_data(self) -> None:
        """Test with unicode characters using real data sample"""
        item = TextContentItem.model_validate(SAMPLE_TEXT_CONTENT_UNICODE)

        assert "可以为我解释" in item.text


class TestToolResultContentItem:
    """Test ToolResultContentItem model"""

    def test_tool_result_content_item_with_model_validate(self) -> None:
        """Test creating tool result content item using model_validate with real data"""
        item = ToolResultContentItem.model_validate(SAMPLE_TOOL_RESULT_SUCCESS)

        assert item.type == "tool_result"
        assert item.tool_use_id == "call_98a174fc29634f1aa752b66f"
        assert "#!/usr/bin/env python3" in item.content
        assert item.is_error is None

    def test_type_default_value(self) -> None:
        """Test that type has default value 'tool_result'"""
        item_data = {
            "tool_use_id": "tool-123",
            "content": "Result",
        }
        item = ToolResultContentItem.model_validate(item_data)

        assert item.type == "tool_result"

    def test_with_is_error_true_real_data(self) -> None:
        """Test with is_error=True using real data sample"""
        item = ToolResultContentItem.model_validate(SAMPLE_TOOL_RESULT_ERROR)

        assert item.is_error is True
        assert "File does not exist" in item.content
        assert item.tool_use_id == "call_d9860daaecc9416e94d7c2f3"

    def test_with_is_error_false(self) -> None:
        """Test with is_error=False"""
        item_data = {
            "type": "tool_result",
            "tool_use_id": "tool-789",
            "content": "Success",
            "is_error": False,
        }
        item = ToolResultContentItem.model_validate(item_data)

        assert item.is_error is False

    def test_empty_content(self) -> None:
        """Test with empty content"""
        item = ToolResultContentItem.model_validate({
            "tool_use_id": "tool-empty",
            "content": "",
        })

        assert item.content == ""

    def test_multiline_content_with_real_data(self) -> None:
        """Test with multiline content using real data sample"""
        item = ToolResultContentItem.model_validate(SAMPLE_TOOL_RESULT_SUCCESS)

        assert "\n" in item.content
        assert "#!/usr/bin/env python3" in item.content

    def test_user_rejected_tool_result_real_data(self) -> None:
        """Test tool result when user rejected the action"""
        item = ToolResultContentItem.model_validate(SAMPLE_TOOL_RESULT_USER_REJECTED)

        assert item.is_error is True
        assert "user doesn't want to proceed" in item.content
        assert "可以为我解释下你实现的内容么" in item.content
