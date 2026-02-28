#!/usr/bin/env python3
"""
Unit tests for ProgressTranscriptItem model
"""

from typing import Any

from vibehist.core.models.transcript_items.progress import (
    AgentProgressData,
    BashProgressData,
    HookProgressData,
    McpProgressData,
    ProgressTranscriptItem,
    SearchResultsReceivedProgressData,
    WaitingForTaskProgressData,
)

# Real data samples from actual Claude Code transcript JSONL files
SAMPLE_PROGRESS_BASH: dict[str, Any] = {
    "parentUuid": "78e37cc0-5a4e-42dc-a10b-4300b7dab1b0",
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "6536ce47-699c-4e07-bb3c-6312f8789222",
    "version": "2.1.49",
    "gitBranch": "test/progress-transcript",
    "slug": "functional-gathering-raccoon",
    "type": "progress",
    "data": {
        "type": "bash_progress",
        "output": "",
        "fullOutput": "",
        "elapsedTimeSeconds": 3,
        "totalLines": 0,
        "totalBytes": 0,
        "taskId": "b7f6f80",
    },
    "toolUseID": "bash-progress-0",
    "parentToolUseID": "call_67306ff6dd1a4e6c8b50055e",
    "uuid": "33d63c70-3b00-4706-9918-68740feb7ccb",
    "timestamp": "2026-02-27T08:22:03.232Z",
}

SAMPLE_PROGRESS_HOOK: dict[str, Any] = {
    "parentUuid": "8e583573-3828-4f4c-a1b6-d7c77c9bec5e",
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "f47647f9-4bd7-4b5d-8ad8-f5f64c50de57",
    "version": "2.1.49",
    "gitBranch": "test/progress-transcript",
    "slug": "wobbly-bouncing-hare",
    "type": "progress",
    "data": {
        "type": "hook_progress",
        "hookEvent": "PostToolUse",
        "hookName": "PostToolUse:Grep",
        "command": "callback",
    },
    "parentToolUseID": "call_0fedc74d7a6a4113b707286e",
    "toolUseID": "call_0fedc74d7a6a4113b707286e",
    "timestamp": "2026-02-24T02:20:59.993Z",
    "uuid": "f9784b79-4226-4e65-8887-8b146812771b",
}

# Real agent_progress data from actual Claude Code transcript files
SAMPLE_PROGRESS_AGENT: dict[str, Any] = {
    "parentUuid": "1daae4b7-c91b-4388-bd30-eb6f1ed2ff68",
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "989b5033-5ed9-45a6-924c-f16d9438b299",
    "version": "2.1.34",
    "gitBranch": "test/progress-transcript",
    "type": "progress",
    "data": {
        "message": {
            "type": "user",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Search the codebase to find "
                            "field definitions of transcript "
                            "when type is 'progress'"
                        ),
                    }
                ],
            },
            "uuid": "476650f6-7f89-48c9-9123-690546cbf632",
            "timestamp": "2026-02-11T01:18:27.511Z",
        },
        "normalizedMessages": [],
        "type": "agent_progress",
        "prompt": "Search the codebase to find field definitions of transcript when type is 'progress'",
        "agentId": "aed26bf",
    },
    "toolUseID": "agent_msg_20260211091823ead29ab0958947b9",
    "parentToolUseID": "call_83dffe55057b4468a0ee5ed4",
    "uuid": "d9bc65f4-37ec-4f43-af0e-93d3c5ab76c7",
    "timestamp": "2026-02-11T01:18:27.513Z",
}

SAMPLE_PROGRESS_MCP: dict[str, Any] = {
    "type": "progress",
    "sessionId": "test-session-id",
    "parentUuid": None,
    "parentToolUseID": "call_test123",
    "toolUseID": "call_mcp456",
    "uuid": "mcp-progress-uuid",
    "timestamp": "2026-02-27T10:00:00.000Z",
    "version": "2.1.49",
    "cwd": "/test/workspace",
    "gitBranch": "main",
    "isSidechain": False,
    "userType": "external",
    "data": {
        "type": "mcp_progress",
        "status": "completed",
        "serverName": "filesystem",
        "toolName": "read_file",
        "elapsedTimeMs": 150,
    },
}

SAMPLE_PROGRESS_SEARCH_RESULTS: dict[str, Any] = {
    "type": "progress",
    "sessionId": "test-session-id",
    "parentUuid": None,
    "parentToolUseID": "call_test123",
    "toolUseID": "call_search456",
    "uuid": "search-progress-uuid",
    "timestamp": "2026-02-27T10:00:00.000Z",
    "version": "2.1.49",
    "cwd": "/test/workspace",
    "gitBranch": "main",
    "isSidechain": False,
    "userType": "external",
    "data": {
        "type": "search_results_received",
        "query": "test query",
        "resultCount": 10,
    },
}

SAMPLE_PROGRESS_WAITING: dict[str, Any] = {
    "type": "progress",
    "sessionId": "test-session-id",
    "parentUuid": None,
    "parentToolUseID": "call_test123",
    "toolUseID": "call_wait456",
    "uuid": "waiting-progress-uuid",
    "timestamp": "2026-02-27T10:00:00.000Z",
    "version": "2.1.49",
    "cwd": "/test/workspace",
    "gitBranch": "main",
    "isSidechain": False,
    "userType": "external",
    "data": {
        "type": "waiting_for_task",
        "taskDescription": "Processing file",
        "taskType": "bash",
    },
}


class TestBashProgressData:
    """Test BashProgressData model"""

    def test_bash_progress_real_data(self) -> None:
        """Test creating BashProgressData using model_validate with real data"""
        data = BashProgressData.model_validate(SAMPLE_PROGRESS_BASH["data"])

        assert data.type == "bash_progress"
        assert data.elapsedTimeSeconds == 3
        assert data.fullOutput == ""
        assert data.output == ""
        assert data.totalLines == 0
        assert data.totalBytes == 0
        assert data.taskId == "b7f6f80"

    def test_bash_progress_fields(self) -> None:
        """Test all BashProgressData fields"""
        data = BashProgressData.model_validate(SAMPLE_PROGRESS_BASH["data"])

        assert hasattr(data, "type")
        assert hasattr(data, "elapsedTimeSeconds")
        assert hasattr(data, "fullOutput")
        assert hasattr(data, "output")
        assert hasattr(data, "totalLines")
        assert hasattr(data, "totalBytes")
        assert hasattr(data, "taskId")


class TestHookProgressData:
    """Test HookProgressData model"""

    def test_hook_progress_real_data(self) -> None:
        """Test creating HookProgressData using model_validate with real data"""
        data = HookProgressData.model_validate(SAMPLE_PROGRESS_HOOK["data"])

        assert data.type == "hook_progress"
        assert data.hookEvent == "PostToolUse"
        assert data.hookName == "PostToolUse:Grep"
        assert data.command == "callback"

    def test_hook_progress_fields(self) -> None:
        """Test all HookProgressData fields"""
        data = HookProgressData.model_validate(SAMPLE_PROGRESS_HOOK["data"])

        assert hasattr(data, "type")
        assert hasattr(data, "hookEvent")
        assert hasattr(data, "hookName")
        assert hasattr(data, "command")


class TestAgentProgressData:
    """Test AgentProgressData model"""

    def test_agent_progress_with_model_validate(self) -> None:
        """Test creating AgentProgressData using model_validate with real data"""
        data = AgentProgressData.model_validate(SAMPLE_PROGRESS_AGENT["data"])

        assert data.type == "agent_progress"
        assert data.agentId == "aed26bf"
        assert (
            data.prompt
            == "Search the codebase to find field definitions of transcript when type is 'progress'"
        )
        assert data.resume is None

    def test_agent_progress_fields(self) -> None:
        """Test all AgentProgressData fields"""
        data = AgentProgressData.model_validate(SAMPLE_PROGRESS_AGENT["data"])

        assert hasattr(data, "type")
        assert hasattr(data, "agentId")
        assert hasattr(data, "prompt")
        assert hasattr(data, "resume")
        assert hasattr(data, "message")
        assert hasattr(data, "normalizedMessages")


class TestMcpProgressData:
    """Test McpProgressData model"""

    def test_mcp_progress_with_model_validate(self) -> None:
        """Test creating McpProgressData using model_validate"""
        data = McpProgressData.model_validate(SAMPLE_PROGRESS_MCP["data"])

        assert data.type == "mcp_progress"
        assert data.status == "completed"
        assert data.serverName == "filesystem"
        assert data.toolName == "read_file"
        assert data.elapsedTimeMs == 150

    def test_mcp_progress_fields(self) -> None:
        """Test all McpProgressData fields"""
        data = McpProgressData.model_validate(SAMPLE_PROGRESS_MCP["data"])

        assert hasattr(data, "type")
        assert hasattr(data, "status")
        assert hasattr(data, "serverName")
        assert hasattr(data, "toolName")
        assert hasattr(data, "elapsedTimeMs")


class TestSearchResultsReceivedProgressData:
    """Test SearchResultsReceivedProgressData model"""

    def test_search_results_with_model_validate(self) -> None:
        """Test creating SearchResultsReceivedProgressData using model_validate"""
        data = SearchResultsReceivedProgressData.model_validate(
            SAMPLE_PROGRESS_SEARCH_RESULTS["data"]
        )

        assert data.type == "search_results_received"
        assert data.query == "test query"
        assert data.resultCount == 10

    def test_search_results_fields(self) -> None:
        """Test all SearchResultsReceivedProgressData fields"""
        data = SearchResultsReceivedProgressData.model_validate(
            SAMPLE_PROGRESS_SEARCH_RESULTS["data"]
        )

        assert hasattr(data, "type")
        assert hasattr(data, "query")
        assert hasattr(data, "resultCount")


class TestWaitingForTaskProgressData:
    """Test WaitingForTaskProgressData model"""

    def test_waiting_for_task_with_model_validate(self) -> None:
        """Test creating WaitingForTaskProgressData using model_validate"""
        data = WaitingForTaskProgressData.model_validate(SAMPLE_PROGRESS_WAITING["data"])

        assert data.type == "waiting_for_task"
        assert data.taskDescription == "Processing file"
        assert data.taskType == "bash"

    def test_waiting_for_task_fields(self) -> None:
        """Test all WaitingForTaskProgressData fields"""
        data = WaitingForTaskProgressData.model_validate(SAMPLE_PROGRESS_WAITING["data"])

        assert hasattr(data, "type")
        assert hasattr(data, "taskDescription")
        assert hasattr(data, "taskType")


class TestProgressTranscriptItem:
    """Test ProgressTranscriptItem model"""

    def test_required_fields_real_data_bash(self) -> None:
        """Test creating ProgressTranscriptItem with bash_progress using real data"""
        item = ProgressTranscriptItem.model_validate(SAMPLE_PROGRESS_BASH)

        assert item.type == "progress"
        assert item.sessionId == "6536ce47-699c-4e07-bb3c-6312f8789222"
        assert item.uuid == "33d63c70-3b00-4706-9918-68740feb7ccb"
        assert item.toolUseID == "bash-progress-0"
        assert item.parentToolUseID == "call_67306ff6dd1a4e6c8b50055e"

    def test_required_fields_real_data_hook(self) -> None:
        """Test creating ProgressTranscriptItem with hook_progress using real data"""
        item = ProgressTranscriptItem.model_validate(SAMPLE_PROGRESS_HOOK)

        assert item.type == "progress"
        assert item.sessionId == "f47647f9-4bd7-4b5d-8ad8-f5f64c50de57"
        assert item.uuid == "f9784b79-4226-4e65-8887-8b146812771b"

    def test_base_fields_real_data(self) -> None:
        """Test base ProgressTranscriptItem fields using real data"""
        item = ProgressTranscriptItem.model_validate(SAMPLE_PROGRESS_BASH)

        assert item.version == "2.1.49"
        assert item.cwd == "/Users/root/workspace/project"
        assert item.gitBranch == "test/progress-transcript"
        assert item.slug == "functional-gathering-raccoon"
        assert item.isSidechain is False
        assert item.userType == "external"

    def test_type_default_value(self) -> None:
        """Test that type field has default value 'progress'"""
        item = ProgressTranscriptItem.model_validate(SAMPLE_PROGRESS_BASH)

        assert item.type == "progress"

    def test_timestamp_parsing_real_data(self) -> None:
        """Test ISO 8601 timestamp parsing using real data"""
        item = ProgressTranscriptItem.model_validate(SAMPLE_PROGRESS_BASH)

        import datetime

        assert isinstance(item.timestamp, datetime.datetime)
        assert item.timestamp.year == 2026
        assert item.timestamp.month == 2
        assert item.timestamp.day == 27

    def test_data_bash_progress_real_data(self) -> None:
        """Test data field with BashProgressData using real data"""
        item = ProgressTranscriptItem.model_validate(SAMPLE_PROGRESS_BASH)

        assert isinstance(item.data, BashProgressData)
        assert item.data.type == "bash_progress"
        assert item.data.elapsedTimeSeconds == 3

    def test_data_hook_progress_real_data(self) -> None:
        """Test data field with HookProgressData using real data"""
        item = ProgressTranscriptItem.model_validate(SAMPLE_PROGRESS_HOOK)

        assert isinstance(item.data, HookProgressData)
        assert item.data.type == "hook_progress"
        assert item.data.hookName == "PostToolUse:Grep"

    def test_agent_id_field(self) -> None:
        """Test agentId field - inside data for agent_progress"""
        item = ProgressTranscriptItem.model_validate(SAMPLE_PROGRESS_AGENT)

        # agentId at the ProgressTranscriptItem level is None
        assert item.agentId is None
        # agentId inside AgentProgressData has the actual value
        assert isinstance(item.data, AgentProgressData)
        assert item.data.agentId == "aed26bf"

    def test_parent_uuid_none_real_data(self) -> None:
        """Test with parentUuid as None"""
        item = ProgressTranscriptItem.model_validate(SAMPLE_PROGRESS_HOOK)

        assert item.parentUuid == "8e583573-3828-4f4c-a1b6-d7c77c9bec5e"

    def test_git_branch_default_when_omitted(self) -> None:
        """Test that gitBranch defaults to 'HEAD' when omitted"""
        data = {
            **SAMPLE_PROGRESS_BASH,
            "gitBranch": None,
        }
        # Remove gitBranch to test default
        del data["gitBranch"]
        item = ProgressTranscriptItem.model_validate(data)

        assert item.gitBranch == "HEAD"

    def test_all_progress_data_types(self) -> None:
        """Test that all progress data types can be validated"""
        bash = ProgressTranscriptItem.model_validate(SAMPLE_PROGRESS_BASH)
        hook = ProgressTranscriptItem.model_validate(SAMPLE_PROGRESS_HOOK)
        agent = ProgressTranscriptItem.model_validate(SAMPLE_PROGRESS_AGENT)
        mcp = ProgressTranscriptItem.model_validate(SAMPLE_PROGRESS_MCP)
        search = ProgressTranscriptItem.model_validate(SAMPLE_PROGRESS_SEARCH_RESULTS)
        waiting = ProgressTranscriptItem.model_validate(SAMPLE_PROGRESS_WAITING)

        assert isinstance(bash.data, BashProgressData)
        assert isinstance(hook.data, HookProgressData)
        assert isinstance(agent.data, AgentProgressData)
        assert isinstance(mcp.data, McpProgressData)
        assert isinstance(search.data, SearchResultsReceivedProgressData)
        assert isinstance(waiting.data, WaitingForTaskProgressData)
