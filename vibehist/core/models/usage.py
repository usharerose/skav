#!/usr/bin/env python3
"""
Usage model
"""

from typing import Any, Literal

from pydantic import BaseModel


class CacheCreation(BaseModel):
    ephemeral_1h_input_tokens: int
    ephemeral_5m_input_tokens: int


class ServerToolUse(BaseModel):
    web_fetch_requests: int | None = None
    web_search_requests: int | None = None


class Usage(BaseModel):
    input_tokens: int
    output_tokens: int

    cache_creation: CacheCreation | None = None
    cache_creation_input_tokens: int | None = None
    cache_read_input_tokens: int | None = None
    inference_geo: str | None = None

    # TODO: check the data type of `iterations` item
    iterations: list[Any] | None = None

    server_tool_use: ServerToolUse | None = None
    service_tier: Literal["standard"] | None = None
    speed: Literal["standard"] | None = None
