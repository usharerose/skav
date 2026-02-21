#!/usr/bin/env python3
"""
Unit tests for TranscriptFile
"""

import json
import os
import pathlib
import uuid

import pytest

from vibehist.core.project_storage_path import ProjectStoragePath
from vibehist.core.transcript_file import TranscriptFile


@pytest.fixture(scope="session")
def agent_id() -> str:
    return "12345"


@pytest.fixture(scope="function")
def transcript_path(
    made_project_storage_path_obj: ProjectStoragePath,
    session_id: uuid.UUID,
) -> pathlib.Path:
    epath = os.path.join(str(made_project_storage_path_obj), f"{session_id}.jsonl")
    return pathlib.Path(epath)


@pytest.fixture(scope="function")
def subagent_transcript_path(
    made_project_storage_path_obj: ProjectStoragePath,
    session_id: uuid.UUID,
    agent_id: str,
) -> pathlib.Path:
    subagent_dir = pathlib.Path(
        os.path.join(
            str(made_project_storage_path_obj),
            str(session_id),
            "subagents",
        )
    )
    subagent_dir.mkdir(parents=True)
    return subagent_dir / f"agent-{agent_id}.jsonl"


class TestTranscriptFileInit:
    def test_init_with_valid_extension(
        self,
        transcript_path: pathlib.Path,
    ) -> None:
        transcript_path.write_text("")

        tf = TranscriptFile(transcript_path)
        assert tf.path == str(transcript_path)
        assert tf.exists is True

    def test_init_with_invalid_extension(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "test.txt"
        file_path.write_text("")

        with pytest.raises(ValueError, match="Invalid transcript file extension"):
            TranscriptFile(file_path)

    def test_init_with_no_extension(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "test"
        file_path.write_text("")

        with pytest.raises(ValueError, match="Invalid transcript file extension"):
            TranscriptFile(file_path)

    def test_init_with_pathlib_path(
        self,
        transcript_path: pathlib.Path,
    ) -> None:
        transcript_path.write_text("")

        tf = TranscriptFile(transcript_path)
        assert tf.path == str(transcript_path)

    def test_init_normalizes_path(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "test.jsonl"
        file_path.write_text("{}\n")

        os.chdir(tmp_path)

        tf = TranscriptFile("test.jsonl")
        assert tf.path == str(file_path)

    def test_init_does_not_load_file_immediately(
        self,
        transcript_path: pathlib.Path,
    ) -> None:
        """Test that initialization is lazy and doesn't load the file."""
        transcript_path.write_text('{"type": "test"}')

        tf = TranscriptFile(transcript_path)
        # File should not be loaded until we iterate
        assert tf._is_loaded is False

    def test_init_creates_empty_items_list(
        self,
        transcript_path: pathlib.Path,
    ) -> None:
        """Test that initialization creates an empty items list."""
        tf = TranscriptFile(transcript_path)

        assert tf._items == []
        assert tf._is_loaded is False


class TestTranscriptFileProperties:
    def test_exists_property_true(
        self,
        transcript_path: pathlib.Path,
    ) -> None:
        transcript_path.write_text("{}")

        tf = TranscriptFile(transcript_path)
        assert tf.exists is True

    def test_exists_property_false(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "nonexistent.jsonl"

        tf = TranscriptFile(file_path)
        assert tf.exists is False

    def test_path_property(
        self,
        transcript_path: pathlib.Path,
    ) -> None:
        transcript_path.write_text("")

        tf = TranscriptFile(transcript_path)
        assert tf.path == str(transcript_path)
        assert isinstance(tf.path, str)

    def test_path_property_does_not_trigger_load(
        self,
        transcript_path: pathlib.Path,
    ) -> None:
        """Test that accessing path property doesn't load the file."""
        transcript_path.write_text('{"type": "test"}')

        tf = TranscriptFile(transcript_path)
        _ = tf.path

        assert tf._is_loaded is False


class TestTranscriptFileIterItems:
    def test_iter_items_empty_file(
        self,
        transcript_path: pathlib.Path,
    ) -> None:
        transcript_path.write_text("")

        tf = TranscriptFile(transcript_path)
        items = list(item for item in tf)

        assert items == []

    def test_iter_items_single_line(
        self,
        transcript_path: pathlib.Path,
    ) -> None:
        data = {"type": "user", "content": "hello"}
        transcript_path.write_text(json.dumps(data))

        tf = TranscriptFile(transcript_path)
        items = list(item for item in tf)

        assert len(items) == 1
        actual, *_ = items
        assert actual == data

    def test_iter_items_multiple_lines(
        self,
        transcript_path: pathlib.Path,
    ) -> None:
        lines = [
            {"type": "user", "content": "hello"},
            {"type": "assistant", "content": "hi"},
            {"type": "user", "content": "bye"},
        ]
        transcript_path.write_text("\n".join(json.dumps(line) for line in lines))

        tf = TranscriptFile(transcript_path)
        items = list(item for item in tf)

        assert len(items) == 3
        first, second, third = items
        assert first["type"] == "user"
        assert second["type"] == "assistant"
        assert third["content"] == "bye"

    def test_iter_items_skip_empty_lines(
        self,
        transcript_path: pathlib.Path,
    ) -> None:
        content = '\n\n{"type": "user"}\n\n\n{"type": "assistant"}\n\n'
        transcript_path.write_text(content)

        tf = TranscriptFile(transcript_path)
        items = list(item for item in tf)

        assert len(items) == 2
        assert items[0]["type"] == "user"
        assert items[1]["type"] == "assistant"

    def test_iter_items_skip_whitespace_lines(
        self,
        transcript_path: pathlib.Path,
    ) -> None:
        content = '{"type": "user"}\n   \n\t\n{"type": "assistant"}\n'
        transcript_path.write_text(content)

        tf = TranscriptFile(transcript_path)
        items = list(item for item in tf)

        assert len(items) == 2

    def test_iter_items_malformed_json(
        self,
        transcript_path: pathlib.Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        content = '{"type": "user"}\nnot json\n{"type": "assistant"}'
        transcript_path.write_text(content)

        tf = TranscriptFile(transcript_path)
        items = list(item for item in tf)

        assert len(items) == 2
        first, second = items
        assert first["type"] == "user"
        assert second["type"] == "assistant"

        assert any("Failed to parse" in record.message for record in caplog.records)

    def test_iter_items_file_not_found(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "nonexistent.jsonl"

        tf = TranscriptFile(file_path)

        with pytest.raises(FileNotFoundError, match="doesn't exist"):
            list(item for item in tf)

    def test_iter_items_preserves_data_types(
        self,
        transcript_path: pathlib.Path,
    ) -> None:
        data = {
            "string": "text",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "null": None,
            "array": [1, 2, 3],
            "nested": {"key": "value"},
        }
        transcript_path.write_text(json.dumps(data))

        tf = TranscriptFile(transcript_path)
        items = list(item for item in tf)

        assert len(items) == 1
        actual, *_ = items
        assert actual["string"] == "text"
        assert actual["number"] == 42
        assert actual["float"] == 3.14
        assert actual["bool"] is True
        assert actual["null"] is None
        assert actual["array"] == [1, 2, 3]
        assert actual["nested"] == {"key": "value"}

    def test_iter_items_multiple_times_uses_cache(
        self,
        transcript_path: pathlib.Path,
    ) -> None:
        """Test that multiple iterations use cached data (lazy loading)."""
        content = '{"type": "user"}\n{"type": "assistant"}'
        transcript_path.write_text(content)

        tf = TranscriptFile(transcript_path)
        first_items = list(tf)
        second_items = list(tf)

        assert first_items == second_items
        assert len(first_items) == 2

    def test_iter_items_sets_loaded_flag(
        self,
        transcript_path: pathlib.Path,
    ) -> None:
        """Test that iteration sets the _is_loaded flag."""
        transcript_path.write_text('{"type": "test"}')

        tf = TranscriptFile(transcript_path)
        assert tf._is_loaded is False

        _ = list(tf)
        assert tf._is_loaded is True

    def test_iter_items_only_loads_once(
        self,
        transcript_path: pathlib.Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that file is only loaded once even with multiple iterations."""
        transcript_path.write_text('{"type": "test"}')

        tf = TranscriptFile(transcript_path)
        load_count = 0

        original_load = tf._load

        def counting_load() -> None:
            nonlocal load_count
            load_count += 1
            original_load()

        monkeypatch.setattr(tf, "_load", counting_load)

        _ = list(tf)
        _ = list(tf)
        _ = list(tf)

        assert load_count == 1


class TestTranscriptFileEdgeCases:
    def test_unicode_content(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "unicode.jsonl"
        data = {
            "emoji": "😀🎉",
            "chinese": "你好世界",
            "arabic": "مرحبا",
            "russian": "Привет",
        }
        file_path.write_text(json.dumps(data), encoding="utf-8")

        tf = TranscriptFile(file_path)
        items = list(item for item in tf)

        assert len(items) == 1
        actual, *_ = items
        assert actual["emoji"] == "😀🎉"
        assert actual["chinese"] == "你好世界"

    def test_special_characters_in_json(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "special.jsonl"
        data = {
            "newline": "line1\nline2",
            "tab": "col1\tcol2",
            "quote": 'He said "hello"',
            "backslash": "path\\to\\file",
        }
        file_path.write_text(json.dumps(data))

        tf = TranscriptFile(file_path)
        items = list(item for item in tf)

        assert len(items) == 1
        actual, *_ = items
        assert "\n" in actual["newline"]
        assert "\t" in actual["tab"]
        assert '"' in actual["quote"]

    def test_file_with_bom(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "bom.jsonl"
        data = {"type": "user"}
        file_path.write_bytes(b"\xef\xbb\xbf" + json.dumps(data).encode("utf-8"))

        tf = TranscriptFile(file_path)
        items = list(item for item in tf)

        assert len(items) == 1

    def test_multiple_malformed_lines(
        self,
        tmp_path: pathlib.Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        file_path = tmp_path / "multi_malformed.jsonl"
        content = '{"type": "user"}\nbad1\n{"type": "assistant"}\nbad2\nbad3\n{"type": "user"}\n'
        file_path.write_text(content)

        tf = TranscriptFile(file_path)
        items = list(item for item in tf)

        assert len(items) == 3
        first, second, third = items
        assert first["type"] == "user"
        assert second["type"] == "assistant"
        assert third["type"] == "user"

        parse_errors = [r for r in caplog.records if "Failed to parse" in r.message]
        assert len(parse_errors) == 3

    def test_trailing_newline(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "trailing.jsonl"
        content = '{"type": "user"}\n{"type": "assistant"}\n\n'
        file_path.write_text(content)

        tf = TranscriptFile(file_path)
        items = list(item for item in tf)

        assert len(items) == 2

    def test_file_with_only_whitespace(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "whitespace_only.jsonl"
        file_path.write_text("   \n  \n\t\n")

        tf = TranscriptFile(file_path)
        items = list(item for item in tf)

        assert items == []


class TestTranscriptFileLazyLoading:
    """Tests for lazy loading behavior and caching."""

    def test_iteration_loads_content_once(
        self,
        transcript_path: pathlib.Path,
    ) -> None:
        """Test that content is loaded once and cached for subsequent iterations."""
        transcript_path.write_text('{"type": "user"}\n{"type": "assistant"}')
        tf = TranscriptFile(transcript_path)

        first_items = list(tf)
        second_items = list(tf)

        assert first_items == second_items
        assert len(first_items) == 2

    def test_property_access_does_not_load(
        self,
        transcript_path: pathlib.Path,
    ) -> None:
        """Test that accessing properties doesn't trigger file loading."""
        transcript_path.write_text('{"type": "test"}')
        tf = TranscriptFile(transcript_path)

        _ = tf.path
        _ = tf.exists
        _ = tf.session_id
        _ = tf.agent_id
        _ = tf.is_subagent

        assert tf._is_loaded is False

    def test_iteration_triggers_load(
        self,
        transcript_path: pathlib.Path,
    ) -> None:
        """Test that iteration triggers file loading."""
        transcript_path.write_text('{"type": "test"}')
        tf = TranscriptFile(transcript_path)

        assert tf._is_loaded is False
        _ = list(tf)
        assert tf._is_loaded is True


class TestTranscriptFileIdentifiers:
    def test_extract_identifiers_session_only(
        self,
        tmp_path: pathlib.Path,
        session_id: uuid.UUID,
    ) -> None:
        file_path = tmp_path / f"{session_id}.jsonl"
        file_path.write_text('{"type": "test"}')

        tf = TranscriptFile(file_path)

        assert tf.session_id == str(session_id)
        assert tf.agent_id is None
        assert tf.is_subagent is False

    def test_extract_identifiers_subagent(
        self,
        subagent_transcript_path: pathlib.Path,
        session_id: uuid.UUID,
        agent_id: str,
    ) -> None:
        subagent_transcript_path.write_text('{"type": "test"}')

        tf = TranscriptFile(subagent_transcript_path)

        assert tf.session_id == str(session_id)
        assert tf.agent_id == agent_id
        assert tf.is_subagent is True

    def test_extract_identifiers_nested_path(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        nested_dir = tmp_path / "some" / "deep" / "path"
        nested_dir.mkdir(parents=True)
        file_path = nested_dir / f"{session_id}.jsonl"
        file_path.write_text('{"type": "test"}')

        tf = TranscriptFile(file_path)

        assert tf.session_id == session_id
        assert tf.agent_id is None
        assert tf.is_subagent is False

    def test_extract_identifiers_invalid_uuid_format(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "not-a-uuid.jsonl"
        file_path.write_text('{"type": "test"}')

        tf = TranscriptFile(file_path)

        assert tf.session_id is None
        assert tf.agent_id is None
        assert tf.is_subagent is False

    def test_extract_identifiers_partial_uuid(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "550e8400-e29b-41d4.jsonl"
        file_path.write_text('{"type": "test"}')

        tf = TranscriptFile(file_path)

        assert tf.session_id is None
        assert tf.agent_id is None

    def test_extract_identifiers_empty_agent_id(
        self,
        tmp_path: pathlib.Path,
        session_id: uuid.UUID,
    ) -> None:
        subagent_dir = tmp_path / str(session_id) / "subagents"
        subagent_dir.mkdir(parents=True)
        file_path = subagent_dir / "agent-.jsonl"
        file_path.write_text('{"type": "test"}')

        tf = TranscriptFile(file_path)

        assert tf.session_id == str(session_id)
        assert tf.agent_id == ""
        assert tf.is_subagent is True

    def test_session_id_property(
        self,
        tmp_path: pathlib.Path,
        session_id: uuid.UUID,
    ) -> None:
        file_path = tmp_path / f"{session_id}.jsonl"
        file_path.write_text('{"type": "user"}')

        tf = TranscriptFile(file_path)

        assert tf.session_id == str(session_id)
        assert isinstance(tf.session_id, str)

    def test_session_id_property_none(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "simple-name.jsonl"
        file_path.write_text('{"type": "user"}')

        tf = TranscriptFile(file_path)

        assert tf.session_id is None

    def test_agent_id_property(
        self,
        subagent_transcript_path: pathlib.Path,
        session_id: uuid.UUID,
        agent_id: str,
    ) -> None:
        subagent_transcript_path.write_text('{"type": "assistant"}')

        tf = TranscriptFile(subagent_transcript_path)

        assert tf.agent_id == agent_id
        assert isinstance(tf.agent_id, str)

    def test_agent_id_property_none_for_main_session(
        self,
        tmp_path: pathlib.Path,
        session_id: uuid.UUID,
    ) -> None:
        file_path = tmp_path / f"{session_id}.jsonl"
        file_path.write_text('{"type": "user"}')

        tf = TranscriptFile(file_path)

        assert tf.agent_id is None

    def test_is_subagent_property_true(
        self,
        subagent_transcript_path: pathlib.Path,
    ) -> None:
        subagent_transcript_path.write_text('{"type": "test"}')

        tf = TranscriptFile(subagent_transcript_path)

        assert tf.is_subagent is True

    def test_is_subagent_property_false(
        self,
        tmp_path: pathlib.Path,
        session_id: uuid.UUID,
    ) -> None:
        file_path = tmp_path / f"{session_id}.jsonl"
        file_path.write_text('{"type": "test"}')

        tf = TranscriptFile(file_path)

        assert tf.is_subagent is False

    def test_is_subagent_property_false_no_uuid(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "random-file.jsonl"
        file_path.write_text('{"type": "test"}')

        tf = TranscriptFile(file_path)

        assert tf.is_subagent is False

    def test_extract_identifiers_uppercase_uuid(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "550E8400-E29B-41D4-A716-446655440000"
        file_path = tmp_path / f"{session_id}.jsonl"
        file_path.write_text('{"type": "test"}')

        tf = TranscriptFile(file_path)

        assert tf.session_id == session_id
        assert tf.agent_id is None

    def test_extract_identifiers_mixed_case_uuid(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        session_id = "550E8400-e29b-41d4-A716-446655440000"
        file_path = tmp_path / f"{session_id}.jsonl"
        file_path.write_text('{"type": "test"}')

        tf = TranscriptFile(file_path)

        assert tf.session_id == session_id
        assert tf.agent_id is None

    def test_extract_identifiers_invalid_agent_id(
        self,
        tmp_path: pathlib.Path,
        session_id: uuid.UUID,
    ) -> None:
        agent_id = "task-worker-123_v2.0"
        subagent_dir = tmp_path / str(session_id) / "subagents"
        subagent_dir.mkdir(parents=True)
        file_path = subagent_dir / f"agent-{agent_id}.jsonl"
        file_path.write_text('{"type": "test"}')

        tf = TranscriptFile(file_path)

        assert tf.session_id == str(session_id)
        assert tf.agent_id == agent_id
        assert tf.is_subagent is True


class TestTranscriptFileHashAndEq:
    def test_hash_same_path(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "test.jsonl"
        file_path.write_text('{"type": "test"}')

        tf1 = TranscriptFile(file_path)
        tf2 = TranscriptFile(file_path)

        assert hash(tf1) == hash(tf2)

    def test_hash_different_path(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path1 = tmp_path / "test1.jsonl"
        file_path2 = tmp_path / "test2.jsonl"
        file_path1.write_text('{"type": "test"}')
        file_path2.write_text('{"type": "test"}')

        tf1 = TranscriptFile(file_path1)
        tf2 = TranscriptFile(file_path2)

        assert hash(tf1) != hash(tf2)

    def test_eq_same_path(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "test.jsonl"
        file_path.write_text('{"type": "test"}')

        tf1 = TranscriptFile(file_path)
        tf2 = TranscriptFile(file_path)

        assert tf1 == tf2

    def test_eq_different_path(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path1 = tmp_path / "test1.jsonl"
        file_path2 = tmp_path / "test2.jsonl"
        file_path1.write_text('{"type": "test"}')
        file_path2.write_text('{"type": "test"}')

        tf1 = TranscriptFile(file_path1)
        tf2 = TranscriptFile(file_path2)

        assert tf1 != tf2

    def test_eq_with_non_transcript_file(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "test.jsonl"
        file_path.write_text('{"type": "test"}')

        tf = TranscriptFile(file_path)

        assert tf != "test.jsonl"
        assert tf != 123
        assert tf != {"path": str(file_path)}

    def test_can_use_in_set(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path1 = tmp_path / "test1.jsonl"
        file_path2 = tmp_path / "test2.jsonl"
        file_path1.write_text('{"type": "test"}')
        file_path2.write_text('{"type": "test"}')

        tf1 = TranscriptFile(file_path1)
        tf2 = TranscriptFile(file_path2)
        tf3 = TranscriptFile(file_path1)  # Same as tf1

        transcript_set = {tf1, tf2, tf3}

        assert len(transcript_set) == 2
        assert tf1 in transcript_set
        assert tf2 in transcript_set
        assert tf3 in transcript_set

    def test_can_use_as_dict_key(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path1 = tmp_path / "test1.jsonl"
        file_path2 = tmp_path / "test2.jsonl"
        file_path1.write_text('{"type": "test"}')
        file_path2.write_text('{"type": "test"}')

        tf1 = TranscriptFile(file_path1)
        tf2 = TranscriptFile(file_path2)

        transcript_dict = {tf1: "first", tf2: "second"}

        assert transcript_dict[tf1] == "first"
        assert transcript_dict[tf2] == "second"

    def test_set_operations(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path1 = tmp_path / "test1.jsonl"
        file_path2 = tmp_path / "test2.jsonl"
        file_path3 = tmp_path / "test3.jsonl"
        file_path1.write_text('{"type": "test"}')
        file_path2.write_text('{"type": "test"}')
        file_path3.write_text('{"type": "test"}')

        tf1 = TranscriptFile(file_path1)
        tf2 = TranscriptFile(file_path2)
        tf3 = TranscriptFile(file_path3)

        set1 = {tf1, tf2}
        set2 = {tf2, tf3}

        union = set1 | set2
        assert len(union) == 3

        intersection = set1 & set2
        assert len(intersection) == 1
        assert tf2 in intersection

        difference = set1 - set2
        assert len(difference) == 1
        assert tf1 in difference
        assert tf2 not in difference

    def test_hash_stability(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "test.jsonl"
        file_path.write_text('{"type": "test"}')

        tf = TranscriptFile(file_path)

        hash1 = hash(tf)
        hash2 = hash(tf)
        hash3 = hash(tf)

        assert hash1 == hash2 == hash3

    def test_eq_reflexive(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "test.jsonl"
        file_path.write_text('{"type": "test"}')

        tf = TranscriptFile(file_path)

        assert tf == tf

    def test_eq_symmetric(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "test.jsonl"
        file_path.write_text('{"type": "test"}')

        tf1 = TranscriptFile(file_path)
        tf2 = TranscriptFile(file_path)

        assert tf1 == tf2
        assert tf2 == tf1

    def test_eq_transitive(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "test.jsonl"
        file_path.write_text('{"type": "test"}')

        tf1 = TranscriptFile(file_path)
        tf2 = TranscriptFile(file_path)
        tf3 = TranscriptFile(file_path)

        assert tf1 == tf2
        assert tf2 == tf3
        assert tf1 == tf3
