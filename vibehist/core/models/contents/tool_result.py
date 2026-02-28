#!/usr/bin/env python3
"""
Tool result content model
"""

from typing import Any, Literal

from pydantic import BaseModel

from .base import FileResultContentDetail
from .text import TextContentItem


class ToolResultContentItem(BaseModel):
    type: Literal["tool_result"] = "tool_result"

    tool_use_id: str
    content: str | list[FileResultContentDetail | TextContentItem | dict[str, Any]]
    is_error: bool | None = None
