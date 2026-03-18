#!/usr/bin/env python3
"""
Message Composer, which converts raw transcript items
into flattened Message structure
"""

import datetime
import json
import logging
import uuid
from typing import Literal

from ..transcripts.models.contents.base import FileResultContentDetail
from ..transcripts.models.contents.text import TextContentItem
from ..transcripts.models.transcript_items import AssistantTranscriptItem, TranscriptItemType
from .models.message import Message, ToolResultItem, ToolUseItem

logger = logging.getLogger(__name__)

# Type aliases for message categories and types
MessageCategory = Literal["assistant", "system", "user"]
MessageType = Literal[
    "assistant", "progress", "system", "thinking", "tool_result", "tool_use", "user"
]


def compose(transcript_items: list[TranscriptItemType]) -> list[Message]:
    """Convert transcript items to flattened Message list.

    This function processes raw transcript items and produces a flattened
    message structure suitable for template rendering. Tool results and
    progress messages are attached to their parent tool_use messages.

    Args:
        transcript_items: List of raw transcript items
        session_id: Session identifier (optional, will extract from items if not provided)

    Returns:
        List of Message objects (excludes nested tool_result and progress items)
    """
    if not transcript_items:
        return []

    transcript_items = sorted(
        transcript_items,
        key=lambda item: getattr(item, "timestamp", datetime.datetime.min),
    )

    message_index: dict[str, Message] = {}
    tool_use_index: dict[str, Message] = {}

    # first round loop: filtering out attached messages
    for item in transcript_items:
        _, msg_type = parse_message_category(item)
        if msg_type in ("tool_result", "progress"):
            continue
        message = transform_message(item)
        if not message:
            continue

        message_index[message.uuid.hex] = message

        if message.type == "tool_use" and message.tool_use:
            tool_use_id = message.tool_use.id
            tool_use_index[tool_use_id] = message

    # Second round loop: attach tool_results and progress to their ancestor tool_use
    for item in transcript_items:
        _, msg_type = parse_message_category(item)
        if msg_type == "tool_result":
            attach_tool_result_from_item(item, tool_use_index)

    # Return flat list (tool_result and progress already excluded)
    return list(message_index.values())


def parse_message_category(item: TranscriptItemType) -> tuple[MessageCategory, MessageType]:
    message = getattr(item, "message", None)
    contents = getattr(message, "content", []) if message else []

    if len(contents) > 0:
        first, *_ = contents
        content_type = getattr(first, "type", None)

        if content_type == "tool_use":
            return "assistant", "tool_use"
        if content_type == "tool_result":
            return "assistant", "tool_result"
        if content_type == "thinking":
            return "assistant", "thinking"

    transcript_type = getattr(item, "type", None)
    if transcript_type == "user":
        return "user", "user"
    if transcript_type == "system":
        return "system", "system"
    if transcript_type == "progress":
        return "assistant", "progress"
    return "assistant", "assistant"


def transform_message(
    item: TranscriptItemType,
) -> Message | None:
    msg_uuid = getattr(item, "uuid", None)
    if not msg_uuid:
        return None

    msg_category, msg_type = parse_message_category(item)
    timestamp = getattr(item, "timestamp", None)

    # Handle session_id - not all transcript types have sessionId
    session_id_str = getattr(item, "sessionId", None)
    if session_id_str is None:
        return None

    content = extract_content(item)

    tool_use = None
    if msg_type == "tool_use":
        tool_use = extract_tool_use(item)

    # Extract model and usage information from AssistantMessage
    # Only assistant messages have model and usage information
    model: str | None = None
    tokens: int | None = None
    if isinstance(item, AssistantTranscriptItem):
        assistant_msg = item.message
        usage = assistant_msg.usage

        model = assistant_msg.model
        tokens = usage.input_tokens + usage.output_tokens

    return Message(
        category=msg_category,
        type=msg_type,
        session_id=uuid.UUID(session_id_str),
        uuid=uuid.UUID(str(msg_uuid)),
        timestamp=timestamp or datetime.datetime.now(),
        model=model,
        tokens=tokens,
        content=content,
        tool_use=tool_use,
        tool_results=[],  # Will be populated during attachment phase
    )


def extract_content(item: TranscriptItemType) -> str | None:
    message = getattr(item, "message", None)
    if not message:
        return None
    content: list[object] | str | None = getattr(message, "content", None)
    if content is None or isinstance(content, str):
        return content
    content_obj, *_ = content
    content_type = getattr(content_obj, "type", None)

    if content_type == "text":
        text = getattr(content_obj, "text", None)
        return text
    if content_type == "thinking":
        thinking = getattr(content_obj, "thinking", None)
        return thinking
    return None


def extract_tool_use(item: TranscriptItemType) -> ToolUseItem | None:
    message = getattr(item, "message", None)
    if not message:
        return None
    content: list[object] | str | None = getattr(message, "content", None)
    if content is None or isinstance(content, str):
        return None

    content_obj, *_ = content
    content_type = getattr(content_obj, "type", None)
    if content_type != "tool_use":
        return None

    tool_use_id = getattr(content_obj, "id", "")
    tool_name = getattr(content_obj, "name", "")
    tool_input = getattr(content_obj, "input", {})
    tool_input_json = json.dumps(tool_input)

    return ToolUseItem(
        id=tool_use_id,
        name=tool_name,
        input_json=tool_input_json,
        icon=get_tool_icon(tool_name),
        description=get_tool_description(tool_name),
        tool_class=f"tool-{tool_name.lower()}",
        programming_language=detect_language(tool_input_json),
    )


def attach_tool_result_from_item(
    item: TranscriptItemType,
    tool_use_index: dict[str, Message],
) -> None:
    message = getattr(item, "message", None)
    if not message:
        return None
    content: list[object] | str | None = getattr(message, "content", None)
    if content is None or isinstance(content, str):
        return None

    content_obj, *_ = content
    content_type = getattr(content_obj, "type", None)
    if content_type != "tool_result":
        return None

    tool_use_id = getattr(content_obj, "tool_use_id", "")
    content_obj_content = getattr(content_obj, "content", "")

    result_content = ""
    if isinstance(content_obj_content, str):
        result_content = content_obj_content
    elif isinstance(content_obj_content, list):
        first, *_ = content_obj_content
        if isinstance(first, TextContentItem):
            result_content = first.text
        elif isinstance(first, FileResultContentDetail):
            result_content = getattr(first.source, "data", "")
        elif isinstance(first, dict):
            result_content = json.dumps(first)
        else:
            result_content = str(first)
    is_error = getattr(content_obj, "is_error", False)
    if is_error is None:
        is_error = False

    if tool_use_id not in tool_use_index:
        return None

    tool_result_item = ToolResultItem(
        content=result_content,
        is_error=is_error,
        status_class="error" if is_error else "success",
        tool_use_id=tool_use_id,
    )
    ancestor_message = tool_use_index[tool_use_id]
    if ancestor_message.tool_results is None:
        ancestor_message.tool_results = []
    ancestor_message.tool_results.append(tool_result_item)
    return None


def get_tool_icon(tool_name: str) -> str:
    icons = {
        "bash": "🐚",
        "editor": "📝",
        "read": "📖",
        "write": "✏️",
        "grep": "🔍",
    }
    return icons.get(tool_name.lower(), "🔧")


def get_tool_description(tool_name: str) -> str | None:
    """Get description for a tool."""
    descriptions = {
        "Bash": "Execute shell commands",
        "Editor": "Edit files",
        "Read": "Read file contents",
        "Write": "Write to files",
        "grep": "Search for patterns",
    }
    return descriptions.get(tool_name)


def detect_language(tool_input: str) -> str:
    if not tool_input:
        return "text"

    if "bash" in tool_input.lower() or "sh" in tool_input.lower():
        return "bash"
    if "python" in tool_input.lower():
        return "python"
    if "javascript" in tool_input.lower() or "node" in tool_input.lower():
        return "javascript"
    return "text"
