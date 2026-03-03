#!/usr/bin/env python3
"""
HTML Transcript Renderer

This module provides the HTMLRenderer class for rendering Claude Code
transcript sessions to HTML using Jinja2 templates.
"""

import logging
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..transcripts.session import Session
from .context import Context

logger = logging.getLogger(__name__)


class HTMLRenderer:
    """Render Claude Code transcripts to HTML using Jinja2 templates."""

    def __init__(
        self,
        template_dir: str | Path | None = None,
        escape_html: bool = True,
    ):
        """
        Initialize the HTML renderer.

        Args:
            template_dir: Path to templates directory. Defaults to skav/templates
            escape_html: Whether to escape HTML in content blocks
        """
        if template_dir is None:
            # Default to skav/templates
            template_dir = Path(__file__).parent.parent / "templates"

        self._template_dir = Path(template_dir)
        self._escape_html = escape_html

        # Setup Jinja2 environment
        self._env = Environment(
            loader=FileSystemLoader(str(self._template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

        # Register custom filters
        self._register_filters()

    def _register_filters(self) -> None:
        """Register custom Jinja2 filters."""

        def strftime(dt: Any, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
            """Format datetime object."""
            if dt is None:
                return ""
            return dt.strftime(fmt)

        def number_format(num: Any) -> str:
            """Format number with thousands separator."""
            if num is None:
                return "0"
            return f"{num:,}"

        self._env.filters["strftime"] = strftime
        self._env.filters["number_format"] = number_format

    def render_session(self, session: Session) -> str:
        """
        Render a session to HTML string.

        Args:
            session: Session object to render

        Returns:
            Rendered HTML string
        """
        try:
            # Build template context
            context = Context.from_session(session)

            # Load and render template
            template = self._env.get_template("session.html")
            html = template.render(**context.model_dump())

            logger.info(f"Rendered session {session.session_id}: {context.message_count} messages")

            return html

        except Exception as e:
            logger.error(f"Error rendering session {session.session_id}: {e}")
            raise

    def render_to_file(
        self,
        session: Session,
        output_path: str | Path,
    ) -> Path:
        """
        Render a session and write to file.

        Args:
            session: Session object to render
            output_path: Path to write HTML file

        Returns:
            Path to written file
        """
        output_path = Path(output_path)

        # Render session
        html = self.render_session(session)

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        output_path.write_text(html, encoding="utf-8")

        logger.info(f"Written rendered HTML to {output_path}")

        return output_path
