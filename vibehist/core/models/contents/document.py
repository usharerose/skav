#!/usr/bin/env python3
"""
Document content model
"""

from typing import Literal

from .base import FileResultContentDetail


class DocumentContentItem(FileResultContentDetail):
    type: Literal["document"] = "document"
