#!/usr/bin/env python3
"""
Unit tests for Usage model
"""

from typing import Any

from skav.transcripts.models.usage import CacheCreation, ServerToolUse, Usage

USAGE_MINIMAL: dict[str, Any] = {
    "input_tokens": 0,
    "output_tokens": 0,
}

USAGE_COMPLETE: dict[str, Any] = {
    "input_tokens": 15946,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 1152,
    "output_tokens": 67,
    "server_tool_use": {
        "web_search_requests": 0,
        "web_fetch_requests": 0,
    },
    "service_tier": "standard",
    "cache_creation": {
        "ephemeral_1h_input_tokens": 0,
        "ephemeral_5m_input_tokens": 0,
    },
    "inference_geo": "",
    "iterations": [],
    "speed": "standard",
}

USAGE_PARTIAL: dict[str, Any] = {
    "input_tokens": 106,
    "output_tokens": 195,
    "cache_read_input_tokens": 62208,
    "server_tool_use": {
        "web_search_requests": 0,
    },
    "service_tier": "standard",
}


class TestUsage:
    """Test Usage model validation and parsing"""

    def test_minimal_usage(self) -> None:
        """Test creating usage with only required fields"""
        usage = Usage.model_validate(USAGE_MINIMAL)

        assert usage.input_tokens == 0
        assert usage.output_tokens == 0
        assert usage.cache_read_input_tokens is None
        assert usage.service_tier is None

    def test_complete_usage(self) -> None:
        """Test usage with all optional fields"""
        usage = Usage.model_validate(USAGE_COMPLETE)

        assert usage.input_tokens == 15946
        assert usage.output_tokens == 67
        assert usage.cache_read_input_tokens == 1152
        assert usage.service_tier == "standard"
        assert usage.speed == "standard"
        assert usage.inference_geo == ""
        assert usage.iterations == []

    def test_partial_usage(self) -> None:
        """Test usage with only some optional fields"""
        usage = Usage.model_validate(USAGE_PARTIAL)

        assert usage.input_tokens == 106
        assert usage.output_tokens == 195
        assert usage.cache_read_input_tokens == 62208
        assert usage.server_tool_use is not None
        assert usage.server_tool_use.web_search_requests == 0
        assert usage.server_tool_use.web_fetch_requests is None
        assert usage.service_tier == "standard"
        assert usage.cache_creation is None

    def test_server_tool_use_none(self) -> None:
        """Test server_tool_use as None"""
        usage = Usage.model_validate(USAGE_MINIMAL)

        assert usage.server_tool_use is None

    def test_cache_creation_none(self) -> None:
        """Test cache_creation as None"""
        usage = Usage.model_validate(USAGE_MINIMAL)

        assert usage.cache_creation is None

    def test_iterations_empty_list(self) -> None:
        """Test iterations as empty list"""
        usage = Usage.model_validate(USAGE_COMPLETE)

        assert usage.iterations == []

    def test_iterations_none(self) -> None:
        """Test iterations as None"""
        usage = Usage.model_validate(USAGE_MINIMAL)

        assert usage.iterations is None

    def test_inference_geo_empty_string(self) -> None:
        """Test inference_geo as empty string"""
        usage = Usage.model_validate(USAGE_COMPLETE)

        assert usage.inference_geo == ""

    def test_inference_geo_none(self) -> None:
        """Test inference_geo as None"""
        usage = Usage.model_validate(USAGE_MINIMAL)

        assert usage.inference_geo is None

    def test_speed_standard(self) -> None:
        """Test speed field"""
        usage = Usage.model_validate(USAGE_COMPLETE)

        assert usage.speed == "standard"

    def test_speed_none(self) -> None:
        """Test speed as None"""
        usage = Usage.model_validate(USAGE_MINIMAL)

        assert usage.speed is None


class TestCacheCreation:
    """Test CacheCreation model validation"""

    def test_cache_creation_fields(self) -> None:
        """Test cache creation fields"""
        cc = CacheCreation.model_validate(
            {
                "ephemeral_1h_input_tokens": 1000,
                "ephemeral_5m_input_tokens": 500,
            }
        )

        assert cc.ephemeral_1h_input_tokens == 1000
        assert cc.ephemeral_5m_input_tokens == 500

    def test_zero_values(self) -> None:
        """Test with zero values"""
        cc = CacheCreation.model_validate(
            {
                "ephemeral_1h_input_tokens": 0,
                "ephemeral_5m_input_tokens": 0,
            }
        )

        assert cc.ephemeral_1h_input_tokens == 0
        assert cc.ephemeral_5m_input_tokens == 0


class TestServerToolUse:
    """Test ServerToolUse model validation"""

    def test_server_tool_use_both_fields(self) -> None:
        """Test server tool use with both fields"""
        stu = ServerToolUse.model_validate(
            {
                "web_search_requests": 1,
                "web_fetch_requests": 2,
            }
        )

        assert stu.web_search_requests == 1
        assert stu.web_fetch_requests == 2

    def test_server_tool_use_single_field(self) -> None:
        """Test server tool use with only one field"""
        stu = ServerToolUse.model_validate(
            {
                "web_search_requests": 1,
            }
        )

        assert stu.web_search_requests == 1
        assert stu.web_fetch_requests is None

    def test_server_tool_use_empty(self) -> None:
        """Test server tool use with empty dict"""
        stu = ServerToolUse.model_validate({})

        assert stu.web_search_requests is None
        assert stu.web_fetch_requests is None
