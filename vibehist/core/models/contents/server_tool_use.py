#!/usr/bin/env python3
"""
Server tool use content model
"""

from typing import Any, Literal

from pydantic import BaseModel


class ServerToolUseContentItem(BaseModel):
    type: Literal["server_tool_use"] = "server_tool_use"

    id: str
    name: str
    input: dict[str, Any]  # TODO: check the data type of `input`
