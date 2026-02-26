#!/usr/bin/env python3
"""
Large Language Model message content models
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


class TextContentItem(BaseModel):
    type: Literal["text"] = "text"
    text: str


class ToolResultContentItem(BaseModel):
    type: Literal["tool_result"] = "tool_result"
    tool_use_id: str
    content: str
    is_error: bool | None = None
