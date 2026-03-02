#!/usr/bin/env python3
"""
Project storage which stores project level session data
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
    def __init__(self, storage_path: ProjectStoragePath) -> None:
        if not storage_path.exists():
            raise FileNotFoundError(
                f"Project storage path doesn't exist: {str(storage_path)}",
            )
        self._storage_path: ProjectStoragePath = storage_path
        self._session_mapping: dict[uuid.UUID, Session] = {}
        self._is_session_loaded: bool = False

    @property
    def storage_path(self) -> str:
        return str(self._storage_path)

    @property
    def sessions(self) -> set[Session]:
        if not self._is_session_loaded:
            self._load_sessions()
        return set(self._session_mapping.values())

    def _load_sessions(self) -> None:
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
        for session in self.sessions:
            yield from session.iter_transcripts()

    def get_tool_result_file_content(
        self, session_id: str | uuid.UUID, tool_use_id: str
    ) -> str | None:
        session = self.get_session(session_id)
        if session is None:
            return None
        return session.get_tool_result_file_content(tool_use_id)
