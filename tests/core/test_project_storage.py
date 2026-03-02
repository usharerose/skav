#!/usr/bin/env python3
"""
Unit tests for ProjectStorage
"""

import json
import os
import pathlib
import uuid

import pytest

from skav.core.models.contents.text import TextContentItem
from skav.core.models.transcript_items import (
    AssistantTranscriptItem,
    UserTranscriptItem,
)
from skav.core.project_storage import ProjectStorage
from skav.core.project_storage_path import ProjectStoragePath
from tests.core.fixtures.sample_transcript_items import (
    generate_minimal_assistant,
    generate_minimal_user,
    generate_sample_assistant,
    generate_sample_user,
)


@pytest.fixture(scope="session")
def session_id2() -> uuid.UUID:
    return uuid.UUID("87654321-4321-4321-4321-cba987654321")


class TestInit:
    def test_init_with_valid_path(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
    ) -> None:
        storage = ProjectStorage(made_project_storage_path_obj)
        assert storage.storage_path == str(made_project_storage_path_obj)

    def test_init_with_invalid_path(
        self,
        project_storage_path_obj: ProjectStoragePath,
    ) -> None:
        with pytest.raises(FileNotFoundError, match="Project storage path doesn't exist"):
            ProjectStorage(project_storage_path_obj)

    def test_init_creates_empty_state(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
    ) -> None:
        """Test that initialization creates empty internal state."""
        storage = ProjectStorage(made_project_storage_path_obj)

        assert storage._session_mapping == {}
        assert storage._is_session_loaded is False


class TestStoragePathProperty:
    def test_storage_path_property_returns_string(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
    ) -> None:
        storage = ProjectStorage(made_project_storage_path_obj)

        assert isinstance(storage.storage_path, str)
        assert storage.storage_path == str(made_project_storage_path_obj)


class TestSessionsProperty:
    def test_sessions_empty_project(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
    ) -> None:
        storage = ProjectStorage(made_project_storage_path_obj)
        assert len(storage.sessions) == 0
        assert isinstance(storage.sessions, set)

    def test_sessions_with_session_file(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(made_project_storage_path_obj), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text("[]")

        storage = ProjectStorage(made_project_storage_path_obj)
        sessions = storage.sessions

        assert len(sessions) == 1
        session = list(sessions)[0]
        assert session.session_id == str(session_id)

    def test_sessions_with_session_directory(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_dir = os.path.join(str(made_project_storage_path_obj), str(session_id))
        os.makedirs(session_dir, exist_ok=True)

        storage = ProjectStorage(made_project_storage_path_obj)
        sessions = storage.sessions

        assert len(sessions) == 1
        session = list(sessions)[0]
        assert session.session_id == str(session_id)

    def test_sessions_with_multiple_sessions(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
        session_id2: uuid.UUID,
    ) -> None:
        session_file1 = os.path.join(str(made_project_storage_path_obj), f"{session_id}.jsonl")
        pathlib.Path(session_file1).write_text("[]")

        session_file2 = os.path.join(str(made_project_storage_path_obj), f"{session_id2}.jsonl")
        pathlib.Path(session_file2).write_text("[]")

        storage = ProjectStorage(made_project_storage_path_obj)
        sessions = storage.sessions

        assert len(sessions) == 2
        session_ids = {s.session_id for s in sessions}
        assert session_ids == {str(session_id), str(session_id2)}

    def test_sessions_lazy_loading(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = f"{session_id}.jsonl"
        with open(os.path.join(str(made_project_storage_path_obj), session_file), "w") as f:
            f.write("[]")

        storage = ProjectStorage(made_project_storage_path_obj)
        assert storage._is_session_loaded is False

        sessions = storage.sessions
        assert storage._is_session_loaded is True

        sessions2 = storage.sessions
        assert sessions == sessions2

    def test_sessions_deduplicates_same_session(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test that when both file and directory exist for same session, only one is created."""
        session_file = os.path.join(str(made_project_storage_path_obj), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text("[]")

        session_dir = os.path.join(str(made_project_storage_path_obj), str(session_id))
        os.makedirs(session_dir, exist_ok=True)

        storage = ProjectStorage(made_project_storage_path_obj)
        sessions = storage.sessions

        # Should only have one session, not two
        assert len(sessions) == 1


class TestLoadSessions:
    """Tests for the _load_sessions method."""

    def test_load_sessions_only_loads_once(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that sessions are only loaded once."""
        session_file = os.path.join(str(made_project_storage_path_obj), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text("[]")

        storage = ProjectStorage(made_project_storage_path_obj)
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
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test that loading sets the _is_session_loaded flag."""
        session_file = os.path.join(str(made_project_storage_path_obj), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text("[]")

        storage = ProjectStorage(made_project_storage_path_obj)
        assert storage._is_session_loaded is False

        storage._load_sessions()
        assert storage._is_session_loaded is True

    def test_load_sessions_skips_invalid_files(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test that files without valid session IDs are skipped."""
        # Valid session file
        session_file = os.path.join(str(made_project_storage_path_obj), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text("[]")

        # Invalid file that doesn't match UUID pattern
        invalid_file = os.path.join(str(made_project_storage_path_obj), "not-a-uuid.txt")
        pathlib.Path(invalid_file).write_text("data")

        storage = ProjectStorage(made_project_storage_path_obj)
        sessions = storage.sessions

        # Should only load the valid session
        assert len(sessions) == 1
        assert list(sessions)[0].session_id == str(session_id)


class TestGetSession:
    def test_get_session_by_id(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = f"{session_id}.jsonl"
        with open(os.path.join(str(made_project_storage_path_obj), session_file), "w") as f:
            f.write("[]")

        storage = ProjectStorage(made_project_storage_path_obj)
        session = storage.get_session(session_id)
        assert session is not None
        assert session.session_id == str(session_id)

    def test_get_session_with_string_id(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = f"{session_id}.jsonl"
        with open(os.path.join(str(made_project_storage_path_obj), session_file), "w") as f:
            f.write("[]")

        storage = ProjectStorage(made_project_storage_path_obj)
        session = storage.get_session(str(session_id))
        assert session is not None

    def test_get_session_not_found(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
    ) -> None:
        storage = ProjectStorage(made_project_storage_path_obj)
        session = storage.get_session(uuid.uuid4())
        assert session is None

    def test_get_session_invalid_id(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
    ) -> None:
        storage = ProjectStorage(made_project_storage_path_obj)
        session = storage.get_session("invalid-uuid")
        assert session is None

    def test_get_session_triggers_load(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test that getting a session triggers loading."""
        session_file = f"{session_id}.jsonl"
        with open(os.path.join(str(made_project_storage_path_obj), session_file), "w") as f:
            f.write("[]")

        storage = ProjectStorage(made_project_storage_path_obj)
        assert storage._is_session_loaded is False

        _ = storage.get_session(session_id)
        assert storage._is_session_loaded is True

    def test_get_session_uses_cache(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that getting session multiple times uses cache."""
        session_file = f"{session_id}.jsonl"
        with open(os.path.join(str(made_project_storage_path_obj), session_file), "w") as f:
            f.write("[]")

        storage = ProjectStorage(made_project_storage_path_obj)
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
        made_project_storage_path_obj: ProjectStoragePath,
    ) -> None:
        storage = ProjectStorage(made_project_storage_path_obj)
        items = list(storage.iter_transcript_items())

        assert items == []
        assert isinstance(items, list)

    def test_iter_transcript_items_single_session(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(made_project_storage_path_obj), f"{session_id}.jsonl")
        first_user_uuid, second_user_uuid = str(uuid.uuid4()), str(uuid.uuid4())
        assistant_uuid = str(uuid.uuid4())
        lines = [
            generate_sample_user(content="hello", user_uuid=first_user_uuid),
            generate_sample_assistant(
                content="hi", assistant_uuid=assistant_uuid, parent_uuid=first_user_uuid
            ),
            generate_sample_user(
                content="bye",
                user_uuid=second_user_uuid,
                parent_uuid=assistant_uuid,
            ),
        ]
        pathlib.Path(session_file).write_text("\n".join(json.dumps(line) for line in lines))

        storage = ProjectStorage(made_project_storage_path_obj)
        items = list(storage.iter_transcript_items())

        assert len(items) == 3
        first, second, third = items
        assert isinstance(first, UserTranscriptItem)
        assert isinstance(second, AssistantTranscriptItem)
        assert isinstance(third, UserTranscriptItem)
        assistant_tf_message_content_item, *_ = second.message.content
        assert isinstance(assistant_tf_message_content_item, TextContentItem)
        assert "hi" in assistant_tf_message_content_item.text

    def test_iter_transcript_items_multiple_sessions(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
        session_id2: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(made_project_storage_path_obj), f"{session_id}.jsonl")
        user_uuid = str(uuid.uuid4())
        assistant_uuid = str(uuid.uuid4())
        lines = [
            generate_minimal_user(user_uuid=user_uuid),
            generate_minimal_assistant(assistant_uuid=assistant_uuid, parent_uuid=user_uuid),
        ]
        pathlib.Path(session_file).write_text("\n".join(json.dumps(line) for line in lines))

        another_session_file = os.path.join(
            str(made_project_storage_path_obj), f"{session_id2}.jsonl"
        )
        second_user_uuid = str(uuid.uuid4())
        another_assistant_uuid = str(uuid.uuid4())
        third_user_uuid = str(uuid.uuid4())
        another_lines = [
            generate_minimal_user(user_uuid=second_user_uuid),
            generate_minimal_assistant(
                assistant_uuid=another_assistant_uuid,
                parent_uuid=second_user_uuid,
            ),
            generate_minimal_user(user_uuid=third_user_uuid),
        ]
        pathlib.Path(another_session_file).write_text(
            "\n".join(json.dumps(line) for line in another_lines),
        )

        storage = ProjectStorage(made_project_storage_path_obj)
        items = list(storage.iter_transcript_items())

        assert len(items) == 5
        user_items = [item for item in items if isinstance(item, UserTranscriptItem)]
        assert len(user_items) == 3
        uuids = {item.uuid for item in user_items}
        assert uuids == {user_uuid, second_user_uuid, third_user_uuid}

    def test_iter_transcript_items_with_subagents(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(made_project_storage_path_obj), f"{session_id}.jsonl")
        first_user_uuid = str(uuid.uuid4())
        second_user_uuid = str(uuid.uuid4())
        main_lines = [
            generate_minimal_user(user_uuid=first_user_uuid),
            generate_minimal_user(user_uuid=second_user_uuid),
        ]
        pathlib.Path(session_file).write_text("\n".join(json.dumps(line) for line in main_lines))

        session_dir = os.path.join(str(made_project_storage_path_obj), str(session_id))
        subagents_dir = os.path.join(session_dir, "subagents")
        os.makedirs(subagents_dir, exist_ok=True)

        agent_file = os.path.join(subagents_dir, "agent-task-123.jsonl")
        first_assistant_uuid = str(uuid.uuid4())
        second_assistant_uuid = str(uuid.uuid4())
        agent_lines = [
            generate_minimal_assistant(assistant_uuid=first_assistant_uuid),
            generate_minimal_assistant(assistant_uuid=second_assistant_uuid),
        ]
        pathlib.Path(agent_file).write_text("\n".join(json.dumps(line) for line in agent_lines))

        storage = ProjectStorage(made_project_storage_path_obj)
        items = list(storage.iter_transcript_items())
        assert len(items) == 4

    def test_iter_transcript_items_lazy_evaluation(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(made_project_storage_path_obj), f"{session_id}.jsonl")
        lines = [generate_minimal_user(content=f"message_{i}") for i in range(100)]
        pathlib.Path(session_file).write_text("\n".join(json.dumps(line) for line in lines))

        storage = ProjectStorage(made_project_storage_path_obj)

        iterator = storage.iter_transcript_items()
        first_ten = []
        for i, item in enumerate(iterator):
            if i >= 10:
                break
            first_ten.append(item)

        assert len(first_ten) == 10
        assert all(isinstance(item, UserTranscriptItem) for item in first_ten)

    def test_iter_transcript_items_preserves_data_types(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(made_project_storage_path_obj), f"{session_id}.jsonl")
        data = generate_minimal_user(content="test")
        pathlib.Path(session_file).write_text(json.dumps(data))

        storage = ProjectStorage(made_project_storage_path_obj)
        items = list(storage.iter_transcript_items())

        assert len(items) == 1
        tf_item, *_ = items
        assert isinstance(tf_item, UserTranscriptItem)
        assert tf_item.type == "user"
        assert tf_item.message.content == "test"
        assert tf_item.sessionId == "12345678-1234-1234-1234-123456789abc"
        assert tf_item.isSidechain is False

    def test_iter_transcript_items_malformed_json_skipped(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        session_file = os.path.join(str(made_project_storage_path_obj), f"{session_id}.jsonl")
        user_uuid = str(uuid.uuid4())
        content = (
            f"{json.dumps(generate_minimal_user(user_uuid=user_uuid))}"
            f"\ninvalid json\n{json.dumps(generate_minimal_assistant())}"
        )
        pathlib.Path(session_file).write_text(content)

        storage = ProjectStorage(made_project_storage_path_obj)
        items = list(storage.iter_transcript_items())

        assert len(items) == 2
        first, second = items
        assert isinstance(first, UserTranscriptItem)
        assert isinstance(second, AssistantTranscriptItem)

        assert any("Failed to parse" in record.message for record in caplog.records)

    def test_iter_transcript_items_can_be_called_multiple_times(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_file = os.path.join(str(made_project_storage_path_obj), f"{session_id}.jsonl")
        user_uuid = str(uuid.uuid4())
        lines = [
            generate_minimal_user(user_uuid=user_uuid),
            generate_minimal_assistant(parent_uuid=user_uuid),
        ]
        pathlib.Path(session_file).write_text("\n".join(json.dumps(line) for line in lines))

        storage = ProjectStorage(made_project_storage_path_obj)

        first_yielded_items = list(storage.iter_transcript_items())
        assert len(first_yielded_items) == 2

        second_yielded_items = list(storage.iter_transcript_items())
        assert len(second_yielded_items) == 2
        assert first_yielded_items == second_yielded_items

    def test_iter_transcript_items_with_empty_session_files(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
        session_id2: uuid.UUID,
    ) -> None:
        session_file1 = os.path.join(str(made_project_storage_path_obj), f"{session_id}.jsonl")
        user_uuid = str(uuid.uuid4())
        pathlib.Path(session_file1).write_text(
            json.dumps(generate_minimal_user(user_uuid=user_uuid))
        )

        session_file2 = os.path.join(str(made_project_storage_path_obj), f"{session_id2}.jsonl")
        pathlib.Path(session_file2).write_text("")

        storage = ProjectStorage(made_project_storage_path_obj)
        items = list(storage.iter_transcript_items())

        assert len(items) == 1
        tf_item, *_ = items
        assert isinstance(tf_item, UserTranscriptItem)


class TestGetToolResultFileContent:
    """Tests for the get_tool_result_file_content method."""

    def test_get_tool_result_content_existing(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        # Create session directory and tool result file
        session_dir = os.path.join(str(made_project_storage_path_obj), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file = os.path.join(tool_results_dir, "call_abc123.txt")
        expected_content = "Tool result content"
        pathlib.Path(tool_result_file).write_text(expected_content)

        storage = ProjectStorage(made_project_storage_path_obj)
        content = storage.get_tool_result_file_content(session_id, "call_abc123")

        assert content == expected_content

    def test_get_tool_result_content_with_string_session_id(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test with string session ID instead of UUID."""
        session_dir = os.path.join(str(made_project_storage_path_obj), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file = os.path.join(tool_results_dir, "call_test.txt")
        pathlib.Path(tool_result_file).write_text("result")

        storage = ProjectStorage(made_project_storage_path_obj)
        content = storage.get_tool_result_file_content(str(session_id), "call_test")

        assert content == "result"

    def test_get_tool_result_content_session_not_found(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
    ) -> None:
        storage = ProjectStorage(made_project_storage_path_obj)
        content = storage.get_tool_result_file_content(uuid.uuid4(), "call_test")

        assert content is None

    def test_get_tool_result_content_tool_use_id_not_found(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_dir = os.path.join(str(made_project_storage_path_obj), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file = os.path.join(tool_results_dir, "call_abc123.txt")
        pathlib.Path(tool_result_file).write_text("result")

        storage = ProjectStorage(made_project_storage_path_obj)
        content = storage.get_tool_result_file_content(session_id, "call_nonexistent")

        assert content is None

    def test_get_tool_result_content_invalid_session_id(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
    ) -> None:
        storage = ProjectStorage(made_project_storage_path_obj)
        content = storage.get_tool_result_file_content("invalid-uuid", "call_test")

        assert content is None

    def test_get_tool_result_content_multiple_tool_results(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        """Test getting content from multiple tool result files."""
        session_dir = os.path.join(str(made_project_storage_path_obj), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file1 = os.path.join(tool_results_dir, "call_abc123.txt")
        pathlib.Path(tool_result_file1).write_text("result 1")

        tool_result_file2 = os.path.join(tool_results_dir, "call_def456.txt")
        pathlib.Path(tool_result_file2).write_text("result 2")

        storage = ProjectStorage(made_project_storage_path_obj)

        assert storage.get_tool_result_file_content(session_id, "call_abc123") == "result 1"
        assert storage.get_tool_result_file_content(session_id, "call_def456") == "result 2"

    def test_get_tool_result_content_empty_file(
        self,
        made_project_storage_path_obj: ProjectStoragePath,
        session_id: uuid.UUID,
    ) -> None:
        session_dir = os.path.join(str(made_project_storage_path_obj), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file = os.path.join(tool_results_dir, "call_empty.txt")
        pathlib.Path(tool_result_file).write_text("")

        storage = ProjectStorage(made_project_storage_path_obj)
        content = storage.get_tool_result_file_content(session_id, "call_empty")

        assert content == ""
