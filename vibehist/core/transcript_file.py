#!/usr/bin/env python3
"""
Transcript file
"""

import json
import logging
import os
import re
from collections.abc import Iterator
from typing import Any

from ..constants import TRANSCRIPT_FILE_EXT
from ..utils import normalize_path

logger = logging.getLogger(__name__)


class TranscriptFile:
    """
    Single transcript file which stores historical messages of a session

    >>> tf = TranscriptFile("/path/to/session.jsonl")
    >>> for item in tf.iter_items():
    ...     print(item)
    >>>
    >>> # load all of them
    >>> items = tf.load()
    """

    def __init__(self, path: str | os.PathLike[str]) -> None:
        self._path = normalize_path(path)
        *_, ext = os.path.splitext(self._path)
        if ext != TRANSCRIPT_FILE_EXT:
            raise ValueError(
                f"Invalid transcript file extension: {path}",
            )
        self._items: list[dict[str, Any]] | None = None
        self._session_id, self._agent_id = self.extract_identifiers()

    @property
    def exists(self) -> bool:
        return os.path.exists(self._path)

    @property
    def path(self) -> str:
        return self._path

    @property
    def session_id(self) -> str | None:
        return self._session_id

    @property
    def agent_id(self) -> str | None:
        return self._agent_id

    @property
    def is_subagent(self) -> bool:
        return self._agent_id is not None

    def iter_items(self) -> Iterator[dict[str, Any]]:
        if not self.exists:
            raise FileNotFoundError(
                f"Transcript file doesn't exist: {self._path}",
            )
        with open(self._path, encoding="utf-8-sig") as f:
            for lineno, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    yield data
                except json.JSONDecodeError:
                    logger.exception(
                        f"Failed to parse {self._path}, line {lineno}: {line[:100]}",
                    )

    def load(self, force: bool = False) -> list[dict[str, Any]]:
        if self._items is None or force:
            self._items = list(self.iter_items())
        return self._items

    def extract_identifiers(self) -> tuple[str | None, str | None]:
        """
        Extract session ID and agent ID from the path
        If the file is a subagent transcript, the agent ID is not None

        :return: tuple[session_id, agent_id]
        :rtype: tuple[str | None, str | None]
        """
        pattern = r".*/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})(?:/subagents/agent-(.*))?\.jsonl$"
        match = re.match(pattern, self._path)
        session_id = match.group(1) if match else None
        agent_id = match.group(2) if match else None
        return session_id, agent_id
