#!/usr/bin/env python3
"""
Thinking metadata model
"""

from typing import Any, Literal

from pydantic import BaseModel


class ThinkingMetadata(BaseModel):
    disabled: bool | None = None

    # TODO: check the enumerable values of `level`
    level: Literal["high"] | str | None = None

    maxThinkingTokens: int | None = None

    # TODO: define data type of `triggers` item
    triggers: list[Any] | None = None
