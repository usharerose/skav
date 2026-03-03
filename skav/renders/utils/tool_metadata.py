#!/usr/bin/env python3
"""
Tool metadata registry for UI rendering.

Provides a centralized registry for tool metadata with type-safe
access and sensible defaults for unknown tools.
"""

from typing import NamedTuple


class ToolInfo(NamedTuple):
    """Immutable tool information for UI rendering.

    Attributes:
        icon: Icon emoji or character for the tool
        description: Human-readable description (None if not available)
        css_class: CSS class name for styling
        programming_language: Language identifier for syntax highlighting
    """

    icon: str
    description: str | None
    css_class: str
    programming_language: str


class ToolMetadataRegistry:
    """Registry for tool metadata with validation and defaults.

    Provides type-safe access to tool metadata with automatic fallback
    to sensible defaults for unknown tools.
    """

    _DEFAULT = ToolInfo(
        icon="🔧",
        description=None,
        css_class="unknown-tool",
        programming_language="JSON",
    )

    _METADATA: dict[str, ToolInfo] = {
        "bash": ToolInfo(
            icon="$",
            description="Run shell command",
            css_class="bash",
            programming_language="BASH",
        ),
        "read": ToolInfo(
            icon="",
            description="Read file contents",
            css_class="read",
            programming_language="JSON",
        ),
        "write": ToolInfo(
            icon="✏️",
            description="Write to file",
            css_class="write",
            programming_language="JSON",
        ),
        "edit": ToolInfo(
            icon="✏️",
            description="Edit file",
            css_class="edit",
            programming_language="JSON",
        ),
        "glob": ToolInfo(
            icon="🔍",
            description="Find files by pattern",
            css_class="glob",
            programming_language="JSON",
        ),
        "grep": ToolInfo(
            icon="🔍",
            description="Search file contents",
            css_class="grep",
            programming_language="JSON",
        ),
        "task": ToolInfo(
            icon="🤖",
            description="Launch agent",
            css_class="task",
            programming_language="JSON",
        ),
    }

    # Server tool metadata (for WebSearch, WebFetch, etc.)
    _SERVER_TOOL = ToolInfo(
        icon="🌐",
        description="Server tool",
        css_class="server-tool",
        programming_language="JSON",
    )

    @classmethod
    def get(cls, tool_name: str) -> ToolInfo:
        """Get tool metadata with fallback to defaults.

        For unknown tools, returns a ToolInfo with the tool name as css_class.

        Args:
            tool_name: Name of the tool (case-insensitive)

        Returns:
            ToolInfo with all required fields
        """
        metadata = cls._METADATA.get(tool_name.lower())

        if metadata is None:
            # Return default with tool name as css_class
            return cls._DEFAULT._replace(css_class=tool_name.lower())

        return metadata

    @classmethod
    def get_server_tool(cls) -> ToolInfo:
        """Get metadata for server-side tools (WebSearch, etc.).

        Returns:
            ToolInfo for server tools
        """
        return cls._SERVER_TOOL

    @classmethod
    def list_tools(cls) -> list[str]:
        """Get list of all registered tool names.

        Returns:
            List of tool names (lowercase)
        """
        return list(cls._METADATA.keys())


# Convenience function for backward compatibility
def get_tool_metadata(tool_name: str) -> ToolInfo:
    """Get tool metadata with fallback to defaults.

    This is a convenience function that delegates to ToolMetadataRegistry.get.

    Args:
        tool_name: Name of the tool (case-insensitive)

    Returns:
        ToolInfo with all required fields
    """
    return ToolMetadataRegistry.get(tool_name)
