#!/usr/bin/env python3
"""
Unit tests for ServerToolUseContentItem model
"""

from typing import Any, cast

import pytest

from skav.transcripts.models.contents.server_tool_use import ServerToolUseContentItem

SAMPLE_SERVER_TOOL_USE_WEB_SEARCH: dict[str, Any] = {
    "type": "server_tool_use",
    "id": "server_web_search_123",
    "name": "web_search",
    "input": {
        "query": "Python pydantic tutorial",
    },
}

SAMPLE_SERVER_TOOL_USE_WEB_FETCH: dict[str, Any] = {
    "type": "server_tool_use",
    "id": "server_web_fetch_456",
    "name": "web_fetch",
    "input": {
        "url": "https://example.com",
        "prompt": "Summarize this page",
    },
}

SAMPLE_SERVER_TOOL_USE_WITH_COMPLEX_INPUT: dict[str, Any] = {
    "type": "server_tool_use",
    "id": "server_test_789",
    "name": "custom_server_tool",
    "input": {
        "param1": "value1",
        "param2": 42,
        "param3": True,
        "param4": ["a", "b", "c"],
    },
}

SAMPLE_SERVER_TOOL_USE_WITH_JSON_STRING_INPUT: dict[str, Any] = {
    "type": "server_tool_use",
    "id": "call_3a668e254f814eaf9f36302d",
    "name": "webReader",
    "input": '{"url":"https://code.claude.com/docs/en/hooks","return_format":"markdown"}',
}


class TestServerToolUseContentItem:
    """Test ServerToolUseContentItem model validation and parsing"""

    def test_required_fields(self) -> None:
        """Test that all required fields are present"""
        item = ServerToolUseContentItem.model_validate(SAMPLE_SERVER_TOOL_USE_WEB_SEARCH)

        assert item.type == "server_tool_use"
        assert item.id == "server_web_search_123"
        assert item.name == "web_search"
        assert isinstance(item.input, dict)

    def test_type_default_value(self) -> None:
        """Test that type has default value 'server_tool_use'"""
        item = ServerToolUseContentItem.model_validate(
            {
                "id": "server_test",
                "name": "test",
                "input": {},
            }
        )

        assert item.type == "server_tool_use"

    def test_server_tool_web_search(self) -> None:
        """Test web_search server tool"""
        item = ServerToolUseContentItem.model_validate(SAMPLE_SERVER_TOOL_USE_WEB_SEARCH)

        assert item.name == "web_search"
        assert isinstance(item.input, dict)
        assert item.input["query"] == "Python pydantic tutorial"

    def test_server_tool_web_fetch(self) -> None:
        """Test web_fetch server tool"""
        item = ServerToolUseContentItem.model_validate(SAMPLE_SERVER_TOOL_USE_WEB_FETCH)

        assert item.name == "web_fetch"
        assert isinstance(item.input, dict)
        assert item.input["url"] == "https://example.com"
        assert item.input["prompt"] == "Summarize this page"

    def test_server_tool_custom(self) -> None:
        """Test custom server tool with complex input"""
        item = ServerToolUseContentItem.model_validate(SAMPLE_SERVER_TOOL_USE_WITH_COMPLEX_INPUT)

        assert item.name == "custom_server_tool"
        assert isinstance(item.input, dict)
        assert item.input["param1"] == "value1"
        assert item.input["param2"] == 42
        assert item.input["param3"] is True
        assert isinstance(item.input["param4"], list)

    def test_input_with_single_param(self) -> None:
        """Test input with single parameter"""
        item = ServerToolUseContentItem.model_validate(SAMPLE_SERVER_TOOL_USE_WEB_SEARCH)

        assert isinstance(item.input, dict)
        assert len(item.input) == 1
        assert "query" in item.input

    def test_input_with_multiple_params(self) -> None:
        """Test input with multiple parameters"""
        item = ServerToolUseContentItem.model_validate(SAMPLE_SERVER_TOOL_USE_WITH_COMPLEX_INPUT)

        assert isinstance(item.input, dict)
        assert len(item.input) == 4
        assert "param1" in item.input
        assert "param2" in item.input

    def test_input_empty_dict(self) -> None:
        """Test input with empty dictionary"""
        item = ServerToolUseContentItem.model_validate(
            {
                "id": "server_test",
                "name": "test",
                "input": {},
            }
        )

        assert item.input == {}

    def test_invalid_type_rejected(self) -> None:
        """Test that invalid type is rejected"""
        data = {
            **SAMPLE_SERVER_TOOL_USE_WEB_SEARCH,
            "type": cast(Any, "invalid_type"),
        }
        with pytest.raises(ValueError):
            ServerToolUseContentItem.model_validate(data)

    def test_input_as_json_string(self) -> None:
        """Test input field as JSON string is auto-parsed to dict"""
        item = ServerToolUseContentItem.model_validate(
            SAMPLE_SERVER_TOOL_USE_WITH_JSON_STRING_INPUT
        )

        assert item.type == "server_tool_use"
        assert item.id == "call_3a668e254f814eaf9f36302d"
        assert item.name == "webReader"
        # Input JSON string is automatically parsed to dict by field_validator
        assert isinstance(item.input, dict)
        assert item.input["url"] == "https://code.claude.com/docs/en/hooks"
        assert item.input["return_format"] == "markdown"

    def test_input_as_dict(self) -> None:
        """Test input field as dictionary"""
        item = ServerToolUseContentItem.model_validate(SAMPLE_SERVER_TOOL_USE_WEB_SEARCH)

        assert isinstance(item.input, dict)
        assert item.input["query"] == "Python pydantic tutorial"
