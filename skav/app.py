#!/usr/bin/env python3
"""
Skav CLI

Command-line interface for rendering Claude Code transcript sessions to HTML.

Usage:
    skav [-p <project_path>] <session_id> [options]

Examples:
    # Render a specific session from current directory
    skav abc123-def4-5678-9abc

    # Render a specific session from a project
    skav -p /path/to/project abc123-def4-5678-9abc

    # Render with custom output path
    skav abc123-def4 -o session.html

    # Render from current directory explicitly
    skav -p . abc123-def4
"""

import argparse
import logging
import sys

from .log import config_logging
from .renders.renderer import HTMLRenderer
from .transcripts import ProjectStorage, ProjectStoragePath
from .utils import normalize_path

logger = logging.getLogger(__name__)


def parse_cmd_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    :return: Parsed arguments
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description="Render Claude Code transcript sessions to HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-p",
        "--project",
        dest="project_path",
        default=".",
        help="Path to project directory (default: current directory)",
    )

    parser.add_argument(
        "session_id",
        help="Session UUID to render",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output_path",
        default=None,
        help="Output HTML file path (default: <session_id>.html)",
    )

    return parser.parse_args()


def resolve_storage_path(project_path: str) -> ProjectStoragePath:
    """
    Resolve a project path to a ProjectStoragePath.

    :param project_path: Path to project directory
    :type project_path: str
    :return: ProjectStoragePath object
    :rtype: ProjectStoragePath
    :raises FileNotFoundError: If storage path doesn't exist
    """
    # Encode the project path to storage path
    storage_path = ProjectStoragePath.encode(project_path)

    if not storage_path.exists():
        raise FileNotFoundError(
            f"Project storage not found: {storage_path}\n"
            f"Please check the project path: {project_path}"
        )

    return storage_path


def main(args: argparse.Namespace) -> int:
    """
    Main entry point for the CLI.

    :param args: Parsed command line arguments
    :type args: argparse.Namespace
    :return: Exit code (0 for success, 1 for error)
    :rtype: int
    """
    config_logging(service_name="skav", debug=False)

    try:
        storage_path = ProjectStoragePath.encode(args.project_path)
        project_storage = ProjectStorage(storage_path)
        session = project_storage.get_session(args.session_id)
        if session is None:
            logger.error(f"Session not found in {storage_path}: {args.session_id}")
            return 1

        output_path = f"{args.session_id}.html"
        if args.output_path is not None:
            output_path = args.output_path
        output_path = normalize_path(output_path)

        renderer = HTMLRenderer()
        renderer.render_to_file(session, output_path)
        logger.info(f"Successfully rendered session to {output_path}")
        return 0
    except FileNotFoundError as e:
        logger.exception(f"Failed to render session: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Failed to render session: {e}")
        return 1


def cli() -> None:
    """
    CLI entry point configured in pyproject.toml.

    Parses command line arguments and invokes main().
    This is the entry point when running `skav` command.
    """
    cmd_args = parse_cmd_args()
    sys.exit(main(cmd_args))


if __name__ == "__main__":
    cli()
