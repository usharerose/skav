#!/usr/bin/env python3
"""
Claude Code Hook Events Handler

This module provides a generic hook handler for processing all Claude Code hook events.
It reads event data from stdin, parses it with type safety, and logs the structured output.

Usage:
    skav --debug

The handler expects JSON input via stdin conforming to one of the EventInput types
defined in `types.py`. All event types from Claude Code hooks are supported.

Event Types:
    - SessionStart, SessionEnd: Session lifecycle
    - UserPromptSubmit: User message submission
    - PreToolUse, PostToolUse, PostToolUseFailure: Tool execution
    - PermissionRequest: Permission prompts
    - Notification: System notifications
    - SubagentStart, SubagentStop: Subagent management
    - And more...

See https://code.claude.com/docs/en/hooks for official documentation.
"""

import argparse
import json
import logging
import sys

from .log import config_logging
from .types import EventInput

logger = logging.getLogger(__name__)


def parse_cmd_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    :return: Parsed arguments with optional `debug` flag
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description="Claude Code Hook Events Handler",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output",
    )
    return parser.parse_args()


def main(debug: bool = False) -> None:
    """
    Main entry point for hook event processing.

    Reads JSON event data from stdin, configures logging, and logs the event.
    The event data is validated against EventInput types at runtime.

    :param debug: Enable debug logging with plain text format
    :type debug: bool
    :raises SystemExit: Exits with code 0 after processing
    """
    config_logging(service_name="skav", debug=debug)
    event_input: EventInput = json.load(sys.stdin)
    logger.info(f"Received event input: {json.dumps(event_input, ensure_ascii=False, indent=2)}")
    sys.exit(0)


def cli() -> None:
    """
    CLI entry point configured in pyproject.toml.

    Parses command line arguments and invokes main() with the debug flag.
    This is the entry point when running `skav` command.
    """
    cmd_args = parse_cmd_args()
    main(debug=cmd_args.debug)


if __name__ == "__main__":
    cli()
