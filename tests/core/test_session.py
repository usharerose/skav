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

USER_HOME = "/home/user"


class TestSessionInit:
    def test_init_with_uuid_session_id(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode(
            os.path.join(str(tmp_path), "workspace", "project"),
        )
        os.makedirs(str(storage_path), exist_ok=True)
        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(storage_path, session_id)

        assert session.session_id == str(session_id)

    def test_init_with_string_session_id(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = str(uuid.uuid4())

        storage_path = ProjectStoragePath.encode(
            os.path.join(str(tmp_path), "workspace", "project"),
        )
        os.makedirs(str(storage_path), exist_ok=True)
        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(storage_path, session_id)

        assert session.session_id == session_id

    def test_init_storage_path_not_exists(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")

        with pytest.raises(FileNotFoundError, match="Project storage path doesn't exist"):
            Session(storage_path, session_id)

    def test_init_session_not_exists(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        with pytest.raises(FileNotFoundError, match="Session .* doesn't exist"):
            Session(storage_path, session_id)

    def test_init_with_session_directory(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_dir = os.path.join(str(storage_path), str(session_id))
        os.makedirs(session_dir, exist_ok=True)

        session = Session(storage_path, session_id)

        assert session.session_id == str(session_id)


class TestSessionPath:
    def test_session_path_default_is_file(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)
        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(storage_path, session_id)

        expected_path = os.path.join(str(storage_path), f"{session_id}.jsonl")
        assert session.session_path() == expected_path

    def test_session_path_is_file_true(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)
        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(storage_path, session_id)

        expected_path = os.path.join(str(storage_path), f"{session_id}.jsonl")
        assert session.session_path(is_file=True) == expected_path

    def test_session_path_is_file_false(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)
        expected_path = os.path.join(str(storage_path), str(session_id))
        os.mkdir(expected_path)

        session = Session(storage_path, session_id)

        assert session.session_path(is_file=False) == expected_path


class TestIterTranscriptFiles:
    def test_iter_transcript_files_with_main_session_file(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        lines = [{"type": "user", "content": "hello"}, {"type": "assistant", "content": "hi"}]
        pathlib.Path(session_file).write_text("\n".join(json.dumps(line) for line in lines))

        session = Session(storage_path, session_id)
        transcript_files = list(session.iter_transcript_files())

        assert len(transcript_files) == 1
        assert str(transcript_files[0].path) == session_file

    def test_iter_transcript_files_with_subagents(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "main"}')

        session_dir = os.path.join(str(storage_path), str(session_id))
        subagents_dir = os.path.join(session_dir, "subagents")
        os.makedirs(subagents_dir, exist_ok=True)

        agent1_file = os.path.join(subagents_dir, "agent-task-123.jsonl")
        pathlib.Path(agent1_file).write_text('{"type": "agent1"}')

        agent2_file = os.path.join(subagents_dir, "agent-bash-456.jsonl")
        pathlib.Path(agent2_file).write_text('{"type": "agent2"}')

        session = Session(storage_path, session_id)
        transcript_files = list(session.iter_transcript_files())

        assert len(transcript_files) == 3
        file_paths = {tf.path for tf in transcript_files}
        assert session_file in file_paths
        assert agent1_file in file_paths
        assert agent2_file in file_paths

    def test_iter_transcript_files_with_session_directory_only(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_dir = os.path.join(str(storage_path), str(session_id))
        subagents_dir = os.path.join(session_dir, "subagents")
        os.makedirs(subagents_dir, exist_ok=True)

        agent_file = os.path.join(subagents_dir, "agent-task-123.jsonl")
        pathlib.Path(agent_file).write_text('{"type": "agent"}')

        session = Session(storage_path, session_id)
        transcript_files = list(session.iter_transcript_files())

        assert len(transcript_files) == 1
        assert str(transcript_files[0].path) == agent_file

    def test_iter_transcript_files_ignores_non_jsonl_files(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "main"}')

        session_dir = os.path.join(str(storage_path), str(session_id))
        os.makedirs(session_dir, exist_ok=True)

        (pathlib.Path(session_dir) / "result.txt").write_text("some result")
        (pathlib.Path(session_dir) / "output.log").write_text("some log")

        session = Session(storage_path, session_id)
        transcript_files = list(session.iter_transcript_files())

        assert len(transcript_files) == 1
        assert str(transcript_files[0].path) == session_file


class TestIterTranscripts:
    def test_iter_transcripts_single_file(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        lines = [
            {"type": "user", "content": "hello"},
            {"type": "assistant", "content": "hi"},
            {"type": "user", "content": "bye"},
        ]
        pathlib.Path(session_file).write_text("\n".join(json.dumps(line) for line in lines))

        session = Session(storage_path, session_id)
        transcripts = list(session.iter_transcripts())

        assert len(transcripts) == 3
        assert transcripts[0]["type"] == "user"
        assert transcripts[1]["type"] == "assistant"
        assert transcripts[2]["content"] == "bye"

    def test_iter_transcripts_multiple_files(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        main_lines = [{"type": "main", "id": 1}, {"type": "main", "id": 2}]
        pathlib.Path(session_file).write_text("\n".join(json.dumps(line) for line in main_lines))

        session_dir = os.path.join(str(storage_path), str(session_id))
        subagents_dir = os.path.join(session_dir, "subagents")
        os.makedirs(subagents_dir, exist_ok=True)

        agent_file = os.path.join(subagents_dir, "agent-task-123.jsonl")
        agent_lines = [{"type": "agent", "id": 3}, {"type": "agent", "id": 4}]
        pathlib.Path(agent_file).write_text("\n".join(json.dumps(line) for line in agent_lines))

        session = Session(storage_path, session_id)
        transcripts = list(session.iter_transcripts())

        assert len(transcripts) == 4
        assert transcripts[0]["type"] == "main"
        assert transcripts[1]["id"] == 2
        assert transcripts[2]["type"] == "agent"
        assert transcripts[3]["id"] == 4

    def test_iter_transcripts_empty_session(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text("")

        session = Session(storage_path, session_id)
        transcripts = list(session.iter_transcripts())

        assert transcripts == []


class TestSessionEquality:
    def test_eq_equal_sessions(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session1 = Session(storage_path, session_id)
        session2 = Session(storage_path, session_id)

        assert session1 == session2

    def test_eq_different_sessions(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id1 = uuid.uuid4()
        session_id2 = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_file1 = os.path.join(str(storage_path), f"{session_id1}.jsonl")
        session_file2 = os.path.join(str(storage_path), f"{session_id2}.jsonl")
        pathlib.Path(session_file1).write_text('{"type": "test1"}')
        pathlib.Path(session_file2).write_text('{"type": "test2"}')

        session1 = Session(storage_path, session_id1)
        session2 = Session(storage_path, session_id2)

        assert session1 != session2

    def test_eq_non_session_object(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(storage_path, session_id)

        assert session != "not a session"
        assert session != 123


class TestSessionHash:
    def test_hash_equal_sessions_have_same_hash(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session1 = Session(storage_path, session_id)
        session2 = Session(storage_path, session_id)

        assert hash(session1) == hash(session2)

    def test_hash_different_sessions_have_different_hashes(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id1 = uuid.uuid4()
        session_id2 = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_file1 = os.path.join(str(storage_path), f"{session_id1}.jsonl")
        session_file2 = os.path.join(str(storage_path), f"{session_id2}.jsonl")
        pathlib.Path(session_file1).write_text('{"type": "test1"}')
        pathlib.Path(session_file2).write_text('{"type": "test2"}')

        session1 = Session(storage_path, session_id1)
        session2 = Session(storage_path, session_id2)

        assert hash(session1) != hash(session2)

    def test_hash_session_can_be_used_in_set(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session1 = Session(storage_path, session_id)
        session2 = Session(storage_path, session_id)

        session_set = {session1, session2}

        assert len(session_set) == 1


class TestIterToolResultFiles:
    def test_iter_tool_result_files_with_results(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_dir = os.path.join(str(storage_path), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file1 = os.path.join(tool_results_dir, "call_abc123.txt")
        pathlib.Path(tool_result_file1).write_text("result 1")

        tool_result_file2 = os.path.join(tool_results_dir, "call_def456.txt")
        pathlib.Path(tool_result_file2).write_text("result 2")

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(storage_path, session_id)
        tool_results = list(session._iter_tool_result_files())

        assert len(tool_results) == 2
        assert set(tool_result_file.tool_use_id for tool_result_file in tool_results) == {
            "call_abc123",
            "call_def456",
        }

    def test_iter_tool_result_files_nested_subdirectories(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_dir = os.path.join(str(storage_path), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        nested_dir = os.path.join(tool_results_dir, "subdir", "nested")
        os.makedirs(nested_dir, exist_ok=True)

        tool_result_file = os.path.join(nested_dir, "call_xyz789.txt")
        pathlib.Path(tool_result_file).write_text("nested result")

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(storage_path, session_id)
        with pytest.raises(ValueError):
            list(session._iter_tool_result_files())

    def test_iter_tool_result_files_ignores_non_txt_files(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_dir = os.path.join(str(storage_path), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file = os.path.join(tool_results_dir, "call_abc123.txt")
        pathlib.Path(tool_result_file).write_text("result")

        (pathlib.Path(tool_results_dir) / "other.json").write_text('{"type": "data"}')
        (pathlib.Path(tool_results_dir) / "output.log").write_text("log content")

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(storage_path, session_id)
        tool_results = list(session._iter_tool_result_files())

        assert len(tool_results) == 1
        assert tool_results[0].tool_use_id == "call_abc123"

    def test_iter_tool_result_files_caches_results(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_dir = os.path.join(str(storage_path), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file = os.path.join(tool_results_dir, "call_abc123.txt")
        pathlib.Path(tool_result_file).write_text("result")

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(storage_path, session_id)

        # First iteration - builds cache
        tool_results1 = list(session._iter_tool_result_files())
        assert len(tool_results1) == 1

        # Second iteration - uses cache
        tool_results2 = list(session._iter_tool_result_files())
        assert len(tool_results2) == 1

        # Both iterations should return the same ToolResultFile objects
        assert tool_results1[0] is tool_results2[0]

    def test_iter_tool_result_files_no_session_directory(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(storage_path, session_id)
        tool_results = list(session._iter_tool_result_files())

        assert tool_results == []


class TestGetToolResultFileContent:
    def test_get_tool_result_content_existing(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_dir = os.path.join(str(storage_path), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file = os.path.join(tool_results_dir, "call_abc123.txt")
        expected_content = "This is the tool result content\nwith multiple lines"
        pathlib.Path(tool_result_file).write_text(expected_content)

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(storage_path, session_id)
        content = session.get_tool_result_file_content("call_abc123")

        assert content == expected_content

    def test_get_tool_result_content_nonexistent(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(storage_path, session_id)
        content = session.get_tool_result_file_content("call_nonexistent")

        assert content is None

    def test_get_tool_result_content_multiple_files(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_dir = os.path.join(str(storage_path), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file1 = os.path.join(tool_results_dir, "call_abc123.txt")
        pathlib.Path(tool_result_file1).write_text("result 1")

        tool_result_file2 = os.path.join(tool_results_dir, "call_def456.txt")
        pathlib.Path(tool_result_file2).write_text("result 2")

        tool_result_file3 = os.path.join(tool_results_dir, "call_xyz789.txt")
        pathlib.Path(tool_result_file3).write_text("result 3")

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(storage_path, session_id)

        assert session.get_tool_result_file_content("call_abc123") == "result 1"
        assert session.get_tool_result_file_content("call_def456") == "result 2"
        assert session.get_tool_result_file_content("call_xyz789") == "result 3"
        assert session.get_tool_result_file_content("call_nonexistent") is None

    def test_get_tool_result_content_uses_cache(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_dir = os.path.join(str(storage_path), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file = os.path.join(tool_results_dir, "call_abc123.txt")
        pathlib.Path(tool_result_file).write_text("result content")

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(storage_path, session_id)

        # First call - builds cache
        content1 = session.get_tool_result_file_content("call_abc123")
        assert content1 == "result content"

        # Second call - uses cache
        content2 = session.get_tool_result_file_content("call_abc123")
        assert content2 == "result content"

    def test_get_tool_result_content_empty_file(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        session_id = uuid.uuid4()

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        os.makedirs(str(storage_path), exist_ok=True)

        session_dir = os.path.join(str(storage_path), str(session_id))
        tool_results_dir = os.path.join(session_dir, "tool-results")
        os.makedirs(tool_results_dir, exist_ok=True)

        tool_result_file = os.path.join(tool_results_dir, "call_empty.txt")
        pathlib.Path(tool_result_file).write_text("")

        session_file = os.path.join(str(storage_path), f"{session_id}.jsonl")
        pathlib.Path(session_file).write_text('{"type": "test"}')

        session = Session(storage_path, session_id)
        content = session.get_tool_result_file_content("call_empty")

        assert content == ""
