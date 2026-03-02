#!/usr/bin/env python3
"""
Server tool use content model
"""

import json
from typing import Any, Literal, cast

from pydantic import BaseModel, field_validator


class ServerToolUseContentItem(BaseModel):
    type: Literal["server_tool_use"] = "server_tool_use"

    id: str
    name: str

    # TODO: check the data type of `input`
    # in reality, the value is JSON dict or JSON string 'til now
    #
    # e.g.
    #   - '{"url":"https://exmaple.com","return_format":"markdown","retain_images":true,"with_links_summary":true}'
    #   - {'url': 'https://blakecrosley.com/en/guides/claude-code', 'timeout': 20}
    input: str | dict[str, Any]

    @field_validator("input", mode="before")
    @classmethod
    def parse_input(cls, v: str | dict[str, Any]) -> str | dict[str, Any]:
        if isinstance(v, str):
            try:
                return cast(dict[str, Any], json.loads(v))
            except json.JSONDecodeError:
                return v
        return v
