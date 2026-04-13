#!/usr/bin/env python3
"""
Skav CLI

Command-line interface for Claude Code transcript analysis.

Usage:
    skav <session_id>                    # Render session (backward compatible)
    skav render <session_id>             # Render session to HTML
    skav event-log                       # Log hook events from stdin

Examples:
    # Render a specific session (backward compatible)
    skav abc123-def4-5678-9abc

    # Render with explicit subcommand
    skav render abc123-def4-5678-9abc

    # Render from a specific project
    skav render -p /path/to/project abc123-def4-5678-9abc

    # Log events (used in Claude Code hooks)
    skav event-log --event-type SessionStart
"""

import argparse
import logging
import sys

from . import __version__
from .commands import event_log as event_log_module
from .commands import install_hooks as install_hooks_module
from .commands import render as render_module
from .log import config_logging

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """
    Create the main argument parser with subcommands.

    :return: Configured argument parser
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Claude Code transcript analysis tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    # Create subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="COMMAND",
    )

    # Render subcommand
    render_parser = subparsers.add_parser(
        "render",
        help="Render Claude Code session to HTML",
        description="Render a Claude Code transcript session to HTML file",
    )
    render_module.parse_render_args(render_parser)

    # Event-log subcommand
    event_log_parser = subparsers.add_parser(
        "event-log",
        help="Log Claude Code hook events",
        description=(
            "Collect and log Claude Code hook events from stdin. "
            "Used in Claude Code hook configuration."
        ),
    )
    event_log_module.parse_event_log_args(event_log_parser)

    # Install-hooks subcommand
    install_hooks_parser = subparsers.add_parser(
        "install-hooks",
        help="Register event-log to Claude Code hooks",
        description=(
            "Configure Claude Code settings.json to register event-log command "
            "to all or specific hook events."
        ),
    )
    install_hooks_module.parse_install_hooks_args(install_hooks_parser)

    return parser


def main(argv: list[str] | None = None) -> int:
    """
    Main entry point for the CLI.

    :param argv: Command line arguments (defaults to sys.argv[1:])
    :type argv: list or None
    :return: Exit code (0 for success, non-zero for error)
    :rtype: int
    """
    config_logging(service_name="skav", debug=False)

    if argv is None:
        argv = sys.argv[1:]

    # Special case: if first arg looks like a session ID (UUID format),
    # treat it as a render command for backward compatibility
    if argv and (
        argv[0].startswith("-") is False and len(argv[0]) == 36 and argv[0].count("-") == 4
    ):
        # Prepend "render" to maintain backward compatibility
        argv = ["render"] + argv

    parser = create_parser()
    args = parser.parse_args(argv)

    # Dispatch to appropriate command
    if args.command == "render":
        return render_module.render_cmd(args)
    elif args.command == "event-log":
        return event_log_module.event_log_cmd(args)
    elif args.command == "install-hooks":
        return install_hooks_module.install_hooks_cmd(args)
    else:
        # No command specified
        parser.print_help()
        return 0


def cli() -> None:
    """
    CLI entry point configured in pyproject.toml.

    This is the entry point when running `skav` command.
    """
    sys.exit(main())


if __name__ == "__main__":
    cli()
