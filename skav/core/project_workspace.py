#!/usr/bin/env python3
"""
Project Workspace Management

This module provides the ProjectWorkspace class for representing the
Claude Code projects workspace directory (typically ~/.claude/projects).
It manages multiple project storage directories and provides access to
all sessions across all projects.

Usage::
    >>> from skav.core import ProjectWorkspace
    >>> workspace = ProjectWorkspace()
    >>> for project in workspace.iter_project_storages():
    ...     print(project.storage_path)
"""

import os
from collections.abc import Iterator

from ..utils import normalize_path
from .project_storage import ProjectStorage
from .project_storage_path import ProjectStoragePath


class ProjectWorkspace:
    """
    Represents the Claude Code projects workspace directory.

    The workspace contains multiple project storage directories, each
    representing a different project. Projects are loaded lazily on
    first access.
    """

    def __init__(
        self,
        path: str | os.PathLike[str] = "~/.claude/projects",
    ) -> None:
        """
        Initialize a ProjectWorkspace instance.

        :param path: Path to the workspace directory
        :type path: str or os.PathLike[str]
        :raises FileNotFoundError: If workspace path doesn't exist
        :raises NotADirectoryError: If workspace path is not a directory
        """
        epath = normalize_path(path)
        if not os.path.exists(epath):
            raise FileNotFoundError(f"Path {epath} doesn't exist")
        if not os.path.isdir(epath):
            raise NotADirectoryError(f"Path {epath} is not a directory")
        self._path: str = epath
        self._project_storage_mapping: dict[str, ProjectStorage] = {}
        self._is_loaded: bool = False

    def __str__(self) -> str:
        """
        Get the string representation of the workspace path.

        :return: Path to the workspace directory
        :rtype: str
        """
        return self._path

    def get_project_storage(self, storage_name: str) -> ProjectStorage | None:
        """
        Get a project storage by storage name.

        :param storage_name: Storage name of the project (e.g., "-project-user-home")
        :type storage_name: str
        :return: The ProjectStorage object if found, None otherwise
        :rtype: ProjectStorage or None
        """
        if not self._is_loaded:
            self._load()
        return self._project_storage_mapping.get(storage_name, None)

    def _load(self) -> None:
        """
        Load all project storages from the workspace directory.

        Scans the directory for subdirectories and creates ProjectStorage
        objects for each. This method is idempotent - subsequent calls
        do nothing.
        """
        if self._is_loaded:
            return

        with os.scandir(self._path) as entries:
            for entry in entries:
                if not entry.is_dir():
                    continue
                storage_path = ProjectStoragePath(entry.name, self._path)
                project = ProjectStorage(storage_path)
                self._project_storage_mapping[entry.name] = project
        self._is_loaded = True

    def iter_project_storages(self) -> Iterator[ProjectStorage]:
        """
        Iterate over all project storages in the workspace.

        :return: Iterator of ProjectStorage objects
        :rtype: Iterator[ProjectStorage]
        """
        if not self._is_loaded:
            self._load()
        yield from self._project_storage_mapping.values()
