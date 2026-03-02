#!/usr/bin/env/python3
"""
Unit tests for ToolUseResult model
"""

from typing import Any, cast

import pytest

from vibehist.core.models.tool_use_result import (
    FileItem,
    QuestionItem,
    StatusChange,
    StructuredPatch,
    TaskSubagent,
    TaskTodoWrite,
    ToolUseResult,
)

TOOL_RESULT_MINIMAL: dict[str, Any] = {
    "mode": "content",
}

TOOL_RESULT_FILE_READ: dict[str, Any] = {
    "type": "text",
    "file": {
        "filePath": "/Users/root/workspace/project/test.py",
        "content": "# Test file\nprint('hello')\n",
        "numLines": 2,
        "startLine": 1,
        "totalLines": 2,
    },
}

TOOL_RESULT_GLOB: dict[str, Any] = {
    "mode": "files_with_matches",
    "filenames": [
        "/Users/root/workspace/project/test.py",
        "/Users/root/workspace/project/main.py",
    ],
    "numFiles": 2,
}

TOOL_RESULT_SHELL: dict[str, Any] = {
    "stdout": "Running tests...\nTests passed: 10\n",
    "stderr": "",
    "interrupted": False,
    "isImage": False,
    "noOutputExpected": False,
}

TOOL_RESULT_SHELL_WITH_INTERPRETATION: dict[str, Any] = {
    "stdout": "",
    "stderr": "",
    "interrupted": False,
    "isImage": False,
    "returnCodeInterpretation": "No matches found",
    "noOutputExpected": False,
}

TOOL_RESULT_GREP: dict[str, Any] = {
    "mode": "content",
    "numFiles": 0,
    "filenames": [],
    "content": "file.py:10:def test_function():\nfile.py:11:    assert True\n",
    "numLines": 2,
    "appliedLimit": 50,
}

TOOL_RESULT_EDIT: dict[str, Any] = {
    "type": "update",
    "mode": "content",
    "filePath": "/Users/root/workspace/project/test.py",
    "oldString": "def old_function():\n    pass\n",
    "newString": "def new_function():\n    return True\n",
    "replaceAll": False,
    "originalFile": "# Original content\n",
    "structuredPatch": [
        {
            "oldStart": 10,
            "oldLines": 2,
            "newStart": 10,
            "newLines": 2,
            "lines": [
                " def old_function():",
                "-    pass",
                "+def new_function():",
                "+    return True",
            ],
        }
    ],
    "userModified": False,
}

TOOL_RESULT_CREATE: dict[str, Any] = {
    "type": "create",
    "filePath": "/Users/root/workspace/project/new_file.py",
    "content": "# New file\nprint('hello')\n",
    "structuredPatch": [],
    "originalFile": None,
}

TOOL_RESULT_MESSAGE: dict[str, Any] = {
    "message": (
        "Entered plan mode. "
        "You should now focus on exploring the codebase "
        "and designing an implementation approach."
    ),
}

TOOL_RESULT_TASK_TODO: dict[str, Any] = {
    "task": {
        "id": "1",
        "subject": "Create test file",
    },
}

TOOL_RESULT_TASK_SUBAGENT: dict[str, Any] = {
    "task": {
        "task_id": "b52e837",
        "task_type": "local_bash",
        "status": "running",
        "description": "Run tests",
        "output": "Running...",
        "exitCode": None,
    },
}

TOOL_RESULT_STATUS_CHANGE: dict[str, Any] = {
    "success": True,
    "taskId": "1",
    "updatedFields": ["status"],
    "statusChange": {
        "from": "pending",
        "to": "completed",
    },
}

TOOL_RESULT_WEB_SEARCH: dict[str, Any] = {
    "query": "pydantic v1 validator mixin inheritance",
    "results": [
        "Web search error: undefined",
        "Based on web search, found relevant resources about Pydantic v1...",
    ],
    "durationSeconds": 19.7,
}

TOOL_RESULT_QUESTIONS: dict[str, Any] = {
    "questions": [
        {
            "question": "What is your preference?",
            "header": "Configuration",
            "options": [
                {"label": "Option A", "description": "Description A"},
                {"label": "Option B", "description": "Description B"},
            ],
            "multiSelect": False,
        }
    ],
    "answers": {
        "What is your preference?": "Option A",
    },
    "annotations": {
        "What is your preference?": {
            "notes": "User selected Option A",
        },
    },
}


class TestToolUseResult:
    """Test ToolUseResult model validation"""

    def test_minimal_result(self) -> None:
        """Test creating minimal tool use result"""
        result = ToolUseResult.model_validate(TOOL_RESULT_MINIMAL)

        assert result.mode == "content"
        assert result.content is None
        assert result.message is None

    def test_file_read_result(self) -> None:
        """Test file read result structure"""
        result = ToolUseResult.model_validate(TOOL_RESULT_FILE_READ)

        assert result.type == "text"
        assert result.file is not None
        assert result.file.filePath == "/Users/root/workspace/project/test.py"
        assert result.file.content == "# Test file\nprint('hello')\n"
        assert result.file.numLines == 2
        assert result.file.startLine == 1
        assert result.file.totalLines == 2

    def test_glob_result(self) -> None:
        """Test glob tool result"""
        result = ToolUseResult.model_validate(TOOL_RESULT_GLOB)

        assert result.mode == "files_with_matches"
        assert result.filenames == [
            "/Users/root/workspace/project/test.py",
            "/Users/root/workspace/project/main.py",
        ]
        assert result.numFiles == 2

    def test_shell_command_result(self) -> None:
        """Test shell command result with stdout/stderr"""
        result = ToolUseResult.model_validate(TOOL_RESULT_SHELL)

        assert result.stdout == "Running tests...\nTests passed: 10\n"
        assert result.stderr == ""
        assert result.interrupted is False
        assert result.isImage is False
        assert result.noOutputExpected is False

    def test_shell_result_with_interpretation(self) -> None:
        """Test shell result with return code interpretation"""
        result = ToolUseResult.model_validate(TOOL_RESULT_SHELL_WITH_INTERPRETATION)

        assert result.stdout == ""
        assert result.stderr == ""
        assert result.returnCodeInterpretation == "No matches found"
        assert result.interrupted is False

    def test_grep_content_mode(self) -> None:
        """Test grep/glob content mode with appliedLimit"""
        result = ToolUseResult.model_validate(TOOL_RESULT_GREP)

        assert result.mode == "content"
        assert result.content is not None
        assert result.numFiles == 0
        assert result.filenames == []
        assert result.numLines == 2
        assert result.appliedLimit == 50

    def test_edit_result(self) -> None:
        """Test edit operation result"""
        result = ToolUseResult.model_validate(TOOL_RESULT_EDIT)

        assert result.type == "update"
        assert result.mode == "content"
        assert result.filePath == "/Users/root/workspace/project/test.py"
        assert result.oldString is not None
        assert "def old_function" in result.oldString
        assert result.newString is not None
        assert "def new_function" in result.newString
        assert result.replaceAll is False
        assert result.userModified is False
        assert result.structuredPatch is not None
        assert len(result.structuredPatch) == 1

    def test_create_file_result(self) -> None:
        """Test create file result"""
        result = ToolUseResult.model_validate(TOOL_RESULT_CREATE)

        assert result.type == "create"
        assert result.filePath == "/Users/root/workspace/project/new_file.py"
        assert result.content is not None
        assert result.originalFile is None
        assert result.structuredPatch == []

    def test_message_only_result(self) -> None:
        """Test message only result"""
        result = ToolUseResult.model_validate(TOOL_RESULT_MESSAGE)

        assert result.message == (
            "Entered plan mode. "
            "You should now focus on exploring the codebase "
            "and designing an implementation approach."
        )

    def test_task_union_todo_write(self) -> None:
        """Test task field with TodoWrite type"""
        result = ToolUseResult.model_validate(TOOL_RESULT_TASK_TODO)

        assert result.task is not None
        assert isinstance(result.task, TaskTodoWrite)
        assert result.task.id == "1"
        assert result.task.subject == "Create test file"

    def test_task_union_subagent(self) -> None:
        """Test task field with Subagent type"""
        result = ToolUseResult.model_validate(TOOL_RESULT_TASK_SUBAGENT)

        assert result.task is not None
        assert isinstance(result.task, TaskSubagent)
        assert result.task.task_id == "b52e837"
        assert result.task.status == "running"
        assert result.task.exitCode is None

    def test_status_change_result(self) -> None:
        """Test status change result"""
        result = ToolUseResult.model_validate(TOOL_RESULT_STATUS_CHANGE)

        assert result.success is True
        assert result.taskId == "1"
        assert result.updatedFields == ["status"]
        assert result.statusChange is not None
        assert result.statusChange.from_ == "pending"
        assert result.statusChange.to == "completed"

    def test_web_search_result(self) -> None:
        """Test web search result"""
        result = ToolUseResult.model_validate(TOOL_RESULT_WEB_SEARCH)

        assert result.query == "pydantic v1 validator mixin inheritance"
        assert result.results is not None
        assert len(result.results) == 2
        assert isinstance(result.results[0], str)
        assert result.durationSeconds == 19.7

    def test_questions_and_answers(self) -> None:
        """Test questions and answers result"""
        result = ToolUseResult.model_validate(TOOL_RESULT_QUESTIONS)

        assert result.questions is not None
        assert len(result.questions) == 1
        assert result.questions[0].question == "What is your preference?"
        assert result.questions[0].multiSelect is False
        assert result.answers is not None
        assert result.answers["What is your preference?"] == "Option A"
        assert result.annotations is not None
        assert result.annotations["What is your preference?"].notes == "User selected Option A"

    @pytest.mark.skip(reason="TODO: implement when the enumerable values of `mode` are defined")
    def test_invalid_mode_rejected(self) -> None:
        """Test that invalid mode is rejected"""
        with pytest.raises(ValueError):
            ToolUseResult.model_validate({"mode": cast(Any, "invalid_mode")})

    @pytest.mark.skip(reason="TODO: implement when the enumerable values of `type` are defined")
    def test_invalid_type_rejected(self) -> None:
        """Test that invalid type is rejected"""
        with pytest.raises(ValueError):
            ToolUseResult.model_validate(
                {
                    "type": cast(Any, "invalid_type"),
                    "mode": "content",
                }
            )

    @pytest.mark.skip(reason="TODO: implement when the enumerable values of `status` are defined")
    def test_invalid_status_rejected(self) -> None:
        """Test that invalid status is rejected"""
        with pytest.raises(ValueError):
            ToolUseResult.model_validate(
                {
                    "status": cast(Any, "invalid_status"),
                }
            )


class TestStructuredPatch:
    """Test StructuredPatch model validation"""

    def test_structured_patch(self) -> None:
        """Test structured patch result"""
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


class TestStatusChange:
    """Test StatusChange model validation"""

    def test_status_change(self) -> None:
        """Test status change structure"""
        change = StatusChange.model_validate({"from": "pending", "to": "completed"})

        assert change.from_ == "pending"  # Note: from is a reserved word, uses alias
        assert change.to == "completed"


class TestQuestionItem:
    """Test QuestionItem model validation"""

    def test_question_item(self) -> None:
        """Test question item structure"""
        question = QuestionItem.model_validate(
            {
                "question": "What is your preference?",
                "header": "Configuration",
                "options": [
                    {"label": "Option A", "description": "Description A"},
                    {"label": "Option B", "description": "Description B"},
                ],
                "multiSelect": False,
            }
        )

        assert question.question == "What is your preference?"
        assert question.header == "Configuration"
        assert len(question.options) == 2
        assert question.options[0].label == "Option A"
        assert question.options[0].description == "Description A"
        assert question.multiSelect is False


class TestTaskTodoWrite:
    """Test TaskTodoWrite model validation"""

    def test_task_todo_write(self) -> None:
        """Test TodoWrite task result"""
        task = TaskTodoWrite.model_validate(
            {
                "id": "1",
                "subject": "Create test file",
            }
        )

        assert task.id == "1"
        assert task.subject == "Create test file"


class TestTaskSubagent:
    """Test TaskSubagent model validation"""

    def test_task_subagent(self) -> None:
        """Test subagent task result"""
        task = TaskSubagent.model_validate(
            {
                "task_id": "b52e837",
                "task_type": "local_bash",
                "status": "running",
                "description": "Run tests",
                "output": "Running...",
                "exitCode": None,
            }
        )

        assert task.task_id == "b52e837"
        assert task.task_type == "local_bash"
        assert task.status == "running"
        assert task.description == "Run tests"
        assert task.output == "Running..."
        assert task.exitCode is None


class TestFileItem:
    """Test FileItem model validation"""

    def test_file_item_full(self) -> None:
        """Test file item with all fields"""
        file_item = FileItem.model_validate(
            {
                "filePath": "/test/file.py",
                "content": "file content",
                "numLines": 100,
                "startLine": 1,
                "totalLines": 100,
            }
        )

        assert file_item.filePath == "/test/file.py"
        assert file_item.content == "file content"
        assert file_item.numLines == 100
        assert file_item.startLine == 1
        assert file_item.totalLines == 100

    def test_file_item_partial(self) -> None:
        """Test file item with partial fields"""
        file_item = FileItem.model_validate(
            {
                "filePath": "/test/file.py",
            }
        )

        assert file_item.filePath == "/test/file.py"
        assert file_item.content is None
        assert file_item.numLines is None
