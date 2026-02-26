#!/usr/bin/env python3
"""
User message model
"""

from typing import Literal

from pydantic import BaseModel

from .content import DocumentContentItem, TextContentItem, ToolResultContentItem


class UserMessage(BaseModel):
    role: Literal["user"] = "user"
    content: str | list[DocumentContentItem | TextContentItem | ToolResultContentItem]
