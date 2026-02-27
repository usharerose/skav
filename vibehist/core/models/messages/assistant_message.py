#!/usr/bin/env python3
"""
Assistant message model
"""

from typing import Literal

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
    stop_reason: Literal["end_turn", "stop_sequence", "tool_use"] | None
    stop_sequence: str | None
    usage: Usage

    content: list[
        ServerToolUseContentItem
        | TextContentItem
        | ToolResultContentItem
        | ThinkingContentItem
        | ToolUseContentItem
    ]

    container: None = None
    context_management: None = None
