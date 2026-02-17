#!/usr/bin/env python3
"""
Unit tests for TranscriptFile
"""

import json
import os
import pathlib

import pytest

from vibehist.core.transcript_file import TranscriptFile


class TestTranscriptFileInit:
    def test_init_with_valid_extension(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "test.jsonl"
        file_path.write_text("")

        tf = TranscriptFile(file_path)
        assert tf.path == str(file_path)
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
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = pathlib.Path(tmp_path) / "test.jsonl"
        file_path.write_text("")

        tf = TranscriptFile(file_path)
        assert tf.path == str(file_path)

    def test_init_normalizes_path(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "test.jsonl"
        file_path.write_text("{}\n")

        os.chdir(tmp_path)

        tf = TranscriptFile("test.jsonl")
        assert tf.path == str(file_path)


class TestTranscriptFileProperties:
    def test_exists_property_true(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "test.jsonl"
        file_path.write_text("{}")

        tf = TranscriptFile(file_path)
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
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "test.jsonl"
        file_path.write_text("")

        tf = TranscriptFile(file_path)
        assert tf.path == str(file_path)
        assert isinstance(tf.path, str)


class TestTranscriptFileIterItems:
    def test_iter_items_empty_file(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "empty.jsonl"
        file_path.write_text("")

        tf = TranscriptFile(file_path)
        items = list(tf.iter_items())

        assert items == []

    def test_iter_items_single_line(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "single.jsonl"
        data = {"type": "user", "content": "hello"}
        file_path.write_text(json.dumps(data))

        tf = TranscriptFile(file_path)
        items = list(tf.iter_items())

        assert len(items) == 1
        actual, *_ = items
        assert actual == data

    def test_iter_items_multiple_lines(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "multiple.jsonl"
        lines = [
            {"type": "user", "content": "hello"},
            {"type": "assistant", "content": "hi"},
            {"type": "user", "content": "bye"},
        ]
        file_path.write_text("\n".join(json.dumps(line) for line in lines))

        tf = TranscriptFile(file_path)
        items = list(tf.iter_items())

        assert len(items) == 3
        first, second, third = items
        assert first["type"] == "user"
        assert second["type"] == "assistant"
        assert third["content"] == "bye"

    def test_iter_items_skip_empty_lines(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "with_empty.jsonl"
        content = '\n\n{"type": "user"}\n\n\n{"type": "assistant"}\n\n'
        file_path.write_text(content)

        tf = TranscriptFile(file_path)
        items = list(tf.iter_items())

        assert len(items) == 2
        assert items[0]["type"] == "user"
        assert items[1]["type"] == "assistant"

    def test_iter_items_skip_whitespace_lines(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "whitespace.jsonl"
        content = '{"type": "user"}\n   \n\t\n{"type": "assistant"}\n'
        file_path.write_text(content)

        tf = TranscriptFile(file_path)
        items = list(tf.iter_items())

        assert len(items) == 2

    def test_iter_items_malformed_json(
        self,
        tmp_path: pathlib.Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        file_path = tmp_path / "malformed.jsonl"
        content = '{"type": "user"}\nnot json\n{"type": "assistant"}'
        file_path.write_text(content)

        tf = TranscriptFile(file_path)
        items = list(tf.iter_items())

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
            list(tf.iter_items())

    def test_iter_items_preserves_data_types(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "types.jsonl"
        data = {
            "string": "text",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "null": None,
            "array": [1, 2, 3],
            "nested": {"key": "value"},
        }
        file_path.write_text(json.dumps(data))

        tf = TranscriptFile(file_path)
        items = list(tf.iter_items())

        assert len(items) == 1
        actual, *_ = items
        assert actual["string"] == "text"
        assert actual["number"] == 42
        assert actual["float"] == 3.14
        assert actual["bool"] is True
        assert actual["null"] is None
        assert actual["array"] == [1, 2, 3]
        assert actual["nested"] == {"key": "value"}

    def test_iter_items_lazy_evaluation(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "lazy.jsonl"
        lines = [{"type": f"message_{i}"} for i in range(100)]
        file_path.write_text("\n".join(json.dumps(line) for line in lines))

        tf = TranscriptFile(file_path)

        iterator = tf.iter_items()
        assert tf._items is None

        first_ten = []
        for i, item in enumerate(iterator):
            if i >= 10:
                break
            first_ten.append(item)

        assert len(first_ten) == 10
        first, *_ = first_ten
        assert first["type"] == "message_0"


class TestTranscriptFileLoad:
    def test_load_empty_file(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "empty.jsonl"
        file_path.write_text("")

        tf = TranscriptFile(file_path)
        items = tf.load()

        assert items == []
        assert isinstance(items, list)

    def test_load_with_valid_data(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "data.jsonl"
        lines = [
            {"type": "user", "id": 1},
            {"type": "assistant", "id": 2},
            {"type": "user", "id": 3},
        ]
        file_path.write_text("\n".join(json.dumps(line) for line in lines))

        tf = TranscriptFile(file_path)
        items = tf.load()

        assert len(items) == 3
        first, _, third = items
        assert first["id"] == 1
        assert third["id"] == 3

    def test_load_force_reload(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "force.jsonl"
        file_path.write_text('{"type": "user"}\n')

        tf = TranscriptFile(file_path)

        items1 = tf.load()
        assert len(items1) == 1

        file_path.write_text('{"type": "user"}\n{"type": "assistant"}\n')

        items_cached = tf.load(force=False)
        assert len(items_cached) == 1

        items2 = tf.load(force=True)
        assert len(items2) == 2
        assert items1 is not items2

    def test_load_after_iter_items(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "mixed.jsonl"
        file_path.write_text('{"type": "user"}\n{"type": "assistant"}\n')

        tf = TranscriptFile(file_path)

        iter_items = list(tf.iter_items())
        assert len(iter_items) == 2

        loaded_items = tf.load()
        assert len(loaded_items) == 2
        assert loaded_items == iter_items

    def test_load_malformed_json_skipped(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "malformed.jsonl"
        content = '{"type": "user"}\ninvalid\n{"type": "assistant"}'
        file_path.write_text(content)

        tf = TranscriptFile(file_path)
        items = tf.load()

        assert len(items) == 2
        first, second = items
        assert first["type"] == "user"
        assert second["type"] == "assistant"


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
        items = list(tf.iter_items())

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
        items = list(tf.iter_items())

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
        items = list(tf.iter_items())

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
        items = list(tf.iter_items())

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
        items = list(tf.iter_items())

        assert len(items) == 2

    def test_file_with_only_whitespace(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "whitespace_only.jsonl"
        file_path.write_text("   \n  \n\t\n")

        tf = TranscriptFile(file_path)
        items = list(tf.iter_items())

        assert items == []
