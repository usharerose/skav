#!/usr/bin/env python3
"""
Unit tests for skav.app module (CLI session rendering)
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from skav.app import main, parse_cmd_args, resolve_storage_path


class TestParseCmdArgs:
    """Test command-line argument parsing."""

    def test_parse_default_args(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test parsing with minimal required args."""
        monkeypatch.setattr("sys.argv", ["skav", "abc123-session-id"])
        args = parse_cmd_args()

        assert args.project_path == "."
        assert args.session_id == "abc123-session-id"
        assert args.output_path is None

    def test_parse_with_project_path(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test parsing with custom project path."""
        monkeypatch.setattr("sys.argv", ["skav", "-p", "/custom/path", "abc123-session-id"])
        args = parse_cmd_args()

        assert args.project_path == "/custom/path"
        assert args.session_id == "abc123-session-id"

    def test_parse_with_output_path(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test parsing with custom output path."""
        monkeypatch.setattr("sys.argv", ["skav", "abc123-session-id", "-o", "output.html"])
        args = parse_cmd_args()

        assert args.session_id == "abc123-session-id"
        assert args.output_path == "output.html"

    def test_parse_with_all_options(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test parsing with all options."""
        monkeypatch.setattr(
            "sys.argv",
            ["skav", "-p", "/custom/path", "abc123-session-id", "-o", "output.html"],
        )
        args = parse_cmd_args()

        assert args.project_path == "/custom/path"
        assert args.session_id == "abc123-session-id"
        assert args.output_path == "output.html"

    def test_parse_missing_session_id(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that session_id is required."""
        monkeypatch.setattr("sys.argv", ["skav"])
        with pytest.raises(SystemExit) as exc_info:
            parse_cmd_args()
        assert exc_info.value.code == 2


class TestResolveStoragePath:
    """Test storage path resolution."""

    def test_resolve_current_directory(self, tmp_path: Path) -> None:
        """Test resolving current directory path."""
        # Create a mock .claude/projects structure
        with patch("skav.app.ProjectStoragePath") as mock_psp:
            mock_instance = MagicMock()
            mock_instance.exists.return_value = True
            mock_psp.encode.return_value = mock_instance

            result = resolve_storage_path(str(tmp_path))

            assert result == mock_instance
            mock_psp.encode.assert_called_once_with(str(tmp_path))

    def test_resolve_nonexistent_path(self, tmp_path: Path) -> None:
        """Test resolving non-existent path raises error."""
        with patch("skav.app.ProjectStoragePath") as mock_psp:
            mock_instance = MagicMock()
            mock_instance.exists.return_value = False
            mock_psp.encode.return_value = mock_instance
            mock_psp.encode.return_value = mock_instance

            with pytest.raises(FileNotFoundError) as exc_info:
                resolve_storage_path(str(tmp_path))

            assert "Project storage not found" in str(exc_info.value)


class TestMain:
    """Test main CLI function."""

    @patch("skav.app.HTMLRenderer")
    @patch("skav.app.ProjectStorage")
    @patch("skav.app.ProjectStoragePath")
    def test_main_successful_render(
        self,
        mock_psp: MagicMock,
        mock_storage: MagicMock,
        mock_renderer: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test successful session rendering."""
        # Setup mocks
        mock_storage_path = MagicMock()
        mock_storage_path.exists.return_value = True
        mock_psp.encode.return_value = mock_storage_path

        mock_project = MagicMock()
        mock_storage.return_value = mock_project

        mock_session = MagicMock()
        mock_project.get_session.return_value = mock_session

        mock_renderer_instance = MagicMock()
        mock_renderer.return_value = mock_renderer_instance

        output_file = tmp_path / "output.html"

        # Create args namespace
        from argparse import Namespace

        args = Namespace(
            project_path=str(tmp_path),
            session_id="abc123-session-id",
            output_path=str(output_file),
        )

        # Run main
        result = main(args)

        # Verify
        assert result == 0
        mock_psp.encode.assert_called_once_with(str(tmp_path))
        mock_project.get_session.assert_called_once_with("abc123-session-id")
        mock_renderer_instance.render_to_file.assert_called_once()

    @patch("skav.app.ProjectStorage")
    @patch("skav.app.resolve_storage_path")
    def test_main_session_not_found(
        self,
        mock_resolve: MagicMock,
        mock_storage: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test handling of non-existent session."""
        # Setup mocks
        mock_storage_path = MagicMock()
        mock_resolve.return_value = mock_storage_path

        mock_project = MagicMock()
        mock_storage.return_value = mock_project
        mock_project.get_session.return_value = None
        mock_project.sessions = []

        # Create args namespace
        from argparse import Namespace

        args = Namespace(
            project_path=str(tmp_path),
            session_id="nonexistent-session",
            output_path=None,
        )

        # Run main
        result = main(args)

        # Verify
        assert result == 1
        mock_project.get_session.assert_called_once_with("nonexistent-session")

    @patch("skav.app.resolve_storage_path")
    def test_main_storage_not_found(
        self,
        mock_resolve: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test handling of non-existent storage."""
        # Setup mock to raise FileNotFoundError
        mock_resolve.side_effect = FileNotFoundError("Storage not found")

        # Create args namespace
        from argparse import Namespace

        args = Namespace(
            project_path=str(tmp_path),
            session_id="abc123-session-id",
            output_path=None,
        )

        # Run main
        result = main(args)

        # Verify
        assert result == 1

    @patch("skav.app.HTMLRenderer")
    @patch("skav.app.ProjectStorage")
    @patch("skav.app.resolve_storage_path")
    def test_main_rendering_error(
        self,
        mock_resolve: MagicMock,
        mock_storage: MagicMock,
        mock_renderer: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test handling of rendering errors."""
        # Setup mocks
        mock_storage_path = MagicMock()
        mock_resolve.return_value = mock_storage_path

        mock_project = MagicMock()
        mock_storage.return_value = mock_project

        mock_session = MagicMock()
        mock_project.get_session.return_value = mock_session

        mock_renderer_instance = MagicMock()
        mock_renderer.return_value = mock_renderer_instance
        mock_renderer_instance.render_to_file.side_effect = Exception("Render error")

        # Create args namespace
        from argparse import Namespace

        args = Namespace(
            project_path=str(tmp_path),
            session_id="abc123-session-id",
            output_path=None,
        )

        # Run main
        result = main(args)

        # Verify - exception should be caught and return 1
        assert result == 1
