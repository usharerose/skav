#!/usr/bin/env python3
"""
Unit tests for SummaryTranscriptItem model
"""

from typing import Any

import pytest

from skav.core.models.transcript_items.summary import (
    SummaryTranscriptItem,
)

SAMPLE_SUMMARY: dict[str, Any] = {
    "type": "summary",
    "summary": "Jira Issue Resolution: feat-10010",
    "leafUuid": "16ee9b2d-6d5b-4ba3-9f60-77f89865ce1c",
}


class TestSummaryTranscriptItem:
    """Test SummaryTranscriptItem model"""

    def test_required_fields(self) -> None:
        """Test creating SummaryTranscriptItem using model_validate"""
        item = SummaryTranscriptItem.model_validate(SAMPLE_SUMMARY)

        assert item.type == "summary"
        assert item.leafUuid == "16ee9b2d-6d5b-4ba3-9f60-77f89865ce1c"
        assert "Jira Issue Resolution" in item.summary

    def test_empty_summary(self) -> None:
        """Test that empty summary is valid"""
        data = {
            "type": "summary",
            "summary": "",
            "leafUuid": "test-uuid",
        }
        item = SummaryTranscriptItem.model_validate(data)

        assert item.summary == ""

    def test_leaf_uuid_required(self) -> None:
        """Test that leafUuid is required"""
        data = {
            "type": "summary",
            "summary": "Test summary",
        }
        with pytest.raises(Exception):  # Pydantic ValidationError
            SummaryTranscriptItem.model_validate(data)
