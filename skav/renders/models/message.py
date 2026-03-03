#!/usr/bin/env python3
"""
Message models for template rendering.

These models provide type-safe, flattened structures for Jinja2 templates.
All fields are directly accessible without nested navigation.
"""

import datetime
import uuid
from typing import Literal

from pydantic import BaseModel


class ToolUseItem(BaseModel):
    id: str
    name: str
    input_json: str
    icon: str
    description: str | None = None

    # CSS class
    tool_class: str
    # For syntax highlighting
    programming_language: str


class ToolResultItem(BaseModel):
    content: str
    is_error: bool = False
    status_class: Literal["error", "success"] = "success"


class Message(BaseModel):
    category: Literal[
        "assistant",
        "file-history-snapshot",
        "progress",
        "queue-operation",
        "summary",
        "system",
        "user",
    ]

    session_id: uuid.UUID | None = None
    message_id: uuid.UUID | None = None
    parent_message_id: uuid.UUID | None = None
    is_sidechain: bool = False
    timestamp: datetime.datetime | None = None

    model: str | None = None
    total_tokens: int | None = None

    text_html: str | None = None

    has_thinking: bool = False
    thinking_text: str | None = None
    thinking_signature: str | None = None

    has_plan: bool = False
    plan_content: str | None = None

    tool_uses: list[ToolUseItem] | None = None
    tool_results: list[ToolResultItem] | None = None
