#!/usr/bin/env python3
"""
Unit tests for ToolResult
"""

import pathlib

import pytest

from vibehist.core.tool_result import ToolResult


class TestToolResultInit:
    def test_valid_path_with_session_id_and_tool_use_id(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "12345678-1234-1234-1234-123456789abc"
        tool_use_id = "call_a1b2c3d4"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"

        result = ToolResult(tool_result_path)

        assert result.path == str(tool_result_path)
        assert result.session_id == session_id
        assert result.tool_use_id == tool_use_id

    def test_invalid_file_extension(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "12345678-1234-1234-1234-123456789abc"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / "call_a1b2c3d4.json"

        with pytest.raises(ValueError, match="Invalid tool result file extension"):
            ToolResult(tool_result_path)

    def test_missing_session_id(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        tool_result_dir = tmp_path / "not-a-uuid" / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / "call_a1b2c3d4.txt"

        with pytest.raises(ValueError, match="Invalid tool result file path"):
            ToolResult(tool_result_path)

    def test_missing_tool_use_id(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "12345678-1234-1234-1234-123456789abc"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / "not_call_a1b2c3d4.txt"

        with pytest.raises(ValueError, match="Invalid tool result file path"):
            ToolResult(tool_result_path)


class TestToolResultProperties:
    def test_exists_property_file_exists(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "12345678-1234-1234-1234-123456789abc"
        tool_use_id = "call_a1b2c3d4"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"
        tool_result_path.write_text("test content")

        result = ToolResult(tool_result_path)

        assert result.exists is True

    def test_exists_property_file_not_exists(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "12345678-1234-1234-1234-123456789abc"
        tool_use_id = "call_a1b2c3d4"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"

        result = ToolResult(tool_result_path)

        assert result.exists is False


class TestToolResultExtractIdentifiers:
    def test_extract_valid_identifiers(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "12345678-1234-1234-1234-123456789abc"
        tool_use_id = "call_a1b2c3d4e5f6"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"

        result = ToolResult(tool_result_path)

        assert result.session_id == session_id
        assert result.tool_use_id == tool_use_id

    def test_extract_with_mixed_case_uuid(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "AbCdEf12-34Ab-56Cd-78Ef-90Ab12345678"
        tool_use_id = "call_test123"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"

        result = ToolResult(tool_result_path)

        assert result.session_id == session_id

    def test_extract_tool_use_id_with_underscores_and_numbers(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "12345678-1234-1234-1234-123456789abc"
        tool_use_id = "call_abc123_def456"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"

        with pytest.raises(ValueError, match="Invalid tool result file path"):
            ToolResult(tool_result_path)


class TestToolResultIterLines:
    def test_iter_lines_single_line(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "12345678-1234-1234-1234-123456789abc"
        tool_use_id = "call_a1b2c3d4"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"
        tool_result_path.write_text("single line")

        result = ToolResult(tool_result_path)
        lines = list(result.iter_lines())

        assert lines == ["single line"]

    def test_iter_lines_multiple_lines(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "12345678-1234-1234-1234-123456789abc"
        tool_use_id = "call_a1b2c3d4"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"
        content = "line 1\nline 2\nline 3"
        tool_result_path.write_text(content)

        result = ToolResult(tool_result_path)
        lines = list(result.iter_lines())

        assert lines == ["line 1", "line 2", "line 3"]

    def test_iter_lines_trailing_newline(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        """Test that trailing newlines are stripped"""
        session_id = "12345678-1234-1234-1234-123456789abc"
        tool_use_id = "call_a1b2c3d4"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"
        tool_result_path.write_text("line 1\nline 2\n")

        result = ToolResult(tool_result_path)
        lines = list(result.iter_lines())

        assert lines == ["line 1", "line 2"]

    def test_iter_lines_empty_file(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "12345678-1234-1234-1234-123456789abc"
        tool_use_id = "call_a1b2c3d4"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"
        tool_result_path.write_text("")

        result = ToolResult(tool_result_path)
        lines = list(result.iter_lines())

        assert lines == []

    def test_iter_lines_caches_content(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "12345678-1234-1234-1234-123456789abc"
        tool_use_id = "call_a1b2c3d4"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"
        tool_result_path.write_text("line 1\nline 2")

        result = ToolResult(tool_result_path)

        lines1 = list(result.iter_lines())
        lines2 = list(result.iter_lines())

        assert lines1 == ["line 1", "line 2"]
        assert lines2 == ["line 1", "line 2"]

    def test_iter_lines_file_not_found(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "12345678-1234-1234-1234-123456789abc"
        tool_use_id = "call_a1b2c3d4"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"

        result = ToolResult(tool_result_path)

        with pytest.raises(FileNotFoundError, match="Tool result file doesn't exist"):
            list(result.iter_lines())

    def test_iter_lines_with_utf8_bom(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "12345678-1234-1234-1234-123456789abc"
        tool_use_id = "call_a1b2c3d4"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"

        with open(tool_result_path, "wb") as f:
            f.write(b"\xef\xbb\xbfline 1\nline 2")

        result = ToolResult(tool_result_path)
        lines = list(result.iter_lines())

        assert lines == ["line 1", "line 2"]


class TestToolResultContent:
    def test_content_returns_full_content(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "12345678-1234-1234-1234-123456789abc"
        tool_use_id = "call_a1b2c3d4"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"
        expected_content = "line 1\nline 2\nline 3"
        tool_result_path.write_text(expected_content)

        result = ToolResult(tool_result_path)

        assert result.content == expected_content

    def test_content_empty_file(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "12345678-1234-1234-1234-123456789abc"
        tool_use_id = "call_a1b2c3d4"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"
        tool_result_path.write_text("")

        result = ToolResult(tool_result_path)

        assert result.content == ""

    def test_content_multiline_with_trailing_newline(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "12345678-1234-1234-1234-123456789abc"
        tool_use_id = "call_a1b2c3d4"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"
        tool_result_path.write_text("line 1\nline 2\n")

        result = ToolResult(tool_result_path)

        assert result.content == "line 1\nline 2"

    def test_content_after_iter_lines(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "12345678-1234-1234-1234-123456789abc"
        tool_use_id = "call_a1b2c3d4"
        tool_result_dir = tmp_path / session_id / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"
        expected_content = "line 1\nline 2"
        tool_result_path.write_text(expected_content)

        result = ToolResult(tool_result_path)

        list(result.iter_lines())

        assert result.content == expected_content
