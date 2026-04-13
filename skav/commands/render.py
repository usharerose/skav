"""
Render command - Render Claude Code sessions to HTML
"""

import argparse
import logging

from ..log import config_logging
from ..renders.renderer import HTMLRenderer
from ..transcripts import ProjectStorage, ProjectStoragePath
from ..utils import normalize_path

logger = logging.getLogger(__name__)


def parse_render_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    Add render command arguments to parser.

    :param parser: Argument parser to add arguments to
    :type parser: argparse.ArgumentParser
    :return: Updated argument parser
    :rtype: argparse.ArgumentParser
    """
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

    return parser


def render_cmd(args: argparse.Namespace) -> int:
    """
    Execute the render command.

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
