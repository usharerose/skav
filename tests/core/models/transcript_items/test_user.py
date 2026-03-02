#!/usr/bin/env python3
"""
Unit tests for UserTranscriptItem model
"""

import datetime
from typing import Any, cast

import pytest

from skav.core.models.contents import ToolResultContentItem
from skav.core.models.messages import UserMessage
from skav.core.models.tool_use_result import ToolUseResult
from skav.core.models.transcript_items.user import UserTranscriptItem

SAMPLE_USER_ENTRY_FULL: dict[str, Any] = {
    "uuid": "fcd3c922-f183-4fe4-9a12-357a87404ae3",
    "timestamp": "2026-02-22T14:57:38.926Z",
    "parentUuid": "7965d3b5-a750-4fee-8da4-18e57b8bb686",
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "1d3713b2-ed06-483d-a7be-92596e87e84c",
    "version": "2.1.49",
    "gitBranch": "master",
    "slug": "sequential-frolicking-treasure",
    "type": "user",
    "message": {
        "role": "user",
        "content": (
            "Implement the following plan:\n\n"
            "# Skav Transcript JSON Schema Design\n\n"
            "## Context\n\n"
            "This document designs a comprehensive schema for Claude Code transcript JSONL data "
            "based on analysis of actual transcript data from project files\n\n"
            "The goal is to understand the structure and patterns of Claude Code transcript data "
            "to inform the Skav project's data collection and analysis capabilities."
        ),
    },
}

SAMPLE_USER_ENTRY_WITH_TOOL_RESULT: dict[str, Any] = {
    "uuid": "64d41045-44bc-4156-8a04-497f2d43ad20",
    "timestamp": "2026-02-22T14:57:42.789Z",
    "parentUuid": "e26025aa-0543-4f40-a4bb-478982ae811b",
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "1d3713b2-ed06-483d-a7be-92596e87e84c",
    "version": "2.1.49",
    "gitBranch": "master",
    "slug": "sequential-frolicking-treasure",
    "type": "user",
    "message": {
        "role": "user",
        "content": [
            {
                "tool_use_id": "call_f6a268fe6491447ba11e1099",
                "type": "tool_result",
                "content": (
                    "     1→#!/usr/bin/env python3\n"
                    '     2→"""\n'
                    "     3→Type definitions for Claude Code Hook events\n"
                    "     4→Based on official documentation: https://code.claude.com/docs/en/hooks\n"
                    '     5→"""\n'
                ),
            }
        ],
    },
}

SAMPLE_USER_ENTRY_WITH_ERROR: dict[str, Any] = {
    "parentUuid": "e26025aa-0543-4f40-a4bb-478982ae811b",
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "1d3713b2-ed06-483d-a7be-92596e87e84c",
    "version": "2.1.49",
    "gitBranch": "master",
    "slug": "sequential-frolicking-treasure",
    "type": "user",
    "message": {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "content": (
                    "File does not exist. "
                    "Note: your current working directory is /Users/root/workspace/project. "
                    "Did you mean models?"
                ),
                "is_error": True,
                "tool_use_id": "call_d9860daaecc9416e94d7c2f3",
            }
        ],
    },
    "uuid": "021bf8c9-3026-4326-a9ce-30cfa69f875c",
    "timestamp": "2026-02-22T14:57:44.985Z",
    "toolUseResult": "Error: File does not exist.",
    "sourceToolAssistantUUID": "e26025aa-0543-4f40-a4bb-478982ae811b",
}

SAMPLE_USER_ENTRY_WITH_THINKING_METADATA: dict[str, Any] = {
    "parentUuid": None,
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "2495d168-c398-4275-b568-6d03b0805685",
    "version": "2.1.39",
    "gitBranch": "master",
    "type": "user",
    "message": {
        "role": "user",
        "content": "请帮我简要分析，当前的claude code支持在哪些事件上增加hook配置？",
    },
    "uuid": "c4fe3537-49ec-47d5-899b-3d6dbb3b7af6",
    "timestamp": "2026-02-12T05:24:52.336Z",
    "thinkingMetadata": {"maxThinkingTokens": 31999},
    "todos": [],
    "permissionMode": "default",
}

SAMPLE_USER_ENTRY_WITH_PERMISSION_MODE_PLAN: dict[str, Any] = {
    "parentUuid": "ac27042d-0d98-492c-aaf8-a6f61d060686",
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "d357933d-7244-48e3-850c-b8887b04aafd",
    "version": "2.1.41",
    "gitBranch": "fix/permission-mode-definition",
    "slug": "clever-mixing-papert",
    "type": "user",
    "message": {
        "role": "user",
        "content": (
            "Please review @/Users/root/workspace/project/ "
            "permission mode definition and implementation"
        ),
    },
    "uuid": "23e2070e-188d-4e1d-b34a-e5ee29416744",
    "timestamp": "2026-02-18T11:22:55.740Z",
    "thinkingMetadata": {"maxThinkingTokens": 31999},
    "todos": [],
    "permissionMode": "plan",
}

SAMPLE_USER_ENTRY_WITH_TOOL_RESULT_DICT: dict[str, Any] = {
    "parentUuid": "e26025aa-0543-4f40-a4bb-478982ae811b",
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "1d3713b2-ed06-483d-a7be-92596e87e84c",
    "version": "2.1.49",
    "gitBranch": "master",
    "slug": "sequential-frolicking-treasure",
    "type": "user",
    "message": {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": "call_f6a268fe6491447ba11e1099",
                "content": "Successfully read the file",
            }
        ],
    },
    "uuid": "75d41045-44bc-4156-8a04-497f2d43ad21",
    "timestamp": "2026-02-22T14:57:42.790Z",
    "toolUseResult": {
        "mode": "files_with_matches",
        "filenames": ["test/file1.py", "test/file2.py"],
        "numFiles": 2,
    },
}


class TestUserTranscriptItem:
    """Test UserTranscriptItem model validation and parsing"""

    def test_required_fields(self) -> None:
        """Test that all required fields are present"""
        entry = UserTranscriptItem.model_validate(SAMPLE_USER_ENTRY_FULL)

        assert entry.type == "user"
        assert entry.sessionId == "1d3713b2-ed06-483d-a7be-92596e87e84c"
        assert entry.uuid == "fcd3c922-f183-4fe4-9a12-357a87404ae3"
        assert isinstance(entry.timestamp, datetime.datetime)
        assert entry.version == "2.1.49"
        assert entry.cwd == "/Users/root/workspace/project"
        assert entry.gitBranch == "master"
        assert entry.isSidechain is False
        assert entry.userType == "external"
        assert "Skav" in entry.message.content

    def test_timestamp_parsing(self) -> None:
        """Test ISO 8601 timestamp parsing"""
        data = {
            **SAMPLE_USER_ENTRY_WITH_ERROR,
        }
        entry = UserTranscriptItem.model_validate(data)

        assert isinstance(entry.timestamp, datetime.datetime)
        assert entry.timestamp.year == 2026
        assert entry.timestamp.month == 2
        assert entry.timestamp.day == 22
        assert entry.timestamp.hour == 14
        assert entry.timestamp.minute == 57
        assert entry.timestamp.second == 44
        assert entry.timestamp.tzinfo is not None

    def test_timestamp_already_datetime(self) -> None:
        """Test that datetime objects pass through unchanged"""
        now = datetime.datetime.now(datetime.timezone.utc)
        entry = UserTranscriptItem(
            sessionId="test",
            uuid="test",
            timestamp=now,
            version="1.0",
            cwd="/test",
            isSidechain=False,
            message=UserMessage(role="user", content="test"),
            userType="external",
        )

        assert entry.timestamp == now

    def test_with_agent_id(self) -> None:
        """Test parsing with agentId field (subagent messages)"""
        data = {
            "sessionId": "test",
            "uuid": "test",
            "timestamp": "2026-02-25T10:00:00Z",
            "version": "1.0",
            "cwd": "/test",
            "gitBranch": "main",
            "isSidechain": True,
            "agentId": "agent-123",
            "message": {"role": "user", "content": "test"},
            "userType": "external",
        }
        entry = UserTranscriptItem.model_validate(data)

        assert entry.agentId == "agent-123"
        assert entry.isSidechain is True

    def test_with_thinking_metadata(self) -> None:
        """Test parsing with thinking metadata"""
        entry = UserTranscriptItem.model_validate(SAMPLE_USER_ENTRY_WITH_THINKING_METADATA)

        assert entry.thinkingMetadata is not None
        assert entry.thinkingMetadata.maxThinkingTokens == 31999
        assert entry.permissionMode == "default"
        assert entry.todos == []

    def test_with_tool_use_result_string(self) -> None:
        """Test parsing with string tool use result"""
        entry = UserTranscriptItem.model_validate(SAMPLE_USER_ENTRY_WITH_ERROR)

        assert entry.toolUseResult == "Error: File does not exist."
        assert entry.sourceToolAssistantUUID == "e26025aa-0543-4f40-a4bb-478982ae811b"

    def test_with_tool_use_result_dict(self) -> None:
        """Test parsing with dict tool use result"""
        entry = UserTranscriptItem.model_validate(SAMPLE_USER_ENTRY_WITH_TOOL_RESULT_DICT)

        assert entry.toolUseResult is not None
        assert isinstance(entry.toolUseResult, ToolUseResult)
        assert entry.toolUseResult.mode == "files_with_matches"
        assert entry.toolUseResult.numFiles == 2
        assert isinstance(entry.toolUseResult.filenames, list)
        assert "test/file1.py" in entry.toolUseResult.filenames

    def test_message_with_list_content(self) -> None:
        """Test message with structured list content"""
        entry = UserTranscriptItem.model_validate(SAMPLE_USER_ENTRY_WITH_TOOL_RESULT)

        assert isinstance(entry.message.content, list)
        assert len(entry.message.content) == 1
        content_item, *_ = entry.message.content
        assert isinstance(content_item, ToolResultContentItem)
        assert content_item.tool_use_id == "call_f6a268fe6491447ba11e1099"
        assert "#!/usr/bin/env python3" in content_item.content

    @pytest.mark.skip(reason="TODO: implement when the enumerable values of `userType` are defined")
    def test_invalid_user_type_rejected(self) -> None:
        """Test that invalid userType is rejected"""
        # Make a copy with invalid userType
        data = {**SAMPLE_USER_ENTRY_FULL, "userType": "invalid"}
        with pytest.raises(ValueError):
            UserTranscriptItem.model_validate(data)

    def test_invalid_timestamp_format(self) -> None:
        """Test that invalid timestamp format is handled"""
        # Make a copy with invalid timestamp
        data = {**SAMPLE_USER_ENTRY_FULL, "timestamp": "invalid-date"}
        with pytest.raises(ValueError):
            UserTranscriptItem.model_validate(data)

    def test_type_default_value(self) -> None:
        """Test that type field has default value 'user'"""
        data = {
            "sessionId": "test",
            "uuid": "test",
            "timestamp": "2026-02-25T10:00:00Z",
            "version": "1.0",
            "cwd": "/test",
            "isSidechain": False,
            "message": {"role": "user", "content": "test"},
            "userType": "external",
        }
        entry = UserTranscriptItem.model_validate(data)
        assert entry.type == "user"

    def test_git_branch_default_when_omitted(self) -> None:
        """Test that gitBranch defaults to 'HEAD' when omitted"""
        data = {
            "sessionId": "test",
            "uuid": "test",
            "timestamp": "2026-02-25T10:00:00Z",
            "version": "1.0",
            "cwd": "/test",
            "isSidechain": False,
            "message": {"role": "user", "content": "test"},
            "userType": "external",
        }
        entry = UserTranscriptItem.model_validate(data)
        assert entry.gitBranch == "HEAD"

    def test_parent_uuid_default_when_omitted(self) -> None:
        """Test that parentUuid defaults to None when omitted"""
        data = {
            "sessionId": "test",
            "uuid": "test",
            "timestamp": "2026-02-25T10:00:00Z",
            "version": "1.0",
            "cwd": "/test",
            "isSidechain": False,
            "message": {"role": "user", "content": "test"},
            "userType": "external",
        }
        entry = UserTranscriptItem.model_validate(data)
        assert entry.parentUuid is None

    def test_parent_uuid_with_value(self) -> None:
        """Test with actual parentUuid value"""
        entry = UserTranscriptItem.model_validate(SAMPLE_USER_ENTRY_FULL)

        assert entry.parentUuid == "7965d3b5-a750-4fee-8da4-18e57b8bb686"

    def test_parent_uuid_none(self) -> None:
        """Test with parentUuid as None"""
        entry = UserTranscriptItem.model_validate(SAMPLE_USER_ENTRY_WITH_THINKING_METADATA)

        assert entry.parentUuid is None

    def test_message_with_multiple_content_items(self) -> None:
        """Test message with multiple content items"""
        data = {
            "sessionId": "test",
            "uuid": "test",
            "timestamp": "2026-02-25T10:00:00Z",
            "version": "1.0",
            "cwd": "/test",
            "gitBranch": "main",
            "isSidechain": False,
            "userType": "external",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "tool-123",
                        "content": "First result",
                    },
                    {
                        "type": "tool_result",
                        "tool_use_id": "tool-456",
                        "content": "Second result",
                    },
                ],
            },
        }
        entry = UserTranscriptItem.model_validate(data)

        assert isinstance(entry.message.content, list)
        assert len(entry.message.content) == 2
        for item in entry.message.content:
            assert isinstance(item, ToolResultContentItem)
        # Use cast to help mypy understand the narrowed type
        item0 = cast(ToolResultContentItem, entry.message.content[0])
        item1 = cast(ToolResultContentItem, entry.message.content[1])
        assert item0.tool_use_id == "tool-123"
        assert item1.tool_use_id == "tool-456"

    def test_slug_field(self) -> None:
        """Test slug field"""
        entry = UserTranscriptItem.model_validate(SAMPLE_USER_ENTRY_FULL)

        assert entry.slug == "sequential-frolicking-treasure"

    def test_is_error_in_tool_result(self) -> None:
        """Test is_error field in tool_result content"""
        entry = UserTranscriptItem.model_validate(SAMPLE_USER_ENTRY_WITH_ERROR)

        assert isinstance(entry.message.content, list)
        content_item, *_ = entry.message.content
        assert isinstance(content_item, ToolResultContentItem)
        assert content_item.is_error is True
        assert "File does not exist" in content_item.content

    def test_permission_mode_default(self) -> None:
        """Test permissionMode with 'default' value"""
        entry = UserTranscriptItem.model_validate(SAMPLE_USER_ENTRY_WITH_THINKING_METADATA)

        assert entry.permissionMode == "default"

    def test_permission_mode_plan(self) -> None:
        """Test permissionMode with 'plan' value"""
        entry = UserTranscriptItem.model_validate(SAMPLE_USER_ENTRY_WITH_PERMISSION_MODE_PLAN)

        assert entry.permissionMode == "plan"
        assert entry.thinkingMetadata is not None
        assert entry.thinkingMetadata.maxThinkingTokens == 31999
        assert entry.todos == []
        assert "permission mode definition and implementation" in entry.message.content
