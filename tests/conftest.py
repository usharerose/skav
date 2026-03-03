#!/usr/bin/env python3
"""
Pytest configuration and fixtures
"""

import json
import os
import pathlib
import re
import uuid
from typing import Any, Literal

import pytest

from skav.transcripts.project_storage_path import ProjectStoragePath


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


@pytest.fixture(scope="session")
def session_id() -> uuid.UUID:
    return uuid.UUID("12345678-1234-1234-1234-123456789abc")


@pytest.fixture(scope="function")
def workspace_path(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path / ".claude" / "projects"


@pytest.fixture(scope="function")
def made_workspace_path(workspace_path: pathlib.Path) -> pathlib.Path:
    workspace_path.mkdir(parents=True, exist_ok=True)
    return workspace_path


@pytest.fixture(scope="function")
def project_storage_path_obj(
    tmp_path: pathlib.Path,
    workspace_path: pathlib.Path,
) -> ProjectStoragePath:
    """
    Create a valid project storage path for testing.

    This fixture creates a workspace under tmp_path to avoid polluting
    the user's actual ~/.claude/projects directory.
    """
    return ProjectStoragePath.encode(tmp_path / "workspace" / "project", workspace_path)


@pytest.fixture(scope="function")
def made_project_storage_path_obj(
    project_storage_path_obj: ProjectStoragePath,
) -> ProjectStoragePath:
    """Create a project storage path that exists on the filesystem."""
    os.makedirs(str(project_storage_path_obj), exist_ok=True)
    return project_storage_path_obj
