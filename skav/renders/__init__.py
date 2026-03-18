#!/usr/bin/env python3
"""
Visualization render components

This module provides HTML rendering capabilities for Claude Code transcripts.

The rendering architecture uses:
- View classes for type-specific transcript transformation
- Router for routing transcripts to appropriate views
- Context for holding template rendering data
- Pydantic models (Message) for type-safe template output
"""

from .context import Context
from .models.message import Message, ToolResultItem, ToolUseItem
from .renderer import HTMLRenderer

__all__ = [
    "Context",
    "Message",
    "ToolUseItem",
    "ToolResultItem",
    "HTMLRenderer",
]
