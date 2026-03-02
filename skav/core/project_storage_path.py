#!/usr/bin/env python3
"""
Claude Code Project Path
"""

import os

from ..utils import normalize_path


class ProjectStoragePath:
    """
    ProjectPath represents the path of a project in the filesystem
    """

    def __init__(
        self,
        storage_name: str,
        workspace_path: str | os.PathLike[str] = "~/.claude/projects",
    ) -> None:
        if not storage_name.startswith("-"):
            raise ValueError(f"Storage name must start with '-': {storage_name}")
        self._storage_name = storage_name
        self._workspace_path = normalize_path(workspace_path)
        self._path = os.path.join(self._workspace_path, self._storage_name)

    @classmethod
    def encode(
        cls,
        project_dir: str | os.PathLike[str],
        workspace_path: str | os.PathLike[str] = "~/.claude/projects",
    ) -> "ProjectStoragePath":
        """
        Instantiate a ProjectPath object from a directory path
        e.g.
            - encode("/home/project/")
            - encode("~/project")

        :param project_dir: the directory path of the project
        :type project_dir: str | os.PathLike[str]
        :param workspace_path: the path of the Claude Code project workspace
        :type workspace_path: str | os.PathLike[str]
        :return: a ProjectStoragePath object
        :rtype: ProjectStoragePath
        """
        project_abspath = normalize_path(str(project_dir))
        storage_name = cls.abspath_to_storage_name(project_abspath)
        return cls(storage_name, workspace_path)

    @staticmethod
    def abspath_to_storage_name(abspath: str) -> str:
        if not os.path.isabs(abspath):
            raise ValueError(f"Path is not absolute: {abspath}")
        parts = []
        while True:
            abspath, tail = os.path.split(abspath)
            if tail:
                parts.append(tail)
                continue
            break
        return f"-{'-'.join(parts[::-1])}"

    @property
    def storage_name(self) -> str:
        return self._storage_name

    @property
    def workspace_path(self) -> str:
        return self._workspace_path

    def exists(self) -> bool:
        return os.path.exists(self._path)

    def __str__(self) -> str:
        return self._path
