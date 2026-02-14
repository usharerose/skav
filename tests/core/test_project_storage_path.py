#!/usr/bin/env python3
"""
Unit tests for ProjectStoragePath
"""

import os
import pathlib

import pytest

from vibehist.core.project_storage_path import ProjectStoragePath

USER_HOME = "/home/user"


class TestEncode:
    def test_encode_absolute_path(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("HOME", USER_HOME)

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        assert storage_path.storage_name == "-home-user-workspace-project"
        assert str(storage_path) == "/home/user/.claude/projects/-home-user-workspace-project"

    def test_encode_user_path(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("HOME", USER_HOME)

        storage_path = ProjectStoragePath.encode("~/workspace/project")
        assert storage_path.storage_name == "-home-user-workspace-project"

    def test_encode_relative_path(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", USER_HOME)

        os.chdir(tmp_path)
        storage_path = ProjectStoragePath.encode("relative/path/to/project")

        project_path = os.path.normpath(os.path.join(tmp_path, "relative/path/to/project"))
        expected = os.path.join(USER_HOME, ".claude/projects", project_path.replace("/", "-"))
        assert str(storage_path) == expected


class TestProperties:
    def test_storage_name_property(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("HOME", USER_HOME)

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        assert storage_path.storage_name == "-home-user-workspace-project"

    def test_workspace_path_property(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("HOME", USER_HOME)

        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        assert storage_path.workspace_path == os.path.expanduser("~/.claude/projects")


class TestExists:
    def test_storage_exists_true(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        expected_storage_path = os.path.join(
            tmp_path, ".claude/projects", "-home-user-workspace-project"
        )
        os.makedirs(expected_storage_path)

        os.chdir(tmp_path)
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        assert storage_path.exists() is True

    def test_storage_exists_false(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        workspace_path = os.path.join(tmp_path, ".claude/projects")
        os.makedirs(workspace_path)

        os.chdir(tmp_path)
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        assert storage_path.exists() is False


class TestValidation:
    def test_storage_name_must_start_with_dash(self) -> None:
        with pytest.raises(ValueError):
            ProjectStoragePath("invalid-name")


class TestToStr:
    def test_str_returns_storage_name(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("HOME", USER_HOME)
        storage_path = ProjectStoragePath.encode("/home/user/workspace/project")
        assert str(storage_path) == "/home/user/.claude/projects/-home-user-workspace-project"
