#!/usr/bin/env python3
"""
Template Rendering Context

This module provides the Context class - a Pydantic data container
that holds template rendering data built from Session objects.
"""

import datetime
import logging
from typing import Any

from pydantic import BaseModel, Field

from ..transcripts.models.transcript_items import TranscriptItemType
from ..transcripts.session import Session
from .models.message import Message
from .router import route

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
        # Load and sort transcripts by timestamp
        transcripts = cls._load_transcripts(session)

        # Extract session metadata from first item
        first_item = transcripts[0] if transcripts else None

        # Build messages using View classes
        messages = cls._build_messages(transcripts, session)

        return cls(
            session_id=session.session_id,
            start_time=first_item.timestamp if first_item else None,
            message_count=len(transcripts),
            cwd=first_item.cwd if first_item else None,
            git_branch=(
                first_item.gitBranch if first_item and first_item.gitBranch != "HEAD" else None
            ),
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

    @staticmethod
    def _build_messages(
        transcripts: list[TranscriptItemType],
        session: Session,
    ) -> list[Message]:
        """
        Build Message list from transcripts using router.

        Args:
            transcripts: List of transcript items
            session: Session for tool result lookups

        Returns:
            List of Message Pydantic models
        """
        messages = []
        for item in transcripts:
            try:
                view = route(item, session)
                message = view.to_message()
                messages.append(message)
            except ValueError as e:
                logger.error(f"Error dispatching view for item type {type(item)}: {e}")
                # Return a fallback message
                # Get session_id if available
                session_id = getattr(session, "session_id", None)
                if session_id:
                    import uuid

                    session_id = uuid.UUID(str(session_id))

                messages.append(
                    Message(
                        session_id=session_id,
                        category="system",
                        timestamp=getattr(item, "timestamp", None),
                        message_id=getattr(item, "uuid", None),
                        parent_message_id=getattr(item, "parentUuid", None),
                        is_sidechain=getattr(item, "isSidechain", False),
                        text_html="<em>Error rendering message</em>",
                    )
                )
        return messages

    def to_template_dict(self) -> dict[str, Any]:
        """
        Convert context to dictionary for template rendering.

        This is an alias for model_dump() for clarity.

        Returns:
            Dictionary with all context fields
        """
        return self.model_dump()
