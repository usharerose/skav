#!/usr/bin/env python3
"""
Thinking Metadata Models

This module defines Pydantic models for thinking-related metadata in Claude Code
transcripts. Thinking mode allows Claude to show its reasoning process before
producing the final response.

The metadata includes:
    - disabled: Whether thinking is disabled for this interaction
    - level: Thinking intensity level (e.g., "high")
    - maxThinkingTokens: Maximum tokens allowed for thinking
    - triggers: Conditions that trigger thinking mode
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
