#!/usr/bin/env python3
"""
Tool use content model
"""

from typing import Any, Literal

from pydantic import BaseModel


class ToolUseContentItem(BaseModel):
    type: Literal["tool_use"] = "tool_use"

    id: str
    name: str

    # TODO: check the data type of `input`
    input: dict[str, Any]
