#!/usr/bin/env python3
"""
Pytest configuration and fixtures
"""

import json
import os
import re
from typing import Any, Literal

import pytest


def load_event_input_fixture(
    event_type: Literal[
        "SessionStart",
        "UserPrompt",
        "PreToolUse",
        "PermissionRequest",
        "PostToolUse",
        "SubagentStop",
        "Stop",
    ],
) -> dict[str, Any]:
    to_snake = re.sub("([a-z0-9])([A-Z])", r"\1_\2", event_type).lower()
    filename = f"{to_snake}.json"
    event_input_fixture_path = os.path.join(
        os.path.dirname(__file__),
        "fixtures",
        "events",
        "input",
        filename,
    )
    with open(event_input_fixture_path) as f:
        data: dict[str, Any] = json.load(f)
        return data


@pytest.fixture(scope="session")
def session_start_event_input() -> dict[str, Any]:
    return load_event_input_fixture("SessionStart")


@pytest.fixture(scope="session")
def user_prompt_event_input() -> dict[str, Any]:
    return load_event_input_fixture("UserPrompt")


@pytest.fixture(scope="session")
def pre_tool_use_event_input() -> dict[str, Any]:
    return load_event_input_fixture("PreToolUse")


@pytest.fixture(scope="session")
def permission_request_event_input() -> dict[str, Any]:
    return load_event_input_fixture("PermissionRequest")


@pytest.fixture(scope="session")
def post_tool_use_event_input() -> dict[str, Any]:
    return load_event_input_fixture("PostToolUse")


@pytest.fixture(scope="session")
def subagent_stop_event_input() -> dict[str, Any]:
    return load_event_input_fixture("SubagentStop")


@pytest.fixture(scope="session")
def stop_event_input() -> dict[str, Any]:
    return load_event_input_fixture("Stop")
