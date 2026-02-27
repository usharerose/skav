#!/usr/bin/env python3
"""
Unit tests for TextContentItem model
"""

from typing import Any, cast

import pytest

from vibehist.core.models.contents.text import TextContentItem

SAMPLE_TEXT_CONTENT_REAL: dict[str, str] = {
    "type": "text",
    "text": (
        "I'll analyze the plan and implement the Pydantic models for VibeHist transcript JSON schema. "
        "Let me first examine the current state of the codebase."
    ),
}

SAMPLE_TEXT_CONTENT_MULTILINE: dict[str, str] = {
    "type": "text",
    "text": (
        "Implement the following plan:\n\n"
        "# VibeHist Transcript JSON Schema Design\n\n"
        "## Context\n\n"
        "This document designs a comprehensive schema for Claude Code transcript JSONL data "
        "based on analysis of:\n"
    ),
}

SAMPLE_TEXT_CONTENT_UNICODE: dict[str, str] = {
    "type": "text",
    "text": "可以为我解释下你实现的内容么",
}


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

    def test_invalid_type_rejected(self) -> None:
        """Test that invalid type is rejected"""
        data = {
            **SAMPLE_TEXT_CONTENT_REAL,
            "type": cast(Any, "invalid_type"),
        }
        with pytest.raises(ValueError):
            TextContentItem.model_validate(data)
