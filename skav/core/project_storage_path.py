#!/usr/bin/env python3
"""
Project Storage Path Management

This module provides the ProjectStoragePath class for representing and
managing paths to Claude Code project storage directories. Claude Code
encodes project directories as storage names using a special format:
paths are reversed and joined with hyphens, prefixed with a hyphen.

Example:
    /home/user/project -> -home-user-project

Usage::
    >>> psp = ProjectStoragePath.encode("/home/user/project")
    >>> print(psp.storage_name)
    -home-user-project
"""

import os

from ..utils import normalize_path


class ProjectStoragePath:
    """
    Represents the path of a Claude Code project in the filesystem.

    Storage names use a special encoding: paths are reversed and joined
    with hyphens, prefixed with a hyphen. For example, /home/user/project
    becomes -home-user-project.
    """

    def __init__(
        self,
        storage_name: str,
        workspace_path: str | os.PathLike[str] = "~/.claude/projects",
    ) -> None:
        """
        Initialize a ProjectStoragePath instance.

        :param storage_name: Encoded storage name (must start with '-')
        :type storage_name: str
        :param workspace_path: Path to the Claude Code projects workspace
        :type workspace_path: str or os.PathLike[str]
        :raises ValueError: If storage_name doesn't start with '-'
        """
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
        Instantiate a ProjectStoragePath object from a directory path.

        This method converts a project directory path to the encoded storage
        name format used by Claude Code.

        Example::

            >>> psp = ProjectStoragePath.encode("/home/user/project")
            >>> print(psp.storage_name)
            -home-user-project

        :param project_dir: The directory path of the project
        :type project_dir: str or os.PathLike[str]
        :param workspace_path: The path of the Claude Code project workspace
        :type workspace_path: str or os.PathLike[str]
        :return: A ProjectStoragePath object
        :rtype: ProjectStoragePath
        """
        project_abspath = normalize_path(str(project_dir))
        storage_name = cls.abspath_to_storage_name(project_abspath)
        return cls(storage_name, workspace_path)

    @staticmethod
    def abspath_to_storage_name(abspath: str) -> str:
        """
        Convert an absolute path to a storage name.

        The path components are reversed and joined with hyphens,
        prefixed with a hyphen. For example, /home/user/project
        becomes -home-user-project.

        :param abspath: Absolute path to convert
        :type abspath: str
        :return: Encoded storage name
        :rtype: str
        :raises ValueError: If path is not absolute
        """
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
        """
        Get the encoded storage name.

        :return: Storage name (e.g., "-home-user-project")
        :rtype: str
        """
        return self._storage_name

    @property
    def workspace_path(self) -> str:
        """
        Get the workspace path.

        :return: Path to the Claude Code projects workspace
        :rtype: str
        """
        return self._workspace_path

    def exists(self) -> bool:
        """
        Check if the project storage directory exists.

        :return: True if the directory exists, False otherwise
        :rtype: bool
        """
        return os.path.exists(self._path)

    def __str__(self) -> str:
        """
        Get the string representation of the path.

        :return: Full path to the project storage directory
        :rtype: str
        """
        return self._path
