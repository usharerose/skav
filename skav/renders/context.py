#!/usr/bin/env python3
"""
Template Rendering Context

This module provides the Context class - a Pydantic data container
that holds template rendering data built from Session objects.
"""

import datetime
import logging

from pydantic import BaseModel, Field

from ..transcripts.models.transcript_items import TranscriptItemType
from ..transcripts.session import Session
from .compose import compose
from .models.message import Message

logger = logging.getLogger(__name__)


class Context(BaseModel):
    """
    Template rendering context data container.

    This is a Pydantic model that holds all data needed for template rendering.
    It provides both direct attribute access and dict conversion for Jinja2.

    Usage:
        context = Context.from_session(session)
        template.render(context=context)
        # or
        template.render(**context.model_dump())
    """

    # Session metadata
    session_id: str
    start_time: datetime.datetime | None = None
    message_count: int
    cwd: str | None = None
    git_branch: str | None = None

    # Token statistics
    tokens: int = 0

    # Messages list (Pydantic models, not dicts)
    messages: list[Message] = Field(default_factory=list)

    @classmethod
    def from_session(cls, session: Session) -> "Context":
        """
        Build Context from a Session object.

        Args:
            session: Session object to build context from

        Returns:
            Context data container with messages and metadata
        """
        transcripts = cls._load_transcripts(session)
        first_item: TranscriptItemType | None = None
        if transcripts:
            first_item, *_ = transcripts
        messages = compose(transcripts)

        # Extract metadata from first item using getattr for type safety
        start_time = getattr(first_item, "timestamp", None) if first_item else None
        cwd = getattr(first_item, "cwd", None) if first_item else None
        git_branch = None
        if first_item:
            branch = getattr(first_item, "gitBranch", None)
            if branch and branch != "HEAD":
                git_branch = branch

        # Calculate total tokens
        tokens = sum(msg.tokens or 0 for msg in messages)

        return cls(
            session_id=session.session_id,
            start_time=start_time,
            message_count=len(messages),
            cwd=cwd,
            git_branch=git_branch,
            tokens=tokens,
            messages=messages,
        )

    @staticmethod
    def _load_transcripts(session: Session) -> list[TranscriptItemType]:
        """
        Load and sort transcripts from session.

        Args:
            session: Session object

        Returns:
            Sorted list of transcript items with timestamps
        """
        all_transcripts = list(session.iter_transcripts())
        transcripts = [
            t for t in all_transcripts if hasattr(t, "timestamp") and t.timestamp is not None
        ]
        transcripts.sort(key=lambda x: x.timestamp)
        return transcripts
