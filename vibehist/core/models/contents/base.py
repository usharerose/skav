#!/usr/bin/env python3
"""
Basic content component models
"""

from typing import Literal

from pydantic import BaseModel


class ContentSource(BaseModel):
    type: Literal["base64"] | str  # TODO: check all of types
    media_type: (
        Literal[
            "application/pdf",
            "image/png",
        ]
        | str
    )  # TODO: check all of media types
    data: str


class FileResultContentDetail(BaseModel):
    type: str  # TODO: check all of types
    source: ContentSource
