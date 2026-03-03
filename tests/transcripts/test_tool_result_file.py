#!/usr/bin/env python3
"""
Unit tests for ToolResultFile
"""

import os
import pathlib
import uuid

import pytest

from skav.transcripts.project_storage_path import ProjectStoragePath
from skav.transcripts.tool_result_file import ToolResultFile


@pytest.fixture(scope="session")
def tool_use_id() -> str:
    return "call_a1b2c3d4"


@pytest.fixture(scope="function")
def tool_result_path(
    made_project_storage_path_obj: ProjectStoragePath,
    session_id: uuid.UUID,
    tool_use_id: str,
) -> pathlib.Path:
    tool_result_dir = pathlib.Path(
        os.path.join(
            str(made_project_storage_path_obj),
            str(session_id),
            "tool-results",
        )
    )
    tool_result_dir.mkdir(parents=True)
    return tool_result_dir / f"{tool_use_id}.txt"


class TestToolResultFileInit:
    def test_valid_path_with_session_id_and_tool_use_id(
        self,
        tool_result_path: pathlib.Path,
        session_id: uuid.UUID,
        tool_use_id: str,
    ) -> None:
        result = ToolResultFile(tool_result_path)

        assert result.path == str(tool_result_path)
        assert result.session_id == str(session_id)
        assert result.tool_use_id == tool_use_id

    def test_init_with_pathlib_object(
        self,
        tool_result_path: pathlib.Path,
        session_id: uuid.UUID,
        tool_use_id: str,
    ) -> None:
        result = ToolResultFile(tool_result_path)

        assert result.path == str(tool_result_path)
        assert result.session_id == str(session_id)
        assert result.tool_use_id == tool_use_id

    def test_invalid_file_extension(
        self,
        tmp_path: pathlib.Path,
        session_id: uuid.UUID,
    ) -> None:
        tool_result_dir = tmp_path / str(session_id) / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / "call_a1b2c3d4.json"

        with pytest.raises(ValueError, match="Invalid tool result file extension"):
            ToolResultFile(tool_result_path)

    def test_invalid_file_extension_without_dot(
        self,
        tmp_path: pathlib.Path,
        session_id: uuid.UUID,
    ) -> None:
        tool_result_dir = tmp_path / str(session_id) / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / "call_a1b2c3d4"

        with pytest.raises(ValueError, match="Invalid tool result file extension"):
            ToolResultFile(tool_result_path)

    def test_missing_session_id(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        tool_result_dir = tmp_path / "not-a-uuid" / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / "call_a1b2c3d4.txt"

        with pytest.raises(ValueError, match="Invalid tool result file path"):
            ToolResultFile(tool_result_path)

    def test_missing_session_id_partial_uuid(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        tool_result_dir = tmp_path / "12345678" / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / "call_a1b2c3d4.txt"

        with pytest.raises(ValueError, match="Invalid tool result file path"):
            ToolResultFile(tool_result_path)

    def test_missing_tool_use_id(
        self,
        tmp_path: pathlib.Path,
        session_id: uuid.UUID,
    ) -> None:
        tool_result_dir = tmp_path / str(session_id) / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / "not_call_a1b2c3d4.txt"

        with pytest.raises(ValueError, match="Invalid tool result file path"):
            ToolResultFile(tool_result_path)

    def test_missing_tool_results_directory(
        self,
        tmp_path: pathlib.Path,
        session_id: uuid.UUID,
    ) -> None:
        tool_result_dir = tmp_path / str(session_id) / "wrong-dir"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / "call_a1b2c3d4.txt"

        with pytest.raises(ValueError, match="Invalid tool result file path"):
            ToolResultFile(tool_result_path)


class TestToolResultFileProperties:
    def test_exists_property_file_exists(
        self,
        tool_result_path: pathlib.Path,
    ) -> None:
        tool_result_path.write_text("test content")
        result = ToolResultFile(tool_result_path)

        assert result.exists is True

    def test_exists_property_file_not_exists(
        self,
        tool_result_path: pathlib.Path,
    ) -> None:
        result = ToolResultFile(tool_result_path)

        assert result.exists is False

    def test_path_property_returns_normalized_path(
        self,
        tool_result_path: pathlib.Path,
    ) -> None:
        result = ToolResultFile(tool_result_path)

        assert isinstance(result.path, str)
        assert result.path == str(tool_result_path)


class TestToolResultFileExtractIdentifiers:
    def test_extract_valid_identifiers(
        self,
        tmp_path: pathlib.Path,
        session_id: uuid.UUID,
    ) -> None:
        tool_use_id = "call_a1b2c3d4e5f6"
        tool_result_dir = tmp_path / str(session_id) / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"

        result = ToolResultFile(tool_result_path)

        assert result.session_id == str(session_id)
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

        result = ToolResultFile(tool_result_path)

        assert result.session_id == session_id
        assert result.tool_use_id == tool_use_id

    def test_extract_tool_use_id_with_underscores_and_numbers(
        self,
        tmp_path: pathlib.Path,
        session_id: uuid.UUID,
    ) -> None:
        tool_use_id = "call_abc123_def456"
        tool_result_dir = tmp_path / str(session_id) / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / f"{tool_use_id}.txt"

        with pytest.raises(ValueError, match="Invalid tool result file path"):
            ToolResultFile(tool_result_path)

    def test_extract_uppercase_in_tool_use_id_rejected(
        self,
        tmp_path: pathlib.Path,
        session_id: uuid.UUID,
    ) -> None:
        tool_result_dir = tmp_path / str(session_id) / "tool-results"
        tool_result_dir.mkdir(parents=True)
        tool_result_path = tool_result_dir / "call_Abc123.txt"

        with pytest.raises(ValueError, match="Invalid tool result file path"):
            ToolResultFile(tool_result_path)


class TestToolResultFileIterLines:
    def test_iter_lines_single_line(
        self,
        tool_result_path: pathlib.Path,
    ) -> None:
        tool_result_path.write_text("single line")
        result = ToolResultFile(tool_result_path)
        lines = list(line for line in result)

        assert lines == ["single line"]

    def test_iter_lines_multiple_lines(
        self,
        tool_result_path: pathlib.Path,
    ) -> None:
        content = "line 1\nline 2\nline 3"
        tool_result_path.write_text(content)
        result = ToolResultFile(tool_result_path)
        lines = list(line for line in result)

        assert lines == ["line 1\n", "line 2\n", "line 3"]

    def test_iter_lines_trailing_newline(
        self,
        tool_result_path: pathlib.Path,
    ) -> None:
        tool_result_path.write_text("line 1\nline 2\n")
        result = ToolResultFile(tool_result_path)
        lines = list(line for line in result)

        assert lines == ["line 1\n", "line 2\n"]

    def test_iter_lines_empty_file(
        self,
        tool_result_path: pathlib.Path,
    ) -> None:
        tool_result_path.write_text("")
        result = ToolResultFile(tool_result_path)
        lines = list(line for line in result)

        assert lines == []

    def test_iter_lines_file_not_found(
        self,
        tool_result_path: pathlib.Path,
    ) -> None:
        result = ToolResultFile(tool_result_path)

        with pytest.raises(FileNotFoundError, match="Tool result file doesn't exist"):
            list(line for line in result)

    def test_iter_lines_with_utf8_bom(
        self,
        tool_result_path: pathlib.Path,
    ) -> None:
        with open(tool_result_path, "wb") as f:
            f.write(b"\xef\xbb\xbfline 1\nline 2")

        result = ToolResultFile(tool_result_path)
        lines = list(line for line in result)

        assert lines == ["line 1\n", "line 2"]

    def test_iter_lines_multiple_times_caches_content(
        self,
        tool_result_path: pathlib.Path,
    ) -> None:
        tool_result_path.write_text("line 1\nline 2")
        result = ToolResultFile(tool_result_path)

        first_iteration = list(result)
        second_iteration = list(result)

        assert first_iteration == second_iteration
        assert first_iteration == ["line 1\n", "line 2"]


class TestToolResultFileContent:
    def test_content_returns_full_content(
        self,
        tool_result_path: pathlib.Path,
    ) -> None:
        expected_content = "line 1\nline 2\nline 3"
        tool_result_path.write_text(expected_content)
        result = ToolResultFile(tool_result_path)

        assert result.content == expected_content

    def test_content_empty_file(
        self,
        tool_result_path: pathlib.Path,
    ) -> None:
        tool_result_path.write_text("")
        result = ToolResultFile(tool_result_path)

        assert result.content == ""

    def test_content_multiline_with_trailing_newline(
        self,
        tool_result_path: pathlib.Path,
    ) -> None:
        tool_result_path.write_text("line 1\nline 2\n")
        result = ToolResultFile(tool_result_path)

        assert result.content == "line 1\nline 2\n"

    def test_content_after_iteration(
        self,
        tool_result_path: pathlib.Path,
    ) -> None:
        expected_content = "line 1\nline 2"
        tool_result_path.write_text(expected_content)
        result = ToolResultFile(tool_result_path)

        _ = list(result)
        assert result.content == expected_content

    def test_content_file_not_found(
        self,
        tool_result_path: pathlib.Path,
    ) -> None:
        result = ToolResultFile(tool_result_path)

        with pytest.raises(FileNotFoundError, match="Tool result file doesn't exist"):
            _ = result.content


class TestToolResultFileLazyLoading:
    def test_iteration_loads_content_once(
        self,
        tool_result_path: pathlib.Path,
    ) -> None:
        tool_result_path.write_text("line 1\nline 2")
        result = ToolResultFile(tool_result_path)

        first_lines = list(result)
        second_lines = list(result)

        assert first_lines == second_lines

    def test_content_and_iteration_share_cache(
        self,
        tool_result_path: pathlib.Path,
    ) -> None:
        tool_result_path.write_text("test content")
        result = ToolResultFile(tool_result_path)

        _ = list(result)
        content = result.content

        assert content == "test content"

    def test_iteration_before_content_uses_cache(
        self,
        tool_result_path: pathlib.Path,
    ) -> None:
        tool_result_path.write_text("test content")
        result = ToolResultFile(tool_result_path)

        _ = result.content
        lines = list(result)

        assert lines == ["test content"]
