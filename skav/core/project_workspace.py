#!/usr/bin/env python3
"""
Workspace represents .claude/projects under the home directory
"""

import os
from collections.abc import Iterator

from ..utils import normalize_path
from .project_storage import ProjectStorage
from .project_storage_path import ProjectStoragePath


class ProjectWorkspace:
    def __init__(
        self,
        path: str | os.PathLike[str] = "~/.claude/projects",
    ) -> None:
        epath = normalize_path(path)
        if not os.path.exists(epath):
            raise FileNotFoundError(f"Path {epath} doesn't exist")
        if not os.path.isdir(epath):
            raise NotADirectoryError(f"Path {epath} is not a directory")
        self._path: str = epath
        self._project_storage_mapping: dict[str, ProjectStorage] = {}
        self._is_loaded: bool = False

    def __str__(self) -> str:
        return self._path

    def get_project_storage(self, storage_name: str) -> ProjectStorage | None:
        if not self._is_loaded:
            self._load()
        return self._project_storage_mapping.get(storage_name, None)

    def _load(self) -> None:
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
        if not self._is_loaded:
            self._load()
        yield from self._project_storage_mapping.values()
