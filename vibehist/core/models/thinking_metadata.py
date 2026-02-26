#!/usr/bin/env python3
"""
Thinking metadata model
"""

from typing import Any, Literal

from pydantic import BaseModel


class ThinkingMetadata(BaseModel):
    disabled: bool | None = None
    level: Literal["high"] | None = None
    maxThinkingTokens: int | None = None
    triggers: list[Any] | None = None  # TODO: define data type of `triggers` item
