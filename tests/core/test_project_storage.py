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

USER_HOME = "/home/user"


class TestInit:
    def test_init_with_valid_path(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        storage = ProjectStorage(storage_path)
        assert storage.storage_path == str(storage_path)

    def test_init_with_invalid_path(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")

        with pytest.raises(FileNotFoundError, match="Project storage path doesn't exist"):
            ProjectStorage(storage_path)


class TestSessionsProperty:
    def test_sessions_empty_project(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        storage = ProjectStorage(storage_path)
        assert len(storage.sessions) == 0
        assert isinstance(storage.sessions, set)

    def test_sessions_lazy_loading(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_id = uuid.uuid4()
        session_file = f"{session_id}.jsonl"
        with open(os.path.join(str(storage_path), session_file), "w") as f:
            f.write("[]")

        storage = ProjectStorage(storage_path)
        sessions = storage.sessions
        sessions2 = storage.sessions
        assert sessions == sessions2


class TestGetSession:
    def test_get_session_by_id(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_id = uuid.uuid4()
        session_file = f"{session_id}.jsonl"
        with open(os.path.join(str(storage_path), session_file), "w") as f:
            f.write("[]")

        storage = ProjectStorage(storage_path)
        session = storage.get_session(session_id)
        assert session is not None
        assert session.session_id == str(session_id)

    def test_get_session_with_string_id(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_id = uuid.uuid4()
        session_file = f"{session_id}.jsonl"
        with open(os.path.join(str(storage_path), session_file), "w") as f:
            f.write("[]")

        storage = ProjectStorage(storage_path)
        session = storage.get_session(str(session_id))
        assert session is not None

    def test_get_session_not_found(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        storage = ProjectStorage(storage_path)
        session = storage.get_session(uuid.uuid4())
        assert session is None

    def test_get_session_invalid_id(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        storage = ProjectStorage(storage_path)
        session = storage.get_session("invalid-uuid")
        assert session is None


class TestIterTranscriptItems:
    def test_iter_transcript_items_empty_project(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        storage = ProjectStorage(storage_path)
        items = list(storage.iter_transcript_items())

        assert items == []
        assert isinstance(items, list)

    def test_iter_transcript_items_single_session(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_id = uuid.uuid4()
        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        lines = [
            {"type": "user", "content": "hello"},
            {"type": "assistant", "content": "hi"},
            {"type": "user", "content": "bye"},
        ]
        pathlib.Path(session_file).write_text("\n".join(json.dumps(line) for line in lines))

        storage = ProjectStorage(storage_path)
        items = list(storage.iter_transcript_items())

        assert len(items) == 3
        assert items[0]["type"] == "user"
        assert items[1]["content"] == "hi"
        assert items[2]["type"] == "user"

    def test_iter_transcript_items_multiple_sessions(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_id1 = uuid.uuid4()
        session_file1 = os.path.join(str(storage_path), f"{session_id1}.jsonl")
        lines1 = [{"type": "user", "id": 1}, {"type": "assistant", "id": 2}]
        pathlib.Path(session_file1).write_text("\n".join(json.dumps(line) for line in lines1))

        session_id2 = uuid.uuid4()
        session_file2 = os.path.join(str(storage_path), f"{session_id2}.jsonl")
        lines2 = [
            {"type": "user", "id": 3},
            {"type": "assistant", "id": 4},
            {"type": "user", "id": 5},
        ]
        pathlib.Path(session_file2).write_text("\n".join(json.dumps(line) for line in lines2))

        storage = ProjectStorage(storage_path)
        items = list(storage.iter_transcript_items())

        assert len(items) == 5
        assert set(item["id"] for item in items) == {1, 2, 3, 4, 5}

    def test_iter_transcript_items_with_subagents(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_id = uuid.uuid4()

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        main_lines = [{"type": "main", "id": 1}, {"type": "main", "id": 2}]
        pathlib.Path(session_file).write_text("\n".join(json.dumps(line) for line in main_lines))

        session_dir = os.path.join(str(storage_path), str(session_id))
        subagents_dir = os.path.join(session_dir, "subagents")
        os.makedirs(subagents_dir, exist_ok=True)

        agent_file = os.path.join(subagents_dir, "agent-task-123.jsonl")
        agent_lines = [{"type": "agent", "id": 3}, {"type": "agent", "id": 4}]
        pathlib.Path(agent_file).write_text("\n".join(json.dumps(line) for line in agent_lines))

        storage = ProjectStorage(storage_path)
        items = list(storage.iter_transcript_items())

        assert len(items) == 4
        assert items[0]["type"] == "main"
        assert items[1]["id"] == 2
        assert items[2]["type"] == "agent"
        assert items[3]["id"] == 4

    def test_iter_transcript_items_lazy_evaluation(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_id = uuid.uuid4()
        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        lines = [{"type": f"message_{i}", "id": i} for i in range(100)]
        pathlib.Path(session_file).write_text("\n".join(json.dumps(line) for line in lines))

        storage = ProjectStorage(storage_path)

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
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_id = uuid.uuid4()
        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
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

        storage = ProjectStorage(storage_path)
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
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_id = uuid.uuid4()
        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        content = '{"type": "user"}\ninvalid json\n{"type": "assistant"}'
        pathlib.Path(session_file).write_text(content)

        storage = ProjectStorage(storage_path)
        items = list(storage.iter_transcript_items())

        assert len(items) == 2
        assert items[0]["type"] == "user"
        assert items[1]["type"] == "assistant"

        assert any("Failed to parse" in record.message for record in caplog.records)

    def test_iter_transcript_items_can_be_called_multiple_times(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_id = uuid.uuid4()
        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        lines = [{"type": "user", "id": 1}, {"type": "assistant", "id": 2}]
        pathlib.Path(session_file).write_text("\n".join(json.dumps(line) for line in lines))

        storage = ProjectStorage(storage_path)

        items1 = list(storage.iter_transcript_items())
        assert len(items1) == 2

        items2 = list(storage.iter_transcript_items())
        assert len(items2) == 2
        assert items1 == items2

    def test_iter_transcript_items_with_empty_session_files(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_id1 = uuid.uuid4()
        session_file1 = os.path.join(str(storage_path), f"{session_id1}.jsonl")
        pathlib.Path(session_file1).write_text('{"type": "user", "id": 1}')

        session_id2 = uuid.uuid4()
        session_file2 = os.path.join(str(storage_path), f"{session_id2}.jsonl")
        pathlib.Path(session_file2).write_text("")

        storage = ProjectStorage(storage_path)
        items = list(storage.iter_transcript_items())

        assert len(items) == 1
        assert items[0]["id"] == 1
