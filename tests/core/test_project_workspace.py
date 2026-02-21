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


@pytest.fixture(scope="session")
def storage_name() -> str:
    """Provide a fixed storage name for testing."""
    return "-home-user-workspace-project"


@pytest.fixture(scope="session")
def storage_name2() -> str:
    """Provide a second fixed storage name for testing."""
    return "-home-user-workspace-project2"


class TestInit:
    def test_init_with_default_path(
        self,
        tmp_path: pathlib.Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test default path uses home directory."""
        monkeypatch.setenv("HOME", str(tmp_path))
        (tmp_path / ".claude/projects").mkdir(parents=True)

        workspace = ProjectWorkspace()
        assert str(workspace) == str(tmp_path / ".claude/projects")

    def test_init_with_custom_path(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        custom_path = tmp_path / "custom" / "workspace"
        custom_path.mkdir(parents=True)

        workspace = ProjectWorkspace(str(custom_path))
        assert str(workspace) == str(custom_path)

    def test_init_with_tilde_expansion(
        self,
        tmp_path: pathlib.Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that tilde expansion works correctly."""
        monkeypatch.setenv("HOME", str(tmp_path))
        (tmp_path / ".claude/projects").mkdir(parents=True)

        workspace = ProjectWorkspace("~/.claude/projects")
        assert str(workspace) == str(tmp_path / ".claude/projects")

    def test_init_with_nonexistent_path(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        with pytest.raises(FileNotFoundError, match="doesn't exist"):
            ProjectWorkspace(str(tmp_path / "nonexistent" / "path"))

    def test_init_with_file_instead_of_directory(
        self,
        tmp_path: pathlib.Path,
    ) -> None:
        file_path = tmp_path / "not_a_directory"
        file_path.write_text("")

        with pytest.raises(NotADirectoryError, match="is not a directory"):
            ProjectWorkspace(str(file_path))

    def test_init_with_pathlib_object(
        self,
        made_workspace_path: pathlib.Path,
    ) -> None:
        """Test that PathLike objects (pathlib.Path) are supported."""
        workspace = ProjectWorkspace(made_workspace_path)
        assert str(workspace) == str(made_workspace_path)

    def test_init_creates_empty_state(
        self,
        made_workspace_path: pathlib.Path,
    ) -> None:
        """Test that initialization creates empty internal state."""
        workspace = ProjectWorkspace(made_workspace_path)

        assert workspace._project_storage_mapping == {}
        assert workspace._is_loaded is False

    def test_str_method(
        self,
        made_workspace_path: pathlib.Path,
    ) -> None:
        workspace = ProjectWorkspace(made_workspace_path)
        assert str(workspace) == str(made_workspace_path)
        assert isinstance(str(workspace), str)


class TestLoadMethod:
    """Tests for the _load method."""

    def test_load_only_loads_once(
        self,
        made_workspace_path: pathlib.Path,
        storage_name: str,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that workspace is only loaded once."""
        project_dir = made_workspace_path / storage_name
        project_dir.mkdir(parents=True)

        workspace = ProjectWorkspace(made_workspace_path)
        load_count = 0

        original_load = workspace._load

        def counting_load() -> None:
            nonlocal load_count
            load_count += 1
            original_load()

        monkeypatch.setattr(workspace, "_load", counting_load)

        _ = list(workspace.iter_project_storages())
        _ = list(workspace.iter_project_storages())
        _ = list(workspace.iter_project_storages())

        assert load_count == 1

    def test_load_sets_loaded_flag(
        self,
        made_workspace_path: pathlib.Path,
    ) -> None:
        """Test that loading sets the _is_loaded flag."""
        workspace = ProjectWorkspace(made_workspace_path)
        assert workspace._is_loaded is False

        workspace._load()
        assert workspace._is_loaded is True

    def test_load_ignores_non_directories(
        self,
        made_workspace_path: pathlib.Path,
    ) -> None:
        """Test that _load skips non-directory entries."""
        project_dir = made_workspace_path / "-valid-project"
        project_dir.mkdir(parents=True)

        # Create a file in the workspace
        (made_workspace_path / "not_a_directory.txt").write_text("test")

        workspace = ProjectWorkspace(made_workspace_path)
        workspace._load()

        # Should only load the directory, not the file
        assert len(workspace._project_storage_mapping) == 1
        assert "-valid-project" in workspace._project_storage_mapping

    def test_load_handles_invalid_project_names(
        self,
        made_workspace_path: pathlib.Path,
    ) -> None:
        """Test that _load handles projects with invalid names (non-standard)."""
        valid_dir = made_workspace_path / "-valid-project"
        valid_dir.mkdir(parents=True)

        # Create a directory that doesn't match the storage name pattern
        # This will cause ProjectStoragePath to raise ValueError
        invalid_dir = made_workspace_path / "non_standard_project"
        invalid_dir.mkdir(parents=True)

        workspace = ProjectWorkspace(made_workspace_path)

        # Should raise ValueError when trying to create ProjectStoragePath
        with pytest.raises(ValueError, match="Storage name must start with"):
            list(workspace.iter_project_storages())


class TestLazyLoading:
    """Tests for lazy loading behavior."""

    def test_iter_project_storages_triggers_load(
        self,
        made_workspace_path: pathlib.Path,
    ) -> None:
        """Test that iteration triggers loading."""
        workspace = ProjectWorkspace(made_workspace_path)
        assert workspace._is_loaded is False

        _ = list(workspace.iter_project_storages())
        assert workspace._is_loaded is True

    def test_get_project_storage_triggers_load(
        self,
        made_workspace_path: pathlib.Path,
        storage_name: str,
    ) -> None:
        """Test that getting project storage triggers loading."""
        project_dir = made_workspace_path / storage_name
        project_dir.mkdir(parents=True)

        workspace = ProjectWorkspace(made_workspace_path)
        assert workspace._is_loaded is False

        _ = workspace.get_project_storage(storage_name)
        assert workspace._is_loaded is True

    def test_multiple_operations_only_load_once(
        self,
        made_workspace_path: pathlib.Path,
        storage_name: str,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that multiple operations only trigger one load."""
        project_dir = made_workspace_path / storage_name
        project_dir.mkdir(parents=True)

        workspace = ProjectWorkspace(made_workspace_path)
        load_count = 0

        original_load = workspace._load

        def counting_load() -> None:
            nonlocal load_count
            load_count += 1
            original_load()

        monkeypatch.setattr(workspace, "_load", counting_load)

        # Multiple operations should only trigger one load
        _ = workspace.get_project_storage(storage_name)
        _ = list(workspace.iter_project_storages())
        _ = workspace.get_project_storage(storage_name)

        assert load_count == 1


class TestIterProjectStorages:
    def test_iter_project_storages_empty_workspace(
        self,
        made_workspace_path: pathlib.Path,
    ) -> None:
        workspace = ProjectWorkspace(made_workspace_path)
        projects = list(workspace.iter_project_storages())

        assert projects == []
        assert isinstance(projects, list)

    def test_iter_project_storages_single_project(
        self,
        made_workspace_path: pathlib.Path,
        storage_name: str,
    ) -> None:
        project_dir = made_workspace_path / storage_name
        project_dir.mkdir(parents=True)

        session_id = uuid.uuid4()
        session_file = project_dir / f"{session_id}.jsonl"
        session_file.write_text('{"type": "test"}')

        workspace = ProjectWorkspace(made_workspace_path)
        projects = list(workspace.iter_project_storages())

        assert len(projects) == 1

    def test_iter_project_storages_multiple_projects(
        self,
        made_workspace_path: pathlib.Path,
        storage_name: str,
        storage_name2: str,
    ) -> None:
        project_dir1 = made_workspace_path / storage_name
        project_dir1.mkdir(parents=True)

        session_id1 = uuid.uuid4()
        session_file1 = project_dir1 / f"{session_id1}.jsonl"
        session_file1.write_text('{"type": "test"}')

        project_dir2 = made_workspace_path / storage_name2
        project_dir2.mkdir(parents=True)

        session_id2 = uuid.uuid4()
        session_file2 = project_dir2 / f"{session_id2}.jsonl"
        session_file2.write_text('{"type": "test"}')

        project_dir3 = made_workspace_path / "-another-project"
        project_dir3.mkdir(parents=True)

        workspace = ProjectWorkspace(made_workspace_path)
        projects = list(workspace.iter_project_storages())

        assert len(projects) == 3

    def test_iter_project_storages_ignores_non_directories(
        self,
        made_workspace_path: pathlib.Path,
        storage_name: str,
    ) -> None:
        project_dir = made_workspace_path / storage_name
        project_dir.mkdir(parents=True)
        session_file = project_dir / f"{uuid.uuid4()}.jsonl"
        session_file.write_text('{"type": "test"}')

        (made_workspace_path / "not_a_directory.txt").write_text("test")

        workspace = ProjectWorkspace(made_workspace_path)
        projects = list(workspace.iter_project_storages())

        assert len(projects) == 1

    def test_iter_project_storages_uses_cache(
        self,
        made_workspace_path: pathlib.Path,
        storage_name: str,
    ) -> None:
        """Test that multiple iterations use cached data."""
        project_dir = made_workspace_path / storage_name
        project_dir.mkdir(parents=True)
        session_file = project_dir / f"{uuid.uuid4()}.jsonl"
        session_file.write_text('{"type": "test"}')

        workspace = ProjectWorkspace(made_workspace_path)

        first_projects = list(workspace.iter_project_storages())
        assert workspace._is_loaded is True

        second_projects = list(workspace.iter_project_storages())
        assert first_projects == second_projects

    def test_iter_project_storages_with_sessions(
        self,
        made_workspace_path: pathlib.Path,
        storage_name: str,
    ) -> None:
        project_dir = made_workspace_path / storage_name
        project_dir.mkdir(parents=True)

        session_ids = [uuid.uuid4() for _ in range(3)]
        for session_id in session_ids:
            session_file = project_dir / f"{session_id}.jsonl"
            session_file.write_text(json.dumps({"type": "test", "id": str(session_id)}))

        workspace = ProjectWorkspace(made_workspace_path)
        projects = list(workspace.iter_project_storages())

        assert len(projects) == 1
        project = projects[0]
        assert len(project.sessions) == 3


class TestGetProjectStorage:
    def test_get_project_storage_by_storage_name(
        self,
        made_workspace_path: pathlib.Path,
        storage_name: str,
    ) -> None:
        project_dir = made_workspace_path / storage_name
        project_dir.mkdir(parents=True)

        session_id = uuid.uuid4()
        session_file = project_dir / f"{session_id}.jsonl"
        session_file.write_text('{"type": "test"}')

        workspace = ProjectWorkspace(made_workspace_path)
        project = workspace.get_project_storage(storage_name)

        assert project is not None
        assert project.storage_path.endswith(storage_name)

    def test_get_project_storage_not_found(
        self,
        made_workspace_path: pathlib.Path,
    ) -> None:
        workspace = ProjectWorkspace(made_workspace_path)
        project = workspace.get_project_storage("-nonexistent-project")

        assert project is None

    def test_get_project_storage_triggers_lazy_loading(
        self,
        made_workspace_path: pathlib.Path,
        storage_name: str,
    ) -> None:
        project_dir = made_workspace_path / storage_name
        project_dir.mkdir(parents=True)

        session_id = uuid.uuid4()
        session_file = project_dir / f"{session_id}.jsonl"
        session_file.write_text('{"type": "test"}')

        workspace = ProjectWorkspace(made_workspace_path)

        assert workspace._project_storage_mapping == {}

        project = workspace.get_project_storage(storage_name)

        assert project is not None
        assert workspace._project_storage_mapping is not None
        assert storage_name in workspace._project_storage_mapping

    def test_get_project_storage_returns_cached(
        self,
        made_workspace_path: pathlib.Path,
        storage_name: str,
    ) -> None:
        project_dir = made_workspace_path / storage_name
        project_dir.mkdir(parents=True)

        session_id = uuid.uuid4()
        session_file = project_dir / f"{session_id}.jsonl"
        session_file.write_text('{"type": "test"}')

        workspace = ProjectWorkspace(made_workspace_path)

        project1 = workspace.get_project_storage(storage_name)
        project2 = workspace.get_project_storage(storage_name)

        assert project1 is project2

    def test_get_project_storage_after_initial_load(
        self,
        made_workspace_path: pathlib.Path,
        storage_name: str,
    ) -> None:
        """Test getting project after initial load via iter."""
        project_dir = made_workspace_path / storage_name
        project_dir.mkdir(parents=True)

        session_id = uuid.uuid4()
        session_file = project_dir / f"{session_id}.jsonl"
        session_file.write_text('{"type": "test"}')

        workspace = ProjectWorkspace(made_workspace_path)

        # Load via iteration
        _ = list(workspace.iter_project_storages())
        assert workspace._is_loaded is True

        # Get should use cached data
        project = workspace.get_project_storage(storage_name)
        assert project is not None
        assert project.storage_path.endswith(storage_name)


class TestMultipleProjects:
    def test_workspace_with_multiple_projects_with_sessions(
        self,
        made_workspace_path: pathlib.Path,
    ) -> None:
        project_configs = [
            ("-project-a", 2),
            ("-project-b", 3),
            ("-project-c", 1),
        ]

        for storage_name, session_count in project_configs:
            project_dir = made_workspace_path / storage_name
            project_dir.mkdir(parents=True, exist_ok=True)

            for _ in range(session_count):
                session_id = uuid.uuid4()
                session_file = project_dir / f"{session_id}.jsonl"
                session_file.write_text(json.dumps({"type": "test", "project": storage_name}))

        workspace = ProjectWorkspace(made_workspace_path)
        projects = list(workspace.iter_project_storages())

        assert len(projects) == 3

        session_counts = {os.path.split(p.storage_path)[-1]: len(p.sessions) for p in projects}
        assert session_counts["-project-a"] == 2
        assert session_counts["-project-b"] == 3
        assert session_counts["-project-c"] == 1

    def test_get_specific_project_from_multiple(
        self,
        made_workspace_path: pathlib.Path,
    ) -> None:
        for i in range(3):
            project_dir = made_workspace_path / f"-project-{i}"
            project_dir.mkdir(parents=True)

            session_id = uuid.uuid4()
            session_file = project_dir / f"{session_id}.jsonl"
            session_file.write_text(json.dumps({"type": "test", "project": i}))

        workspace = ProjectWorkspace(made_workspace_path)

        project = workspace.get_project_storage("-project-1")
        assert project is not None
        assert project.storage_path.endswith("-project-1")

        project_0 = workspace.get_project_storage("-project-0")
        project_2 = workspace.get_project_storage("-project-2")
        assert project_0 is not None
        assert project_2 is not None

    def test_iter_multiple_projects_correct_ordering(
        self,
        made_workspace_path: pathlib.Path,
    ) -> None:
        """Test that iteration returns all projects consistently."""
        storage_names = ["-project-a", "-project-b", "-project-c"]

        for storage_name in storage_names:
            project_dir = made_workspace_path / storage_name
            project_dir.mkdir(parents=True)

        workspace = ProjectWorkspace(made_workspace_path)

        projects1 = list(workspace.iter_project_storages())
        projects2 = list(workspace.iter_project_storages())

        assert len(projects1) == len(projects2) == len(storage_names)
        # Should return same project instances (cached)
        assert set(id(p) for p in projects1) == set(id(p) for p in projects2)
