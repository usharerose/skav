#!/usr/bin/env python3
"""
Unit tests for ToolResultContentItem model
"""

from typing import Any, cast

import pytest

from skav.core.models.contents.tool_result import ToolResultContentItem

# Real data samples from actual Claude Code transcript JSONL files
SAMPLE_TOOL_RESULT_SUCCESS: dict[str, Any] = {
    "type": "tool_result",
    "tool_use_id": "call_98a174fc29634f1aa752b66f",
    "content": (
        "     1→#!/usr/bin/env python3\n"
        '     2→"""\n'
        "     3→Type definitions for Claude Code Hook events\n"
        "     4→Based on official documentation: https://code.claude.com/docs/en/hooks\n"
        '     5→"""\n'
    ),
}

SAMPLE_TOOL_RESULT_ERROR: dict[str, Any] = {
    "type": "tool_result",
    "content": (
        "File does not exist. "
        "Note: your current working directory is /Users/root/workspace/project. "
        "Did you mean models?"
    ),
    "is_error": True,
    "tool_use_id": "call_d9860daaecc9416e94d7c2f3",
}

SAMPLE_TOOL_RESULT_USER_REJECTED: dict[str, Any] = {
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
        item = ToolResultContentItem.model_validate(
            {
                "tool_use_id": "tool-empty",
                "content": "",
            }
        )

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

    def test_invalid_type_rejected(self) -> None:
        """Test that invalid type is rejected"""
        data = {
            **SAMPLE_TOOL_RESULT_SUCCESS,
            "type": cast(Any, "invalid_type"),
        }
        with pytest.raises(ValueError):
            ToolResultContentItem.model_validate(data)
