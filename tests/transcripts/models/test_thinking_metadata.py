#!/usr/bin/env python3
"""
Unit tests for ThinkingMetadata model
"""

from typing import Any, cast

import pytest

from skav.transcripts.models.thinking_metadata import ThinkingMetadata

SAMPLE_THINKING_METADATA_MAX_TOKENS = {
    "maxThinkingTokens": 31999,
}

SAMPLE_THINKING_METADATA_EMPTY: dict[str, Any] = {}

SYNTHETIC_THINKING_METADATA_DISABLED_TRUE = {
    "disabled": True,
}

SYNTHETIC_THINKING_METADATA_DISABLED_FALSE = {
    "disabled": False,
}

SYNTHETIC_THINKING_METADATA_LEVEL_HIGH = {
    "level": "high",
}

SYNTHETIC_THINKING_METADATA_WITH_TRIGGERS = {
    "triggers": [{"type": "keyword"}, {"type": "complex"}],
}

SYNTHETIC_THINKING_METADATA_COMPLETE = {
    "disabled": False,
    "level": "high",
    "maxThinkingTokens": 200000,
    "triggers": [{"type": "keyword"}, {"type": "complex"}],
}


class TestThinkingMetadata:
    """Test ThinkingMetadata model validation and parsing"""

    def test_empty_metadata_with_model_validate(self) -> None:
        """Test creating empty metadata using model_validate with real data"""
        metadata = ThinkingMetadata.model_validate(SAMPLE_THINKING_METADATA_EMPTY)

        assert metadata.disabled is None
        assert metadata.level is None
        assert metadata.maxThinkingTokens is None
        assert metadata.triggers is None

    def test_with_max_thinking_tokens_real_data(self) -> None:
        """Test metadata with maxThinkingTokens using real data"""
        metadata = ThinkingMetadata.model_validate(SAMPLE_THINKING_METADATA_MAX_TOKENS)

        assert metadata.maxThinkingTokens == 31999
        assert metadata.disabled is None
        assert metadata.level is None
        assert metadata.triggers is None

    def test_with_disabled_true_with_model_validate(self) -> None:
        """Test metadata with disabled=True using model_validate"""
        metadata = ThinkingMetadata.model_validate(SYNTHETIC_THINKING_METADATA_DISABLED_TRUE)

        assert metadata.disabled is True
        assert metadata.level is None
        assert metadata.maxThinkingTokens is None
        assert metadata.triggers is None

    def test_with_disabled_false_with_model_validate(self) -> None:
        """Test metadata with disabled=False using model_validate"""
        metadata = ThinkingMetadata.model_validate(SYNTHETIC_THINKING_METADATA_DISABLED_FALSE)

        assert metadata.disabled is False

    def test_with_level_high_with_model_validate(self) -> None:
        """Test metadata with level='high' using model_validate"""
        metadata = ThinkingMetadata.model_validate(SYNTHETIC_THINKING_METADATA_LEVEL_HIGH)

        assert metadata.level == "high"
        assert metadata.disabled is None
        assert metadata.maxThinkingTokens is None
        assert metadata.triggers is None

    def test_with_triggers_with_model_validate(self) -> None:
        """Test metadata with triggers list using model_validate"""
        metadata = ThinkingMetadata.model_validate(SYNTHETIC_THINKING_METADATA_WITH_TRIGGERS)

        assert metadata.triggers is not None
        assert len(metadata.triggers) == 2
        assert metadata.triggers[0]["type"] == "keyword"
        assert metadata.disabled is None
        assert metadata.level is None
        assert metadata.maxThinkingTokens is None

    def test_complete_metadata_with_model_validate(self) -> None:
        """Test metadata with all fields populated using model_validate"""
        metadata = ThinkingMetadata.model_validate(SYNTHETIC_THINKING_METADATA_COMPLETE)

        assert metadata.disabled is False
        assert metadata.level == "high"
        assert metadata.maxThinkingTokens == 200000
        assert metadata.triggers is not None
        assert len(metadata.triggers) == 2

    def test_level_literal_accepts_high_with_model_validate(self) -> None:
        """Test that level accepts 'high' as valid value using model_validate"""
        metadata = ThinkingMetadata.model_validate({"level": "high"})

        assert metadata.level == "high"

    def test_level_accepts_none_with_model_validate(self) -> None:
        """Test that level accepts None using model_validate"""
        metadata = ThinkingMetadata.model_validate({"level": None})

        assert metadata.level is None

    @pytest.mark.skip(reason="TODO: implement when the enumerable values of `level` are defined")
    def test_level_rejects_invalid_value(self) -> None:
        """Test that level rejects invalid values"""
        with pytest.raises(ValueError):
            ThinkingMetadata.model_validate({"level": cast(Any, "medium")})

        with pytest.raises(ValueError):
            ThinkingMetadata.model_validate({"level": cast(Any, "low")})

    def test_max_thinking_tokens_zero_with_model_validate(self) -> None:
        """Test maxThinkingTokens with zero value using model_validate"""
        metadata = ThinkingMetadata.model_validate({"maxThinkingTokens": 0})

        assert metadata.maxThinkingTokens == 0

    def test_max_thinking_tokens_negative_with_model_validate(self) -> None:
        """Test maxThinkingTokens with negative value using model_validate"""
        metadata = ThinkingMetadata.model_validate({"maxThinkingTokens": -1})

        assert metadata.maxThinkingTokens == -1

    def test_max_thinking_tokens_large_value_with_model_validate(self) -> None:
        """Test maxThinkingTokens with large value using model_validate"""
        metadata = ThinkingMetadata.model_validate({"maxThinkingTokens": 999999})

        assert metadata.maxThinkingTokens == 999999

    def test_max_thinking_tokens_real_value(self) -> None:
        """Test maxThinkingTokens with real value from data"""
        metadata = ThinkingMetadata.model_validate(SAMPLE_THINKING_METADATA_MAX_TOKENS)

        assert metadata.maxThinkingTokens == 31999

    def test_triggers_empty_list_with_model_validate(self) -> None:
        """Test triggers with empty list using model_validate"""
        metadata = ThinkingMetadata.model_validate({"triggers": []})

        assert metadata.triggers == []
        assert len(metadata.triggers) == 0

    def test_triggers_with_complex_objects_with_model_validate(self) -> None:
        """Test triggers with complex objects using model_validate"""
        triggers_data = [
            {"type": "keyword", "pattern": "explain"},
            {"type": "complex", "threshold": 0.8},
            {"type": "custom", "config": {"key": "value"}},
        ]
        metadata = ThinkingMetadata.model_validate({"triggers": triggers_data})

        assert metadata.triggers is not None
        assert len(metadata.triggers) == 3
        assert metadata.triggers[2]["config"]["key"] == "value"

    def test_partial_metadata_disabled_and_level_with_model_validate(self) -> None:
        """Test metadata with disabled and level only using model_validate"""
        metadata = ThinkingMetadata.model_validate({"disabled": True, "level": "high"})

        assert metadata.disabled is True
        assert metadata.level == "high"
        assert metadata.maxThinkingTokens is None
        assert metadata.triggers is None

    def test_partial_metadata_tokens_and_triggers_with_model_validate(self) -> None:
        """Test metadata with maxThinkingTokens and triggers only using model_validate"""
        metadata = ThinkingMetadata.model_validate(
            {"maxThinkingTokens": 100000, "triggers": [{"type": "test"}]}
        )

        assert metadata.disabled is None
        assert metadata.level is None
        assert metadata.maxThinkingTokens == 100000
        assert metadata.triggers is not None

    def test_model_dump_with_real_data(self) -> None:
        """Test model_dump returns dictionary using real data"""
        metadata = ThinkingMetadata.model_validate(SYNTHETIC_THINKING_METADATA_COMPLETE)

        dumped = metadata.model_dump()

        assert dumped["disabled"] is False
        assert dumped["level"] == "high"
        assert dumped["maxThinkingTokens"] == 200000
        assert dumped["triggers"] is not None

    def test_model_dump_with_max_tokens_real_data(self) -> None:
        """Test model_dump with real maxThinkingTokens data"""
        metadata = ThinkingMetadata.model_validate(SAMPLE_THINKING_METADATA_MAX_TOKENS)

        dumped = metadata.model_dump()

        assert dumped["maxThinkingTokens"] == 31999

    def test_model_dump_exclude_none_with_model_validate(self) -> None:
        """Test model_dump with exclude_none using model_validate"""
        metadata = ThinkingMetadata.model_validate(SYNTHETIC_THINKING_METADATA_DISABLED_TRUE)

        dumped = metadata.model_dump(exclude_none=True)

        assert dumped["disabled"] is True
        assert "level" not in dumped
        assert "maxThinkingTokens" not in dumped
        assert "triggers" not in dumped

    def test_model_dump_json_with_real_data(self) -> None:
        """Test model_dump_json returns JSON string using real data"""
        metadata = ThinkingMetadata.model_validate(SAMPLE_THINKING_METADATA_MAX_TOKENS)

        json_str = metadata.model_dump_json()

        assert isinstance(json_str, str)
        assert "31999" in json_str

    def test_update_disabled_field_with_model_validate(self) -> None:
        """Test updating disabled field using model_copy"""
        metadata = ThinkingMetadata.model_validate(SYNTHETIC_THINKING_METADATA_DISABLED_TRUE)
        updated = metadata.model_copy(update={"disabled": False})

        assert metadata.disabled is True  # Original unchanged
        assert updated.disabled is False

    def test_update_level_field_with_model_validate(self) -> None:
        """Test updating level field using model_copy"""
        metadata = ThinkingMetadata.model_validate(SYNTHETIC_THINKING_METADATA_LEVEL_HIGH)
        updated = metadata.model_copy(update={"level": None})

        assert metadata.level == "high"  # Original unchanged
        assert updated.level is None

    def test_update_max_thinking_tokens_field_with_model_validate(self) -> None:
        """Test updating maxThinkingTokens field using model_copy with real data"""
        metadata = ThinkingMetadata.model_validate(SAMPLE_THINKING_METADATA_MAX_TOKENS)
        updated = metadata.model_copy(update={"maxThinkingTokens": 200000})

        assert metadata.maxThinkingTokens == 31999  # Original unchanged
        assert updated.maxThinkingTokens == 200000
