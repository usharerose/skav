#!/usr/bin/env python3
"""
Message Models

This package defines Pydantic models for different types of messages in
Claude Code transcripts. Messages represent the communication between
the user and the AI assistant.

Message Types:
    - UserMessage: Messages sent by the user (prompts, attachments)
    - AssistantMessage: Responses from the AI assistant (with content, thinking, tool use)
    - ProgressMessage: Progress updates for long-running operations
    - AttachmentMessage: File attachments uploaded by the user

Each message type can contain multiple content items (text, images, tool use, etc.)
as defined in the contents package.
"""

from .assistant import AssistantMessage
from .attachment import AttachmentMessage
from .progress import ProgressMessage
from .user import UserMessage

__all__ = [
    "AssistantMessage",
    "AttachmentMessage",
    "ProgressMessage",
    "UserMessage",
]
