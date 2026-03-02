#!/usr/bin/env python3
"""
Sample transcript item data for testing

This module provides helper functions to generate realistic mock data
for transcript items, matching the structure from real Claude Code transcripts.
"""

import uuid
from typing import Any


def generate_sample_user(
    content: str = "hello",
    user_uuid: str | None = None,
    parent_uuid: str | None = None,
    session_id: str = "12345678-1234-1234-1234-123456789abc",
) -> dict[str, Any]:
    """Generate a sample user transcript item."""
    return {
        "uuid": user_uuid or str(uuid.uuid4()),
        "timestamp": "2026-02-22T14:57:38.926Z",
        "parentUuid": parent_uuid or str(uuid.uuid4()),
        "isSidechain": False,
        "userType": "external",
        "cwd": "/Users/root/workspace/project",
        "sessionId": session_id,
        "version": "2.1.49",
        "gitBranch": "master",
        "slug": "test-user-item",
        "type": "user",
        "message": {
            "role": "user",
            "content": content,
        },
    }


def generate_sample_assistant(
    content: str = "hi",
    assistant_uuid: str | None = None,
    parent_uuid: str | None = None,
    session_id: str = "12345678-1234-1234-1234-123456789abc",
) -> dict[str, Any]:
    """Generate a sample assistant transcript item."""
    return {
        "parentUuid": parent_uuid or str(uuid.uuid4()),
        "isSidechain": False,
        "userType": "external",
        "cwd": "/Users/root/workspace/project",
        "sessionId": session_id,
        "version": "2.1.49",
        "gitBranch": "master",
        "slug": "test-assistant-item",
        "message": {
            "id": f"msg_{uuid.uuid4().hex}",
            "type": "message",
            "role": "assistant",
            "model": "claude-sonnet-4-6",
            "content": [
                {
                    "type": "text",
                    "text": content,
                }
            ],
            "stop_reason": None,
            "stop_sequence": None,
            "usage": {
                "input_tokens": 10,
                "output_tokens": 5,
            },
        },
        "type": "assistant",
        "uuid": assistant_uuid or str(uuid.uuid4()),
        "timestamp": "2026-02-22T14:57:42.788Z",
    }


def generate_sample_system(
    content: str = "system message",
    system_uuid: str | None = None,
    session_id: str = "12345678-1234-1234-1234-123456789abc",
) -> dict[str, Any]:
    """Generate a sample system transcript item."""
    return {
        "uuid": system_uuid or str(uuid.uuid4()),
        "timestamp": "2026-02-22T14:57:40.000Z",
        "parentUuid": None,
        "isSidechain": False,
        "userType": "external",
        "cwd": "/Users/root/workspace/project",
        "sessionId": session_id,
        "version": "2.1.49",
        "gitBranch": "master",
        "slug": "test-system-item",
        "type": "system",
        "message": {
            "role": "system",
            "content": content,
        },
    }


def generate_minimal_user(
    content: str = "hello",
    user_uuid: str | None = None,
) -> dict[str, Any]:
    """Generate a minimal user transcript item with only required fields."""
    return {
        "uuid": user_uuid or str(uuid.uuid4()),
        "timestamp": "2026-02-22T14:57:38.926Z",
        "isSidechain": False,
        "userType": "external",
        "cwd": "/Users/root/workspace/project",
        "sessionId": "12345678-1234-1234-1234-123456789abc",
        "version": "2.1.49",
        "type": "user",
        "message": {
            "role": "user",
            "content": content,
        },
    }


def generate_minimal_assistant(
    content: str = "hi",
    assistant_uuid: str | None = None,
    parent_uuid: str | None = None,
) -> dict[str, Any]:
    """Generate a minimal assistant transcript item with only required fields."""
    msg_uuid = uuid.uuid4() if assistant_uuid is None else uuid.UUID(assistant_uuid)
    return {
        "parentUuid": parent_uuid or str(uuid.uuid4()),
        "isSidechain": False,
        "userType": "external",
        "cwd": "/Users/root/workspace/project",
        "sessionId": "12345678-1234-1234-1234-123456789abc",
        "version": "2.1.49",
        "type": "assistant",
        "message": {
            "id": f"msg_{msg_uuid.hex}",
            "type": "message",
            "role": "assistant",
            "model": "claude-sonnet-4-6",
            "content": [
                {
                    "type": "text",
                    "text": content,
                }
            ],
            "stop_reason": None,
            "stop_sequence": None,
            "usage": {
                "input_tokens": 10,
                "output_tokens": 5,
            },
        },
        "uuid": assistant_uuid or str(uuid.uuid4()),
        "timestamp": "2026-02-22T14:57:42.788Z",
    }
