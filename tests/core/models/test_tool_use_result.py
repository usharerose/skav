#!/usr/bin/env/python3
"""
Unit tests for ToolUseResult model
"""

from typing import Any, cast

import pytest

from vibehist.core.models.tool_use_result import (
    QuestionItem,
    StatusChange,
    StructuredPatch,
    TaskSubagent,
    TaskTodoWrite,
    ToolUseResult,
)
from vibehist.core.models.usage import CacheCreation, ServerToolUse, Usage

SAMPLE_USAGE_WITH_CACHE: dict[str, Any] = {
    "input_tokens": 12361,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 8448,
    "output_tokens": 133,
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

SAMPLE_USAGE_MINIMAL: dict[str, Any] = {
    "input_tokens": 0,
    "output_tokens": 0,
}

SAMPLE_TOOL_RESULT_FILE_READ: dict[str, Any] = {
    "tool_use_id": "call_98a174fc29634f1aa752b66f",
    "content": (
        "     1→#!/usr/bin/env python3\n"
        '     2→"""\n'
        "     3→Type definitions for Claude Code Hook events\n"
        "     4→Based on official documentation: https://code.claude.com/docs/en/hooks\n"
        '     5→"""\n'
    ),
}

SAMPLE_TOOL_RESULT_ERROR: dict[str, Any] = {
    "tool_use_id": "call_d9860daaecc9416e94d7c2f3",
    "content": (
        "File does not exist. "
        "Note: your current working directory is /Users/root/workspace/project. "
        "Did you mean models?"
    ),
}

SAMPLE_TOOL_RESULT_GLOB: dict[str, Any] = {
    "tool_use_id": "call_ea6db1d11e5248be8875da9d",
    "content": (
        "/Users/root/workspace/project/vibehist/__init__.py\n"
        "/Users/root/workspace/project/vibehist/app.py\n"
        "/Users/root/workspace/project/vibehist/types.py"
    ),
}

# Synthetic samples for fields not found in real data
SYNTHETIC_TODO_WRITE: dict[str, Any] = {
    "id": "1",
    "subject": "Create test file",
}

SYNTHETIC_SUBAGENT: dict[str, Any] = {
    "task_id": "b52e837",
    "task_type": "local_bash",
    "status": "running",
    "description": "Run tests",
    "output": "Running...",
    "exitCode": None,
}

SYNTHETIC_QUESTION: dict[str, Any] = {
    "question": "What is your favorite color?",
    "header": "Preference",
    "options": [
        {"label": "Red", "value": "red"},
        {"label": "Blue", "value": "blue"},
    ],
    "multiSelect": False,
}


class TestToolUseResult:
    """Test ToolUseResult model validation"""

    def test_minimal_result_with_model_validate(self) -> None:
        """Test minimal tool use result using model_validate"""
        result = ToolUseResult.model_validate({"mode": "content"})

        assert result.mode == "content"
        assert result.content is None
        assert result.message is None

    def test_file_read_result_with_model_validate(self) -> None:
        """Test file read result structure using model_validate"""
        result_data = {
            "type": "text",
            "file": {
                "filePath": "/test/file.py",
                "content": "file content",
                "numLines": 100,
                "startLine": 1,
                "totalLines": 100,
            },
        }
        result = ToolUseResult.model_validate(result_data)

        assert result.type == "text"
        assert result.file is not None
        assert result.file.filePath == "/test/file.py"
        assert result.file.content == "file content"
        assert result.file.numLines == 100

    def test_glob_result_with_model_validate(self) -> None:
        """Test glob tool result using model_validate"""
        result_data = {
            "mode": "files_with_matches",
            "filenames": ["file1.py", "file2.py"],
            "numFiles": 2,
        }
        result = ToolUseResult.model_validate(result_data)

        assert result.mode == "files_with_matches"
        assert result.filenames == ["file1.py", "file2.py"]
        assert result.numFiles == 2

    def test_usage_with_cache_info_real_data(self) -> None:
        """Test usage with cache statistics using real data"""
        usage = Usage.model_validate(SAMPLE_USAGE_WITH_CACHE)

        assert usage.input_tokens == 12361
        assert usage.output_tokens == 133
        assert usage.cache_read_input_tokens == 8448
        assert usage.service_tier == "standard"
        assert usage.server_tool_use is not None
        assert usage.server_tool_use.web_search_requests == 0
        assert usage.cache_creation is not None
        assert usage.cache_creation.ephemeral_5m_input_tokens == 0

    def test_usage_minimal_real_data(self) -> None:
        """Test minimal usage using real data"""
        usage = Usage.model_validate(SAMPLE_USAGE_MINIMAL)

        assert usage.input_tokens == 0
        assert usage.output_tokens == 0
        assert usage.cache_read_input_tokens is None
        assert usage.service_tier is None

    def test_task_todo_write_with_model_validate(self) -> None:
        """Test TodoWrite task result using model_validate"""
        task = TaskTodoWrite.model_validate(SYNTHETIC_TODO_WRITE)

        assert task.id == "1"
        assert task.subject == "Create test file"

    def test_task_subagent_with_model_validate(self) -> None:
        """Test subagent task result using model_validate"""
        task = TaskSubagent.model_validate(SYNTHETIC_SUBAGENT)

        assert task.task_id == "b52e837"
        assert task.task_type == "local_bash"
        assert task.status == "running"
        assert task.description == "Run tests"
        assert task.output == "Running..."
        assert task.exitCode is None

    def test_result_with_usage_real_data(self) -> None:
        """Test tool result with usage information using real data"""
        result_data = {
            "mode": "content",
            "content": "Result content",
            "usage": SAMPLE_USAGE_MINIMAL,
        }
        result = ToolUseResult.model_validate(result_data)

        assert result.usage is not None
        assert result.usage.input_tokens == 0
        assert result.usage.output_tokens == 0

    def test_question_item_with_model_validate(self) -> None:
        """Test question item structure using model_validate"""
        question = QuestionItem.model_validate(SYNTHETIC_QUESTION)

        assert question.question == "What is your favorite color?"
        assert question.header == "Preference"
        assert len(question.options) == 2
        assert question.options[0].label == "Red"
        assert question.options[0].value == "red"
        assert question.multiSelect is False

    def test_answers_dict_with_model_validate(self) -> None:
        """Test answers dictionary using model_validate"""
        result = ToolUseResult.model_validate(
            {
                "mode": "content",
                "answers": {
                    "color": "red",
                    "size": "large",
                },
            }
        )

        assert result.answers is not None
        assert result.answers["color"] == "red"
        assert result.answers["size"] == "large"

    def test_edit_result_with_model_validate(self) -> None:
        """Test edit operation result using model_validate"""
        result = ToolUseResult.model_validate(
            {
                "type": "update",
                "mode": "content",
                "oldString": "old code",
                "newString": "new code",
                "replaceAll": False,
                "file": {
                    "filePath": "/test.py",
                    "content": "updated content",
                },
                "userModified": False,
            }
        )

        assert result.type == "update"
        assert result.oldString == "old code"
        assert result.newString == "new code"
        assert result.replaceAll is False
        assert result.userModified is False

    def test_structured_patch_with_model_validate(self) -> None:
        """Test structured patch result using model_validate"""
        patch = StructuredPatch.model_validate(
            {
                "lines": ["line1", "line2", "line3"],
                "newLines": 3,
                "newStart": 10,
                "oldLines": 2,
                "oldStart": 10,
            }
        )

        assert patch.lines == ["line1", "line2", "line3"]
        assert patch.newLines == 3
        assert patch.newStart == 10
        assert patch.oldLines == 2
        assert patch.oldStart == 10

    def test_status_change_with_model_validate(self) -> None:
        """Test status change structure using model_validate"""
        change = StatusChange.model_validate({"from": "pending", "to": "completed"})

        assert change.from_ == "pending"  # Note: from is a reserved word, uses alias
        assert change.to == "completed"

    def test_invalid_mode_rejected(self) -> None:
        """Test that invalid mode is rejected"""
        with pytest.raises(ValueError):
            ToolUseResult.model_validate({"mode": cast(Any, "invalid_mode")})

    def test_invalid_type_rejected(self) -> None:
        """Test that invalid type is rejected"""
        with pytest.raises(ValueError):
            ToolUseResult.model_validate(
                {
                    "type": cast(Any, "invalid_type"),
                    "mode": "content",
                }
            )

    def test_invalid_status_rejected(self) -> None:
        """Test that invalid status is rejected"""
        with pytest.raises(ValueError):
            ToolUseResult.model_validate(
                {
                    "status": cast(Any, "invalid_status"),
                }
            )

    def test_task_union_todo_write_with_model_validate(self) -> None:
        """Test task field with TodoWrite type using model_validate"""
        result = ToolUseResult.model_validate({"task": SYNTHETIC_TODO_WRITE})

        assert result.task is not None
        # Should be parsed as TaskTodoWrite
        assert isinstance(result.task, TaskTodoWrite)
        assert result.task.id == "1"

    def test_task_union_subagent_with_model_validate(self) -> None:
        """Test task field with Subagent type using model_validate"""
        result = ToolUseResult.model_validate({"task": SYNTHETIC_SUBAGENT})

        assert result.task is not None
        # Should be parsed as TaskSubagent
        assert isinstance(result.task, TaskSubagent)
        assert result.task.task_id == "b52e837"

    def test_empty_usage_with_model_validate(self) -> None:
        """Test usage with zero tokens using real data"""
        usage = Usage.model_validate(SAMPLE_USAGE_MINIMAL)

        assert usage.input_tokens == 0
        assert usage.output_tokens == 0

    def test_server_tool_use_with_model_validate(self) -> None:
        """Test server_tool_use using model_validate with real data"""
        stu = ServerToolUse.model_validate(SAMPLE_USAGE_WITH_CACHE["server_tool_use"])

        assert stu.web_search_requests == 0
        assert stu.web_fetch_requests == 0

    def test_cache_creation_with_model_validate(self) -> None:
        """Test cache_creation using model_validate with real data"""
        cc = CacheCreation.model_validate(SAMPLE_USAGE_WITH_CACHE["cache_creation"])

        assert cc.ephemeral_1h_input_tokens == 0
        assert cc.ephemeral_5m_input_tokens == 0
