#!/usr/bin/env python3
"""
Unit tests for ProgressMessage model
"""

from typing import Any

from vibehist.core.models.messages.progress import Data, ProgressMessage

SAMPLE_PROGRESS_MESSAGE: dict[str, Any] = {
    "type": "progress",
    "data": {
        "type": "bash_progress",
        "output": (
            "/Users/root/workspace/project/app.py\n"
            "/Users/root/workspace/project/constants.py\n"
            "/Users/root/workspace/project/log.py"
        ),
        "fullOutput": (
            "/Users/root/workspace/project/app.py\n"
            "/Users/root/workspace/project/constants.py\n"
            "/Users/root/workspace/project/log.py\n"
            "/Users/root/workspace/project/README.md\n"
            "/Users/root/workspace/project/Dockerfile\n"
            "/Users/root/workspace/project/requirements.txt\n"
            "/Users/root/workspace/project/setup.py"
        ),
        "elapsedTimeSeconds": 2,
        "totalLines": 7,
    },
    "toolUseID": "bash-progress-0",
    "parentToolUseID": "call_51819490f11642ff9e4103e6",
    "uuid": "2ff480a2-7428-4540-8a0f-f93be98935c5",
    "timestamp": "2026-01-20T15:10:39.272Z",
}

# Synthetic data for testing with output
SAMPLE_PROGRESS_WITH_OUTPUT: dict[str, Any] = {
    "type": "progress",
    "uuid": "test-uuid-123",
    "timestamp": "2026-02-27T10:00:00.000Z",
    "parentToolUseID": None,
    "toolUseID": "bash-progress-1",
    "data": {
        "type": "bash_progress",
        "output": "Processing file...\nSome output here",
        "fullOutput": "Full output:\nProcessing file...\nSome output here\nComplete!",
        "elapsedTimeSeconds": 5,
        "totalLines": 100,
    },
}


class TestData:
    """Test Data model (progress data)"""

    def test_data_with_model_validate(self) -> None:
        """Test creating Data using model_validate"""
        data = Data.model_validate(SAMPLE_PROGRESS_MESSAGE["data"])

        assert data.type == "bash_progress"
        assert data.elapsedTimeSeconds == 2
        assert data.totalLines == 7
        assert "/Users/root/workspace/project/constants.py" in data.output
        assert "/Users/root/workspace/project/setup.py" in data.fullOutput

    def test_data_with_output(self) -> None:
        """Test Data with actual output values"""
        data = Data.model_validate(SAMPLE_PROGRESS_WITH_OUTPUT["data"])

        assert data.output == "Processing file...\nSome output here"
        assert data.fullOutput == "Full output:\nProcessing file...\nSome output here\nComplete!"
        assert data.totalLines == 100

    def test_data_fields(self) -> None:
        """Test all Data fields"""
        data = Data.model_validate(SAMPLE_PROGRESS_WITH_OUTPUT["data"])

        assert hasattr(data, "type")
        assert hasattr(data, "elapsedTimeSeconds")
        assert hasattr(data, "fullOutput")
        assert hasattr(data, "output")
        assert hasattr(data, "totalLines")


class TestProgressMessage:
    """Test ProgressMessage model"""

    def test_required_fields_real_data(self) -> None:
        """Test creating ProgressMessage using model_validate with real data"""
        message = ProgressMessage.model_validate(SAMPLE_PROGRESS_MESSAGE)

        assert message.type == "progress"
        assert message.uuid == "2ff480a2-7428-4540-8a0f-f93be98935c5"
        assert message.toolUseID == "bash-progress-0"
        assert message.parentToolUseID == "call_51819490f11642ff9e4103e6"

    def test_type_default_value(self) -> None:
        """Test that type has default value 'progress'"""
        message = ProgressMessage.model_validate(SAMPLE_PROGRESS_MESSAGE)

        assert message.type == "progress"

    def test_timestamp_parsing_real_data(self) -> None:
        """Test ISO 8601 timestamp parsing using real data"""
        message = ProgressMessage.model_validate(SAMPLE_PROGRESS_MESSAGE)

        import datetime

        assert isinstance(message.timestamp, datetime.datetime)
        assert message.timestamp.year == 2026
        assert message.timestamp.month == 1
        assert message.timestamp.day == 20
        assert message.timestamp.hour == 15
        assert message.timestamp.minute == 10
        assert message.timestamp.second == 39

    def test_data_field_real_data(self) -> None:
        """Test data field contains correct Data model"""
        message = ProgressMessage.model_validate(SAMPLE_PROGRESS_MESSAGE)

        assert isinstance(message.data, Data)
        assert message.data.type == "bash_progress"
        assert message.data.elapsedTimeSeconds == 2

    def test_parent_tool_use_id_none(self) -> None:
        """Test with parentToolUseID as None"""
        message = ProgressMessage.model_validate(SAMPLE_PROGRESS_WITH_OUTPUT)

        assert message.parentToolUseID is None

    def test_parent_tool_use_id_with_value(self) -> None:
        """Test with parentToolUseID as value"""
        message = ProgressMessage.model_validate(SAMPLE_PROGRESS_MESSAGE)

        assert message.parentToolUseID == "call_51819490f11642ff9e4103e6"
