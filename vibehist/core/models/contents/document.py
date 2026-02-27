#!/usr/bin/env python3
"""
Document content model
"""

from typing import Literal

from pydantic import BaseModel


class DocumentContentSource(BaseModel):
    type: Literal["base64"] = "base64"

    media_type: Literal["application/pdf"]
    data: str


class DocumentContentItem(BaseModel):
    type: Literal["document"] = "document"

    source: DocumentContentSource
