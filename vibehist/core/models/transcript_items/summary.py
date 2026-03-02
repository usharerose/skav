#!/usr/bin/env python3
"""
Summuary transcript item model
"""

from typing import Literal

from pydantic import BaseModel


class SummaryTranscriptItem(BaseModel):
    type: Literal["summary"] = "summary"

    summary: str
    leafUuid: str
