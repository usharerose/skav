#!/usr/bin/env python3
"""
Transcript File Processing

This module provides the TranscriptFile class for reading and parsing
Claude Code transcript files (.jsonl format). Each transcript file contains
a sequence of transcript items representing the conversation history.

Transcript files use JSON Lines format - one JSON object per line.
Each line is validated against the TranscriptItemType union using Pydantic.

Usage::
    >>> tf = TranscriptFile("/path/to/session.jsonl")
    >>> for item in tf:
    ...     print(item)
    >>>
    >>> # Or load all at once
    >>> items = list(tf)
"""

import json
import logging
import os
import re
from collections.abc import Iterator
from typing import Any, cast

from ..constants import TRANSCRIPT_FILE_EXT
from ..utils import normalize_path
from .models import WrappedTranscriptItem
from .models.transcript_items import TranscriptItemType

logger = logging.getLogger(__name__)


class TranscriptFile:
    """
    Single transcript file which stores historical messages of a session.

    The file must be a .jsonl file. Each line is parsed and validated
    as a WrappedTranscriptItem using Pydantic models.

    Example usage::

        >>> tf = TranscriptFile("/path/to/session.jsonl")
        >>> for item in tf:
        ...     print(item)
    """

    def __init__(self, path: str | os.PathLike[str]) -> None:
        """
        Initialize a TranscriptFile instance.

        :param path: Path to the .jsonl transcript file
        :type path: str or os.PathLike[str]
        :raises ValueError: If file extension is not .jsonl
        """
        self._path = normalize_path(path)
        *_, ext = os.path.splitext(self._path)
        if ext != TRANSCRIPT_FILE_EXT:
            raise ValueError(
                f"Invalid transcript file extension: {path}",
            )
        self._items: list[TranscriptItemType] = []
        self._is_loaded: bool = False
        self._session_id, self._agent_id = self.extract_identifiers()

    @property
    def exists(self) -> bool:
        """
        Check if the transcript file exists on filesystem.

        :return: True if the file exists, False otherwise
        :rtype: bool
        """
        return os.path.exists(self._path)

    @property
    def path(self) -> str:
        """
        Get the normalized path to the transcript file.

        :return: Absolute path to the transcript file
        :rtype: str
        """
        return self._path

    @property
    def session_id(self) -> str | None:
        """
        Get the session UUID extracted from the file path.

        :return: Session UUID string, or None if not found
        :rtype: str or None
        """
        return self._session_id

    @property
    def agent_id(self) -> str | None:
        """
        Get the agent ID if this is a subagent transcript.

        :return: Agent ID string for subagents, None for main session
        :rtype: str or None
        """
        return self._agent_id

    @property
    def is_subagent(self) -> bool:
        """
        Check if this transcript belongs to a subagent.

        :return: True if this is a subagent transcript, False for main session
        :rtype: bool
        """
        return self._agent_id is not None

    def _load(self) -> None:
        """
        Load and parse all transcript items from the JSONL file.

        This method is idempotent - subsequent calls do nothing.
        Each line is parsed as JSON and validated using Pydantic models.
        Invalid lines are logged and skipped.

        :raises FileNotFoundError: If the transcript file doesn't exist
        :raises Exception: If validation fails for any transcript item
        """
        if self._is_loaded:
            return

        if not self.exists:
            raise FileNotFoundError(
                f"Transcript file doesn't exist: {self._path}",
            )
        with open(self._path, encoding="utf-8-sig") as f:
            for lineno, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                data: dict[str, Any] | None = None
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    logger.exception(
                        f"Failed to parse {self._path}, line {lineno}: {line[:100]}",
                    )
                    continue
                data = cast(dict[str, Any], data)
                try:
                    wrapped_dm = WrappedTranscriptItem.model_validate(data)
                except Exception as e:
                    logger.exception(f"Failed to validate transcript item: {data}", exc_info=e)
                    raise
                self._items.append(wrapped_dm.root)
        self._is_loaded = True

    def __iter__(self) -> Iterator[TranscriptItemType]:
        """
        Iterate over all transcript items in the file.

        Loads the file on first access if not already loaded.

        :return: Iterator of transcript items
        :rtype: Iterator[TranscriptItemType]
        """
        if not self._is_loaded:
            self._load()
        yield from self._items

    def extract_identifiers(self) -> tuple[str | None, str | None]:
        """
        Extract session ID and agent ID from the path.

        Uses regex to match the path pattern:
        - Main session: .../{uuid}.jsonl
        - Subagent: .../{uuid}/subagents/agent-{id}.jsonl

        :return: Tuple of (session_id, agent_id). agent_id is None for main sessions.
        :rtype: tuple[str or None, str or None]
        """
        pattern = (
            r".*/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"
            r"(?:/subagents/agent-(.*))?\.jsonl$"
        )
        match = re.match(pattern, self._path)
        session_id = match.group(1) if match else None
        agent_id = match.group(2) if match else None
        return session_id, agent_id

    def __hash__(self) -> int:
        return hash(self._path)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TranscriptFile):
            return False
        return self._path == other._path
