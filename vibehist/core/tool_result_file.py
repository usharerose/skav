#!/usr/bin/env python3
"""
Tool result file for large tool result
"""

import os
import re
from collections.abc import Iterator
from typing import cast

from ..constants import TOOL_RESULT_FILE_EXT
from ..utils import normalize_path


class ToolResultFile:
    def __init__(self, path: str | os.PathLike[str]) -> None:
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
        return self._path

    @property
    def exists(self) -> bool:
        return os.path.exists(self._path)

    @property
    def session_id(self) -> str:
        return cast(str, self._session_id)

    @property
    def tool_use_id(self) -> str:
        return cast(str, self._tool_use_id)

    def extract_identifiers(self) -> tuple[str | None, str | None]:
        """
        Extract session ID and tool use ID from the path

        :return: tuple[session_id, tool_use_id]
        :rtype: tuple[str | None, str | None]
        """
        pattern = r".*/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})/tool-results/(call_[a-z0-9]+).txt$"
        match = re.match(pattern, self._path)
        session_id = match.group(1) if match else None
        tool_use_id = match.group(2) if match else None
        return session_id, tool_use_id

    def _load(self) -> None:
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
        if not self._is_loaded:
            self._load()
        yield from self._lines

    @property
    def content(self) -> str:
        if not self._is_loaded:
            self._load()
        return "".join(self._lines)
