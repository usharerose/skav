#!/usr/bin/env python3
"""
Project storage which stores project level session data
"""

import logging
import os
import uuid
from collections.abc import Iterator
from typing import Any

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
        self._session_mapping: dict[uuid.UUID, Session] | None = None

    @property
    def storage_path(self) -> str:
        return str(self._storage_path)

    @property
    def sessions(self) -> set[Session]:
        """
        Lazy load and return all sessions
        """
        if self._session_mapping is None:
            _ = list(self.iter_sessions())
        session_set: set[Session] = set()
        if self._session_mapping is not None:
            session_set.update(self._session_mapping.values())
        return session_set

    def iter_sessions(self) -> Iterator[Session]:
        if self._session_mapping is not None:
            yield from self._session_mapping.values()
            return None

        self._session_mapping = {}

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
                yield session
        return None

    def get_session(self, session_id: str | uuid.UUID) -> Session | None:
        if isinstance(session_id, str):
            try:
                session_id = uuid.UUID(session_id)
            except ValueError as e:
                logger.exception(f"Badly session_id: {session_id}", exc_info=e)
                return None
        if self._session_mapping is None:
            list(self.iter_sessions())
        if self._session_mapping is not None:
            return self._session_mapping.get(session_id, None)
        return None

    def iter_transcript_items(self) -> Iterator[dict[str, Any]]:
        for session in self.sessions:
            yield from session.iter_transcripts()
