#!/usr/bin/env python3
"""
Unit tests for AssistantTranscriptItem model
"""

import datetime
from typing import Any

import pytest

from vibehist.core.models.transcript_items.assistant import AssistantTranscriptItem

SAMPLE_ASSISTANT_ENTRY_TEXT_ONLY: dict[str, Any] = {
    "parentUuid": "fcd3c922-f183-4fe4-9a12-357a87404ae3",
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "1d3713b2-ed06-483d-a7be-92596e87e84c",
    "version": "2.1.49",
    "gitBranch": "master",
    "slug": "sequential-frolicking-treasure",
    "message": {
        "id": "msg_2026022222573947d4e82262af4dc8",
        "type": "message",
        "role": "assistant",
        "model": "glm-4.7",
        "content": [
            {
                "type": "text",
                "text": (
                    "I'll analyze the plan and implement the Pydantic models "
                    "for VibeHist transcript JSON schema. "
                    "Let me first examine the current state of the codebase."
                ),
            }
        ],
        "stop_reason": None,
        "stop_sequence": None,
        "usage": {
            "input_tokens": 0,
            "output_tokens": 0,
        },
    },
    "type": "assistant",
    "uuid": "67ea2d00-a937-4b88-a219-c8b57b5637d7",
    "timestamp": "2026-02-22T14:57:42.788Z",
}

SAMPLE_ASSISTANT_ENTRY_WITH_TOOL_USE: dict[str, Any] = {
    "parentUuid": "67ea2d00-a937-4b88-a219-c8b57b5637d7",
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "1d3713b2-ed06-483d-a7be-92596e87e84c",
    "version": "2.1.49",
    "gitBranch": "master",
    "slug": "sequential-frolicking-treasure",
    "message": {
        "id": "msg_2026022222573947d4e82262af4dc8",
        "type": "message",
        "role": "assistant",
        "model": "glm-4.7",
        "content": [
            {
                "type": "tool_use",
                "id": "call_d9860daaecc9416e94d7c2f3",
                "name": "Read",
                "input": {
                    "file_path": "/Users/root/workspace/project/core/models.py",
                },
            }
        ],
        "stop_reason": None,
        "stop_sequence": None,
        "usage": {
            "input_tokens": 0,
            "output_tokens": 0,
        },
    },
    "type": "assistant",
    "uuid": "e26025aa-0543-4f40-a4bb-478982ae811b",
    "timestamp": "2026-02-22T14:57:42.789Z",
}

SAMPLE_ASSISTANT_ENTRY_WITH_THINKING: dict[str, Any] = {
    "parentUuid": "fcd3c922-f183-4fe4-9a12-357a87404ae3",
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "1d3713b2-ed06-483d-a7be-92596e87e84c",
    "version": "2.1.49",
    "gitBranch": "master",
    "slug": "sequential-frolicking-treasure",
    "message": {
        "id": "msg_2026022222573947d4e82262af4dc9",
        "type": "message",
        "role": "assistant",
        "model": "claude-sonnet-4-6",
        "content": [
            {
                "type": "thinking",
                "thinking": "I need to analyze the codebase structure to understand the requirements.",
                "signature": "",
            }
        ],
        "stop_reason": None,
        "stop_sequence": None,
        "usage": {
            "input_tokens": 100,
            "output_tokens": 50,
        },
    },
    "type": "assistant",
    "uuid": "78ea2d00-a937-4b88-a219-c8b57b5637d8",
    "timestamp": "2026-02-22T14:57:42.790Z",
}

SAMPLE_ASSISTANT_ENTRY_WITH_SERVER_TOOL_USE: dict[str, Any] = {
    "parentUuid": "fcd3c922-f183-4fe4-9a12-357a87404ae3",
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "1d3713b2-ed06-483d-a7be-92596e87e84c",
    "version": "2.1.49",
    "gitBranch": "master",
    "slug": "sequential-frolicking-treasure",
    "message": {
        "id": "msg_2026022222573947d4e82262af4dc10",
        "type": "message",
        "role": "assistant",
        "model": "claude-sonnet-4-6",
        "content": [
            {
                "type": "server_tool_use",
                "id": "call_127247113f964b7f8b1234567",
                "name": "webReader",
                "input": {"url": "https://example.com"},
            }
        ],
        "stop_reason": None,
        "stop_sequence": None,
        "usage": {
            "input_tokens": 200,
            "output_tokens": 100,
        },
    },
    "type": "assistant",
    "uuid": "89ea2d00-a937-4b88-a219-c8b57b5637d9",
    "timestamp": "2026-02-22T14:57:42.791Z",
}

SAMPLE_ASSISTANT_ENTRY_WITH_API_ERROR: dict[str, Any] = {
    "parentUuid": "fcd3c922-f183-4fe4-9a12-357a87404ae3",
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "1d3713b2-ed06-483d-a7be-92596e87e84c",
    "version": "2.1.49",
    "gitBranch": "master",
    "slug": "sequential-frolicking-treasure",
    "message": {
        "id": "msg_2026022222573947d4e82262af4dc11",
        "type": "message",
        "role": "assistant",
        "model": "claude-sonnet-4-6",
        "content": [
            {
                "type": "text",
                "text": "An error occurred while processing your request.",
            }
        ],
        "stop_reason": None,
        "stop_sequence": None,
        "usage": {
            "input_tokens": 50,
            "output_tokens": 25,
        },
    },
    "type": "assistant",
    "uuid": "90ea2d00-a937-4b88-a219-c8b57b5637d10",
    "timestamp": "2026-02-22T14:57:42.792Z",
    "error": "API request failed",
    "isApiErrorMessage": True,
}


class TestAssistantTranscriptItem:
    """Test AssistantTranscriptItem model validation and parsing"""

    def test_required_fields(self) -> None:
        """Test that all required fields are present"""
        entry = AssistantTranscriptItem.model_validate(SAMPLE_ASSISTANT_ENTRY_TEXT_ONLY)

        assert entry.type == "assistant"
        assert entry.sessionId == "1d3713b2-ed06-483d-a7be-92596e87e84c"
        assert entry.uuid == "67ea2d00-a937-4b88-a219-c8b57b5637d7"
        assert entry.parentUuid == "fcd3c922-f183-4fe4-9a12-357a87404ae3"
        assert isinstance(entry.timestamp, datetime.datetime)
        assert entry.version == "2.1.49"
        assert entry.cwd == "/Users/root/workspace/project"
        assert entry.gitBranch == "master"
        assert entry.isSidechain is False
        assert entry.userType == "external"
        assert entry.message.id == "msg_2026022222573947d4e82262af4dc8"
        assert entry.message.model == "glm-4.7"

    def test_timestamp_parsing(self) -> None:
        """Test ISO 8601 timestamp parsing"""
        entry = AssistantTranscriptItem.model_validate(SAMPLE_ASSISTANT_ENTRY_TEXT_ONLY)

        assert isinstance(entry.timestamp, datetime.datetime)
        assert entry.timestamp.year == 2026
        assert entry.timestamp.month == 2
        assert entry.timestamp.day == 22
        assert entry.timestamp.hour == 14
        assert entry.timestamp.minute == 57
        assert entry.timestamp.second == 42
        assert entry.timestamp.tzinfo is not None

    def test_with_slug_field(self) -> None:
        """Test slug field"""
        entry = AssistantTranscriptItem.model_validate(SAMPLE_ASSISTANT_ENTRY_TEXT_ONLY)

        assert entry.slug == "sequential-frolicking-treasure"

    def test_with_agent_id_none(self) -> None:
        """Test agentId is None by default"""
        entry = AssistantTranscriptItem.model_validate(SAMPLE_ASSISTANT_ENTRY_TEXT_ONLY)

        assert entry.agentId is None

    def test_with_agent_id_set(self) -> None:
        """Test with agentId field set (subagent message)"""
        data = {
            **SAMPLE_ASSISTANT_ENTRY_TEXT_ONLY,
            "isSidechain": True,
            "agentId": "agent-123",
            "uuid": "test-uuid",
        }
        entry = AssistantTranscriptItem.model_validate(data)

        assert entry.agentId == "agent-123"
        assert entry.isSidechain is True

    def test_with_error_field(self) -> None:
        """Test with error field"""
        data = {
            **SAMPLE_ASSISTANT_ENTRY_TEXT_ONLY,
            "uuid": "test-uuid",
            "error": "An error occurred",
        }
        entry = AssistantTranscriptItem.model_validate(data)

        assert entry.error == "An error occurred"

    def test_with_api_error_message(self) -> None:
        """Test with isApiErrorMessage field"""
        entry = AssistantTranscriptItem.model_validate(SAMPLE_ASSISTANT_ENTRY_WITH_API_ERROR)

        assert entry.isApiErrorMessage is True
        assert entry.error == "API request failed"

    def test_message_with_text_content(self) -> None:
        """Test message with text content"""
        entry = AssistantTranscriptItem.model_validate(SAMPLE_ASSISTANT_ENTRY_TEXT_ONLY)

        assert isinstance(entry.message.content, list)
        assert len(entry.message.content) == 1
        assert entry.message.content[0].type == "text"
        assert "Pydantic models" in entry.message.content[0].text

    def test_message_with_tool_use_content(self) -> None:
        """Test message with tool_use content"""
        entry = AssistantTranscriptItem.model_validate(SAMPLE_ASSISTANT_ENTRY_WITH_TOOL_USE)

        assert isinstance(entry.message.content, list)
        assert len(entry.message.content) == 1
        assert entry.message.content[0].type == "tool_use"
        assert entry.message.content[0].id == "call_d9860daaecc9416e94d7c2f3"
        assert entry.message.content[0].name == "Read"

    def test_message_with_thinking_content(self) -> None:
        """Test message with thinking content"""
        entry = AssistantTranscriptItem.model_validate(SAMPLE_ASSISTANT_ENTRY_WITH_THINKING)

        assert isinstance(entry.message.content, list)
        assert len(entry.message.content) == 1
        assert entry.message.content[0].type == "thinking"
        assert "analyze the codebase" in entry.message.content[0].thinking

    def test_message_with_server_tool_use_content(self) -> None:
        """Test message with server_tool_use content"""
        entry = AssistantTranscriptItem.model_validate(SAMPLE_ASSISTANT_ENTRY_WITH_SERVER_TOOL_USE)

        assert isinstance(entry.message.content, list)
        assert len(entry.message.content) == 1
        assert entry.message.content[0].type == "server_tool_use"
        assert entry.message.content[0].name == "webReader"

    def test_invalid_user_type_rejected(self) -> None:
        """Test that invalid userType is rejected"""
        data = {**SAMPLE_ASSISTANT_ENTRY_TEXT_ONLY, "userType": "invalid"}
        with pytest.raises(ValueError):
            AssistantTranscriptItem.model_validate(data)

    def test_invalid_timestamp_format(self) -> None:
        """Test that invalid timestamp format is handled"""
        data = {**SAMPLE_ASSISTANT_ENTRY_TEXT_ONLY, "timestamp": "invalid-date"}
        with pytest.raises(ValueError):
            AssistantTranscriptItem.model_validate(data)

    def test_type_default_value(self) -> None:
        """Test that type field has default value 'assistant'"""
        # Create minimal data without type field
        data = {
            "sessionId": "test",
            "parentUuid": "parent",
            "uuid": "test",
            "timestamp": "2026-02-25T10:00:00Z",
            "version": "1.0",
            "cwd": "/test",
            "isSidechain": False,
            "message": {
                "id": "msg-test",
                "type": "message",
                "role": "assistant",
                "model": "test-model",
                "content": [{"type": "text", "text": "test"}],
                "stop_reason": None,
                "stop_sequence": None,
                "usage": {"input_tokens": 0, "output_tokens": 0},
            },
        }
        entry = AssistantTranscriptItem.model_validate(data)
        assert entry.type == "assistant"

    def test_user_type_default_value(self) -> None:
        """Test that userType field has default value 'external'"""
        data = {
            **SAMPLE_ASSISTANT_ENTRY_TEXT_ONLY,
            "userType": "external",
        }
        entry = AssistantTranscriptItem.model_validate(data)
        assert entry.userType == "external"

    def test_git_branch_default_when_omitted(self) -> None:
        """Test that gitBranch defaults to 'HEAD' when omitted"""
        data = {
            "sessionId": "test",
            "parentUuid": "parent",
            "uuid": "test",
            "timestamp": "2026-02-25T10:00:00Z",
            "version": "1.0",
            "cwd": "/test",
            "isSidechain": False,
            "message": {
                "id": "msg-test",
                "type": "message",
                "role": "assistant",
                "model": "test-model",
                "content": [{"type": "text", "text": "test"}],
                "stop_reason": None,
                "stop_sequence": None,
                "usage": {"input_tokens": 0, "output_tokens": 0},
            },
        }
        entry = AssistantTranscriptItem.model_validate(data)
        assert entry.gitBranch == "HEAD"
