#!/usr/bin/env python3
"""
Unit tests for ToolUseContentItem model
"""

from typing import Any

import pytest

from vibehist.core.models.contents.tool_use import ToolUseContentItem

SAMPLE_TOOL_USE_READ: dict[str, Any] = {
    "type": "tool_use",
    "id": "call_d9860daaecc9416e94d7c2f3",
    "name": "Read",
    "input": {
        "file_path": "/Users/root/workspace/project/core/models.py",
    },
}

SAMPLE_TOOL_USE_BASH: dict[str, Any] = {
    "type": "tool_use",
    "id": "call_abc123",
    "name": "Bash",
    "input": {
        "command": "echo 'Hello, World!'",
        "description": "Print hello",
    },
}

SAMPLE_TOOL_USE_GLOB: dict[str, Any] = {
    "type": "tool_use",
    "id": "call_xyz789",
    "name": "Glob",
    "input": {
        "pattern": "**/*.py",
    },
}


class TestToolUseContentItem:
    """Test ToolUseContentItem model validation and parsing"""

    def test_required_fields_real_data(self) -> None:
        """Test that all required fields are present using real data"""
        item = ToolUseContentItem.model_validate(SAMPLE_TOOL_USE_READ)

        assert item.type == "tool_use"
        assert item.id == "call_d9860daaecc9416e94d7c2f3"
        assert item.name == "Read"
        assert isinstance(item.input, dict)
        assert item.input["file_path"] == "/Users/root/workspace/project/core/models.py"

    def test_type_default_value(self) -> None:
        """Test that type has default value 'tool_use'"""
        item = ToolUseContentItem.model_validate(
            {
                "id": "call_test",
                "name": "test",
                "input": {},
            }
        )

        assert item.type == "tool_use"

    def test_tool_use_read_real_data(self) -> None:
        """Test Read tool use using real data"""
        item = ToolUseContentItem.model_validate(SAMPLE_TOOL_USE_READ)

        assert item.name == "Read"
        assert "file_path" in item.input

    def test_tool_use_bash(self) -> None:
        """Test Bash tool use"""
        item = ToolUseContentItem.model_validate(SAMPLE_TOOL_USE_BASH)

        assert item.name == "Bash"
        assert item.input["command"] == "echo 'Hello, World!'"

    def test_tool_use_glob(self) -> None:
        """Test Glob tool use"""
        item = ToolUseContentItem.model_validate(SAMPLE_TOOL_USE_GLOB)

        assert item.name == "Glob"
        assert item.input["pattern"] == "**/*.py"

    def test_input_with_single_param(self) -> None:
        """Test input with single parameter"""
        item = ToolUseContentItem.model_validate(SAMPLE_TOOL_USE_READ)

        assert len(item.input) == 1
        assert "file_path" in item.input

    def test_input_with_multiple_params(self) -> None:
        """Test input with multiple parameters"""
        item = ToolUseContentItem.model_validate(SAMPLE_TOOL_USE_BASH)

        assert "command" in item.input
        assert "description" in item.input

    def test_input_empty_dict(self) -> None:
        """Test input with empty dictionary"""
        item = ToolUseContentItem.model_validate(
            {
                "id": "call_test",
                "name": "test",
                "input": {},
            }
        )

        assert item.input == {}

    def test_invalid_type_rejected(self) -> None:
        """Test that invalid type is rejected"""
        from typing import cast

        data = {
            **SAMPLE_TOOL_USE_READ,
            "type": cast(Any, "invalid_type"),
        }
        with pytest.raises(ValueError):
            ToolUseContentItem.model_validate(data)
