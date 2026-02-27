#!/usr/bin/env python3
"""
Tool result content model
"""

from typing import Literal

from pydantic import BaseModel


class ToolResultContentItem(BaseModel):
    type: Literal["tool_result"] = "tool_result"

    tool_use_id: str
    content: str
    is_error: bool | None = None
