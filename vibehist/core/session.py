#!/usr/bin/env python3
"""
Session
"""

import logging
import os
import uuid
from collections.abc import Iterator
from typing import Any

from ..constants import TRANSCRIPT_FILE_EXT
from .project_storage_path import ProjectStoragePath
from .transcript_file import TranscriptFile

logger = logging.getLogger(__name__)


class Session:
    def __init__(
        self,
        storage_path: ProjectStoragePath,
        session_id: str | uuid.UUID,
    ) -> None:
        self._storage_path: ProjectStoragePath = storage_path
        if not self._storage_path.exists():
            raise FileNotFoundError(
                f"Project storage path doesn't exist: {self._storage_path}",
            )

        if isinstance(session_id, str):
            session_id = uuid.UUID(session_id)
        self._session_id: uuid.UUID = session_id
        if not any(
            [
                os.path.exists(self.session_path()),
                os.path.exists(self.session_path(is_file=False)),
            ]
        ):
            raise FileNotFoundError(
                f"Session <{self._session_id}> doesn't exist in project storage: {self._storage_path}",
            )
        self._transcript_files: set[TranscriptFile] | None = None

    @property
    def session_id(self) -> str:
        return str(self._session_id)

    def session_path(self, is_file: bool = True) -> str:
        """
        :param is_file: True for session transcript file
                        False for session directory with subagent transcript files and tool results
        :type is_file: bool
        :return: session path
        :rtype: str
        """
        entry_name = f"{self._session_id}"
        if is_file:
            entry_name = f"{entry_name}{TRANSCRIPT_FILE_EXT}"
        return os.path.join(str(self._storage_path), entry_name)

    def iter_transcripts(self) -> Iterator[dict[str, Any]]:
        for tf in self.iter_transcript_files():
            yield from tf.iter_items()

    def iter_transcript_files(self) -> Iterator[TranscriptFile]:
        if self._transcript_files is not None:
            yield from self._transcript_files
            return
        self._transcript_files = set()
        tf_path = self.session_path()
        if os.path.exists(tf_path):
            tf = TranscriptFile(self.session_path())
            self._transcript_files.add(tf)
            yield tf

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
                yield subagent_tf
