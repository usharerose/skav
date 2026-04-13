"""
Event log command - Collect and log Claude Code hook events
"""

import argparse
import json
import logging
import os
import sys

import platformdirs
from platformdirs.unix import Unix

from ..log import config_logging
from ..types import EventInput
from ..utils import normalize_path

logger = logging.getLogger(__name__)


def get_default_log_dir() -> str:
    """
    Get the default event log directory following XDG Base Directory specification.

    :return: Path to the event log directory
    :rtype: str
    """
    base_dir = platformdirs.user_config_dir("skav")
    if sys.platform == "darwin":
        base_dir = Unix("skav").user_config_dir
    events_dir = os.path.join(base_dir, "events")
    return events_dir


def parse_event_log_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    Add event-log command arguments to parser.

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
        help=(f"Directory to store event logs (default: {get_default_log_dir()})"),
    )

    return parser


def capture_event_input() -> EventInput | None:
    """
    Read event input from stdin.

    :return: Parsed event input, or None if parsing failed
    :rtype: EventInput or None
    """
    try:
        data: EventInput = json.load(sys.stdin)
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from stdin: {e}")
    except Exception as e:
        logger.error(f"Failed to read from stdin: {e}")
    return None


def event_log_cmd(args: argparse.Namespace) -> int:
    """
    Execute the event-log command.

    This command:
    1. Reads event JSON from stdin
    2. Determines the event type
    3. Appends the event to the appropriate log file in JSONL format

    Usage in Claude Code hooks:
        "command": "skav event-log --event-type SessionStart"

    :param args: Parsed command line arguments
    :type args: argparse.Namespace
    :return: Exit code (0 for success, 1 for error)
    :rtype: int
    """
    config_logging(service_name="skav", debug=False)

    event_input = capture_event_input()
    if event_input is None:
        logger.error("No valid event input received from stdin")
        return 1

    session_id: str = event_input["session_id"]
    log_dir = normalize_path(args.log_dir) if args.log_dir else get_default_log_dir()
    os.makedirs(log_dir, exist_ok=True)
    file_path = os.path.join(log_dir, f"{session_id}.jsonl")
    with open(file_path, "a", encoding="utf-8") as f:
        json.dump(event_input, f, ensure_ascii=False)
        f.write("\n")
    return 0
