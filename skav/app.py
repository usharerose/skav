#!/usr/bin/env python3
"""
Claude Code Hook Events Handler
A generic hook handler that can process all Claude Code hook events
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
    Parse command line arguments
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
    config_logging(service_name="skav", debug=debug)
    event_input: EventInput = json.load(sys.stdin)
    logger.info(f"Received event input: {json.dumps(event_input, ensure_ascii=False, indent=2)}")
    sys.exit(0)


def cli() -> None:
    """
    CLI entrypoint
    """
    cmd_args = parse_cmd_args()
    main(debug=cmd_args.debug)


if __name__ == "__main__":
    cli()
