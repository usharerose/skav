#!/usr/bin/env python3
"""
HTML Transcript Renderer

This module provides the HTMLRenderer class for rendering Claude Code
transcript sessions to HTML using Jinja2 templates.
"""

import datetime
import logging
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..transcripts.session import Session
from ..utils import normalize_path
from .context import Context

logger = logging.getLogger(__name__)


def format_datetime(a_date: datetime.datetime | str | None) -> str:
    if not a_date:
        return ""

    if isinstance(a_date, str):
        try:
            date_obj = datetime.datetime.fromisoformat(a_date.replace("Z", "+00:00"))
            return date_obj.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return a_date
    return a_date.strftime("%Y-%m-%d %H:%M:%S")


class HTMLRenderer:
    """Renderer for Message objects to HTML.

    This renderer produces a flattened HTML structure suitable for
    displaying chat conversations with tool calls and results.
    """

    def __init__(self, templates_dir: str | os.PathLike[str] | None = None):
        if templates_dir is None:
            templates_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "templates",
            )
        self._env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

        self._env.filters["format_timestamp"] = format_datetime

    def render_session(self, session: Session) -> str:
        """
        Render a session to HTML string.

        Args:
            session: Session object to render

        Returns:
            Rendered HTML string
        """
        context = Context.from_session(session)
        template = self._env.get_template("index.html")
        html = template.render(**context.model_dump())
        return html

    def render_to_file(
        self,
        session: Session,
        output_path: str | os.PathLike[str],
    ) -> str:
        output: str = normalize_path(output_path)
        html = self.render_session(session)

        output_dir = os.path.dirname(output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"Written rendered HTML to {output_path}")

        return output
