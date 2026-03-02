#!/usr/bin/env python3
"""
Unit tests for ThinkingContentItem model
"""

import pytest

from vibehist.core.models.contents.thinking import ThinkingContentItem

SAMPLE_THINKING_CONTENT: dict[str, str] = {
    "type": "thinking",
    "thinking": (
        "Let me analyze this problem step by step. First, I need to understand the requirements..."
    ),
    "signature": "thinking_signature_abc123",
}

SAMPLE_THINKING_CONTENT_SHORT: dict[str, str] = {
    "type": "thinking",
    "thinking": "Quick analysis needed.",
    "signature": "sig_xyz",
}


class TestThinkingContentItem:
    """Test ThinkingContentItem model validation and parsing"""

    def test_required_fields(self) -> None:
        """Test that all required fields are present"""
        item = ThinkingContentItem.model_validate(SAMPLE_THINKING_CONTENT)

        assert item.type == "thinking"
        assert item.thinking == (
            "Let me analyze this problem step by step. "
            "First, I need to understand the requirements..."
        )
        assert item.signature == "thinking_signature_abc123"

    def test_type_default_value(self) -> None:
        """Test that type has default value 'thinking'"""
        item = ThinkingContentItem.model_validate(
            {
                "thinking": "Test thinking",
                "signature": "test_sig",
            }
        )

        assert item.type == "thinking"

    def test_thinking_field_long(self) -> None:
        """Test with long thinking content"""
        item = ThinkingContentItem.model_validate(SAMPLE_THINKING_CONTENT)

        assert "step by step" in item.thinking
        assert "requirements" in item.thinking

    def test_thinking_field_short(self) -> None:
        """Test with short thinking content"""
        item = ThinkingContentItem.model_validate(SAMPLE_THINKING_CONTENT_SHORT)

        assert item.thinking == "Quick analysis needed."

    def test_thinking_field_multiline(self) -> None:
        """Test with multiline thinking content"""
        item = ThinkingContentItem.model_validate(
            {
                "type": "thinking",
                "thinking": "Line 1\nLine 2\nLine 3",
                "signature": "test_sig",
            }
        )

        assert "\n" in item.thinking
        assert item.thinking == "Line 1\nLine 2\nLine 3"

    def test_thinking_field_empty(self) -> None:
        """Test with empty thinking content"""
        item = ThinkingContentItem.model_validate(
            {
                "type": "thinking",
                "thinking": "",
                "signature": "test_sig",
            }
        )

        assert item.thinking == ""

    def test_signature_field(self) -> None:
        """Test signature field"""
        item = ThinkingContentItem.model_validate(SAMPLE_THINKING_CONTENT)

        assert item.signature == "thinking_signature_abc123"

    def test_signature_field_short(self) -> None:
        """Test with short signature"""
        item = ThinkingContentItem.model_validate(SAMPLE_THINKING_CONTENT_SHORT)

        assert item.signature == "sig_xyz"

    def test_signature_field_with_special_chars(self) -> None:
        """Test signature with special characters"""
        item = ThinkingContentItem.model_validate(
            {
                "type": "thinking",
                "thinking": "Test",
                "signature": "sig_with-123.abc",
            }
        )

        assert item.signature == "sig_with-123.abc"

    def test_invalid_type_rejected(self) -> None:
        """Test that invalid type is rejected"""
        from typing import Any, cast

        data = {
            **SAMPLE_THINKING_CONTENT,
            "type": cast(Any, "invalid_type"),
        }
        with pytest.raises(ValueError):
            ThinkingContentItem.model_validate(data)
