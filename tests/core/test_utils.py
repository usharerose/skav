#!/usr/bin/env python3
"""
Unit tests for utils
"""

import os
import pathlib

import pytest

from vibehist.utils import normalize_path

USER_HOME = "/home/user"


class TestNormalizeAbsolutePath:
    def test_absolute_path_no_changes(self) -> None:
        path = "/usr/local/bin"
        result = normalize_path(path)
        assert result == "/usr/local/bin"

    def test_absolute_path_with_trailing_slash(self) -> None:
        path = "/usr/local/bin/"
        result = normalize_path(path)
        assert result == "/usr/local/bin"

    def test_absolute_path_with_dots(self) -> None:
        path = "/usr/local/../bin"
        result = normalize_path(path)
        assert result == "/usr/bin"


class TestNormalizeUserPath:
    def test_user_home_expansion(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("HOME", USER_HOME)

        path = "~/workspace/project"
        result = normalize_path(path)
        assert result == "/home/user/workspace/project"

    def test_user_home_with_relative(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        os.chdir(tmp_path)

        path = "~/../other"
        result = normalize_path(path)
        expected = os.path.normpath(os.path.join(tmp_path, "..", "other"))
        assert result == expected

    def test_user_home_at_end(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("HOME", USER_HOME)

        path = "/var/~"
        result = normalize_path(path)
        assert result == "/var/~"


class TestNormalizeEnvVars:
    def test_expand_simple_env_var(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("PROJECT_DIR", "/opt/project")

        path = "$PROJECT_DIR/src"
        result = normalize_path(path)
        assert result == "/opt/project/src"

    def test_expand_multiple_env_vars(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("HOME", USER_HOME)
        monkeypatch.setenv("PROJECT", "myproject")

        path = "$HOME/$PROJECT"
        result = normalize_path(path)
        assert result == "/home/user/myproject"

    def test_expand_env_var_with_braces(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("PROJECT", "/opt/project")

        path = "${PROJECT}/bin"
        result = normalize_path(path)
        assert result == "/opt/project/bin"

    def test_expand_empty_env_var(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.delenv("UNDEFINED_VAR", raising=False)
        os.chdir(tmp_path)

        path = "$UNDEFINED_VAR/path"
        result = normalize_path(path)
        assert result == os.path.join(tmp_path, "$UNDEFINED_VAR/path")

    def test_expand_env_var_in_middle(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("APP", "myapp")

        path = "/opt/$APP/data"
        result = normalize_path(path)
        assert result == "/opt/myapp/data"


class TestNormalizeRelativePath:
    def test_relative_path_from_root(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        os.chdir(tmp_path)

        path = "relative/path"
        result = normalize_path(path)
        assert os.path.isabs(result)
        assert "relative/path" in result

    def test_relative_path_with_dots(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        os.chdir(tmp_path)

        (tmp_path / "dir1").mkdir()
        path = "dir1/../dir2"
        result = normalize_path(path)
        assert os.path.isabs(result)
        assert result.endswith("/dir2")

    def test_relative_path_with_current_dir(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        os.chdir(tmp_path)

        path = "./config.yml"
        result = normalize_path(path)
        assert os.path.isabs(result)
        assert result.endswith("/config.yml")
        # normpath removed .
        assert "/./" not in result


class TestNormalizePathLike:
    def test_pathlib_path_object(self) -> None:
        path = pathlib.Path("/usr/local/bin")
        result = normalize_path(path)
        assert result == "/usr/local/bin"

    def test_pathlib_path_with_tilde(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("HOME", "/test/user")

        path = pathlib.Path("~/project")
        result = normalize_path(path)
        assert result == "/test/user/project"


class TestNormalizeCombinations:
    def test_user_and_env_vars(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("HOME", "/home/user")
        monkeypatch.setenv("WORKSPACE", "workspace")

        path = "~/$WORKSPACE/project"
        result = normalize_path(path)
        assert result == "/home/user/workspace/project"

    def test_relative_with_env_var(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("DATA", "data")
        os.chdir(tmp_path)

        path = "$DATA/../config"
        result = normalize_path(path)
        expected = os.path.normpath(os.path.join(tmp_path, "data", "..", "config"))
        assert result == expected

    def test_complex_path(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setenv("SUBDIR", "subdir")

        os.chdir(tmp_path)

        path = "~/$SUBDIR/./../config.yml"
        result = normalize_path(path)
        expected = os.path.normpath(os.path.join(tmp_path, "subdir", "..", "config.yml"))
        assert result == expected


class TestNormalizeEdgeCases:
    def test_empty_string(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        os.chdir(tmp_path)

        result = normalize_path("")
        assert result == str(tmp_path)

    def test_dots_only(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        os.chdir(tmp_path)

        result = normalize_path("..")
        expected = os.path.dirname(tmp_path) if tmp_path != tmp_path.parent else tmp_path
        assert result == expected

    def test_multiple_slashes(self) -> None:
        path = "///usr///local////bin"
        result = normalize_path(path)
        assert result == "/usr/local/bin"

    def test_trailing_slash(self) -> None:
        path = "/usr/local/bin/"
        result = normalize_path(path)
        assert result == "/usr/local/bin"
        assert not result.endswith("/")

    def test_path_with_extra_slashes(self) -> None:
        path = "/usr//local///bin"
        result = normalize_path(path)
        assert result == "/usr/local/bin"
