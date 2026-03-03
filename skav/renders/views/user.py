#!/usr/bin/env python3
"""
User message view
"""

import uuid

from ...transcripts.models.contents import (
    DocumentContentItem,
    TextContentItem,
    ToolResultContentItem,
)
from ...transcripts.models.transcript_items import UserTranscriptItem
from ...transcripts.session import Session
from ..models import Message, ToolResultItem
from ..utils.markdown import markdown_to_html
from .base import BaseView


class UserView(BaseView):
    """
    View for user transcript item
    """

    def __init__(
        self,
        item: UserTranscriptItem,
        session: Session | None = None,
    ):
        self._item: UserTranscriptItem = item
        self._session: Session | None = session

    @classmethod
    def from_transcript(
        cls,
        item: UserTranscriptItem,
        session: Session | None = None,
    ) -> "UserView":
        return cls(item, session)

    def to_message(self) -> Message:
        text_html = self._extract_text_html()
        has_plan, plan_content = self._extract_plan_content()
        tool_results = self._extract_tool_results()
        return Message(
            category="user",
            session_id=uuid.UUID(self._item.sessionId),
            message_id=uuid.UUID(self._item.uuid),
            parent_message_id=uuid.UUID(self._item.parentUuid) if self._item.parentUuid else None,
            is_sidechain=self._item.isSidechain,
            timestamp=self._item.timestamp,
            has_plan=has_plan,
            plan_content=plan_content,
            text_html=text_html,
            tool_results=tool_results if tool_results else None,
        )

    def _extract_plan_content(self) -> tuple[bool, str | None]:
        has_plan: bool = False
        plan_content: str | None = None
        if self._item.planContent:
            has_plan = True
            plan_content = markdown_to_html(self._item.planContent)
        return has_plan, plan_content

    def _extract_text_html(self) -> str | None:
        content = self._item.message.content
        if isinstance(content, str):
            return markdown_to_html(content)

        text_html: str | None = None
        for item in content:
            if isinstance(item, TextContentItem):
                text_html = markdown_to_html(item.text)
            elif isinstance(item, DocumentContentItem):
                if text_html is None:
                    text_html = ""
                text_html += f"<p><em>📎 Document: {item.source.media_type}</em></p>"
        return text_html

    def _extract_tool_results(self) -> list[ToolResultItem]:
        tool_results: list[ToolResultItem] = []
        content = self._item.message.content
        if isinstance(content, str):
            return tool_results
        for item in content:
            if not isinstance(item, ToolResultContentItem):
                continue
            tool_result_content: str | None = None
            if self._session:
                tool_result_content = self._session.get_tool_result_file_content(item.tool_use_id)
            if tool_result_content is None:
                tool_result_content = ""
            tool_result_content = markdown_to_html(tool_result_content)
            tool_results.append(
                ToolResultItem(
                    content=tool_result_content,
                    is_error=item.is_error or False,
                    status_class="error" if item.is_error or False else "success",
                )
            )
        return tool_results
