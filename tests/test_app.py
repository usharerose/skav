#!/usr/bin/env python3
"""
Unit tests for skav.app module
"""

import io
import json
from typing import Any

import pytest

from skav.app import main, parse_cmd_args


class TestParseCmdArgs:
    def test_parse_default_args(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr("sys.argv", ["skav"])
        args = parse_cmd_args()
        assert args.debug is False

    def test_parse_with_debug_flag(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr("sys.argv", ["skav", "--debug"])
        args = parse_cmd_args()
        assert args.debug is True


class TestMain:
    def test_main_with_session_start_event(
        self,
        session_start_event_input: dict[str, Any],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mock_stdin = io.StringIO(json.dumps(session_start_event_input))
        monkeypatch.setattr("sys.stdin", mock_stdin)

        def mock_exit(code: int) -> None:
            raise SystemExit(code)

        monkeypatch.setattr("sys.exit", mock_exit)

        with pytest.raises(SystemExit) as exc_info:
            main(debug=False)

        assert exc_info.value.code == 0

    def test_main_with_user_prompt_event(
        self,
        user_prompt_event_input: dict[str, Any],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mock_stdin = io.StringIO(json.dumps(user_prompt_event_input))
        monkeypatch.setattr("sys.stdin", mock_stdin)

        def mock_exit(code: int) -> None:
            raise SystemExit(code)

        monkeypatch.setattr("sys.exit", mock_exit)

        with pytest.raises(SystemExit) as exc_info:
            main(debug=False)

        assert exc_info.value.code == 0

    def test_main_with_invalid_json(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mock_stdin = io.StringIO("invalid json {")
        monkeypatch.setattr("sys.stdin", mock_stdin)

        def mock_exit(code: int) -> None:
            raise SystemExit(code)

        monkeypatch.setattr("sys.exit", mock_exit)

        # Current implementation does not handle JSON decode errors
        # Expecting json.JSONDecodeError to be raised
        with pytest.raises(json.JSONDecodeError):
            main(debug=False)

    def test_main_debug_mode(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        event_input: dict[str, Any] = {
            "session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            "transcript_path": "/path/to/transcript/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.jsonl",
            "cwd": "/path/to/repository",
            "hook_event_name": "SessionStart",
            "source": "startup",
            "model": "claude-sonnet-4-5-20260212",
        }

        mock_stdin = io.StringIO(json.dumps(event_input))
        monkeypatch.setattr("sys.stdin", mock_stdin)

        def mock_exit(code: int) -> None:
            raise SystemExit(code)

        monkeypatch.setattr("sys.exit", mock_exit)

        with pytest.raises(SystemExit) as exc_info:
            main(debug=True)

        assert exc_info.value.code == 0

    def test_main_with_pre_tool_use_event(
        self,
        pre_tool_use_event_input: dict[str, Any],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mock_stdin = io.StringIO(json.dumps(pre_tool_use_event_input))
        monkeypatch.setattr("sys.stdin", mock_stdin)

        def mock_exit(code: int) -> None:
            raise SystemExit(code)

        monkeypatch.setattr("sys.exit", mock_exit)

        with pytest.raises(SystemExit) as exc_info:
            main(debug=False)

        assert exc_info.value.code == 0

    def test_main_with_permission_request_event(
        self,
        permission_request_event_input: dict[str, Any],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mock_stdin = io.StringIO(json.dumps(permission_request_event_input))
        monkeypatch.setattr("sys.stdin", mock_stdin)

        def mock_exit(code: int) -> None:
            raise SystemExit(code)

        monkeypatch.setattr("sys.exit", mock_exit)

        with pytest.raises(SystemExit) as exc_info:
            main(debug=False)

        assert exc_info.value.code == 0

    def test_main_with_post_tool_use_event(
        self,
        post_tool_use_event_input: dict[str, Any],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mock_stdin = io.StringIO(json.dumps(post_tool_use_event_input))
        monkeypatch.setattr("sys.stdin", mock_stdin)

        def mock_exit(code: int) -> None:
            raise SystemExit(code)

        monkeypatch.setattr("sys.exit", mock_exit)

        with pytest.raises(SystemExit) as exc_info:
            main(debug=False)

        assert exc_info.value.code == 0

    def test_main_with_subagent_stop_event(
        self,
        subagent_stop_event_input: dict[str, Any],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mock_stdin = io.StringIO(json.dumps(subagent_stop_event_input))
        monkeypatch.setattr("sys.stdin", mock_stdin)

        def mock_exit(code: int) -> None:
            raise SystemExit(code)

        monkeypatch.setattr("sys.exit", mock_exit)

        with pytest.raises(SystemExit) as exc_info:
            main(debug=False)

        assert exc_info.value.code == 0

    def test_main_with_stop_event(
        self,
        stop_event_input: dict[str, Any],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mock_stdin = io.StringIO(json.dumps(stop_event_input))
        monkeypatch.setattr("sys.stdin", mock_stdin)

        def mock_exit(code: int) -> None:
            raise SystemExit(code)

        monkeypatch.setattr("sys.exit", mock_exit)

        with pytest.raises(SystemExit) as exc_info:
            main(debug=False)

        assert exc_info.value.code == 0
