#!/usr/bin/env python3
"""
Tool Result File Processing

This module provides the ToolResultFile class for reading tool execution
result files stored by Claude Code. Tool results are stored separately from
transcripts when they are large, keeping the transcript files lightweight.

Tool result files use the pattern: {session_uuid}/tool-results/{tool_use_id}.txt

Usage::
    >>> trf = ToolResultFile("/path/to/session/tool-results/call_abc123.txt")
    >>> print(trf.content)
"""

import os
import re
from collections.abc import Iterator
from typing import cast

from ..constants import TOOL_RESULT_FILE_EXT
from ..utils import normalize_path


class ToolResultFile:
    """
    Represents a tool execution result file.

    Tool result files store the output of tool executions separately from
    the main transcript to keep transcript files lightweight.
    """

    def __init__(self, path: str | os.PathLike[str]) -> None:
        """
        Initialize a ToolResultFile instance.

        :param path: Path to the tool result file
        :type path: str or os.PathLike[str]
        :raises ValueError: If file extension is not .txt or path pattern is invalid
        """
        self._path = normalize_path(path)
        *_, ext = os.path.splitext(self._path)
        if ext != TOOL_RESULT_FILE_EXT:
            raise ValueError(
                f"Invalid tool result file extension: {path}",
            )
        self._session_id, self._tool_use_id = self.extract_identifiers()
        if any(identifier is None for identifier in (self._session_id, self._tool_use_id)):
            raise ValueError(f"Invalid tool result file path: {path}")
        self._lines: list[str] = []
        self._is_loaded: bool = False

    @property
    def path(self) -> str:
        """
        Get the normalized path to the tool result file.

        :return: Absolute path to the tool result file
        :rtype: str
        """
        return self._path

    @property
    def exists(self) -> bool:
        """
        Check if the tool result file exists on filesystem.

        :return: True if the file exists, False otherwise
        :rtype: bool
        """
        return os.path.exists(self._path)

    @property
    def session_id(self) -> str:
        """
        Get the session UUID extracted from the file path.

        :return: Session UUID string
        :rtype: str
        """
        return cast(str, self._session_id)

    @property
    def tool_use_id(self) -> str:
        """
        Get the tool use ID extracted from the file path.

        :return: Tool use ID string (e.g., "call_abc123")
        :rtype: str
        """
        return cast(str, self._tool_use_id)

    def extract_identifiers(self) -> tuple[str | None, str | None]:
        """
        Extract session ID and tool use ID from the path.

        Uses regex to match the path pattern:
        .../{session_uuid}/tool-results/{tool_use_id}.txt

        :return: Tuple of (session_id, tool_use_id)
        :rtype: tuple[str or None, str or None]
        """
        pattern = (
            r".*/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"
            r"/tool-results/(call_[a-z0-9]+).txt$"
        )
        match = re.match(pattern, self._path)
        session_id = match.group(1) if match else None
        tool_use_id = match.group(2) if match else None
        return session_id, tool_use_id

    def _load(self) -> None:
        """
        Load all lines from the tool result file.

        This method is idempotent - subsequent calls do nothing.

        :raises FileNotFoundError: If the tool result file doesn't exist
        """
        if self._is_loaded:
            return

        if not self.exists:
            raise FileNotFoundError(
                f"Tool result file doesn't exist: {self._path}",
            )
        with open(self._path, encoding="utf-8-sig") as f:
            for line in f:
                self._lines.append(line)
        self._is_loaded = True

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over all lines in the tool result file.

        :return: Iterator of lines from the file
        :rtype: Iterator[str]
        """
        if not self._is_loaded:
            self._load()
        yield from self._lines

    @property
    def content(self) -> str:
        """
        Get the complete content of the tool result file.

        :return: All lines joined together as a single string
        :rtype: str
        """
        if not self._is_loaded:
            self._load()
        return "".join(self._lines)
