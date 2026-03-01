#!/usr/bin/env python3
"""
User message model
"""

from typing import Any, Literal

from pydantic import BaseModel

from ..contents import (
    DocumentContentItem,
    TextContentItem,
    ToolResultContentItem,
)


class UserMessage(BaseModel):
    role: Literal["user"] = "user"

    # TODO: check the enumerable types of `content` item when it's a list
    content: (
        str | list[DocumentContentItem | TextContentItem | ToolResultContentItem | dict[str, Any]]
    )
