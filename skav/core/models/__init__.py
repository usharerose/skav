#!/usr/bin/env python3
"""
Claude Code Transcript Models

This package contains Pydantic models for representing Claude Code transcript data.
Transcripts are stored as JSONL files with one item per line, each validated against
these models.

Model Hierarchy:
    - transcript_items: Top-level transcript item types (User, Assistant, System, etc.)
    - messages: Normalized message models (UserMessage, AssistantMessage, etc.)
    - contents: Message content types (Text, Thinking, ToolUse, ToolResult, etc.)
    - tool_use_result: Detailed tool execution result models
    - usage: Token usage and caching metadata
    - thinking_metadata: Thinking mode configuration

All models use Pydantic for validation and can be instantiated from
transcript JSON data using model_validate().
"""

from .transcript_items import WrappedTranscriptItem

__all__ = ["WrappedTranscriptItem"]
