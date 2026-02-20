#!/usr/bin/env python3
"""
Unit tests for Session
"""

import json
import os
import pathlib
import uuid

import pytest

from vibehist.core.project_storage_path import ProjectStoragePath
from vibehist.core.session import Session


@pytest.fixture
def project_storage_path(tmp_path: pathlib.Path) -> ProjectStoragePath:
    """Create a valid project storage path for testing."""
    return ProjectStoragePath.encode(tmp_path / "workspace" / "project")


@pytest.fixture
def session_id() -> uuid.UUID:
    """Provide a fixed session ID for testing."""
    return uuid.UUID("12345678-1234-1234-1234-123456789abc")


@pytest.fixture
def created_storage_path(
    project_storage_path: ProjectStoragePath,
) -> ProjectStoragePath:
    """Create a project storage path that exists on filesystem."""
    os.makedirs(str(project_storage_path), exist_ok=True)
    return project_storage_path


class TestSessionInit:
    def test_init_with_uuid_session_id(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(created_storage_path, session_id)

        assert session.session_id == str(session_id)
        assert isinstance(session._session_id, uuid.UUID)

    def test_init_with_string_session_id(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_id_str = str(session_id)
        session_file = os.path.join(str(created_storage_path), f"{session_id_str}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(created_storage_path, session_id_str)

        assert session.session_id == session_id_str
        assert isinstance(session._session_id, uuid.UUID)

    def test_init_storage_path_not_exists(
        self,
        project_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        with pytest.raises(FileNotFoundError, match="Project storage path doesn't exist"):
            Session(project_storage_path, session_id)

    def test_init_session_not_exists(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session = Session(created_storage_path, session_id)
        assert not session.exists

    def test_init_with_session_directory(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_dir = os.path.join(str(created_storage_path), str(session_id))
        os.makedirs(session_dir, exist_ok=True)

        session = Session(created_storage_path, session_id)

        assert session.session_id == str(session_id)
        assert session.exists

    def test_init_creates_empty_state(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test that initialization creates empty internal state."""
        session = Session(created_storage_path, session_id)

        assert session._transcript_files == set()
        assert session._is_tf_loaded is False
        assert session._tool_result_file_mapping == {}
        assert session._is_trf_loaded is False

    def test_init_with_invalid_string_session_id(
        self,
        created_storage_path: ProjectStoragePath,
    ) -> None:
        """Test that invalid session ID strings raise an error."""
        with pytest.raises(ValueError):
            Session(created_storage_path, "not-a-uuid")


class TestSessionPath:
    def test_session_path_default_is_file(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(created_storage_path, session_id)

        expected_path = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        assert session.session_path() == expected_path

    def test_session_path_is_file_true(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(created_storage_path, session_id)

        expected_path = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        assert session.session_path(is_file=True) == expected_path

    def test_session_path_is_file_false(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        expected_path = os.path.join(str(created_storage_path), str(session_id))
        os.mkdir(expected_path)

        session = Session(created_storage_path, session_id)

        assert session.session_path(is_file=False) == expected_path


class TestSessionExists:
    def test_exists_property_true_with_file(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(created_storage_path, session_id)

        assert session.exists is True

    def test_exists_property_true_with_directory(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_dir = os.path.join(str(created_storage_path), str(session_id))
        os.makedirs(session_dir, exist_ok=True)

        session = Session(created_storage_path, session_id)

        assert session.exists is True

    def test_exists_property_false(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session = Session(created_storage_path, session_id)

        assert session.exists is False


class TestIterTranscripts:
    def test_iter_transcripts_single_file(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        lines = [
            {"type": "user", "content": "hello"},
            {"type": "assistant", "content": "hi"},
            {"type": "user", "content": "bye"},
        ]
        pathlib.Path(session_file).write_text("\n".join(json.dumps(line) for line in lines))

        session = Session(created_storage_path, session_id)
        transcripts = list(session.iter_transcripts())

        assert len(transcripts) == 3
        assert transcripts[0]["type"] == "user"
        assert transcripts[1]["type"] == "assistant"
        assert transcripts[2]["content"] == "bye"

    def test_iter_transcripts_multiple_files(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        main_lines = [{"type": "main", "id": 1}, {"type": "main", "id": 2}]
        pathlib.Path(session_file).write_text("\n".join(json.dumps(line) for line in main_lines))

        session_dir = os.path.join(str(created_storage_path), str(session_id))
        subagents_dir = os.path.join(session_dir, "subagents")
        os.makedirs(subagents_dir, exist_ok=True)

        agent_file = os.path.join(subagents_dir, "agent-task-123.jsonl")
        agent_lines = [{"type": "agent", "id": 3}, {"type": "agent", "id": 4}]
        pathlib.Path(agent_file).write_text("\n".join(json.dumps(line) for line in agent_lines))

        session = Session(created_storage_path, session_id)
        transcripts = {item["id"]: item for item in session.iter_transcripts()}

        assert len(transcripts) == 4
        assert transcripts[1]["type"] == "main"
        assert transcripts[2]["type"] == "main"
        assert transcripts[3]["type"] == "agent"
        assert transcripts[4]["type"] == "agent"

    def test_iter_transcripts_empty_session(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text("")

        session = Session(created_storage_path, session_id)
        transcripts = list(session.iter_transcripts())

        assert transcripts == []

    def test_iter_transcripts_session_not_exists(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test that iterating transcripts for non-existent session raises error."""
        session = Session(created_storage_path, session_id)

        with pytest.raises(FileNotFoundError, match="doesn't exist in project storage"):
            list(session.iter_transcripts())

    def test_iter_transcripts_uses_cache(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test that multiple iterations use cached transcript files."""
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        lines = [{"type": "test", "id": 1}]
        pathlib.Path(session_file).write_text(json.dumps(lines[0]))

        # Create directory to trigger _is_tf_loaded flag being set
        session_dir = os.path.join(str(created_storage_path), str(session_id))
        os.makedirs(session_dir, exist_ok=True)

        session = Session(created_storage_path, session_id)

        # First iteration - loads transcript files
        first_transcripts = list(session.iter_transcripts())
        assert session._is_tf_loaded is True

        # Second iteration - uses cached files
        second_transcripts = list(session.iter_transcripts())
        assert first_transcripts == second_transcripts

    def test_iter_transcripts_sets_loaded_flag(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test that iteration sets the _is_tf_loaded flag when directory exists."""
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        # Create directory to trigger _is_tf_loaded flag being set
        session_dir = os.path.join(str(created_storage_path), str(session_id))
        os.makedirs(session_dir, exist_ok=True)

        session = Session(created_storage_path, session_id)
        assert session._is_tf_loaded is False

        _ = list(session.iter_transcripts())
        assert session._is_tf_loaded is True


class TestSessionLazyLoading:
    """Tests for lazy loading behavior."""

    def test_iter_transcripts_only_loads_once(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that transcript files are only loaded once."""
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        # Create directory to ensure _is_tf_loaded flag gets set
        session_dir = os.path.join(str(created_storage_path), str(session_id))
        os.makedirs(session_dir, exist_ok=True)

        session = Session(created_storage_path, session_id)
        load_count = 0

        original_load = session._load_transcript_files

        def counting_load() -> None:
            nonlocal load_count
            load_count += 1
            original_load()

        monkeypatch.setattr(session, "_load_transcript_files", counting_load)

        _ = list(session.iter_transcripts())
        _ = list(session.iter_transcripts())
        _ = list(session.iter_transcripts())

        assert load_count == 1

    def test_get_tool_result_loads_tool_result_files(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test that getting tool result loads tool result files."""
        session_dir = os.path.join(str(created_storage_path), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file = os.path.join(tool_results_dir, "call_test.txt")
        pathlib.Path(tool_result_file).write_text("result")

        session = Session(created_storage_path, session_id)
        assert session._is_trf_loaded is False

        _ = session.get_tool_result_file_content("call_test")
        assert session._is_trf_loaded is True

    def test_get_tool_result_only_loads_once(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that tool result files are only loaded once."""
        session_dir = os.path.join(str(created_storage_path), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file = os.path.join(tool_results_dir, "call_test.txt")
        pathlib.Path(tool_result_file).write_text("result")

        session = Session(created_storage_path, session_id)
        load_count = 0

        original_load = session._load_tool_result_files

        def counting_load() -> None:
            nonlocal load_count
            load_count += 1
            original_load()

        monkeypatch.setattr(session, "_load_tool_result_files", counting_load)

        _ = session.get_tool_result_file_content("call_test")
        _ = session.get_tool_result_file_content("call_test")
        _ = session.get_tool_result_file_content("call_test")

        assert load_count == 1


class TestSessionEquality:
    def test_eq_equal_sessions(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session1 = Session(created_storage_path, session_id)
        session2 = Session(created_storage_path, session_id)

        assert session1 == session2

    def test_eq_different_sessions(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_id2 = uuid.uuid4()
        session_file1 = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        session_file2 = os.path.join(str(created_storage_path), f"{session_id2}.jsonl")
        pathlib.Path(session_file1).write_text('{"type": "test1"}')
        pathlib.Path(session_file2).write_text('{"type": "test2"}')

        session1 = Session(created_storage_path, session_id)
        session2 = Session(created_storage_path, session_id2)

        assert session1 != session2

    def test_eq_non_session_object(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(created_storage_path, session_id)

        assert session != "not a session"
        assert session != 123

    def test_eq_reflexive(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(created_storage_path, session_id)
        assert session == session

    def test_eq_symmetric(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session1 = Session(created_storage_path, session_id)
        session2 = Session(created_storage_path, session_id)

        assert session1 == session2
        assert session2 == session1

    def test_eq_transitive(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session1 = Session(created_storage_path, session_id)
        session2 = Session(created_storage_path, session_id)
        session3 = Session(created_storage_path, session_id)

        assert session1 == session2
        assert session2 == session3
        assert session1 == session3


class TestSessionHash:
    def test_hash_equal_sessions_have_same_hash(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session1 = Session(created_storage_path, session_id)
        session2 = Session(created_storage_path, session_id)

        assert hash(session1) == hash(session2)

    def test_hash_different_sessions_have_different_hashes(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_id2 = uuid.uuid4()
        session_file1 = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        session_file2 = os.path.join(str(created_storage_path), f"{session_id2}.jsonl")
        pathlib.Path(session_file1).write_text('{"type": "test1"}')
        pathlib.Path(session_file2).write_text('{"type": "test2"}')

        session1 = Session(created_storage_path, session_id)
        session2 = Session(created_storage_path, session_id2)

        assert hash(session1) != hash(session2)

    def test_hash_session_can_be_used_in_set(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session1 = Session(created_storage_path, session_id)
        session2 = Session(created_storage_path, session_id)

        session_set = {session1, session2}

        assert len(session_set) == 1

    def test_hash_session_can_be_used_as_dict_key(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session1 = Session(created_storage_path, session_id)
        session2 = Session(created_storage_path, session_id)

        session_dict = {session1: "first", session2: "second"}

        assert len(session_dict) == 1
        assert session_dict[session1] == "second"

    def test_hash_stability(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test that hash is stable across multiple calls."""
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(created_storage_path, session_id)

        hash1 = hash(session)
        hash2 = hash(session)
        hash3 = hash(session)

        assert hash1 == hash2 == hash3


class TestGetToolResultFileContent:
    def test_get_tool_result_content_existing(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_dir = os.path.join(str(created_storage_path), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file = os.path.join(tool_results_dir, "call_abc123.txt")
        expected_content = "This is the tool result content\nwith multiple lines"
        pathlib.Path(tool_result_file).write_text(expected_content)

        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(created_storage_path, session_id)
        content = session.get_tool_result_file_content("call_abc123")

        assert content == expected_content

    def test_get_tool_result_content_nonexistent(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(created_storage_path, session_id)
        content = session.get_tool_result_file_content("call_nonexistent")

        assert content is None

    def test_get_tool_result_content_multiple_files(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_dir = os.path.join(str(created_storage_path), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file1 = os.path.join(tool_results_dir, "call_abc123.txt")
        pathlib.Path(tool_result_file1).write_text("result 1")

        tool_result_file2 = os.path.join(tool_results_dir, "call_def456.txt")
        pathlib.Path(tool_result_file2).write_text("result 2")

        tool_result_file3 = os.path.join(tool_results_dir, "call_xyz789.txt")
        pathlib.Path(tool_result_file3).write_text("result 3")

        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(created_storage_path, session_id)

        assert session.get_tool_result_file_content("call_abc123") == "result 1"
        assert session.get_tool_result_file_content("call_def456") == "result 2"
        assert session.get_tool_result_file_content("call_xyz789") == "result 3"
        assert session.get_tool_result_file_content("call_nonexistent") is None

    def test_get_tool_result_content_uses_cache(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_dir = os.path.join(str(created_storage_path), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file = os.path.join(tool_results_dir, "call_abc123.txt")
        pathlib.Path(tool_result_file).write_text("result content")

        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(created_storage_path, session_id)

        # First call - builds cache
        content1 = session.get_tool_result_file_content("call_abc123")
        assert content1 == "result content"

        # Second call - uses cache
        content2 = session.get_tool_result_file_content("call_abc123")
        assert content2 == "result content"

    def test_get_tool_result_content_empty_file(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_dir = os.path.join(str(created_storage_path), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file = os.path.join(tool_results_dir, "call_empty.txt")
        pathlib.Path(tool_result_file).write_text("")

        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(created_storage_path, session_id)
        content = session.get_tool_result_file_content("call_empty")

        assert content == ""

    def test_get_tool_result_content_no_tool_results_directory(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test that missing tool-results directory returns None and sets loaded flag."""
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        # Create session directory to ensure _is_trf_loaded flag gets set
        session_dir = os.path.join(str(created_storage_path), str(session_id))
        os.makedirs(session_dir, exist_ok=True)

        session = Session(created_storage_path, session_id)
        content = session.get_tool_result_file_content("call_test")

        assert content is None
        # Flag should be set since directory exists (even if tool-results doesn't)
        assert session._is_trf_loaded is True
