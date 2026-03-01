#!/usr/bin/env python3
"""
Unit tests for System transcript item models
"""

from typing import Any

import pytest

from vibehist.core.models.transcript_items.system import (
    BaseSystemTranscriptItem,
    CompactMetadata,
    HookInfo,
    MicrocompactMetadata,
    SystemApiErrorMetadata,
    SystemApiErrorTranscriptItem,
    SystemCompactBoundaryTranscriptItem,
    SystemLocalCommandTranscriptItem,
    SystemMicrocompactBoundaryTranscriptItem,
    SystemStopHookSummaryTranscriptItem,
    SystemTranscriptItem,
    SystemTurnDurationTranscriptItem,
)

SAMPLE_SYSTEM_API_ERROR: dict[str, Any] = {
    "parentUuid": "d9c8166a-70e9-420f-8ad6-d9d4b36cf0ef",
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "f47647f9-4bd7-4b5d-8ad8-f5f64c50de57",
    "version": "2.1.49",
    "gitBranch": "feat/system-model",
    "slug": "wobbly-bouncing-hare",
    "type": "system",
    "subtype": "api_error",
    "level": "error",
    "error": {
        "status": 500,
        "headers": {},
        "requestID": None,
        "error": {
            "type": "error",
            "error": {
                "type": "api_error",
                "message": "Internal Network Failure",
            },
            "request_id": "2026022410491644774536211b4479",
        },
    },
    "retryInMs": 592.0580048627735,
    "retryAttempt": 1,
    "maxRetries": 10,
    "timestamp": "2026-02-24T02:49:16.867Z",
    "uuid": "a22cfa7c-5a3c-4a6e-bdbf-02ef23e1086c",
}

SAMPLE_SYSTEM_TURN_DURATION: dict[str, Any] = {
    "parentUuid": "28d032c6-6f03-4e38-81d2-1e124c9521e7",
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "f47647f9-4bd7-4b5d-8ad8-f5f64c50de57",
    "version": "2.1.49",
    "gitBranch": "feat/system-model",
    "slug": "wobbly-bouncing-hare",
    "type": "system",
    "subtype": "turn_duration",
    "durationMs": 33717,
    "timestamp": "2026-02-24T02:21:27.141Z",
    "uuid": "e6b62072-304b-4c4a-8aec-34b6921e71a4",
    "isMeta": False,
}

SAMPLE_SYSTEM_COMPACT_BOUNDARY: dict[str, Any] = {
    "parentUuid": None,
    "logicalParentUuid": "55e5ed54-d95d-46a8-8a0a-7deff24c770d",
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "a41ea044-80d1-41c0-8164-908d1a0ff2b1",
    "version": "2.1.49",
    "gitBranch": "feat/system-model",
    "slug": "smooth-skipping-turtle",
    "type": "system",
    "subtype": "compact_boundary",
    "content": "Conversation compacted",
    "isMeta": False,
    "timestamp": "2026-02-24T10:41:09.493Z",
    "uuid": "17306af6-e827-4460-b6b3-dfdb758fab7c",
    "level": "info",
    "compactMetadata": {
        "trigger": "auto",
        "preTokens": 168213,
    },
}

SAMPLE_SYSTEM_MICROCOMPACT_BOUNDARY: dict[str, Any] = {
    "parentUuid": "2ceeda71-d66a-4147-b084-600b65448cdd",
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "a41ea044-80d1-41c0-8164-908d1a0ff2b1",
    "version": "2.1.49",
    "gitBranch": "feat/system-model",
    "slug": "smooth-skipping-turtle",
    "type": "system",
    "subtype": "microcompact_boundary",
    "content": "Context microcompacted",
    "isMeta": False,
    "timestamp": "2026-02-25T08:47:10.299Z",
    "uuid": "c06067c5-4b9b-4c28-a6d1-88d5c2ace4e0",
    "level": "info",
    "microcompactMetadata": {
        "trigger": "auto",
        "preTokens": 58819,
        "tokensSaved": 20697,
        "compactedToolIds": [
            "call_d1aa9bb694474bd4a80131f9",
            "call_9d117ddbb4714694a3076183",
            "call_f6fe0c1b0c5c43258e49a971",
        ],
        "clearedAttachmentUUIDs": [],
    },
}

SAMPLE_SYSTEM_STOP_HOOK_SUMMARY: dict[str, Any] = {
    "parentUuid": "dbfc3edb-c3a5-4509-92b4-64deac4f6fd1",
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Users/root/workspace/project",
    "sessionId": "bd3743ba-e026-425e-9abe-687dd061aaa4",
    "version": "2.1.41",
    "gitBranch": "feat/collect-transcript",
    "slug": "goofy-dancing-pumpkin",
    "type": "system",
    "subtype": "stop_hook_summary",
    "hookCount": 1,
    "hookInfos": [
        {
            "command": (
                'PYTHONPATH="$CLAUDE_PROJECT_DIR" '
                '"$CLAUDE_PROJECT_DIR"/.venv/bin/python -m vibehist.app --debug'
            )
        }
    ],
    "hookErrors": [],
    "preventedContinuation": False,
    "stopReason": "",
    "hasOutput": True,
    "level": "suggestion",
    "timestamp": "2026-02-17T11:49:27.208Z",
    "uuid": "c10587b6-acf0-4642-aee0-aeb65ba03fa8",
    "toolUseID": "467a2f8b-3b8b-4300-b3c3-3cf417796d0a",
}

SAMPLE_SYSTEM_LOCAL_COMMAND: dict[str, Any] = {
    "type": "system",
    "subtype": "local_command",
    "sessionId": "test-session-id",
    "parentUuid": None,
    "uuid": "local-command-uuid-123",
    "timestamp": "2026-02-27T10:00:00.000Z",
    "version": "2.1.49",
    "cwd": "/test/workspace",
    "gitBranch": "main",
    "isSidechain": False,
    "userType": "external",
    "content": "Running local command: echo 'test'",
    "isMeta": False,
    "level": "info",
}


class TestSystemTurnDurationTranscriptItem:
    """Test SystemTurnDurationTranscriptItem model"""

    def test_required_fields(self) -> None:
        """Test creating SystemTurnDurationTranscriptItem"""
        item = SystemTurnDurationTranscriptItem.model_validate(SAMPLE_SYSTEM_TURN_DURATION)

        assert item.type == "system"
        assert item.subtype == "turn_duration"
        assert item.durationMs == 33717
        assert item.isMeta is False

    def test_base_fields(self) -> None:
        """Test base SystemTranscriptItem fields"""
        item = SystemTurnDurationTranscriptItem.model_validate(SAMPLE_SYSTEM_TURN_DURATION)

        assert item.sessionId == "f47647f9-4bd7-4b5d-8ad8-f5f64c50de57"
        assert item.uuid == "e6b62072-304b-4c4a-8aec-34b6921e71a4"
        assert item.parentUuid == "28d032c6-6f03-4e38-81d2-1e124c9521e7"
        assert item.version == "2.1.49"
        assert item.cwd == "/Users/root/workspace/project"
        assert item.gitBranch == "feat/system-model"
        assert item.slug == "wobbly-bouncing-hare"
        assert item.isSidechain is False
        assert item.userType == "external"


class TestSystemApiErrorTranscriptItem:
    """Test SystemApiErrorTranscriptItem model"""

    def test_required_fields(self) -> None:
        """Test creating SystemApiErrorTranscriptItem"""
        item = SystemApiErrorTranscriptItem.model_validate(SAMPLE_SYSTEM_API_ERROR)

        assert item.type == "system"
        assert item.subtype == "api_error"
        assert item.level == "error"
        assert item.retryAttempt == 1
        assert item.maxRetries == 10
        assert abs(item.retryInMs - 592.058) < 0.001

    def test_error_structure(self) -> None:
        """Test error field structure"""
        item = SystemApiErrorTranscriptItem.model_validate(SAMPLE_SYSTEM_API_ERROR)

        assert item.error.status == 500
        assert item.error.headers == {}
        assert item.error.requestID is None
        assert isinstance(item.error.error, SystemApiErrorMetadata)
        assert item.error.error.request_id == "2026022410491644774536211b4479"


class TestSystemCompactBoundaryTranscriptItem:
    """Test SystemCompactBoundaryTranscriptItem model"""

    def test_required_fields(self) -> None:
        """Test creating SystemCompactBoundaryTranscriptItem"""
        item = SystemCompactBoundaryTranscriptItem.model_validate(SAMPLE_SYSTEM_COMPACT_BOUNDARY)

        assert item.type == "system"
        assert item.subtype == "compact_boundary"
        assert item.content == "Conversation compacted"
        assert item.isMeta is False
        assert item.level == "info"

    def test_compact_metadata(self) -> None:
        """Test compactMetadata field"""
        item = SystemCompactBoundaryTranscriptItem.model_validate(SAMPLE_SYSTEM_COMPACT_BOUNDARY)

        assert isinstance(item.compactMetadata, CompactMetadata)
        assert item.compactMetadata.trigger == "auto"
        assert item.compactMetadata.preTokens == 168213

    def test_logical_parent_uuid(self) -> None:
        """Test logicalParentUuid field"""
        item = SystemCompactBoundaryTranscriptItem.model_validate(SAMPLE_SYSTEM_COMPACT_BOUNDARY)

        assert item.logicalParentUuid == "55e5ed54-d95d-46a8-8a0a-7deff24c770d"


class TestSystemMicrocompactBoundaryTranscriptItem:
    """Test SystemMicrocompactBoundaryTranscriptItem model"""

    def test_required_fields(self) -> None:
        """Test creating SystemMicrocompactBoundaryTranscriptItem"""
        item = SystemMicrocompactBoundaryTranscriptItem.model_validate(
            SAMPLE_SYSTEM_MICROCOMPACT_BOUNDARY
        )

        assert item.type == "system"
        assert item.subtype == "microcompact_boundary"
        assert item.content == "Context microcompacted"
        assert item.isMeta is False

    def test_microcompact_metadata(self) -> None:
        """Test microcompactMetadata field"""
        item = SystemMicrocompactBoundaryTranscriptItem.model_validate(
            SAMPLE_SYSTEM_MICROCOMPACT_BOUNDARY
        )

        assert isinstance(item.microcompactMetadata, MicrocompactMetadata)
        assert item.microcompactMetadata.trigger == "auto"
        assert item.microcompactMetadata.preTokens == 58819
        assert item.microcompactMetadata.tokensSaved == 20697
        assert len(item.microcompactMetadata.compactedToolIds) == 3
        assert item.microcompactMetadata.clearedAttachmentUUIDs == []


class TestSystemStopHookSummaryTranscriptItem:
    """Test SystemStopHookSummaryTranscriptItem model"""

    def test_required_fields(self) -> None:
        """Test creating SystemStopHookSummaryTranscriptItem"""
        item = SystemStopHookSummaryTranscriptItem.model_validate(SAMPLE_SYSTEM_STOP_HOOK_SUMMARY)

        assert item.type == "system"
        assert item.subtype == "stop_hook_summary"
        assert item.level == "suggestion"
        assert item.hookCount == 1
        assert item.hasOutput is True
        assert item.preventedContinuation is False

    def test_hook_infos(self) -> None:
        """Test hookInfos field"""
        item = SystemStopHookSummaryTranscriptItem.model_validate(SAMPLE_SYSTEM_STOP_HOOK_SUMMARY)

        assert len(item.hookInfos) == 1
        assert isinstance(item.hookInfos[0], HookInfo)
        assert item.hookInfos[0].command == (
            'PYTHONPATH="$CLAUDE_PROJECT_DIR" '
            '"$CLAUDE_PROJECT_DIR"/.venv/bin/python -m vibehist.app --debug'
        )
        assert item.hookInfos[0].durationMs is None

    def test_hook_errors(self) -> None:
        """Test hookErrors field"""
        item = SystemStopHookSummaryTranscriptItem.model_validate(SAMPLE_SYSTEM_STOP_HOOK_SUMMARY)

        assert item.hookErrors == []
        assert item.stopReason == ""
        assert item.toolUseID == "467a2f8b-3b8b-4300-b3c3-3cf417796d0a"


class TestSystemLocalCommandTranscriptItem:
    """Test SystemLocalCommandTranscriptItem model"""

    def test_required_fields(self) -> None:
        """Test creating with data"""
        item = SystemLocalCommandTranscriptItem.model_validate(SAMPLE_SYSTEM_LOCAL_COMMAND)

        assert item.type == "system"
        assert item.subtype == "local_command"
        assert item.content == "Running local command: echo 'test'"
        assert item.isMeta is False
        assert item.level == "info"


class TestSystemTranscriptItem:
    """Test SystemTranscriptItem discriminated union routing via RootModel"""

    def test_routes_to_turn_duration(self) -> None:
        """Test RootModel routes to SystemTurnDurationTranscriptItem"""
        item = SystemTranscriptItem.model_validate(SAMPLE_SYSTEM_TURN_DURATION)
        result = item.root

        assert isinstance(result, SystemTurnDurationTranscriptItem)
        assert result.subtype == "turn_duration"
        assert hasattr(result, "durationMs")

    def test_routes_to_api_error(self) -> None:
        """Test RootModel routes to SystemApiErrorTranscriptItem"""
        item = SystemTranscriptItem.model_validate(SAMPLE_SYSTEM_API_ERROR)
        result = item.root

        assert isinstance(result, SystemApiErrorTranscriptItem)
        assert result.subtype == "api_error"
        assert hasattr(result, "error")
        assert hasattr(result, "retryAttempt")

    def test_routes_to_compact_boundary(self) -> None:
        """Test RootModel routes to SystemCompactBoundaryTranscriptItem"""
        item = SystemTranscriptItem.model_validate(SAMPLE_SYSTEM_COMPACT_BOUNDARY)
        result = item.root

        assert isinstance(result, SystemCompactBoundaryTranscriptItem)
        assert result.subtype == "compact_boundary"
        assert hasattr(result, "compactMetadata")
        assert hasattr(result, "logicalParentUuid")

    def test_routes_to_microcompact_boundary(self) -> None:
        """Test RootModel routes to SystemMicrocompactBoundaryTranscriptItem"""
        item = SystemTranscriptItem.model_validate(SAMPLE_SYSTEM_MICROCOMPACT_BOUNDARY)
        result = item.root

        assert isinstance(result, SystemMicrocompactBoundaryTranscriptItem)
        assert result.subtype == "microcompact_boundary"
        assert hasattr(result, "microcompactMetadata")

    def test_routes_to_stop_hook_summary(self) -> None:
        """Test RootModel routes to SystemStopHookSummaryTranscriptItem"""
        item = SystemTranscriptItem.model_validate(SAMPLE_SYSTEM_STOP_HOOK_SUMMARY)
        result = item.root

        assert isinstance(result, SystemStopHookSummaryTranscriptItem)
        assert result.subtype == "stop_hook_summary"
        assert hasattr(result, "hookInfos")
        assert hasattr(result, "toolUseID")

    def test_routes_to_local_command(self) -> None:
        """Test RootModel routes to SystemLocalCommandTranscriptItem"""
        item = SystemTranscriptItem.model_validate(SAMPLE_SYSTEM_LOCAL_COMMAND)
        result = item.root

        assert isinstance(result, SystemLocalCommandTranscriptItem)
        assert result.subtype == "local_command"
        assert hasattr(result, "content")

    def test_all_inherit_from_base(self) -> None:
        """Test all items are instances of BaseSystemTranscriptItem"""
        items = [
            SystemTranscriptItem.model_validate(SAMPLE_SYSTEM_TURN_DURATION).root,
            SystemTranscriptItem.model_validate(SAMPLE_SYSTEM_API_ERROR).root,
            SystemTranscriptItem.model_validate(SAMPLE_SYSTEM_COMPACT_BOUNDARY).root,
        ]

        for item in items:
            assert isinstance(item, BaseSystemTranscriptItem)

    @pytest.mark.skip(reason="TODO: implement when the enumerable values of `subtype` are defined")
    def test_invalid_subtype_rejected(self) -> None:
        """Test that invalid subtype is rejected"""
        invalid_data = {
            **SAMPLE_SYSTEM_TURN_DURATION,
            "subtype": "invalid_subtype",
        }
        with pytest.raises(Exception):
            SystemTranscriptItem.model_validate(invalid_data)

    def test_type_narrowing_with_isinstance(self) -> None:
        """Test type narrowing using isinstance after validation"""
        items = [
            SystemTranscriptItem.model_validate(SAMPLE_SYSTEM_API_ERROR).root,
            SystemTranscriptItem.model_validate(SAMPLE_SYSTEM_TURN_DURATION).root,
        ]

        api_errors = [i for i in items if isinstance(i, SystemApiErrorTranscriptItem)]
        durations = [i for i in items if isinstance(i, SystemTurnDurationTranscriptItem)]

        assert len(api_errors) == 1
        assert len(durations) == 1
        assert hasattr(api_errors[0], "error")
        assert hasattr(durations[0], "durationMs")
