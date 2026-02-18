#!/usr/bin/env python3
"""
Unit tests for ProjectWorkspace
"""

import json
import os
import pathlib
import uuid

import pytest

from vibehist.core.project_workspace import ProjectWorkspace

USER_HOME = "/home/user"


class TestInit:
    def test_init_with_default_path(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        os.makedirs(os.path.join(str(tmp_path), ".claude/projects"), exist_ok=True)

        workspace = ProjectWorkspace()
        assert str(workspace) == os.path.join(str(tmp_path), ".claude/projects")

    def test_init_with_custom_path(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))

        custom_path = tmp_path / "custom" / "workspace"
        custom_path.mkdir(parents=True)

        workspace = ProjectWorkspace(str(custom_path))
        assert str(workspace) == str(custom_path)

    def test_init_with_tilde_expansion(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        os.makedirs(os.path.join(str(tmp_path), ".claude/projects"), exist_ok=True)

        workspace = ProjectWorkspace("~/.claude/projects")
        assert str(workspace) == os.path.join(str(tmp_path), ".claude/projects")

    def test_init_with_nonexistent_path(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))

        with pytest.raises(FileNotFoundError, match="doesn't exist"):
            ProjectWorkspace("/nonexistent/path")

    def test_init_with_file_instead_of_directory(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))

        file_path = tmp_path / "not_a_directory"
        file_path.write_text("")

        with pytest.raises(NotADirectoryError, match="is not a directory"):
            ProjectWorkspace(str(file_path))

    def test_str_method(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))

        custom_path = tmp_path / "workspace"
        custom_path.mkdir(parents=True)

        workspace = ProjectWorkspace(str(custom_path))
        assert str(workspace) == str(custom_path)
        assert isinstance(str(workspace), str)


class TestIterProjectStorages:
    def test_iter_project_storages_empty_workspace(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        os.makedirs(os.path.join(str(tmp_path), ".claude/projects"), exist_ok=True)

        workspace = ProjectWorkspace()
        projects = list(workspace.iter_project_storages())

        assert projects == []
        assert isinstance(projects, list)

    def test_iter_project_storages_single_project(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))

        project_dir = tmp_path / ".claude" / "projects" / "-home-user-workspace-project"
        project_dir.mkdir(parents=True)

        session_id = uuid.uuid4()
        session_file = project_dir / f"{session_id}.jsonl"
        session_file.write_text('{"type": "test"}')

        workspace = ProjectWorkspace()
        projects = list(workspace.iter_project_storages())

        assert len(projects) == 1

    def test_iter_project_storages_multiple_projects(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))

        projects_base = tmp_path / ".claude" / "projects"
        projects_base.mkdir(parents=True)

        for i in range(3):
            project_dir = projects_base / f"-home-user-workspace-project{i}"
            project_dir.mkdir(parents=True)

            session_id = uuid.uuid4()
            session_file = project_dir / f"{session_id}.jsonl"
            session_file.write_text(f'{{"type": "project{i}"}}')

        workspace = ProjectWorkspace()
        projects = list(workspace.iter_project_storages())

        assert len(projects) == 3

    def test_iter_project_storages_ignores_non_directories(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))

        projects_base = tmp_path / ".claude" / "projects"
        projects_base.mkdir(parents=True)

        project_dir = projects_base / "-home-user-workspace-project"
        project_dir.mkdir(parents=True)
        session_file = project_dir / f"{uuid.uuid4()}.jsonl"
        session_file.write_text('{"type": "test"}')

        (projects_base / "not_a_directory.txt").write_text("test")

        workspace = ProjectWorkspace()
        projects = list(workspace.iter_project_storages())

        assert len(projects) == 1

    def test_iter_project_storages_ignores_non_standard_names(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))

        projects_base = tmp_path / ".claude" / "projects"
        projects_base.mkdir(parents=True)

        standard_project = projects_base / "-home-user-workspace-project"
        standard_project.mkdir(parents=True)
        session_file = standard_project / f"{uuid.uuid4()}.jsonl"
        session_file.write_text('{"type": "standard"}')

        non_standard_dir = projects_base / "non_standard_project"
        non_standard_dir.mkdir(parents=True)
        session_file2 = non_standard_dir / f"{uuid.uuid4()}.jsonl"
        session_file2.write_text('{"type": "non_standard"}')

        workspace = ProjectWorkspace()
        with pytest.raises(
            ValueError, match="Storage name must start with '-': non_standard_project"
        ):
            list(workspace.iter_project_storages())

    def test_iter_project_storages_lazy_loading(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))

        projects_base = tmp_path / ".claude" / "projects"
        projects_base.mkdir(parents=True)

        project_dir = projects_base / "-home-user-workspace-project"
        project_dir.mkdir(parents=True)
        session_file = project_dir / f"{uuid.uuid4()}.jsonl"
        session_file.write_text('{"type": "test"}')

        workspace = ProjectWorkspace()

        assert workspace._project_storage_mapping is None

        projects1 = list(workspace.iter_project_storages())
        assert len(projects1) == 1
        assert workspace._project_storage_mapping is not None

        projects2 = list(workspace.iter_project_storages())
        assert len(projects2) == 1

    def test_iter_project_storages_with_sessions(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))

        projects_base = tmp_path / ".claude" / "projects"
        projects_base.mkdir(parents=True)

        project_dir = projects_base / "-home-user-workspace-project"
        project_dir.mkdir(parents=True)

        session_ids = [uuid.uuid4() for _ in range(3)]
        for session_id in session_ids:
            session_file = project_dir / f"{session_id}.jsonl"
            session_file.write_text(json.dumps({"type": "test", "id": str(session_id)}))

        workspace = ProjectWorkspace()
        projects = list(workspace.iter_project_storages())

        assert len(projects) == 1
        project = projects[0]
        assert len(project.sessions) == 3


class TestGetProjectStorage:
    def test_get_project_storage_by_storage_name(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))

        projects_base = tmp_path / ".claude" / "projects"
        projects_base.mkdir(parents=True)

        storage_name = "-home-user-workspace-project"
        project_dir = projects_base / storage_name
        project_dir.mkdir(parents=True)

        session_id = uuid.uuid4()
        session_file = project_dir / f"{session_id}.jsonl"
        session_file.write_text('{"type": "test"}')

        workspace = ProjectWorkspace()
        project = workspace.get_project_storage(storage_name)

        assert project is not None
        assert project.storage_path.endswith(storage_name)

    def test_get_project_storage_not_found(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))
        os.makedirs(os.path.join(str(tmp_path), ".claude/projects"), exist_ok=True)

        workspace = ProjectWorkspace()
        project = workspace.get_project_storage("-nonexistent-project")

        assert project is None

    def test_get_project_storage_triggers_lazy_loading(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))

        projects_base = tmp_path / ".claude" / "projects"
        projects_base.mkdir(parents=True)

        storage_name = "-home-user-workspace-project"
        project_dir = projects_base / storage_name
        project_dir.mkdir(parents=True)

        session_id = uuid.uuid4()
        session_file = project_dir / f"{session_id}.jsonl"
        session_file.write_text('{"type": "test"}')

        workspace = ProjectWorkspace()

        assert workspace._project_storage_mapping is None

        project = workspace.get_project_storage(storage_name)

        assert project is not None
        assert workspace._project_storage_mapping is not None

    def test_get_project_storage_returns_cached(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))

        projects_base = tmp_path / ".claude" / "projects"
        projects_base.mkdir(parents=True)

        storage_name = "-home-user-workspace-project"
        project_dir = projects_base / storage_name
        project_dir.mkdir(parents=True)

        session_id = uuid.uuid4()
        session_file = project_dir / f"{session_id}.jsonl"
        session_file.write_text('{"type": "test"}')

        workspace = ProjectWorkspace()

        project1 = workspace.get_project_storage(storage_name)
        project2 = workspace.get_project_storage(storage_name)

        assert project1 is project2


class TestMultipleProjects:
    def test_workspace_with_multiple_projects_with_sessions(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))

        projects_base = tmp_path / ".claude" / "projects"
        projects_base.mkdir(parents=True)

        project_configs = [
            ("-project-a", 2),
            ("-project-b", 3),
            ("-project-c", 1),
        ]

        for storage_name, session_count in project_configs:
            project_dir = projects_base / storage_name
            project_dir.mkdir(parents=True, exist_ok=True)

            for _ in range(session_count):
                session_id = uuid.uuid4()
                session_file = project_dir / f"{session_id}.jsonl"
                session_file.write_text(json.dumps({"type": "test", "project": storage_name}))

        workspace = ProjectWorkspace()
        projects = list(workspace.iter_project_storages())

        assert len(projects) == 3

        session_counts = {os.path.split(p.storage_path)[-1]: len(p.sessions) for p in projects}
        assert session_counts["-project-a"] == 2
        assert session_counts["-project-b"] == 3
        assert session_counts["-project-c"] == 1

    def test_get_specific_project_from_multiple(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path,
    ) -> None:
        monkeypatch.setenv("HOME", str(tmp_path))

        projects_base = tmp_path / ".claude" / "projects"
        projects_base.mkdir(parents=True)

        for i in range(3):
            project_dir = projects_base / f"-project-{i}"
            project_dir.mkdir(parents=True)

            session_id = uuid.uuid4()
            session_file = project_dir / f"{session_id}.jsonl"
            session_file.write_text(json.dumps({"type": "test", "project": i}))

        workspace = ProjectWorkspace()

        project = workspace.get_project_storage("-project-1")
        assert project is not None
        assert project.storage_path.endswith("-project-1")

        project_0 = workspace.get_project_storage("-project-0")
        project_2 = workspace.get_project_storage("-project-2")
        assert project_0 is not None
        assert project_2 is not None
