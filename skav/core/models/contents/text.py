#!/usr/bin/env python3
"""
Text content model
"""

from typing import Literal

from pydantic import BaseModel


class TextContentItem(BaseModel):
    type: Literal["text"] = "text"
    text: str
