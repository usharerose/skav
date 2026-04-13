"""
Install-hooks command - Register event-log to Claude Code hooks
"""

import argparse
import json
import logging
import os
import shutil
import sys
from typing import Any

from ..log import config_logging
from ..utils import normalize_path

logger = logging.getLogger(__name__)

EVENT_NAMES = [
    "SessionStart",
    "SessionEnd",
    "UserPromptSubmit",
    "PreToolUse",
    "PostToolUse",
    "PostToolUseFailure",
    "PermissionRequest",
    "SubagentStart",
    "SubagentStop",
    "Stop",
    "StopFailure",
    "TeammateIdle",
    "TaskCreated",
    "TaskCompleted",
    "PreCompact",
    "PostCompact",
    "Setup",
    "Elicitation",
    "ElicitationResult",
    "ConfigChange",
    "WorktreeCreate",
    "WorktreeRemove",
    "InstructionsLoaded",
    "FileChanged",
    "CwdChanged",
    "Notification",
]


def parse_install_hooks_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    Add install-hooks command arguments to parser.

    :param parser: Argument parser to add arguments to
    :type parser: argparse.ArgumentParser
    :return: Updated argument parser
    :rtype: argparse.ArgumentParser
    """
    parser.add_argument(
        "-l",
        "--log-dir",
        dest="log_dir",
        default=None,
        help="Custom log directory for event logs",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without actually modifying settings.json",
    )

    parser.add_argument(
        "--events",
        dest="events",
        nargs="+",
        default=None,
        help=("Specific hook events to configure (default: all)."),
    )

    return parser


def get_skav_executable() -> str:
    """
    Get the skav executable path for hooks.

    :return: Skav executable path
    :rtype: str
    """
    # Get the skav executable path
    skav_path = shutil.which("skav")
    if skav_path:
        return skav_path

    # Fallback to current Python executable
    python_exec = sys.executable
    # Check if we're in a virtual environment
    if os.path.exists(os.path.join(os.path.dirname(python_exec), "skav")):
        return f"{python_exec} -m skav"

    # Default to 'skav' and rely on PATH
    return "skav"


def remove_skav_hooks(settings: dict[str, Any], event_name: str) -> None:
    """
    Remove existing skav hooks for a specific event.

    :param settings: Settings dictionary
    :type settings: dict
    :param event_name: Event name to remove skav hooks from
    :type event_name: str
    """
    if "hooks" not in settings:
        return

    hooks = settings["hooks"]
    if event_name not in hooks:
        return

    event_hooks = hooks[event_name]
    if not isinstance(event_hooks, list):
        return

    # Remove entries that contain skav event-log command
    filtered_hooks = []
    for entry in event_hooks:
        if not isinstance(entry, dict):
            filtered_hooks.append(entry)
            continue

        entry_hooks = entry.get("hooks", [])
        if not isinstance(entry_hooks, list):
            filtered_hooks.append(entry)
            continue

        # Filter out skav event-log hooks
        filtered_entry_hooks = [
            h
            for h in entry_hooks
            if not (
                isinstance(h, dict) and "command" in h and "skav event-log" in str(h["command"])
            )
        ]

        # Only keep the entry if it still has hooks or wasn't a skav hook
        if filtered_entry_hooks or not any(
            "skav event-log" in str(h.get("command", ""))
            for h in entry_hooks
            if isinstance(h, dict)
        ):
            entry["hooks"] = filtered_entry_hooks
            filtered_hooks.append(entry)

    hooks[event_name] = filtered_hooks


def add_or_update_hook(
    settings: dict[str, Any], event_name: str, command: str, matcher: str = "*"
) -> None:
    """
    Add or update a hook for a specific event.

    :param settings: Settings dictionary
    :type settings: dict
    :param event_name: Event name to add hook to
    :type event_name: str
    :param command: Command to execute
    :type command: str
    :param matcher: Matcher pattern (default: "*")
    :type matcher: str
    """
    remove_skav_hooks(settings, event_name)

    if "hooks" not in settings:
        settings["hooks"] = {}

    if event_name not in settings["hooks"]:
        settings["hooks"][event_name] = []

    event_hooks = settings["hooks"][event_name]

    hook_entry = {
        "matcher": matcher,
        "hooks": [
            {
                "type": "command",
                "command": command,
            }
        ],
    }

    event_hooks.append(hook_entry)


def install_hooks_cmd(args: argparse.Namespace) -> int:
    """
    Execute the install-hooks command to configure Claude Code hooks.

    :param args: Parsed command line arguments
    :type args: argparse.Namespace
    :return: Exit code (0 for success, 1 for error)
    :rtype: int
    """
    config_logging(service_name="skav", debug=False)

    # Filter events if specified
    events = (
        [event for event in args.events if event in EVENT_NAMES] if args.events else EVENT_NAMES
    )

    settings_file_path = normalize_path("~/.claude/settings.json")

    # Load existing settings
    settings = {}
    if os.path.exists(settings_file_path):
        try:
            with open(settings_file_path, encoding="utf-8") as f:
                settings = json.load(f)
        except json.JSONDecodeError:
            logger.exception("Failed to parse settings.json")
            return 1

    # Get skav executable path
    skav_exec = get_skav_executable()

    cmd = f"{skav_exec} event-log"
    if args.log_dir:
        cmd = f"{cmd} --log-dir {args.log_dir}"

    for event in events:
        add_or_update_hook(settings, event, cmd, matcher="*")

    if args.dry_run:
        logger.info(json.dumps(settings, ensure_ascii=False))
        return 0

    # Create directory if it doesn't exist
    settings_dir = os.path.dirname(settings_file_path)
    if settings_dir and not os.path.exists(settings_dir):
        os.makedirs(settings_dir, exist_ok=True)

    # Write updated settings
    with open(settings_file_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

    return 0
