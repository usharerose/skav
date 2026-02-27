#!/usr/bin/env python3
"""
Large Language Model message models
"""

from .assistant_message import AssistantMessage
from .user_message import UserMessage

__all__ = [
    "AssistantMessage",
    "UserMessage",
]
