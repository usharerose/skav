#!/usr/bin/env python3
"""
Thinking content model
"""

from typing import Literal

from pydantic import BaseModel


class ThinkingContentItem(BaseModel):
    type: Literal["thinking"] = "thinking"

    thinking: str
    signature: str
