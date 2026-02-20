#!/usr/bin/env python3
"""
Unit tests for ProjectStorage
"""

import json
import os
import pathlib
import uuid

import pytest

from vibehist.core.project_storage import ProjectStorage
from vibehist.core.project_storage_path import ProjectStoragePath


@pytest.fixture
def project_storage_path(tmp_path: pathlib.Path) -> ProjectStoragePath:
    """Create a valid project storage path for testing."""
    return ProjectStoragePath.encode(tmp_path / "workspace" / "project")


@pytest.fixture
def created_storage_path(
    project_storage_path: ProjectStoragePath,
) -> ProjectStoragePath:
    """Create a project storage path that exists on filesystem."""
    os.makedirs(str(project_storage_path), exist_ok=True)
    return project_storage_path


@pytest.fixture
def session_id() -> uuid.UUID:
    """Provide a fixed session ID for testing."""
    return uuid.UUID("12345678-1234-1234-1234-123456789abc")


@pytest.fixture
def session_id2() -> uuid.UUID:
    """Provide a second fixed session ID for testing."""
    return uuid.UUID("87654321-4321-4321-4321-cba987654321")


class TestInit:
    def test_init_with_valid_path(
        self,
        created_storage_path: ProjectStoragePath,
    ) -> None:
        storage = ProjectStorage(created_storage_path)
        assert storage.storage_path == str(created_storage_path)

    def test_init_with_invalid_path(
        self,
        project_storage_path: ProjectStoragePath,
    ) -> None:
        with pytest.raises(FileNotFoundError, match="Project storage path doesn't exist"):
            ProjectStorage(project_storage_path)

    def test_init_creates_empty_state(
        self,
        created_storage_path: ProjectStoragePath,
    ) -> None:
        """Test that initialization creates empty internal state."""
        storage = ProjectStorage(created_storage_path)

        assert storage._session_mapping == {}
        assert storage._is_session_loaded is False


class TestStoragePathProperty:
    def test_storage_path_property_returns_string(
        self,
        created_storage_path: ProjectStoragePath,
    ) -> None:
        storage = ProjectStorage(created_storage_path)

        assert isinstance(storage.storage_path, str)
        assert storage.storage_path == str(created_storage_path)


class TestSessionsProperty:
    def test_sessions_empty_project(
        self,
        created_storage_path: ProjectStoragePath,
    ) -> None:
        storage = ProjectStorage(created_storage_path)
        assert len(storage.sessions) == 0
        assert isinstance(storage.sessions, set)

    def test_sessions_with_session_file(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text("[]")

        storage = ProjectStorage(created_storage_path)
        sessions = storage.sessions

        assert len(sessions) == 1
        session = list(sessions)[0]
        assert session.session_id == str(session_id)

    def test_sessions_with_session_directory(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_dir = os.path.join(str(created_storage_path), str(session_id))
        os.makedirs(session_dir, exist_ok=True)

        storage = ProjectStorage(created_storage_path)
        sessions = storage.sessions

        assert len(sessions) == 1
        session = list(sessions)[0]
        assert session.session_id == str(session_id)

    def test_sessions_with_multiple_sessions(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
        session_id2: uuid.UUID,
    ) -> None:
        session_file1 = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file1).write_text("[]")

        session_file2 = os.path.join(str(created_storage_path), f"{session_id2}.jsonl")
        pathlib.Path(session_file2).write_text("[]")

        storage = ProjectStorage(created_storage_path)
        sessions = storage.sessions

        assert len(sessions) == 2
        session_ids = {s.session_id for s in sessions}
        assert session_ids == {str(session_id), str(session_id2)}

    def test_sessions_lazy_loading(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = f"{session_id}.jsonl"
        with open(os.path.join(str(created_storage_path), session_file), "w") as f:
            f.write("[]")

        storage = ProjectStorage(created_storage_path)
        assert storage._is_session_loaded is False

        sessions = storage.sessions
        assert storage._is_session_loaded is True

        sessions2 = storage.sessions
        assert sessions == sessions2

    def test_sessions_deduplicates_same_session(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test that when both file and directory exist for same session, only one is created."""
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text("[]")

        session_dir = os.path.join(str(created_storage_path), str(session_id))
        os.makedirs(session_dir, exist_ok=True)

        storage = ProjectStorage(created_storage_path)
        sessions = storage.sessions

        # Should only have one session, not two
        assert len(sessions) == 1


class TestLoadSessions:
    """Tests for the _load_sessions method."""

    def test_load_sessions_only_loads_once(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that sessions are only loaded once."""
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text("[]")

        storage = ProjectStorage(created_storage_path)
        load_count = 0

        original_load = storage._load_sessions

        def counting_load() -> None:
            nonlocal load_count
            load_count += 1
            original_load()

        monkeypatch.setattr(storage, "_load_sessions", counting_load)

        _ = storage.sessions
        _ = storage.sessions
        _ = storage.sessions

        assert load_count == 1

    def test_load_sessions_sets_loaded_flag(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test that loading sets the _is_session_loaded flag."""
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text("[]")

        storage = ProjectStorage(created_storage_path)
        assert storage._is_session_loaded is False

        storage._load_sessions()
        assert storage._is_session_loaded is True

    def test_load_sessions_skips_invalid_files(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test that files without valid session IDs are skipped."""
        # Valid session file
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text("[]")

        # Invalid file that doesn't match UUID pattern
        invalid_file = os.path.join(str(created_storage_path), "not-a-uuid.txt")
        pathlib.Path(invalid_file).write_text("data")

        storage = ProjectStorage(created_storage_path)
        sessions = storage.sessions

        # Should only load the valid session
        assert len(sessions) == 1
        assert list(sessions)[0].session_id == str(session_id)


class TestGetSession:
    def test_get_session_by_id(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = f"{session_id}.jsonl"
        with open(os.path.join(str(created_storage_path), session_file), "w") as f:
            f.write("[]")

        storage = ProjectStorage(created_storage_path)
        session = storage.get_session(session_id)
        assert session is not None
        assert session.session_id == str(session_id)

    def test_get_session_with_string_id(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = f"{session_id}.jsonl"
        with open(os.path.join(str(created_storage_path), session_file), "w") as f:
            f.write("[]")

        storage = ProjectStorage(created_storage_path)
        session = storage.get_session(str(session_id))
        assert session is not None

    def test_get_session_not_found(
        self,
        created_storage_path: ProjectStoragePath,
    ) -> None:
        storage = ProjectStorage(created_storage_path)
        session = storage.get_session(uuid.uuid4())
        assert session is None

    def test_get_session_invalid_id(
        self,
        created_storage_path: ProjectStoragePath,
    ) -> None:
        storage = ProjectStorage(created_storage_path)
        session = storage.get_session("invalid-uuid")
        assert session is None

    def test_get_session_triggers_load(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test that getting a session triggers loading."""
        session_file = f"{session_id}.jsonl"
        with open(os.path.join(str(created_storage_path), session_file), "w") as f:
            f.write("[]")

        storage = ProjectStorage(created_storage_path)
        assert storage._is_session_loaded is False

        _ = storage.get_session(session_id)
        assert storage._is_session_loaded is True

    def test_get_session_uses_cache(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that getting session multiple times uses cache."""
        session_file = f"{session_id}.jsonl"
        with open(os.path.join(str(created_storage_path), session_file), "w") as f:
            f.write("[]")

        storage = ProjectStorage(created_storage_path)
        load_count = 0

        original_load = storage._load_sessions

        def counting_load() -> None:
            nonlocal load_count
            load_count += 1
            original_load()

        monkeypatch.setattr(storage, "_load_sessions", counting_load)

        _ = storage.get_session(session_id)
        _ = storage.get_session(session_id)
        _ = storage.get_session(session_id)

        assert load_count == 1


class TestIterTranscriptItems:
    def test_iter_transcript_items_empty_project(
        self,
        created_storage_path: ProjectStoragePath,
    ) -> None:
        storage = ProjectStorage(created_storage_path)
        items = list(storage.iter_transcript_items())

        assert items == []
        assert isinstance(items, list)

    def test_iter_transcript_items_single_session(
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

        storage = ProjectStorage(created_storage_path)
        items = list(storage.iter_transcript_items())

        assert len(items) == 3
        assert items[0]["type"] == "user"
        assert items[1]["content"] == "hi"
        assert items[2]["type"] == "user"

    def test_iter_transcript_items_multiple_sessions(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
        session_id2: uuid.UUID,
    ) -> None:
        session_file1 = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        lines1 = [{"type": "user", "id": 1}, {"type": "assistant", "id": 2}]
        pathlib.Path(session_file1).write_text("\n".join(json.dumps(line) for line in lines1))

        session_file2 = os.path.join(str(created_storage_path), f"{session_id2}.jsonl")
        lines2 = [
            {"type": "user", "id": 3},
            {"type": "assistant", "id": 4},
            {"type": "user", "id": 5},
        ]
        pathlib.Path(session_file2).write_text("\n".join(json.dumps(line) for line in lines2))

        storage = ProjectStorage(created_storage_path)
        items = list(storage.iter_transcript_items())

        assert len(items) == 5
        assert set(item["id"] for item in items) == {1, 2, 3, 4, 5}

    def test_iter_transcript_items_with_subagents(
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

        storage = ProjectStorage(created_storage_path)
        item_mapping = {item["id"]: item for item in storage.iter_transcript_items()}
        assert len(item_mapping) == 4
        assert item_mapping[1]["type"] == "main"
        assert item_mapping[2]["type"] == "main"
        assert item_mapping[3]["type"] == "agent"
        assert item_mapping[4]["type"] == "agent"

    def test_iter_transcript_items_lazy_evaluation(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        lines = [{"type": f"message_{i}", "id": i} for i in range(100)]
        pathlib.Path(session_file).write_text("\n".join(json.dumps(line) for line in lines))

        storage = ProjectStorage(created_storage_path)

        iterator = storage.iter_transcript_items()
        first_ten = []
        for i, item in enumerate(iterator):
            if i >= 10:
                break
            first_ten.append(item)

        assert len(first_ten) == 10
        assert first_ten[0]["id"] == 0
        assert first_ten[9]["id"] == 9

    def test_iter_transcript_items_preserves_data_types(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        data = {
            "string": "text",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "null": None,
            "array": [1, 2, 3],
            "nested": {"key": "value"},
        }
        pathlib.Path(session_file).write_text(json.dumps(data))

        storage = ProjectStorage(created_storage_path)
        items = list(storage.iter_transcript_items())

        assert len(items) == 1
        actual = items[0]
        assert actual["string"] == "text"
        assert actual["number"] == 42
        assert actual["float"] == 3.14
        assert actual["bool"] is True
        assert actual["null"] is None
        assert actual["array"] == [1, 2, 3]
        assert actual["nested"] == {"key": "value"}

    def test_iter_transcript_items_malformed_json_skipped(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        content = '{"type": "user"}\ninvalid json\n{"type": "assistant"}'
        pathlib.Path(session_file).write_text(content)

        storage = ProjectStorage(created_storage_path)
        items = list(storage.iter_transcript_items())

        assert len(items) == 2
        assert items[0]["type"] == "user"
        assert items[1]["type"] == "assistant"

        assert any("Failed to parse" in record.message for record in caplog.records)

    def test_iter_transcript_items_can_be_called_multiple_times(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        lines = [{"type": "user", "id": 1}, {"type": "assistant", "id": 2}]
        pathlib.Path(session_file).write_text("\n".join(json.dumps(line) for line in lines))

        storage = ProjectStorage(created_storage_path)

        items1 = list(storage.iter_transcript_items())
        assert len(items1) == 2

        items2 = list(storage.iter_transcript_items())
        assert len(items2) == 2
        assert items1 == items2

    def test_iter_transcript_items_with_empty_session_files(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
        session_id2: uuid.UUID,
    ) -> None:
        session_file1 = os.path.join(str(created_storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file1).write_text('{"type": "user", "id": 1}')

        session_file2 = os.path.join(str(created_storage_path), f"{session_id2}.jsonl")
        pathlib.Path(session_file2).write_text("")

        storage = ProjectStorage(created_storage_path)
        items = list(storage.iter_transcript_items())

        assert len(items) == 1
        assert items[0]["id"] == 1


class TestGetToolResultFileContent:
    """Tests for the get_tool_result_file_content method."""

    def test_get_tool_result_content_existing(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        # Create session directory and tool result file
        session_dir = os.path.join(str(created_storage_path), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file = os.path.join(tool_results_dir, "call_abc123.txt")
        expected_content = "Tool result content"
        pathlib.Path(tool_result_file).write_text(expected_content)

        storage = ProjectStorage(created_storage_path)
        content = storage.get_tool_result_file_content(session_id, "call_abc123")

        assert content == expected_content

    def test_get_tool_result_content_with_string_session_id(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test with string session ID instead of UUID."""
        session_dir = os.path.join(str(created_storage_path), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file = os.path.join(tool_results_dir, "call_test.txt")
        pathlib.Path(tool_result_file).write_text("result")

        storage = ProjectStorage(created_storage_path)
        content = storage.get_tool_result_file_content(str(session_id), "call_test")

        assert content == "result"

    def test_get_tool_result_content_session_not_found(
        self,
        created_storage_path: ProjectStoragePath,
    ) -> None:
        storage = ProjectStorage(created_storage_path)
        content = storage.get_tool_result_file_content(uuid.uuid4(), "call_test")

        assert content is None

    def test_get_tool_result_content_tool_use_id_not_found(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_dir = os.path.join(str(created_storage_path), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file = os.path.join(tool_results_dir, "call_abc123.txt")
        pathlib.Path(tool_result_file).write_text("result")

        storage = ProjectStorage(created_storage_path)
        content = storage.get_tool_result_file_content(session_id, "call_nonexistent")

        assert content is None

    def test_get_tool_result_content_invalid_session_id(
        self,
        created_storage_path: ProjectStoragePath,
    ) -> None:
        storage = ProjectStorage(created_storage_path)
        content = storage.get_tool_result_file_content("invalid-uuid", "call_test")

        assert content is None

    def test_get_tool_result_content_multiple_tool_results(
        self,
        created_storage_path: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test getting content from multiple tool result files."""
        session_dir = os.path.join(str(created_storage_path), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file1 = os.path.join(tool_results_dir, "call_abc123.txt")
        pathlib.Path(tool_result_file1).write_text("result 1")

        tool_result_file2 = os.path.join(tool_results_dir, "call_def456.txt")
        pathlib.Path(tool_result_file2).write_text("result 2")

        storage = ProjectStorage(created_storage_path)

        assert storage.get_tool_result_file_content(session_id, "call_abc123") == "result 1"
        assert storage.get_tool_result_file_content(session_id, "call_def456") == "result 2"

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

        storage = ProjectStorage(created_storage_path)
        content = storage.get_tool_result_file_content(session_id, "call_empty")

        assert content == ""
