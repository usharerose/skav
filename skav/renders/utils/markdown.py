#!/usr/bin/env python3
"""
Markdown processing utilities.
"""

import html
import logging

import markdown as md

logger = logging.getLogger(__name__)


def markdown_to_html(text: str) -> str:
    """
    Convert markdown text to HTML.

    Args:
        text: Markdown formatted text

    Returns:
        HTML string
    """
    html_text: str = ""
    try:
        html_text = md.markdown(
            text,
            extensions=["fenced_code", "codehilite", "nl2br"],
        )
    except Exception as e:
        logger.exception(f"Error converting markdown to HTML: {e}")
        html_text = html.escape(text)
    return html_text
