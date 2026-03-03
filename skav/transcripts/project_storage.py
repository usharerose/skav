#!/usr/bin/env python3
"""
Project Storage Management

This module provides the ProjectStorage class for managing all session data
within a project's storage directory. It aggregates sessions and provides
convenient access to transcripts and tool results across the entire project.

Usage::
    >>> from skav.transcripts import ProjectStorage, ProjectStoragePath
    >>> storage = ProjectStorage(ProjectStoragePath("/path/to/.claude/projects"))
    >>> for item in storage.iter_transcript_items():
    ...     print(item)
"""

import logging
import os
import uuid
from collections.abc import Iterator

from .models.transcript_items import TranscriptItemType
from .project_storage_path import ProjectStoragePath
from .session import Session

logger = logging.getLogger(__name__)


class ProjectStorage:
    """
    Manages all session data within a project's storage directory.

    Provides access to all sessions, their transcripts, and tool results.
    Sessions are loaded lazily on first access.
    """

    def __init__(self, storage_path: ProjectStoragePath) -> None:
        """
        Initialize a ProjectStorage instance.

        :param storage_path: Path to the project storage directory
        :type storage_path: ProjectStoragePath
        :raises FileNotFoundError: If storage path doesn't exist
        """
        if not storage_path.exists():
            raise FileNotFoundError(
                f"Project storage path doesn't exist: {str(storage_path)}",
            )
        self._storage_path: ProjectStoragePath = storage_path
        self._session_mapping: dict[uuid.UUID, Session] = {}
        self._is_session_loaded: bool = False

    @property
    def storage_path(self) -> str:
        """
        Get the path to the project storage directory.

        :return: Path to the project storage directory
        :rtype: str
        """
        return str(self._storage_path)

    @property
    def sessions(self) -> set[Session]:
        """
        Get all sessions in the project storage.

        Loads sessions on first access if not already loaded.

        :return: Set of all Session objects in the project
        :rtype: set[Session]
        """
        if not self._is_session_loaded:
            self._load_sessions()
        return set(self._session_mapping.values())

    def _load_sessions(self) -> None:
        """
        Load all sessions from the project storage directory.

        Scans the directory for session files and directories,
        creating Session objects for each unique session ID.
        """
        if self._is_session_loaded:
            return

        def _extract_session_id(entry: os.DirEntry[str]) -> uuid.UUID | None:
            session_id: uuid.UUID | None = None
            if entry.is_dir():
                session_id = uuid.UUID(entry.name)
            else:
                session_id_str, *_ = entry.name.split(".")
                session_id = uuid.UUID(session_id_str)
            return session_id

        session_ids: set[uuid.UUID] = set()
        with os.scandir(str(self._storage_path)) as entries:
            for entry in entries:
                session_id: uuid.UUID | None = None
                try:
                    session_id = _extract_session_id(entry)
                except Exception as e:
                    logger.exception(f"Error extracting session ID: {entry.name}", exc_info=e)

                if session_id is None or session_id in session_ids:
                    continue

                session_ids.add(session_id)
                session = Session(self._storage_path, session_id)
                self._session_mapping[session_id] = session
        self._is_session_loaded = True

    def get_session(self, session_id: str | uuid.UUID) -> Session | None:
        """
        Get a specific session by ID.

        :param session_id: Session UUID as string or UUID object
        :type session_id: str or uuid.UUID
        :return: The Session object if found, None otherwise
        :rtype: Session or None
        """
        if isinstance(session_id, str):
            try:
                session_id = uuid.UUID(session_id)
            except ValueError as e:
                logger.exception(f"Badly session_id: {session_id}", exc_info=e)
                return None

        if not self._is_session_loaded:
            self._load_sessions()
        return self._session_mapping.get(session_id, None)

    def iter_transcript_items(self) -> Iterator[TranscriptItemType]:
        """
        Iterate over all transcript items across all sessions.

        :return: Iterator of transcript items from all sessions
        :rtype: Iterator[TranscriptItemType]
        """
        for session in self.sessions:
            yield from session.iter_transcripts()

    def get_tool_result_file_content(
        self, session_id: str | uuid.UUID, tool_use_id: str
    ) -> str | None:
        """
        Get the content of a tool result file.

        :param session_id: Session UUID as string or UUID object
        :type session_id: str or uuid.UUID
        :param tool_use_id: Tool use ID to look up
        :type tool_use_id: str
        :return: The tool result content if found, None otherwise
        :rtype: str or None
        """
        session = self.get_session(session_id)
        if session is None:
            return None
        return session.get_tool_result_file_content(tool_use_id)
