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
    status_class: Literal["error", "success", "progress"] = "success"
    tool_use_id: str | None = None  # ID of the matching tool_use


class Message(BaseModel):
    category: Literal[
        "assistant",
        "system",
        "user",
    ]
    type: Literal[
        "assistant",
        "progress",
        "system",
        "thinking",
        "tool_result",
        "tool_use",
        "user",
    ]

    session_id: uuid.UUID
    uuid: uuid.UUID
    timestamp: datetime.datetime

    model: str | None = None
    tokens: int | None = None

    content: str | None = None

    tool_use: ToolUseItem | None = None
    tool_results: list[ToolResultItem] | None = None
