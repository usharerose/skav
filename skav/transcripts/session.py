#!/usr/bin/env python3
"""
Session Management

This module provides the Session class for representing and accessing
Claude Code session data. A session encompasses all transcript files
(main session and subagents) and tool result files for a given session UUID.

The Session class aggregates data from multiple files:
- Main session transcript: {uuid}.jsonl
- Subagent transcripts: {uuid}/subagents/agent-{id}.jsonl
- Tool results: {uuid}/tool_results/{tool_use_id}.json

Usage:
    >>> from skav.transcripts import Session, ProjectStoragePath
    >>> storage = ProjectStoragePath("/path/to/.claude/projects")
    >>> session = Session(storage, "session-uuid")
    >>> for item in session.iter_transcripts():
    ...     print(item)
"""

import logging
import os
import uuid
from collections.abc import Iterator

from ..constants import TOOL_RESULT_FILE_EXT, TRANSCRIPT_FILE_EXT
from .models.transcript_items import TranscriptItemType
from .project_storage_path import ProjectStoragePath
from .tool_result_file import ToolResultFile
from .transcript_file import TranscriptFile

logger = logging.getLogger(__name__)


class Session:
    """Represents a Claude Code session with all its data.

    A session aggregates transcript files (main and subagents) and tool result files.
    Data is loaded lazily on first access to avoid unnecessary I/O.
    """

    def __init__(
        self,
        storage_path: ProjectStoragePath,
        session_id: str | uuid.UUID,
    ) -> None:
        """
        Initialize a Session instance.

        :param storage_path: Project storage path containing the session
        :type storage_path: ProjectStoragePath
        :param session_id: Session UUID as string or UUID object
        :type session_id: str or uuid.UUID
        :raises FileNotFoundError: If storage path doesn't exist
        """
        self._storage_path: ProjectStoragePath = storage_path
        if not self._storage_path.exists():
            raise FileNotFoundError(
                f"Project storage path doesn't exist: {self._storage_path}",
            )

        if isinstance(session_id, str):
            session_id = uuid.UUID(session_id)
        self._session_id: uuid.UUID = session_id

        self._transcript_files: set[TranscriptFile] = set()
        self._is_tf_loaded: bool = False
        self._tool_result_file_mapping: dict[str, ToolResultFile] = {}
        self._is_trf_loaded: bool = False

    @property
    def exists(self) -> bool:
        """
        Check if the session exists in storage.

        :return: True if either the session file or directory exists
        :rtype: bool
        """
        return any(
            [
                os.path.exists(self.session_path()),
                os.path.exists(self.session_path(is_file=False)),
            ]
        )

    @property
    def session_id(self) -> str:
        """
        Get the session ID as a string.

        :return: Session UUID as string
        :rtype: str
        """
        return str(self._session_id)

    def session_path(self, is_file: bool = True) -> str:
        """
        Get the filesystem path for the session.

        :param is_file: If True, return path to session transcript file;
                        If False, return path to session directory
                        containing subagents and tool results
        :type is_file: bool
        :return: Absolute path to the session file or directory
        :rtype: str
        """
        entry_name = f"{self._session_id}"
        if is_file:
            entry_name = f"{entry_name}{TRANSCRIPT_FILE_EXT}"
        return os.path.join(str(self._storage_path), entry_name)

    def _load_transcript_files(self) -> None:
        """
        Load all transcript files for the session.

        Loads the main session transcript and all subagent transcripts.
        This method is idempotent - subsequent calls do nothing.

        :raises FileNotFoundError: If session doesn't exist in storage
        """
        if self._is_tf_loaded:
            return

        if not self.exists:
            raise FileNotFoundError(
                f"Session <{self._session_id}> doesn't exist in project storage: {self._storage_path}",
            )

        tf_path = self.session_path()
        if os.path.exists(tf_path):
            tf = TranscriptFile(self.session_path())
            self._transcript_files.add(tf)

        dir_path = self.session_path(is_file=False)
        if not os.path.exists(dir_path):
            return
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file_path)
                if ext != TRANSCRIPT_FILE_EXT:
                    continue
                subagent_tf = TranscriptFile(file_path)
                self._transcript_files.add(subagent_tf)
        self._is_tf_loaded = True

    def iter_transcripts(self) -> Iterator[TranscriptItemType]:
        """
        Iterate over all transcript items in the session.

        Yields items from the main transcript and all subagent transcripts.

        :return: Iterator of transcript items with proper type discrimination
        :rtype: Iterator[TranscriptItemType]

        Example::

            >>> for item in session.iter_transcripts():
            ...     if isinstance(item, AssistantTranscriptItem):
            ...         print(f"Assistant: {item.content}")
        """
        if not self._is_tf_loaded:
            self._load_transcript_files()

        for tf in self._transcript_files:
            yield from tf

    def _load_tool_result_files(self) -> None:
        """
        Load all tool result files for the session.

        Scans the session directory for tool result files and builds a mapping
        from tool_use_id to ToolResultFile objects.

        :raises FileNotFoundError: If session doesn't exist in storage
        """
        if self._is_trf_loaded:
            return

        if not self.exists:
            raise FileNotFoundError(
                f"Session <{self._session_id}> doesn't exist in project storage: {self._storage_path}",
            )

        dir_path = self.session_path(is_file=False)
        if not os.path.exists(dir_path):
            return
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file_path)
                if ext != TOOL_RESULT_FILE_EXT:
                    continue
                tool_result_file = ToolResultFile(file_path)
                self._tool_result_file_mapping[tool_result_file.tool_use_id] = tool_result_file
        self._is_trf_loaded = True

    def __hash__(self) -> int:
        return hash((str(self._storage_path), str(self._session_id)))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Session):
            return False
        return all(
            [
                self._storage_path == other._storage_path,
                self._session_id == other._session_id,
            ]
        )

    def get_tool_result_file_content(self, tool_use_id: str) -> str | None:
        """
        Get the content of a tool result file by tool_use_id.

        :param tool_use_id: The tool use ID to look up
        :type tool_use_id: str
        :return: The tool result content, or None if not found
        :rtype: str or None
        """
        if not self._is_trf_loaded:
            self._load_tool_result_files()

        trf = self._tool_result_file_mapping.get(tool_use_id, None)
        if trf is not None:
            return trf.content
        return None
