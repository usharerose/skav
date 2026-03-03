#!/usr/bin/env python3
"""
Assistant message model
"""

from typing import Any, Literal

from pydantic import BaseModel

from ..contents import (
    ServerToolUseContentItem,
    TextContentItem,
    ThinkingContentItem,
    ToolResultContentItem,
    ToolUseContentItem,
)
from ..usage import Usage


class AssistantMessage(BaseModel):
    type: Literal["message"] = "message"
    role: Literal["assistant"] = "assistant"

    id: str
    model: str

    # TODO: check the enumerable values of `stop_reason`
    stop_reason: Literal["end_turn", "stop_sequence", "tool_use"] | str | None

    stop_sequence: str | None
    usage: Usage

    # TODO: check the enumerable types of `content` item
    content: list[
        ServerToolUseContentItem
        | TextContentItem
        | ToolResultContentItem
        | ThinkingContentItem
        | ToolUseContentItem
        | dict[str, Any]
    ]

    container: None = None
    context_management: None = None
