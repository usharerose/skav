#!/usr/bin/env python3
"""
Basic content component models
"""

from typing import Literal

from pydantic import BaseModel


class ContentSource(BaseModel):
    # TODO: check the enumerable values of `type`
    type: Literal["base64"] | str

    # TODO: check all of media types
    media_type: (
        Literal[
            "application/pdf",
            "image/png",
        ]
        | str
    )

    data: str


class FileResultContentDetail(BaseModel):
    # TODO: check the enumerable values of `type`
    type: str

    source: ContentSource
